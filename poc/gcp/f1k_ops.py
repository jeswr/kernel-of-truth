#!/usr/bin/env python3
"""Fork-independent F1-K operational foundations.

This module intentionally excludes the governance layer pending issue #53.
Its selftest is pure/local and never contacts GCP or another network service.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
import os
import re
import stat
import subprocess
import sys
import tempfile
import urllib.parse
import urllib.request
import uuid
from datetime import datetime, timedelta, timezone
from decimal import Decimal, InvalidOperation, localcontext
from pathlib import Path


_METADATA_ROOT = "http://metadata.google.internal/computeMetadata/v1/"
_COMPUTE_SERVICE = "services/6F81-5844-456A"
_CATALOG_ROOT = (
    "https://cloudbilling.googleapis.com/v1/%s/skus" % _COMPUTE_SERVICE
)
_BOOT_ID_PATH = Path("/proc/sys/kernel/random/boot_id")
_MAX_HTTP_BYTES = 64 << 20

_DECIMAL_RE = re.compile(
    r"[+-]?(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)(?:[eE][+-]?[0-9]+)?\Z"
)
_METADATA_PATH_RE = re.compile(
    r"(?:instance|project)(?:/[A-Za-z0-9_.@-]+)+\Z"
)
_PROJECT_ID_RE = re.compile(r"[a-z][a-z0-9-]{4,28}[a-z0-9]\Z")
_INSTANCE_NAME_RE = re.compile(
    r"[a-z](?:[a-z0-9-]{0,61}[a-z0-9])?\Z"
)
_ZONE_RE = re.compile(r"[a-z]+-[a-z0-9]+[0-9]-[a-z]\Z")
_SKU_ID_RE = re.compile(r"[0-9A-F]{4}(?:-[0-9A-F]{4}){2}\Z")
_NUMERIC_ID_RE = re.compile(r"[1-9][0-9]{0,19}\Z")
_RFC3339_RE = re.compile(
    r"(?P<date>[0-9]{4}-[0-9]{2}-[0-9]{2})T"
    r"(?P<clock>[0-9]{2}:[0-9]{2}:[0-9]{2})"
    r"(?P<fraction>\.[0-9]+)?"
    r"(?P<zone>Z|[+-][0-9]{2}:[0-9]{2})\Z"
)


class F1KOpsError(RuntimeError):
    """Fail-closed operational refusal with a stable ERR_* code."""

    def __init__(self, code: str, message: str):
        self.code = code
        self.message = message
        super().__init__("ERR_%s: %s" % (code, message))


def _die(code: str, msg: str) -> None:
    print("ERR_%s: %s" % (code, msg), file=sys.stderr)
    raise SystemExit(2)


def _decimal_value(value, *, field: str) -> Decimal:
    if not isinstance(field, str) or not field:
        raise ValueError("field must be a nonempty string")

    if isinstance(value, bool) or isinstance(value, float):
        raise ValueError(
            "%s must be a decimal string, integer, or Decimal; "
            "binary float is forbidden" % field
        )

    if isinstance(value, Decimal):
        parsed = value
    elif isinstance(value, int):
        parsed = Decimal(value)
    elif isinstance(value, str):
        if value != value.strip() or not _DECIMAL_RE.fullmatch(value):
            raise ValueError(
                "%s is not a strict decimal: %r" % (field, value)
            )
        try:
            parsed = Decimal(value)
        except InvalidOperation as exc:
            raise ValueError(
                "%s is not a decimal: %r" % (field, value)
            ) from exc
    else:
        raise ValueError(
            "%s must be a decimal string, integer, or Decimal, got %s"
            % (field, type(value).__name__)
        )

    if not parsed.is_finite():
        raise ValueError("%s must be finite" % field)
    return parsed


def canonical_decimal(value, *, field) -> str:
    """Return an exact finite positive decimal in exponent-free form.

    Python floats are refused rather than converted through their binary
    representation. No Decimal normalization operation that could apply the
    ambient Decimal precision is used.
    """
    parsed = _decimal_value(value, field=field)
    if parsed <= 0:
        raise ValueError("%s must be > 0" % field)

    rendered = format(parsed, "f")
    if "." in rendered:
        rendered = rendered.rstrip("0").rstrip(".")
    return rendered


def canonical_json_bytes(record) -> bytes:
    """Encode sorted compact UTF-8 JSON followed by exactly one newline."""
    text = json.dumps(
        record,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )
    return text.encode("utf-8", errors="strict") + b"\n"


def _normalized_final_path(path) -> Path:
    raw = os.fspath(path)
    if not isinstance(raw, str):
        raise TypeError("path must be text, not bytes")
    if not raw or "\x00" in raw or os.path.normpath(raw) != raw:
        raise ValueError(
            "final path is empty or not lexically normalized: %r" % raw
        )

    result = Path(raw)
    if result.name in ("", ".", ".."):
        raise ValueError(
            "final path has no normal file component: %r" % raw
        )
    return result


def _reject_symlink_or_special_final(path: Path) -> None:
    try:
        metadata = path.lstat()
    except FileNotFoundError:
        return

    if stat.S_ISLNK(metadata.st_mode):
        raise ValueError(
            "refusing symlinked final component: %s" % path
        )
    if not stat.S_ISREG(metadata.st_mode):
        raise ValueError(
            "refusing non-regular final component: %s" % path
        )


def _write_all(fd: int, payload: bytes) -> None:
    view = memoryview(payload)
    offset = 0
    while offset < len(view):
        written = os.write(fd, view[offset:])
        if written <= 0:
            raise OSError("short write while publishing JSON")
        offset += written


def atomic_write_json(path, record, *, mode=0o600) -> str:
    """Durably replace path with canonical JSON and return its SHA-256.

    The temporary file is created in the destination directory. The file is
    fsynced before os.replace, and the directory is fsynced afterward.
    """
    final = _normalized_final_path(path)
    if (
        isinstance(mode, bool)
        or not isinstance(mode, int)
        or not 0 <= mode <= 0o777
    ):
        raise ValueError("mode must contain only permission bits")

    parent = final.parent
    try:
        parent_stat = parent.stat()
    except OSError as exc:
        raise OSError(
            "cannot stat destination directory %s: %s" % (parent, exc)
        ) from exc
    if not stat.S_ISDIR(parent_stat.st_mode):
        raise ValueError(
            "destination parent is not a directory: %s" % parent
        )

    _reject_symlink_or_special_final(final)

    payload = canonical_json_bytes(record)
    expected_sha256 = hashlib.sha256(payload).hexdigest()
    dir_flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
    dir_fd = os.open(os.fspath(parent), dir_flags)
    temp_fd = -1
    temp_name = None

    try:
        temp_fd, temp_name = tempfile.mkstemp(
            prefix=".%s." % final.name,
            suffix=".tmp",
            dir=os.fspath(parent),
        )
        os.fchmod(temp_fd, mode)
        _write_all(temp_fd, payload)
        os.fsync(temp_fd)
        os.close(temp_fd)
        temp_fd = -1

        # Never silently replace a pre-existing final-component symlink.
        _reject_symlink_or_special_final(final)
        os.replace(temp_name, os.fspath(final))
        temp_name = None
        os.fsync(dir_fd)
    finally:
        if temp_fd >= 0:
            os.close(temp_fd)
        if temp_name is not None:
            try:
                os.unlink(temp_name)
            except FileNotFoundError:
                pass
        os.close(dir_fd)

    return expected_sha256


def _validate_metadata_path(path: str) -> None:
    if not isinstance(path, str) or not _METADATA_PATH_RE.fullmatch(path):
        raise F1KOpsError(
            "F1K_METADATA_PATH",
            "metadata path must be a normalized instance/... or "
            "project/... path: %r" % (path,),
        )


def _metadata_http_get(path: str, timeout_s: float) -> bytes:
    url = _METADATA_ROOT + urllib.parse.quote(
        path, safe="/-_.@"
    )
    request = urllib.request.Request(
        url,
        headers={"Metadata-Flavor": "Google"},
        method="GET",
    )

    # Metadata must never be reached through an ambient HTTP proxy.
    opener = urllib.request.build_opener(
        urllib.request.ProxyHandler({})
    )
    with opener.open(request, timeout=timeout_s) as response:
        if response.headers.get("Metadata-Flavor") != "Google":
            raise F1KOpsError(
                "F1K_METADATA",
                "metadata response omitted Metadata-Flavor: Google",
            )
        body = response.read(_MAX_HTTP_BYTES + 1)

    if len(body) > _MAX_HTTP_BYTES:
        raise F1KOpsError(
            "F1K_METADATA", "metadata response exceeds size limit"
        )
    return body


def read_live_instance_metadata(
    path, *, timeout_s=2.0, transport=None
) -> str:
    """Read one GCE metadata path.

    An injected transport is called as transport(path, timeout_s) and must
    return str or bytes. The default sends Metadata-Flavor: Google directly
    to the fixed GCE metadata host.
    """
    _validate_metadata_path(path)

    if isinstance(timeout_s, bool):
        raise ValueError("timeout_s must be finite and > 0")
    try:
        timeout = float(timeout_s)
    except (TypeError, ValueError) as exc:
        raise ValueError(
            "timeout_s must be finite and > 0"
        ) from exc
    if not math.isfinite(timeout) or timeout <= 0:
        raise ValueError("timeout_s must be finite and > 0")

    getter = _metadata_http_get if transport is None else transport
    try:
        raw = getter(path, timeout)
    except F1KOpsError:
        raise
    except Exception as exc:
        raise F1KOpsError(
            "F1K_METADATA",
            "metadata read failed for %s: %s" % (path, exc),
        ) from exc

    if isinstance(raw, bytes):
        try:
            value = raw.decode("utf-8", errors="strict")
        except UnicodeDecodeError as exc:
            raise F1KOpsError(
                "F1K_METADATA",
                "metadata %s is not UTF-8" % path,
            ) from exc
    elif isinstance(raw, str):
        value = raw
    else:
        raise F1KOpsError(
            "F1K_METADATA",
            "metadata transport returned %s for %s"
            % (type(raw).__name__, path),
        )

    if not value or "\x00" in value:
        raise F1KOpsError(
            "F1K_METADATA",
            "metadata %s is empty/malformed" % path,
        )
    if len(value.encode("utf-8")) > _MAX_HTTP_BYTES:
        raise F1KOpsError(
            "F1K_METADATA",
            "metadata %s exceeds size limit" % path,
        )
    return value


def _json_no_constant(value: str):
    raise ValueError("non-finite JSON constant %s" % value)


def _gcloud_compute_get(
    *, project_id: str, zone: str, instance_name: str
) -> dict:
    command = [
        "gcloud",
        "compute",
        "instances",
        "describe",
        instance_name,
        "--project",
        project_id,
        "--zone",
        zone,
        "--format=json",
        "--quiet",
    ]
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=20,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise F1KOpsError(
            "F1K_COMPUTE",
            "gcloud instances describe failed: %s" % exc,
        ) from exc

    if result.returncode != 0:
        tail = (
            (result.stderr or result.stdout)
            .strip()
            .splitlines()[-1:]
        )
        raise F1KOpsError(
            "F1K_COMPUTE",
            "gcloud instances describe exit %d%s"
            % (
                result.returncode,
                ": " + tail[0] if tail else "",
            ),
        )

    try:
        value = json.loads(
            result.stdout,
            parse_float=Decimal,
            parse_constant=_json_no_constant,
        )
    except (TypeError, ValueError) as exc:
        raise F1KOpsError(
            "F1K_COMPUTE",
            "malformed Compute JSON: %s" % exc,
        ) from exc

    if not isinstance(value, dict):
        raise F1KOpsError(
            "F1K_COMPUTE",
            "Compute response is not an object",
        )
    return value


def _strict_string(value, *, field: str, pattern=None) -> str:
    if (
        not isinstance(value, str)
        or not value
        or value != value.strip()
    ):
        raise F1KOpsError(
            "F1K_IDENTITY",
            "%s is missing/malformed" % field,
        )

    if pattern is not None and not pattern.fullmatch(value):
        raise F1KOpsError(
            "F1K_IDENTITY",
            "%s is malformed: %r" % (field, value),
        )
    return value


def _utc_timestamp(value, *, field: str, code: str) -> str:
    """Validate RFC3339 and normalize its offset to UTC Z exactly."""
    if not isinstance(value, str):
        raise F1KOpsError(
            code,
            "%s must be RFC3339: %r" % (field, value),
        )

    match = _RFC3339_RE.fullmatch(value)
    if match is None:
        raise F1KOpsError(
            code,
            "%s must be RFC3339: %r" % (field, value),
        )

    try:
        base = datetime.strptime(
            match.group("date") + "T" + match.group("clock"),
            "%Y-%m-%dT%H:%M:%S",
        )
    except ValueError as exc:
        raise F1KOpsError(
            code,
            "%s is not a real timestamp: %r" % (field, value),
        ) from exc

    zone_text = match.group("zone")
    if zone_text == "Z":
        offset = timezone.utc
    else:
        hours = int(zone_text[1:3])
        minutes = int(zone_text[4:6])
        if hours > 23 or minutes > 59:
            raise F1KOpsError(
                code,
                "%s has an invalid UTC offset: %r" % (field, value),
            )
        delta = timedelta(hours=hours, minutes=minutes)
        if zone_text[0] == "-":
            delta = -delta
        offset = timezone(delta)

    converted = base.replace(tzinfo=offset).astimezone(timezone.utc)
    return (
        converted.strftime("%Y-%m-%dT%H:%M:%S")
        + (match.group("fraction") or "")
        + "Z"
    )


def _resource_tail(
    value, *, field: str, collection: str
) -> str:
    text = _strict_string(value, field=field)
    marker = "/%s/" % collection
    if marker not in text:
        raise F1KOpsError(
            "F1K_IDENTITY",
            "%s has wrong resource form" % field,
        )

    tail = text.rsplit(marker, 1)[-1]
    if "/" in tail or not tail:
        raise F1KOpsError(
            "F1K_IDENTITY",
            "%s has wrong resource form" % field,
        )
    return tail


def _read_boot_id() -> str:
    try:
        raw = _BOOT_ID_PATH.read_text(
            encoding="ascii"
        ).strip()
        parsed = uuid.UUID(raw)
    except (OSError, UnicodeError, ValueError) as exc:
        raise F1KOpsError(
            "F1K_IDENTITY",
            "cannot read a valid local boot_id",
        ) from exc

    canonical = str(parsed)
    if raw.lower() != canonical:
        raise F1KOpsError(
            "F1K_IDENTITY",
            "local boot_id is not canonical",
        )
    return canonical


def resolve_live_instance_identity(
    *, metadata_transport=None, compute_transport=None
) -> dict:
    """Resolve and cross-bind local metadata to Compute instances.get.

    compute_transport is called with keyword arguments project_id, zone, and
    instance_name. It must return a full Compute instance object.
    """
    def metadata(path):
        return read_live_instance_metadata(
            path, transport=metadata_transport
        )

    instance_id = _strict_string(
        metadata("instance/id"),
        field="metadata instance/id",
        pattern=_NUMERIC_ID_RE,
    )
    instance_name = _strict_string(
        metadata("instance/name"),
        field="metadata instance/name",
        pattern=_INSTANCE_NAME_RE,
    )
    project_id = _strict_string(
        metadata("project/project-id"),
        field="metadata project/project-id",
        pattern=_PROJECT_ID_RE,
    )
    project_number = _strict_string(
        metadata("project/numeric-project-id"),
        field="metadata project/numeric-project-id",
        pattern=_NUMERIC_ID_RE,
    )

    zone_resource = _strict_string(
        metadata("instance/zone"),
        field="metadata instance/zone",
    )
    zone_match = re.fullmatch(
        r"projects/([1-9][0-9]{0,19})/"
        r"zones/([a-z]+-[a-z0-9]+[0-9]-[a-z])",
        zone_resource,
    )
    if (
        zone_match is None
        or zone_match.group(1) != project_number
    ):
        raise F1KOpsError(
            "F1K_IDENTITY",
            "metadata zone is malformed/project-mismatched",
        )
    zone = zone_match.group(2)

    machine_resource = _strict_string(
        metadata("instance/machine-type"),
        field="metadata instance/machine-type",
    )
    machine_match = re.fullmatch(
        r"projects/([1-9][0-9]{0,19})/"
        r"machineTypes/([a-z][a-z0-9-]{0,62})",
        machine_resource,
    )
    if (
        machine_match is None
        or machine_match.group(1) != project_number
    ):
        raise F1KOpsError(
            "F1K_IDENTITY",
            "metadata machine type is malformed/project-mismatched",
        )
    machine_type = machine_match.group(2)

    getter = (
        _gcloud_compute_get
        if compute_transport is None
        else compute_transport
    )
    try:
        compute = getter(
            project_id=project_id,
            zone=zone,
            instance_name=instance_name,
        )
    except F1KOpsError:
        raise
    except Exception as exc:
        raise F1KOpsError(
            "F1K_COMPUTE",
            "Compute instance lookup failed: %s" % exc,
        ) from exc

    if not isinstance(compute, dict):
        raise F1KOpsError(
            "F1K_COMPUTE",
            "Compute transport returned non-object",
        )

    compute_id = _strict_string(
        compute.get("id"),
        field="Compute id",
        pattern=_NUMERIC_ID_RE,
    )
    compute_name = _strict_string(
        compute.get("name"),
        field="Compute name",
        pattern=_INSTANCE_NAME_RE,
    )

    if compute_name != instance_name:
        raise F1KOpsError(
            "F1K_IDENTITY_RECREATED",
            "Compute name %r != metadata name %r"
            % (compute_name, instance_name),
        )
    if compute_id != instance_id:
        raise F1KOpsError(
            "F1K_IDENTITY_RECREATED",
            "Compute numeric id %s != local metadata id %s; "
            "same-name instance may have been recreated"
            % (compute_id, instance_id),
        )

    compute_zone = _resource_tail(
        compute.get("zone"),
        field="Compute zone",
        collection="zones",
    )
    compute_machine = _resource_tail(
        compute.get("machineType"),
        field="Compute machineType",
        collection="machineTypes",
    )
    if (
        compute_zone != zone
        or compute_machine != machine_type
    ):
        raise F1KOpsError(
            "F1K_IDENTITY",
            "Compute zone/machine type does not match local metadata",
        )

    self_link = _strict_string(
        compute.get("selfLink"),
        field="Compute selfLink",
    )
    wanted_suffix = (
        "/projects/%s/zones/%s/instances/%s"
        % (project_id, zone, instance_name)
    )
    if not self_link.endswith(wanted_suffix):
        raise F1KOpsError(
            "F1K_IDENTITY",
            "Compute selfLink is not bound to metadata "
            "project/zone/name",
        )

    scheduling = compute.get("scheduling")
    if not isinstance(scheduling, dict):
        raise F1KOpsError(
            "F1K_IDENTITY",
            "Compute scheduling is missing",
        )

    provisioning_model = scheduling.get(
        "provisioningModel"
    )
    if provisioning_model != "SPOT":
        raise F1KOpsError(
            "F1K_IDENTITY_MODEL",
            "Compute scheduling.provisioningModel %r != SPOT"
            % provisioning_model,
        )

    last_start = _utc_timestamp(
        compute.get("lastStartTimestamp"),
        field="Compute lastStartTimestamp",
        code="F1K_IDENTITY",
    )
    boot_id = _read_boot_id()

    # Detect an injected or otherwise unstable identity resolution.
    if metadata("instance/id") != instance_id:
        raise F1KOpsError(
            "F1K_IDENTITY_RECREATED",
            "local metadata instance ID changed during resolution",
        )

    return {
        "instance_id": instance_id,
        "name": instance_name,
        "project_id": project_id,
        "project_number": project_number,
        "zone": zone,
        "machine_type": machine_type,
        "provisioning_model": provisioning_model,
        "last_start_timestamp": last_start,
        "boot_id": boot_id,
    }


def _catalog_http_list(
    *, project_id: str, region: str
) -> dict:
    del project_id, region

    try:
        token_raw = _metadata_http_get(
            "instance/service-accounts/default/token",
            2.0,
        )
        token_doc = json.loads(
            token_raw.decode("utf-8")
        )
        token = token_doc.get("access_token")
        if not isinstance(token, str) or not token:
            raise ValueError("access_token missing")
    except Exception as exc:
        if isinstance(exc, F1KOpsError):
            raise
        raise F1KOpsError(
            "F1K_RATE_QUOTE",
            "cannot obtain attached service-account token: %s"
            % exc,
        ) from exc

    all_skus = []
    page_token = None
    seen_tokens = set()

    while True:
        query = {
            "currencyCode": "USD",
            "pageSize": "5000",
        }
        if page_token is not None:
            query["pageToken"] = page_token

        url = (
            _CATALOG_ROOT
            + "?"
            + urllib.parse.urlencode(query)
        )
        request = urllib.request.Request(
            url,
            headers={
                "Authorization": "Bearer " + token,
                "Accept": "application/json",
            },
            method="GET",
        )

        try:
            with urllib.request.urlopen(
                request, timeout=20
            ) as response:
                body = response.read(_MAX_HTTP_BYTES + 1)

            if len(body) > _MAX_HTTP_BYTES:
                raise ValueError(
                    "catalog page exceeds size limit"
                )

            page = json.loads(
                body.decode("utf-8"),
                parse_float=Decimal,
                parse_constant=_json_no_constant,
            )
        except Exception as exc:
            raise F1KOpsError(
                "F1K_RATE_QUOTE",
                "Cloud Billing Catalog request failed: %s"
                % exc,
            ) from exc

        if (
            not isinstance(page, dict)
            or not isinstance(page.get("skus"), list)
        ):
            raise F1KOpsError(
                "F1K_RATE_QUOTE",
                "Cloud Billing Catalog returned malformed JSON",
            )

        all_skus.extend(page["skus"])
        page_token = page.get("nextPageToken")
        if not page_token:
            break
        if (
            not isinstance(page_token, str)
            or page_token in seen_tokens
        ):
            raise F1KOpsError(
                "F1K_RATE_QUOTE",
                "Cloud Billing Catalog pagination is malformed",
            )
        seen_tokens.add(page_token)

    return {"skus": all_skus}


_COMPONENT_SPECS = (
    {
        "component": "n2d_vcpu",
        "description": re.compile(
            r"Spot Preemptible N2D AMD Instance Core "
            r"running in .+\Z"
        ),
        "resource_family": "Compute",
        "usage_type": "Preemptible",
        "usage_unit": "h",
        "quantity": Decimal(8),
    },
    {
        "component": "n2d_ram_gib",
        "description": re.compile(
            r"Spot Preemptible N2D AMD Instance Ram "
            r"running in .+\Z"
        ),
        "resource_family": "Compute",
        "usage_type": "Preemptible",
        "usage_unit": "GiBy.h",
        "quantity": Decimal(64),
    },
    {
        "component": "local_ssd_gib",
        "description": re.compile(
            r"SSD backed Local Storage attached to Spot "
            r"Preemptible VMs(?: in .+)?\Z"
        ),
        "resource_family": "Storage",
        "usage_type": "Preemptible",
        "usage_unit": "GiBy.h",
        "quantity": None,
    },
)


def _catalog_skus(response) -> list:
    if isinstance(response, dict):
        if response.get("nextPageToken"):
            raise F1KOpsError(
                "F1K_RATE_QUOTE",
                "injected Catalog response is incomplete "
                "(nextPageToken present)",
            )
        skus = response.get("skus")
    else:
        skus = response

    if not isinstance(skus, (list, tuple)):
        raise F1KOpsError(
            "F1K_RATE_QUOTE",
            "Catalog response has no SKU list",
        )
    if not skus:
        raise F1KOpsError(
            "F1K_RATE_QUOTE",
            "Catalog quote returned no SKUs",
        )
    if not all(isinstance(item, dict) for item in skus):
        raise F1KOpsError(
            "F1K_RATE_QUOTE",
            "Catalog SKU list is malformed",
        )
    return list(skus)


def _sku_matches(
    sku: dict, spec: dict, *, region: str
) -> bool:
    description = sku.get("description")
    if (
        not isinstance(description, str)
        or not spec["description"].fullmatch(description)
    ):
        return False

    if sku.get("serviceProviderName") != "Google":
        return False

    category = sku.get("category")
    if not isinstance(category, dict):
        return False
    if (
        category.get("serviceDisplayName") != "Compute Engine"
        or category.get("resourceFamily")
        != spec["resource_family"]
        or category.get("usageType")
        != spec["usage_type"]
        or not isinstance(
            category.get("resourceGroup"), str
        )
        or not category.get("resourceGroup")
    ):
        return False

    service_regions = sku.get("serviceRegions")
    if (
        not isinstance(service_regions, list)
        or not service_regions
        or not all(
            isinstance(value, str)
            for value in service_regions
        )
        or len(set(service_regions)) != len(service_regions)
        or region not in service_regions
    ):
        return False

    geo = sku.get("geoTaxonomy")
    if not isinstance(geo, dict):
        return False
    geo_regions = geo.get("regions")
    if (
        geo.get("type")
        not in ("REGIONAL", "MULTI_REGIONAL")
        or not isinstance(geo_regions, list)
        or region not in geo_regions
    ):
        return False

    return True


def _parse_catalog_time(
    value, *, field: str
) -> tuple[str, datetime]:
    canonical = _utc_timestamp(
        value,
        field=field,
        code="F1K_RATE_SKU",
    )
    parsed = datetime.fromisoformat(
        canonical[:-1] + "+00:00"
    )
    return canonical, parsed


def _latest_pricing(
    sku: dict, *, observed: datetime
) -> tuple[dict, str]:
    timeline = sku.get("pricingInfo")
    if not isinstance(timeline, list) or not timeline:
        raise F1KOpsError(
            "F1K_RATE_SKU",
            "SKU pricingInfo is missing",
        )

    candidates = []
    seen = set()

    for index, info in enumerate(timeline):
        if not isinstance(info, dict):
            raise F1KOpsError(
                "F1K_RATE_SKU",
                "SKU pricingInfo is malformed",
            )

        effective, parsed = _parse_catalog_time(
            info.get("effectiveTime"),
            field="pricingInfo[%d].effectiveTime" % index,
        )
        if effective in seen:
            raise F1KOpsError(
                "F1K_RATE_SKU",
                "duplicate pricing effectiveTime in SKU",
            )
        seen.add(effective)

        if parsed <= observed:
            candidates.append(
                (parsed, info, effective)
            )

    if not candidates:
        raise F1KOpsError(
            "F1K_RATE_SKU",
            "SKU has no pricing effective at observation time",
        )

    _, info, effective = max(
        candidates, key=lambda item: item[0]
    )
    return info, effective


def _money_decimal(money, *, field: str) -> Decimal:
    if (
        not isinstance(money, dict)
        or money.get("currencyCode") != "USD"
    ):
        raise F1KOpsError(
            "F1K_RATE_SKU",
            "%s is not USD Money" % field,
        )

    units = money.get("units", "0")
    nanos = money.get("nanos", 0)

    if (
        not isinstance(units, str)
        or not re.fullmatch(r"-?[0-9]+", units)
    ):
        raise F1KOpsError(
            "F1K_RATE_SKU",
            "%s.units is malformed" % field,
        )
    if (
        isinstance(nanos, bool)
        or not isinstance(nanos, int)
    ):
        raise F1KOpsError(
            "F1K_RATE_SKU",
            "%s.nanos is malformed" % field,
        )
    if not -999999999 <= nanos <= 999999999:
        raise F1KOpsError(
            "F1K_RATE_SKU",
            "%s.nanos is out of range" % field,
        )

    whole = int(units)
    if (
        (whole > 0 and nanos < 0)
        or (whole < 0 and nanos > 0)
    ):
        raise F1KOpsError(
            "F1K_RATE_SKU",
            "%s Money signs disagree" % field,
        )

    value = Decimal(whole) + Decimal(nanos).scaleb(-9)
    if not value.is_finite() or value <= 0:
        raise F1KOpsError(
            "F1K_RATE_SKU",
            "%s must be finite and > 0" % field,
        )
    return value


def _price_for_sku(
    sku: dict, spec: dict, *, observed: datetime
) -> tuple[Decimal, str, str]:
    sku_id = sku.get("skuId")
    if (
        not isinstance(sku_id, str)
        or not _SKU_ID_RE.fullmatch(sku_id)
    ):
        raise F1KOpsError(
            "F1K_RATE_SKU",
            "selected SKU has malformed skuId",
        )

    if (
        sku.get("name")
        != "%s/skus/%s" % (_COMPUTE_SERVICE, sku_id)
    ):
        raise F1KOpsError(
            "F1K_RATE_SKU",
            "selected SKU name/id/service binding is malformed",
        )

    info, effective = _latest_pricing(
        sku, observed=observed
    )

    conversion = info.get("currencyConversionRate")
    if conversion is not None:
        try:
            conversion_value = _decimal_value(
                conversion,
                field="currencyConversionRate",
            )
        except ValueError as exc:
            raise F1KOpsError(
                "F1K_RATE_SKU", str(exc)
            ) from exc
        if conversion_value != 1:
            raise F1KOpsError(
                "F1K_RATE_SKU",
                "Catalog USD currencyConversionRate != 1",
            )

    aggregation = info.get("aggregationInfo")
    if aggregation not in (None, {}):
        if isinstance(aggregation, dict):
            meaningful = {
                key: value
                for key, value in aggregation.items()
                if value
                not in (
                    None,
                    0,
                    "AGGREGATION_LEVEL_UNSPECIFIED",
                    "AGGREGATION_INTERVAL_UNSPECIFIED",
                )
            }
        else:
            meaningful = {"invalid": aggregation}

        if meaningful:
            raise F1KOpsError(
                "F1K_RATE_SKU",
                "selected SKU requires unsupported aggregation",
            )

    expression = info.get("pricingExpression")
    if not isinstance(expression, dict):
        raise F1KOpsError(
            "F1K_RATE_SKU",
            "pricingExpression is missing",
        )

    if expression.get("usageUnit") != spec["usage_unit"]:
        raise F1KOpsError(
            "F1K_RATE_SKU",
            "%s usageUnit %r != %s"
            % (
                spec["component"],
                expression.get("usageUnit"),
                spec["usage_unit"],
            ),
        )

    tiers = expression.get("tieredRates")
    if not isinstance(tiers, list) or len(tiers) != 1:
        raise F1KOpsError(
            "F1K_RATE_SKU",
            "selected SKU must have exactly one price tier",
        )

    tier = tiers[0]
    if not isinstance(tier, dict):
        raise F1KOpsError(
            "F1K_RATE_SKU",
            "selected SKU tier is malformed",
        )

    try:
        start = _decimal_value(
            tier.get("startUsageAmount", 0),
            field="tier.startUsageAmount",
        )
    except ValueError as exc:
        raise F1KOpsError(
            "F1K_RATE_SKU", str(exc)
        ) from exc

    if start != 0:
        raise F1KOpsError(
            "F1K_RATE_SKU",
            "selected SKU price tier does not start at zero",
        )

    unit_price = _money_decimal(
        tier.get("unitPrice"),
        field="%s unitPrice" % spec["component"],
    )
    return unit_price, effective, sku_id


def resolve_live_rate(
    *,
    project_id,
    zone,
    machine_type,
    local_ssd_count,
    observed_at_utc=None,
    catalog_transport=None,
) -> tuple[str, dict]:
    """Resolve the N2D + Local SSD all-in Spot construction rate.

    catalog_transport is called with keyword arguments project_id and region.
    It returns either a services.skus.list response object or a SKU sequence.
    """
    if (
        not isinstance(project_id, str)
        or not _PROJECT_ID_RE.fullmatch(project_id)
    ):
        raise F1KOpsError(
            "F1K_RATE_TARGET",
            "project_id is malformed",
        )
    if (
        not isinstance(zone, str)
        or not _ZONE_RE.fullmatch(zone)
    ):
        raise F1KOpsError(
            "F1K_RATE_TARGET",
            "zone is malformed",
        )

    region = zone.rsplit("-", 1)[0]
    if region != "us-central1":
        raise F1KOpsError(
            "F1K_RATE_TARGET",
            "construction rate is defined only for us-central1",
        )
    if machine_type != "n2d-highmem-8":
        raise F1KOpsError(
            "F1K_RATE_TARGET",
            "machine_type %r != n2d-highmem-8"
            % machine_type,
        )
    if (
        isinstance(local_ssd_count, bool)
        or not isinstance(local_ssd_count, int)
        or local_ssd_count
        not in (1, 2, 4, 8, 16, 24)
    ):
        raise F1KOpsError(
            "F1K_RATE_TARGET",
            "local_ssd_count is not valid for N2D",
        )

    if observed_at_utc is None:
        observed_at_utc = (
            datetime.now(timezone.utc)
            .isoformat(timespec="seconds")
            .replace("+00:00", "Z")
        )

    observed_at_utc = _utc_timestamp(
        observed_at_utc,
        field="observed_at_utc",
        code="F1K_RATE_TARGET",
    )
    observed = datetime.fromisoformat(
        observed_at_utc[:-1] + "+00:00"
    )

    transport = (
        _catalog_http_list
        if catalog_transport is None
        else catalog_transport
    )
    try:
        response = transport(
            project_id=project_id,
            region=region,
        )
    except F1KOpsError:
        raise
    except Exception as exc:
        raise F1KOpsError(
            "F1K_RATE_QUOTE",
            "Cloud Billing Catalog quote failed: %s" % exc,
        ) from exc

    skus = _catalog_skus(response)
    selected = []
    selected_ids = set()
    total = Decimal(0)

    with localcontext() as context:
        context.prec = 80

        for spec_template in _COMPONENT_SPECS:
            spec = dict(spec_template)
            if spec["component"] == "local_ssd_gib":
                spec["quantity"] = Decimal(
                    local_ssd_count * 375
                )

            matches = [
                sku
                for sku in skus
                if _sku_matches(
                    sku, spec, region=region
                )
            ]
            if len(matches) != 1:
                raise F1KOpsError(
                    "F1K_RATE_SKU",
                    "%s requires exactly one region/usage-matched "
                    "SKU; found %d"
                    % (spec["component"], len(matches)),
                )

            sku = matches[0]
            unit_price, effective, sku_id = _price_for_sku(
                sku,
                spec,
                observed=observed,
            )

            if sku_id in selected_ids:
                raise F1KOpsError(
                    "F1K_RATE_SKU",
                    "one SKU matched multiple components",
                )
            selected_ids.add(sku_id)

            quantity = spec["quantity"]
            hourly = unit_price * quantity
            if not hourly.is_finite() or hourly <= 0:
                raise F1KOpsError(
                    "F1K_RATE_SKU",
                    "%s hourly price is invalid"
                    % spec["component"],
                )

            total += hourly
            category = sku["category"]
            selected.append(
                {
                    "component": spec["component"],
                    "description": sku["description"],
                    "hourly_usd_decimal": canonical_decimal(
                        hourly,
                        field="%s hourly price"
                        % spec["component"],
                    ),
                    "pricing_effective_time": effective,
                    "quantity_decimal": canonical_decimal(
                        quantity,
                        field="%s quantity"
                        % spec["component"],
                    ),
                    "resource_family": category[
                        "resourceFamily"
                    ],
                    "resource_group": category[
                        "resourceGroup"
                    ],
                    "service_regions": sorted(
                        sku["serviceRegions"]
                    ),
                    "sku_id": sku_id,
                    "unit_price_usd_decimal":
                        canonical_decimal(
                            unit_price,
                            field="%s unit price"
                            % spec["component"],
                        ),
                    "usage_type": category["usageType"],
                    "usage_unit": spec["usage_unit"],
                }
            )

    rate = canonical_decimal(
        total, field="all-in Spot rate"
    )
    evidence = {
        "components": selected,
        "currency": "USD",
        "excluded": [
            "boot_or_control_pd",
            "cloud_storage",
            "egress",
            "logging",
            "operations",
        ],
        "local_ssd_count_decimal": canonical_decimal(
            local_ssd_count,
            field="local_ssd_count",
        ),
        "machine_type": machine_type,
        "observed_at_utc": observed_at_utc,
        "project_id": project_id,
        "region": region,
        "schema": "kot-f1k-rate-evidence/1",
        "sha256_rule": (
            "sha256(canonical_json_bytes("
            "record_without_sha256))"
        ),
        "source": (
            "cloud-billing-catalog-v1/"
            "services.skus.list"
        ),
        "source_service": _COMPUTE_SERVICE,
        "usd_per_hour_decimal": rate,
        "zone": zone,
    }
    evidence["sha256"] = hashlib.sha256(
        canonical_json_bytes(evidence)
    ).hexdigest()
    return rate, evidence


# --- governance layer (ledger/lease/attestation) pending issue #53 A/B/C ---


def selftest() -> int:
    """Run the $0 pure/local fork-independent foundation oracle."""
    print(
        "SELFTEST SCOPE: $0 pure/local fork-independent foundation; "
        "fake metadata, Compute, and Catalog transports only; "
        "NO network, gcloud, GCP resources, or spend."
    )
    passed = 0
    total = 0

    def check(label, function):
        nonlocal passed, total
        total += 1
        try:
            ok = bool(function())
            detail = ""
        except Exception as exc:
            ok = False
            detail = " (%s: %s)" % (
                type(exc).__name__,
                exc,
            )

        print(
            "  %s%s%s"
            % (
                "ok:  " if ok else "FAIL: ",
                label,
                detail,
            )
        )
        passed += int(ok)

    def refuses_value(function):
        try:
            function()
        except ValueError:
            return True
        return False

    def refuses_ops(code, function):
        try:
            function()
        except F1KOpsError as exc:
            return exc.code == code
        return False

    check(
        "decimal equivalents 0.190 and 1.90e-1 -> 0.19",
        lambda: (
            canonical_decimal(
                "0.190", field="rate"
            ) == "0.19"
            and canonical_decimal(
                "1.90e-1", field="rate"
            ) == "0.19"
        ),
    )
    check(
        "decimal precision 0.10000000000000001 preserved",
        lambda: canonical_decimal(
            "0.10000000000000001",
            field="rate",
        ) == "0.10000000000000001",
    )
    check(
        "binary float refused",
        lambda: refuses_value(
            lambda: canonical_decimal(
                0.19, field="rate"
            )
        ),
    )
    check(
        "decimal NaN refused",
        lambda: refuses_value(
            lambda: canonical_decimal(
                "NaN", field="rate"
            )
        ),
    )
    check(
        "decimal Infinity refused",
        lambda: refuses_value(
            lambda: canonical_decimal(
                "Infinity", field="rate"
            )
        ),
    )
    check(
        "decimal -1 refused",
        lambda: refuses_value(
            lambda: canonical_decimal(
                "-1", field="rate"
            )
        ),
    )
    check(
        "decimal zero refused",
        lambda: refuses_value(
            lambda: canonical_decimal(
                "0", field="rate"
            )
        ),
    )
    check(
        "malformed decimal exponent refused",
        lambda: refuses_value(
            lambda: canonical_decimal(
                "1e+", field="rate"
            )
        ),
    )

    def json_test():
        left = canonical_json_bytes(
            {"z": "é", "a": [2, 1]}
        )
        right = canonical_json_bytes(
            {"a": [2, 1], "z": "é"}
        )
        return (
            left
            == right
            == b'{"a":[2,1],"z":"\xc3\xa9"}\n'
            and not left.startswith(b"\xef\xbb\xbf")
            and not left.endswith(b"\n\n")
        )

    check(
        "canonical JSON deterministic UTF-8/sorted/compact/newline",
        json_test,
    )

    def atomic_happy_test():
        with tempfile.TemporaryDirectory(
            prefix="kot-f1k-ops-selftest-"
        ) as raw:
            path = Path(raw) / "state.json"
            digest = atomic_write_json(
                path,
                {"generation": 1},
                mode=0o640,
            )
            payload = canonical_json_bytes(
                {"generation": 1}
            )
            return (
                path.read_bytes() == payload
                and digest
                == hashlib.sha256(payload).hexdigest()
                and stat.S_IMODE(path.stat().st_mode)
                == 0o640
            )

    check(
        "atomic JSON publishes one complete new file + correct SHA/mode",
        atomic_happy_test,
    )

    def atomic_interruption_test():
        global _write_all

        with tempfile.TemporaryDirectory(
            prefix="kot-f1k-ops-selftest-"
        ) as raw:
            path = Path(raw) / "state.json"
            atomic_write_json(
                path, {"generation": "old"}
            )
            old = path.read_bytes()
            saved = _write_all

            def interrupted(fd, payload):
                os.write(
                    fd,
                    payload[:max(1, len(payload) // 2)],
                )
                raise OSError(
                    "injected mid-write interruption"
                )

            _write_all = interrupted
            refused = False
            try:
                atomic_write_json(
                    path, {"generation": "new"}
                )
            except OSError:
                refused = True
            finally:
                _write_all = saved

            leftovers = list(
                Path(raw).glob(
                    ".state.json.*.tmp"
                )
            )
            return (
                refused
                and path.read_bytes() == old
                and not leftovers
            )

    check(
        "atomic injected mid-write leaves complete old bytes",
        atomic_interruption_test,
    )

    check(
        "atomic non-normalized final path refused",
        lambda: refuses_value(
            lambda: atomic_write_json(
                "/tmp/kot-f1k-ops-selftest/"
                "x/../state.json",
                {"x": 1},
            )
        ),
    )

    def atomic_symlink_test():
        with tempfile.TemporaryDirectory(
            prefix="kot-f1k-ops-selftest-"
        ) as raw:
            root = Path(raw)
            referent = root / "referent.json"
            referent.write_bytes(b"referent\n")
            link = root / "state.json"
            link.symlink_to(referent.name)

            refused = refuses_value(
                lambda: atomic_write_json(
                    link, {"replacement": True}
                )
            )
            return (
                refused
                and link.is_symlink()
                and referent.read_bytes()
                == b"referent\n"
            )

    check(
        "atomic symlinked final component refused",
        atomic_symlink_test,
    )

    metadata_calls = []

    def one_metadata(path, timeout):
        metadata_calls.append((path, timeout))
        return b"123456789"

    check(
        "metadata fake transport read (no network)",
        lambda: (
            read_live_instance_metadata(
                "instance/id",
                timeout_s=1.25,
                transport=one_metadata,
            ) == "123456789"
            and metadata_calls
            == [("instance/id", 1.25)]
        ),
    )

    metadata_fixture = {
        "instance/id": "1234567890123456789",
        "instance/name": "kot-f1k-run",
        "project/project-id": "test-project",
        "project/numeric-project-id": "987654321",
        "instance/zone": (
            "projects/987654321/"
            "zones/us-central1-a"
        ),
        "instance/machine-type": (
            "projects/987654321/"
            "machineTypes/n2d-highmem-8"
        ),
    }

    def identity_metadata(path, timeout):
        del timeout
        return metadata_fixture[path]

    compute_fixture = {
        "id": "1234567890123456789",
        "name": "kot-f1k-run",
        "zone": (
            "https://www.googleapis.com/compute/v1/"
            "projects/test-project/zones/us-central1-a"
        ),
        "machineType": (
            "https://www.googleapis.com/compute/v1/"
            "projects/test-project/zones/us-central1-a/"
            "machineTypes/n2d-highmem-8"
        ),
        "selfLink": (
            "https://www.googleapis.com/compute/v1/"
            "projects/test-project/zones/us-central1-a/"
            "instances/kot-f1k-run"
        ),
        "scheduling": {
            "provisioningModel": "SPOT"
        },
        "lastStartTimestamp": (
            "2026-07-17T17:00:00.123456-07:00"
        ),
    }

    def identity_compute(**kwargs):
        if kwargs != {
            "project_id": "test-project",
            "zone": "us-central1-a",
            "instance_name": "kot-f1k-run",
        }:
            raise AssertionError(
                "wrong Compute lookup binding"
            )
        return copy.deepcopy(compute_fixture)

    def identity_happy_test():
        result = resolve_live_instance_identity(
            metadata_transport=identity_metadata,
            compute_transport=identity_compute,
        )
        return (
            result["instance_id"]
            == metadata_fixture["instance/id"]
            and result["project_id"]
            == "test-project"
            and result["project_number"]
            == "987654321"
            and result["zone"]
            == "us-central1-a"
            and result["machine_type"]
            == "n2d-highmem-8"
            and result["provisioning_model"]
            == "SPOT"
            and result["last_start_timestamp"]
            == "2026-07-18T00:00:00.123456Z"
            and str(uuid.UUID(result["boot_id"]))
            == result["boot_id"]
        )

    check(
        "live identity happy path binds numeric ID + SPOT + boot",
        identity_happy_test,
    )

    def recreated_compute(**kwargs):
        del kwargs
        value = copy.deepcopy(compute_fixture)
        value["id"] = "9999999999999999999"
        return value

    check(
        "live identity refuses recreated same-name VM",
        lambda: refuses_ops(
            "F1K_IDENTITY_RECREATED",
            lambda: resolve_live_instance_identity(
                metadata_transport=identity_metadata,
                compute_transport=recreated_compute,
            ),
        ),
    )

    def standard_compute(**kwargs):
        del kwargs
        value = copy.deepcopy(compute_fixture)
        value["scheduling"][
            "provisioningModel"
        ] = "STANDARD"
        return value

    check(
        "live identity refuses STANDARD provisioning model",
        lambda: refuses_ops(
            "F1K_IDENTITY_MODEL",
            lambda: resolve_live_instance_identity(
                metadata_transport=identity_metadata,
                compute_transport=standard_compute,
            ),
        ),
    )

    def make_sku(
        sku_id,
        description,
        resource_family,
        resource_group,
        usage_type,
        usage_unit,
        nanos,
    ):
        return {
            "name": "%s/skus/%s"
            % (_COMPUTE_SERVICE, sku_id),
            "skuId": sku_id,
            "description": description,
            "category": {
                "serviceDisplayName": "Compute Engine",
                "resourceFamily": resource_family,
                "resourceGroup": resource_group,
                "usageType": usage_type,
            },
            "serviceRegions": ["us-central1"],
            "serviceProviderName": "Google",
            "geoTaxonomy": {
                "type": "MULTI_REGIONAL",
                "regions": ["us-central1"],
            },
            "pricingInfo": [
                {
                    "effectiveTime": (
                        "2026-07-01T00:00:00Z"
                    ),
                    "currencyConversionRate": 1,
                    "pricingExpression": {
                        "usageUnit": usage_unit,
                        "tieredRates": [
                            {
                                "startUsageAmount": 0,
                                "unitPrice": {
                                    "currencyCode": "USD",
                                    "units": "0",
                                    "nanos": nanos,
                                },
                            }
                        ],
                    },
                }
            ],
        }

    catalog_fixture = [
        make_sku(
            "1111-AAAA-0001",
            "Spot Preemptible N2D AMD Instance "
            "Core running in Americas",
            "Compute",
            "N2DAMDCore",
            "Preemptible",
            "h",
            10000000,
        ),
        make_sku(
            "2222-BBBB-0002",
            "Spot Preemptible N2D AMD Instance "
            "Ram running in Americas",
            "Compute",
            "N2DAMDram",
            "Preemptible",
            "GiBy.h",
            1000000,
        ),
        make_sku(
            "3333-CCCC-0003",
            "SSD backed Local Storage attached "
            "to Spot Preemptible VMs",
            "Storage",
            "LocalSSD",
            "Preemptible",
            "GiBy.h",
            100000,
        ),
    ]

    def rate_call(skus):
        def fake_catalog(**kwargs):
            if kwargs != {
                "project_id": "test-project",
                "region": "us-central1",
            }:
                raise AssertionError(
                    "wrong Catalog lookup binding"
                )
            return {"skus": copy.deepcopy(skus)}

        return resolve_live_rate(
            project_id="test-project",
            zone="us-central1-a",
            machine_type="n2d-highmem-8",
            local_ssd_count=2,
            observed_at_utc=(
                "2026-07-18T00:00:00Z"
            ),
            catalog_transport=fake_catalog,
        )

    def rate_happy_test():
        rate, evidence = rate_call(
            catalog_fixture
        )
        unhashed = dict(evidence)
        digest = unhashed.pop("sha256")
        components = {
            item["component"]:
                item["hourly_usd_decimal"]
            for item in evidence["components"]
        }
        return (
            rate == "0.219"
            and evidence["usd_per_hour_decimal"]
            == rate
            and components
            == {
                "n2d_vcpu": "0.08",
                "n2d_ram_gib": "0.064",
                "local_ssd_gib": "0.075",
            }
            and digest
            == hashlib.sha256(
                canonical_json_bytes(unhashed)
            ).hexdigest()
        )

    check(
        "live rate exact 3-component sum + canonical evidence SHA",
        rate_happy_test,
    )

    check(
        "live rate refuses missing SKU",
        lambda: refuses_ops(
            "F1K_RATE_SKU",
            lambda: rate_call(
                catalog_fixture[:2]
            ),
        ),
    )

    duplicate_catalog = copy.deepcopy(
        catalog_fixture
    )
    duplicate = copy.deepcopy(
        duplicate_catalog[0]
    )
    duplicate["skuId"] = "4444-DDDD-0004"
    duplicate["name"] = "%s/skus/%s" % (
        _COMPUTE_SERVICE,
        duplicate["skuId"],
    )
    duplicate_catalog.append(duplicate)

    check(
        "live rate refuses duplicate component SKU",
        lambda: refuses_ops(
            "F1K_RATE_SKU",
            lambda: rate_call(
                duplicate_catalog
            ),
        ),
    )

    wrong_region_catalog = copy.deepcopy(
        catalog_fixture
    )
    wrong_region_catalog[1][
        "serviceRegions"
    ] = ["us-east1"]
    wrong_region_catalog[1][
        "geoTaxonomy"
    ]["regions"] = ["us-east1"]

    check(
        "live rate refuses wrong-region SKU",
        lambda: refuses_ops(
            "F1K_RATE_SKU",
            lambda: rate_call(
                wrong_region_catalog
            ),
        ),
    )

    wrong_usage_catalog = copy.deepcopy(
        catalog_fixture
    )
    wrong_usage_catalog[0][
        "category"
    ]["usageType"] = "OnDemand"

    check(
        "live rate refuses wrong-usage-type SKU",
        lambda: refuses_ops(
            "F1K_RATE_SKU",
            lambda: rate_call(
                wrong_usage_catalog
            ),
        ),
    )

    def outage(**kwargs):
        del kwargs
        raise OSError(
            "injected quote outage"
        )

    check(
        "live rate refuses quote outage",
        lambda: refuses_ops(
            "F1K_RATE_QUOTE",
            lambda: resolve_live_rate(
                project_id="test-project",
                zone="us-central1-a",
                machine_type="n2d-highmem-8",
                local_ssd_count=2,
                observed_at_utc=(
                    "2026-07-18T00:00:00Z"
                ),
                catalog_transport=outage,
            ),
        ),
    )

    print(
        "SELFTEST: %d/%d PASS"
        % (passed, total)
    )
    return 0 if passed == total else 2


def _main() -> int:
    if len(sys.argv) < 2:
        _die(
            "F1K_OPS_USAGE",
            "usage: f1k_ops.py selftest",
        )

    command = sys.argv[1]
    if command == "selftest":
        parser = argparse.ArgumentParser(
            prog="f1k_ops.py selftest"
        )
        parser.parse_args(sys.argv[2:])
        return selftest()

    _die(
        "F1K_OPS_USAGE",
        "unknown command %r (expected selftest)"
        % command,
    )
    return 2


if __name__ == "__main__":
    try:
        raise SystemExit(_main())
    except F1KOpsError as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(2)
    except ValueError as exc:
        _die("F1K_OPS_INPUT", str(exc))
