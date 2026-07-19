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
_SHA256_RE = re.compile(r"[0-9a-f]{64}\Z")

CONSTRUCTION_READY_SCHEMA = "kot-f1k-construction-ready/1"
BRINGUP_GATE_SCHEMA = "kot-f1k-bringup-gate/2"
CONSTRUCTION_HANDOFF_SCHEMA = "kot-f1k-construction-handoff/1"
READY_GATE_BINDING_SCHEMA = "kot-f1k-ready-gate-binding/1"
RUNTIME_LICENSE_SCHEMA = "kot-f1k-runtime-license/1"
RATE_EVIDENCE_SCHEMA = "kot-f1k-rate-evidence/1"

CONSTRUCTION_BUILDER_SHA256 = (
    "a92be3e4fe535c1dfefc41e2a422e010"
    "d25e8e40cf8e4cc123e7d829d63e9e61"
)
CONSTRUCTION_READY_PATH = (
    "/home/ubuntu/f1k-gate/construction-ready.json"
)
BRINGUP_GATE_PATH = "/home/ubuntu/f1k-gate/bringup-gate.json"
CONSTRUCTION_HANDOFF_PATH = (
    "/home/ubuntu/f1k-gate/construction-handoff.json"
)
RATE_EVIDENCE_PATH = (
    "/home/ubuntu/f1k-gate/live-rate-evidence.json"
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


def _closed_contract_object(value, *, field, keys, code):
    if not isinstance(value, dict):
        raise F1KOpsError(
            code, "%s must be an object" % field
        )
    expected = set(keys)
    actual = set(value)
    if actual != expected:
        raise F1KOpsError(
            code,
            "%s fields differ (missing=%s unknown=%s)"
            % (
                field,
                sorted(expected - actual),
                sorted(actual - expected),
            ),
        )
    return value


def _contract_string(value, *, field, code):
    if (
        not isinstance(value, str)
        or not value
        or value != value.strip()
        or "\x00" in value
    ):
        raise F1KOpsError(
            code, "%s must be a nonempty string" % field
        )
    return value


def _contract_sha256(value, *, field, code):
    if (
        not isinstance(value, str)
        or not _SHA256_RE.fullmatch(value)
    ):
        raise F1KOpsError(
            code, "%s must be a lowercase SHA-256" % field
        )
    return value


def _contract_timestamp(value, *, field, code):
    normalized = _utc_timestamp(
        value, field=field, code=code
    )
    if normalized != value:
        raise F1KOpsError(
            code,
            "%s must use canonical UTC Z form" % field,
        )
    return value


def _contract_uuid(value, *, field, code):
    try:
        parsed = uuid.UUID(value)
    except (AttributeError, TypeError, ValueError) as exc:
        raise F1KOpsError(
            code, "%s must be a canonical UUID" % field
        ) from exc
    if str(parsed) != value:
        raise F1KOpsError(
            code, "%s must be a canonical UUID" % field
        )
    return value


def _contract_path(value, *, field, code):
    if (
        not isinstance(value, str)
        or not value
        or "\x00" in value
        or not os.path.isabs(value)
        or os.path.normpath(value) != value
    ):
        raise F1KOpsError(
            code,
            "%s must be a normalized absolute path" % field,
        )
    return value


def _contract_contained(path, root, *, field, code):
    try:
        contained = (
            os.path.commonpath([root, path]) == root
        )
    except ValueError:
        contained = False
    if not contained or path == root:
        raise F1KOpsError(
            code,
            "%s escapes its reviewed root" % field,
        )


def _contract_positive_int(value, *, field, code):
    if (
        isinstance(value, bool)
        or not isinstance(value, int)
        or value < 1
    ):
        raise F1KOpsError(
            code,
            "%s must be a positive integer" % field,
        )
    return value


def _contract_decimal(value, *, field, code):
    if not isinstance(value, str):
        raise F1KOpsError(
            code,
            "%s must be a canonical decimal string; "
            "JSON numbers are forbidden" % field,
        )
    try:
        normalized = canonical_decimal(
            value, field=field
        )
    except ValueError as exc:
        raise F1KOpsError(code, str(exc)) from exc
    if normalized != value:
        raise F1KOpsError(
            code,
            "%s is not canonical: %r" % (field, value),
        )
    return value


def _contract_pin_decimal(value, *, field, code):
    # PIN_GB is a landed compatibility field, not an accounting
    # quantity. The current READY/GREEN writers emit it as a JSON
    # number; normalize it before comparing the two contracts.
    if isinstance(value, bool):
        raise F1KOpsError(
            code, "%s must be a positive number" % field
        )
    if isinstance(value, float):
        if not math.isfinite(value):
            raise F1KOpsError(
                code, "%s must be finite" % field
            )
        value = repr(value)
    try:
        return canonical_decimal(value, field=field)
    except ValueError as exc:
        raise F1KOpsError(code, str(exc)) from exc


def _contract_number(value, *, field, code):
    if (
        isinstance(value, bool)
        or not isinstance(value, (int, float))
        or not math.isfinite(float(value))
    ):
        raise F1KOpsError(
            code, "%s must be a finite JSON number" % field
        )
    return value


def _contract_string_list(
    value, *, field, code, unique=False
):
    if (
        not isinstance(value, list)
        or not value
        or not all(
            isinstance(item, str)
            and item
            and "\x00" not in item
            for item in value
        )
        or (
            unique
            and len(set(value)) != len(value)
        )
    ):
        raise F1KOpsError(
            code,
            "%s must be a nonempty%s string list"
            % (
                field,
                " unique" if unique else "",
            ),
        )
    return value


def _validate_contract_identity(
    value, *, field, code
):
    identity = _closed_contract_object(
        value,
        field=field,
        keys=(
            "instance_id",
            "name",
            "project_id",
            "project_number",
            "zone",
            "machine_type",
            "provisioning_model",
            "last_start_timestamp",
            "boot_id",
        ),
        code=code,
    )
    for name in (
        "instance_id",
        "name",
        "project_id",
        "project_number",
        "zone",
        "machine_type",
        "provisioning_model",
    ):
        _contract_string(
            identity[name],
            field="%s.%s" % (field, name),
            code=code,
        )
    if not _NUMERIC_ID_RE.fullmatch(
        identity["instance_id"]
    ):
        raise F1KOpsError(
            code, "%s.instance_id is malformed" % field
        )
    if not _INSTANCE_NAME_RE.fullmatch(
        identity["name"]
    ):
        raise F1KOpsError(
            code, "%s.name is malformed" % field
        )
    if not _PROJECT_ID_RE.fullmatch(
        identity["project_id"]
    ):
        raise F1KOpsError(
            code, "%s.project_id is malformed" % field
        )
    if not _NUMERIC_ID_RE.fullmatch(
        identity["project_number"]
    ):
        raise F1KOpsError(
            code, "%s.project_number is malformed" % field
        )
    if not _ZONE_RE.fullmatch(identity["zone"]):
        raise F1KOpsError(
            code, "%s.zone is malformed" % field
        )
    if identity["machine_type"] != "n2d-highmem-8":
        raise F1KOpsError(
            code,
            "%s.machine_type is not licensed" % field,
        )
    if identity["provisioning_model"] != "SPOT":
        raise F1KOpsError(
            code, "%s is not SPOT" % field
        )
    _contract_timestamp(
        identity["last_start_timestamp"],
        field=field + ".last_start_timestamp",
        code=code,
    )
    _contract_uuid(
        identity["boot_id"],
        field=field + ".boot_id",
        code=code,
    )
    return identity


def _validate_path_sha(value, *, field, code):
    pair = _closed_contract_object(
        value,
        field=field,
        keys=("path", "sha256"),
        code=code,
    )
    _contract_path(
        pair["path"],
        field=field + ".path",
        code=code,
    )
    _contract_sha256(
        pair["sha256"],
        field=field + ".sha256",
        code=code,
    )
    return pair


def validate_ready(record):
    """Validate the closed landed construction READY /1 contract."""
    code = "F1K_READY"
    ready = _closed_contract_object(
        record,
        field="ready",
        keys=(
            "schema",
            "status",
            "created_at_utc",
            "instance",
            "timing_results",
            "payload",
            "builder",
            "engine",
            "tokenizer",
            "dump_patch",
            "token_sidecar",
            "pin",
            "launch",
            "paths",
            "engine_tests",
        ),
        code=code,
    )
    if ready["schema"] != CONSTRUCTION_READY_SCHEMA:
        raise F1KOpsError(
            code, "ready schema is not /1"
        )
    if ready["status"] != "READY":
        raise F1KOpsError(
            code, "ready status is not READY"
        )
    _contract_timestamp(
        ready["created_at_utc"],
        field="ready.created_at_utc",
        code=code,
    )
    identity = _validate_contract_identity(
        ready["instance"],
        field="ready.instance",
        code=code,
    )

    timing = _closed_contract_object(
        ready["timing_results"],
        field="ready.timing_results",
        keys=(
            "boot_id",
            "result_set_sha256",
            "pin_sha256",
            "t1_sample_ids",
            "t2_sample_ids",
        ),
        code=code,
    )
    _contract_uuid(
        timing["boot_id"],
        field="ready.timing_results.boot_id",
        code=code,
    )
    for name in (
        "result_set_sha256",
        "pin_sha256",
    ):
        _contract_sha256(
            timing[name],
            field="ready.timing_results." + name,
            code=code,
        )
    for name in (
        "t1_sample_ids",
        "t2_sample_ids",
    ):
        _contract_string_list(
            timing[name],
            field="ready.timing_results." + name,
            code=code,
            unique=True,
        )
    if timing["boot_id"] != identity["boot_id"]:
        raise F1KOpsError(
            code,
            "READY timing boot_id differs from identity",
        )

    payload = _closed_contract_object(
        ready["payload"],
        field="ready.payload",
        keys=(
            "root",
            "source_manifest",
            "bundle_manifest",
        ),
        code=code,
    )
    payload_root = _contract_path(
        payload["root"],
        field="ready.payload.root",
        code=code,
    )
    source_manifest = _validate_path_sha(
        payload["source_manifest"],
        field="ready.payload.source_manifest",
        code=code,
    )
    bundle_manifest = _closed_contract_object(
        payload["bundle_manifest"],
        field="ready.payload.bundle_manifest",
        keys=("path", "sha256", "file_count"),
        code=code,
    )
    _contract_path(
        bundle_manifest["path"],
        field="ready.payload.bundle_manifest.path",
        code=code,
    )
    _contract_sha256(
        bundle_manifest["sha256"],
        field="ready.payload.bundle_manifest.sha256",
        code=code,
    )
    _contract_positive_int(
        bundle_manifest["file_count"],
        field="ready.payload.bundle_manifest.file_count",
        code=code,
    )

    builder = _closed_contract_object(
        ready["builder"],
        field="ready.builder",
        keys=("path", "sha256", "argv_base"),
        code=code,
    )
    _contract_path(
        builder["path"],
        field="ready.builder.path",
        code=code,
    )
    if (
        builder["sha256"]
        != CONSTRUCTION_BUILDER_SHA256
    ):
        raise F1KOpsError(
            code, "construction builder pin drift"
        )
    builder_argv = _contract_string_list(
        builder["argv_base"],
        field="ready.builder.argv_base",
        code=code,
    )
    _contract_path(
        builder_argv[0],
        field="ready.builder.argv_base[0]",
        code=code,
    )

    engine = _closed_contract_object(
        ready["engine"],
        field="ready.engine",
        keys=(
            "argv",
            "executable_path",
            "sha256",
            "weights_artifact_path",
            "weights_artifact_sha256",
        ),
        code=code,
    )
    engine_argv = _contract_string_list(
        engine["argv"],
        field="ready.engine.argv",
        code=code,
    )
    for name in (
        "executable_path",
        "weights_artifact_path",
    ):
        _contract_path(
            engine[name],
            field="ready.engine." + name,
            code=code,
        )
    for name in (
        "sha256",
        "weights_artifact_sha256",
    ):
        _contract_sha256(
            engine[name],
            field="ready.engine." + name,
            code=code,
        )
    if engine_argv != [
        engine["executable_path"],
        "64",
        "4",
        "8",
    ]:
        raise F1KOpsError(
            code, "construction engine argv shape drift"
        )

    tokenizer = _closed_contract_object(
        ready["tokenizer"],
        field="ready.tokenizer",
        keys=("argv", "artifact_path", "sha256"),
        code=code,
    )
    tokenizer_argv = _contract_string_list(
        tokenizer["argv"],
        field="ready.tokenizer.argv",
        code=code,
    )
    _contract_path(
        tokenizer["artifact_path"],
        field="ready.tokenizer.artifact_path",
        code=code,
    )
    _contract_sha256(
        tokenizer["sha256"],
        field="ready.tokenizer.sha256",
        code=code,
    )
    if (
        len(tokenizer_argv) != 3
        or tokenizer_argv[0] != builder_argv[0]
        or tokenizer_argv[2]
        != tokenizer["artifact_path"]
    ):
        raise F1KOpsError(
            code, "tokenizer argv/artifact seam drift"
        )
    _contract_path(
        tokenizer_argv[1],
        field="ready.tokenizer.argv[1]",
        code=code,
    )

    dump_patch = _closed_contract_object(
        ready["dump_patch"],
        field="ready.dump_patch",
        keys=("artifact_path", "sha256"),
        code=code,
    )
    _contract_path(
        dump_patch["artifact_path"],
        field="ready.dump_patch.artifact_path",
        code=code,
    )
    _contract_sha256(
        dump_patch["sha256"],
        field="ready.dump_patch.sha256",
        code=code,
    )
    token_sidecar = _validate_path_sha(
        ready["token_sidecar"],
        field="ready.token_sidecar",
        code=code,
    )
    pin = _closed_contract_object(
        ready["pin"],
        field="ready.pin",
        keys=("path", "sha256", "pin_gb"),
        code=code,
    )
    _contract_path(
        pin["path"],
        field="ready.pin.path",
        code=code,
    )
    _contract_sha256(
        pin["sha256"],
        field="ready.pin.sha256",
        code=code,
    )
    _contract_pin_decimal(
        pin["pin_gb"],
        field="ready.pin.pin_gb",
        code=code,
    )
    if timing["pin_sha256"] != pin["sha256"]:
        raise F1KOpsError(
            code,
            "READY timing pin differs from campaign pin",
        )

    launch = _closed_contract_object(
        ready["launch"],
        field="ready.launch",
        keys=("layers", "environment"),
        code=code,
    )
    if launch["layers"] != list(range(3, 78)):
        raise F1KOpsError(
            code,
            "construction layers are not exactly 3..77",
        )
    environment = _closed_contract_object(
        launch["environment"],
        field="ready.launch.environment",
        keys=(
            "SNAP",
            "TOK_SHA256",
            "OMP_NUM_THREADS",
            "OMP_DYNAMIC",
            "OMP_PROC_BIND",
            "OMP_WAIT_POLICY",
            "COLI_OMP_TUNED",
        ),
        code=code,
    )
    if not all(
        isinstance(value, str) and value
        for value in environment.values()
    ):
        raise F1KOpsError(
            code,
            "READY launch environment must be strings",
        )
    _contract_path(
        environment["SNAP"],
        field="ready.launch.environment.SNAP",
        code=code,
    )
    if (
        environment["TOK_SHA256"]
        != tokenizer["sha256"]
        or not re.fullmatch(
            r"[1-9][0-9]*",
            environment["OMP_NUM_THREADS"],
        )
        or environment["OMP_DYNAMIC"] != "FALSE"
        or environment["OMP_PROC_BIND"] != "close"
        or environment["OMP_WAIT_POLICY"] != "active"
        or environment["COLI_OMP_TUNED"] != "1"
    ):
        raise F1KOpsError(
            code, "READY launch environment drift"
        )

    paths = _closed_contract_object(
        ready["paths"],
        field="ready.paths",
        keys=("rundir", "workdir", "out"),
        code=code,
    )
    for name in paths:
        _contract_path(
            paths[name],
            field="ready.paths." + name,
            code=code,
        )

    expected_builder_argv = [
        builder_argv[0],
        builder["path"],
        "construct",
        "--mode",
        "real",
        "--layers",
        ",".join(
            str(layer) for layer in range(3, 78)
        ),
        "--tokenizer-sha",
        tokenizer["sha256"],
        "--tokenizer-artifact",
        tokenizer["artifact_path"],
        "--engine-weights-sha",
        engine["weights_artifact_sha256"],
        "--engine-weights-artifact",
        engine["weights_artifact_path"],
        "--dump-patch-sha",
        dump_patch["sha256"],
        "--dump-patch-artifact",
        dump_patch["artifact_path"],
        "--out",
        paths["out"],
        "--workdir",
        paths["workdir"],
    ]
    if builder_argv != expected_builder_argv:
        raise F1KOpsError(
            code,
            "builder argv is not the exact READY shape",
        )
    if any(
        token.startswith(
            ("--engine-c", "--tokenizer-c")
        )
        for token in builder_argv
    ):
        raise F1KOpsError(
            code,
            "builder argv contains a guard-owned seam",
        )

    for field, path in (
        ("source manifest", source_manifest["path"]),
        ("bundle manifest", bundle_manifest["path"]),
        ("builder", builder["path"]),
        ("tokenizer wrapper", tokenizer_argv[1]),
        ("dump patch", dump_patch["artifact_path"]),
    ):
        _contract_contained(
            path,
            payload_root,
            field=field,
            code=code,
        )

    tests = ready["engine_tests"]
    if not isinstance(tests, list) or not tests:
        raise F1KOpsError(
            code,
            "ready.engine_tests must be a nonempty list",
        )
    names = []
    for index, test in enumerate(tests):
        item = _closed_contract_object(
            test,
            field="ready.engine_tests[%d]" % index,
            keys=(
                "name",
                "path",
                "sha256",
                "verdict",
            ),
            code=code,
        )
        names.append(
            _contract_string(
                item["name"],
                field=(
                    "ready.engine_tests[%d].name"
                    % index
                ),
                code=code,
            )
        )
        _contract_path(
            item["path"],
            field=(
                "ready.engine_tests[%d].path"
                % index
            ),
            code=code,
        )
        _contract_sha256(
            item["sha256"],
            field=(
                "ready.engine_tests[%d].sha256"
                % index
            ),
            code=code,
        )
        if item["verdict"] != "PASS":
            raise F1KOpsError(
                code,
                "READY engine evidence is not PASS",
            )
    if (
        len(names) != 6
        or set(names)
        != {
            "kae",
            "dump-a",
            "dump-b",
            "dump-c",
            "functional-inertness",
            "tokenizer-engine-agreement",
        }
    ):
        raise F1KOpsError(
            code,
            "READY engine evidence set is incomplete",
        )

    return copy.deepcopy(ready)


def validate_gate(record):
    """Validate the closed landed GREEN bring-up gate /2 contract."""
    code = "F1K_GATE_CONTRACT"
    gate = _closed_contract_object(
        record,
        field="gate",
        keys=(
            "schema",
            "verdict",
            "reasons",
            "checks",
            "f",
            "tokenizer",
            "corpus_sha256",
            "sample",
            "model",
            "pin",
            "model_bundle",
            "pin_engagement",
            "rate",
            "projection",
            "dump_gate",
            "thresholds",
            "semantics",
        ),
        code=code,
    )
    if gate["schema"] != BRINGUP_GATE_SCHEMA:
        raise F1KOpsError(
            code, "gate schema is not /2"
        )
    if (
        gate["verdict"] != "GREEN"
        or gate["reasons"] != []
    ):
        raise F1KOpsError(
            code, "gate is not an unqualified GREEN"
        )

    checks = _closed_contract_object(
        gate["checks"],
        field="gate.checks",
        keys=(
            "rate_in_window",
            "f_le_threshold",
            "central_hours_in_window",
            "central_usd_in_window",
            "hi_band_below_caps",
            "dump_preconditions_pass",
            "functional_inertness_pass",
            "lo_band_above_floors",
            "prefills_ge_min",
            "tokenizer_real",
            "pin_regime_pinned",
            "pin_engagement_pass",
        ),
        code=code,
    )
    if not all(
        value is True for value in checks.values()
    ):
        raise F1KOpsError(
            code,
            "GREEN gate has a false/non-boolean check",
        )

    f_record = _closed_contract_object(
        gate["f"],
        field="gate.f",
        keys=(
            "blended",
            "threshold",
            "branch",
            "per_population",
            "convention",
        ),
        code=code,
    )
    _contract_number(
        f_record["blended"],
        field="gate.f.blended",
        code=code,
    )
    _contract_number(
        f_record["threshold"],
        field="gate.f.threshold",
        code=code,
    )
    if (
        f_record["branch"] != "LE"
        or not isinstance(
            f_record["per_population"], dict
        )
    ):
        raise F1KOpsError(
            code,
            "gate f branch/populations are malformed",
        )
    _contract_string(
        f_record["convention"],
        field="gate.f.convention",
        code=code,
    )

    tokenizer = _closed_contract_object(
        gate["tokenizer"],
        field="gate.tokenizer",
        keys=("mode", "mock_f", "sha256"),
        code=code,
    )
    if (
        tokenizer["mode"] != "REAL"
        or tokenizer["mock_f"] is not None
    ):
        raise F1KOpsError(
            code, "GREEN tokenizer is not REAL"
        )
    _contract_sha256(
        tokenizer["sha256"],
        field="gate.tokenizer.sha256",
        code=code,
    )

    corpus = _closed_contract_object(
        gate["corpus_sha256"],
        field="gate.corpus_sha256",
        keys=(
            "construction-manifest.jsonl",
            "test.jsonl",
            "dev.jsonl",
            "guard.jsonl",
        ),
        code=code,
    )
    for name, digest in corpus.items():
        _contract_sha256(
            digest,
            field="gate.corpus_sha256." + name,
            code=code,
        )

    sample = _closed_contract_object(
        gate["sample"],
        field="gate.sample",
        keys=(
            "seed",
            "rule",
            "realized_bin_edges_Tp",
            "n",
            "t1_sample_ids",
            "entries",
        ),
        code=code,
    )
    if (
        isinstance(sample["seed"], bool)
        or not isinstance(sample["seed"], int)
    ):
        raise F1KOpsError(
            code, "gate.sample.seed must be an integer"
        )
    _closed_contract_object(
        sample["rule"],
        field="gate.sample.rule",
        keys=(
            "quantile_edges",
            "bin_alloc",
            "cont_tokens",
            "pop_floor",
            "t1_n",
            "text",
        ),
        code=code,
    )
    t1_ids = _contract_string_list(
        sample["t1_sample_ids"],
        field="gate.sample.t1_sample_ids",
        code=code,
        unique=True,
    )
    if (
        not isinstance(sample["entries"], list)
        or not sample["entries"]
    ):
        raise F1KOpsError(
            code, "gate.sample.entries must be nonempty"
        )
    t2_ids = []
    for index, entry in enumerate(
        sample["entries"]
    ):
        item = _closed_contract_object(
            entry,
            field="gate.sample.entries[%d]" % index,
            keys=(
                "sample_id",
                "key",
                "pop",
                "bin",
                "W",
                "T",
                "Tp",
                "why",
            ),
            code=code,
        )
        for name in (
            "sample_id",
            "key",
            "pop",
            "why",
        ):
            _contract_string(
                item[name],
                field=(
                    "gate.sample.entries[%d].%s"
                    % (index, name)
                ),
                code=code,
            )
        for name in ("bin", "W", "T", "Tp"):
            if (
                isinstance(item[name], bool)
                or not isinstance(item[name], int)
                or item[name] < 0
            ):
                raise F1KOpsError(
                    code,
                    "gate sample integer field is "
                    "malformed",
                )
        t2_ids.append(item["sample_id"])
    if (
        len(set(t2_ids)) != len(t2_ids)
        or not set(t1_ids).issubset(t2_ids)
        or sample["n"] != len(t2_ids)
    ):
        raise F1KOpsError(
            code,
            "gate sample IDs/count are incoherent",
        )

    _closed_contract_object(
        gate["model"],
        field="gate.model",
        keys=(
            "type",
            "knots_raw",
            "knots_isotonic",
            "isotonic_repairs",
            "se_rule",
            "cont_tokens_addend",
        ),
        code=code,
    )

    pin = _closed_contract_object(
        gate["pin"],
        field="gate.pin",
        keys=(
            "pin_file_sha256",
            "pin_gb",
            "pin_file_path",
            "regime",
            "derivation",
            "role",
            "note",
        ),
        code=code,
    )
    _contract_sha256(
        pin["pin_file_sha256"],
        field="gate.pin.pin_file_sha256",
        code=code,
    )
    _contract_pin_decimal(
        pin["pin_gb"],
        field="gate.pin.pin_gb",
        code=code,
    )
    _contract_path(
        pin["pin_file_path"],
        field="gate.pin.pin_file_path",
        code=code,
    )
    if (
        pin["regime"] != "pinned-bringup"
        or not isinstance(pin["derivation"], dict)
    ):
        raise F1KOpsError(
            code,
            "gate pin regime/derivation is malformed",
        )
    for name in ("role", "note"):
        _contract_string(
            pin[name],
            field="gate.pin." + name,
            code=code,
        )

    model_bundle = _closed_contract_object(
        gate["model_bundle"],
        field="gate.model_bundle",
        keys=(
            "add7_src_sha256",
            "tokens_full_sha256",
            "rule",
        ),
        code=code,
    )
    for name in (
        "add7_src_sha256",
        "tokens_full_sha256",
    ):
        _contract_sha256(
            model_bundle[name],
            field="gate.model_bundle." + name,
            code=code,
        )
    _contract_string(
        model_bundle["rule"],
        field="gate.model_bundle.rule",
        code=code,
    )

    pin_engagement = _closed_contract_object(
        gate["pin_engagement"],
        field="gate.pin_engagement",
        keys=("pass", "problems", "rule"),
        code=code,
    )
    if (
        pin_engagement["pass"] is not True
        or pin_engagement["problems"] != []
    ):
        raise F1KOpsError(
            code,
            "gate pin engagement is not an "
            "unqualified pass",
        )

    rate = _closed_contract_object(
        gate["rate"],
        field="gate.rate",
        keys=(
            "usd_per_hour",
            "usd_per_hour_decimal",
            "source",
        ),
        code=code,
    )
    rate_decimal = _contract_decimal(
        rate["usd_per_hour_decimal"],
        field="gate.rate.usd_per_hour_decimal",
        code=code,
    )
    rate_float = _contract_number(
        rate["usd_per_hour"],
        field="gate.rate.usd_per_hour",
        code=code,
    )
    if rate_float != float(rate_decimal):
        raise F1KOpsError(
            code,
            "gate compatibility rate differs from "
            "canonical rate",
        )
    _contract_string(
        rate["source"],
        field="gate.rate.source",
        code=code,
    )

    projection = _closed_contract_object(
        gate["projection"],
        field="gate.projection",
        keys=(
            "prefills",
            "replace_included",
            "instance_hours",
            "usd_total",
            "blended_s_per_prefill_central",
            "hours_by_population_central",
            "per_average_naive_hours_RETIRED",
            "per_average_divergence_pct",
            "reserve",
        ),
        code=code,
    )
    for name in ("instance_hours", "usd_total"):
        _closed_contract_object(
            projection[name],
            field="gate.projection." + name,
            keys=("central", "hi", "lo"),
            code=code,
        )
    _closed_contract_object(
        projection["reserve"],
        field="gate.projection.reserve",
        keys=(
            "usd",
            "hours_at_rate",
            "rule",
            "usd_central_with_reserve",
            "hours_central_with_reserve",
        ),
        code=code,
    )

    dump_gate = _closed_contract_object(
        gate["dump_gate"],
        field="gate.dump_gate",
        keys=(
            "a",
            "b",
            "c",
            "functional_inertness",
            "rule",
        ),
        code=code,
    )
    if any(
        dump_gate[name] != "PASS"
        for name in (
            "a",
            "b",
            "c",
            "functional_inertness",
        )
    ):
        raise F1KOpsError(
            code,
            "gate dump prerequisites are not all PASS",
        )
    _closed_contract_object(
        gate["thresholds"],
        field="gate.thresholds",
        keys=(
            "instance_hours",
            "usd_total",
            "rate_window",
            "prefills_min",
        ),
        code=code,
    )
    _contract_string(
        gate["semantics"],
        field="gate.semantics",
        code=code,
    )
    return copy.deepcopy(gate)


def validate_ready_gate_binding(ready, gate):
    """Cross-bind READY and GREEN and return a normalized binding."""
    ready = validate_ready(ready)
    gate = validate_gate(gate)
    code = "F1K_READY_GATE_BINDING"

    pairs = (
        (
            ready["token_sidecar"]["sha256"],
            gate["model_bundle"][
                "tokens_full_sha256"
            ],
            "token sidecar",
        ),
        (
            ready["tokenizer"]["sha256"],
            gate["tokenizer"]["sha256"],
            "tokenizer",
        ),
        (
            ready["pin"]["sha256"],
            gate["pin"]["pin_file_sha256"],
            "pin",
        ),
        (
            ready["payload"]["source_manifest"][
                "sha256"
            ],
            gate["corpus_sha256"][
                "construction-manifest.jsonl"
            ],
            "construction corpus",
        ),
    )
    for left, right, field in pairs:
        if left != right:
            raise F1KOpsError(
                code, "%s SHA mismatch" % field
            )
    if (
        ready["pin"]["path"]
        != gate["pin"]["pin_file_path"]
    ):
        raise F1KOpsError(
            code, "pin path mismatch"
        )
    pin_gb = _contract_pin_decimal(
        ready["pin"]["pin_gb"],
        field="ready.pin.pin_gb",
        code=code,
    )
    gate_pin_gb = _contract_pin_decimal(
        gate["pin"]["pin_gb"],
        field="gate.pin.pin_gb",
        code=code,
    )
    if pin_gb != gate_pin_gb:
        raise F1KOpsError(
            code, "PIN_GB mismatch"
        )

    sample = gate["sample"]
    t2_ids = [
        item["sample_id"]
        for item in sample["entries"]
    ]
    if (
        ready["timing_results"]["t1_sample_ids"]
        != sample["t1_sample_ids"]
        or ready["timing_results"]["t2_sample_ids"]
        != t2_ids
    ):
        raise F1KOpsError(
            code,
            "READY/gate timing sample IDs mismatch",
        )

    return {
        "schema": READY_GATE_BINDING_SCHEMA,
        "builder_sha256":
            ready["builder"]["sha256"],
        "tokens_full_sha256":
            ready["token_sidecar"]["sha256"],
        "pin_sha256": ready["pin"]["sha256"],
        "pin_gb_decimal": pin_gb,
        "tokenizer_sha256":
            ready["tokenizer"]["sha256"],
        "construction_manifest_sha256":
            ready["payload"]["source_manifest"][
                "sha256"
            ],
        "timing_result_set_sha256":
            ready["timing_results"][
                "result_set_sha256"
            ],
        "sample_sha256": hashlib.sha256(
            canonical_json_bytes(sample)
        ).hexdigest(),
    }


def validate_handoff(record):
    """Validate the closed lean-B construction handoff /1."""
    code = "F1K_HANDOFF"
    handoff = _closed_contract_object(
        record,
        field="handoff",
        keys=(
            "schema",
            "created_at_utc",
            "mode",
            "instance",
            "ready",
            "gate",
            "binding",
            "rate",
            "provider",
            "paths",
            "service",
        ),
        code=code,
    )
    if (
        handoff["schema"]
        != CONSTRUCTION_HANDOFF_SCHEMA
        or handoff["mode"] != "initial"
    ):
        raise F1KOpsError(
            code,
            "handoff schema/mode is not lean-B "
            "initial /1",
        )
    _contract_timestamp(
        handoff["created_at_utc"],
        field="handoff.created_at_utc",
        code=code,
    )
    identity = _validate_contract_identity(
        handoff["instance"],
        field="handoff.instance",
        code=code,
    )

    ready_ref = _closed_contract_object(
        handoff["ready"],
        field="handoff.ready",
        keys=("path", "sha256", "schema", "status"),
        code=code,
    )
    _contract_path(
        ready_ref["path"],
        field="handoff.ready.path",
        code=code,
    )
    _contract_sha256(
        ready_ref["sha256"],
        field="handoff.ready.sha256",
        code=code,
    )
    if (
        ready_ref["path"] != CONSTRUCTION_READY_PATH
        or ready_ref["schema"]
        != CONSTRUCTION_READY_SCHEMA
        or ready_ref["status"] != "READY"
    ):
        raise F1KOpsError(
            code,
            "handoff READY reference is not canonical",
        )

    gate_ref = _closed_contract_object(
        handoff["gate"],
        field="handoff.gate",
        keys=("path", "sha256", "schema", "verdict"),
        code=code,
    )
    _contract_path(
        gate_ref["path"],
        field="handoff.gate.path",
        code=code,
    )
    _contract_sha256(
        gate_ref["sha256"],
        field="handoff.gate.sha256",
        code=code,
    )
    if (
        gate_ref["path"] != BRINGUP_GATE_PATH
        or gate_ref["schema"] != BRINGUP_GATE_SCHEMA
        or gate_ref["verdict"] != "GREEN"
    ):
        raise F1KOpsError(
            code,
            "handoff GREEN reference is not canonical",
        )

    binding = _closed_contract_object(
        handoff["binding"],
        field="handoff.binding",
        keys=(
            "schema",
            "builder_sha256",
            "tokens_full_sha256",
            "pin_sha256",
            "pin_gb_decimal",
            "tokenizer_sha256",
            "construction_manifest_sha256",
            "timing_result_set_sha256",
            "sample_sha256",
        ),
        code=code,
    )
    if (
        binding["schema"]
        != READY_GATE_BINDING_SCHEMA
        or binding["builder_sha256"]
        != CONSTRUCTION_BUILDER_SHA256
    ):
        raise F1KOpsError(
            code,
            "handoff binding schema/builder pin drift",
        )
    for name in (
        "builder_sha256",
        "tokens_full_sha256",
        "pin_sha256",
        "tokenizer_sha256",
        "construction_manifest_sha256",
        "timing_result_set_sha256",
        "sample_sha256",
    ):
        _contract_sha256(
            binding[name],
            field="handoff.binding." + name,
            code=code,
        )
    _contract_decimal(
        binding["pin_gb_decimal"],
        field="handoff.binding.pin_gb_decimal",
        code=code,
    )

    rate = _closed_contract_object(
        handoff["rate"],
        field="handoff.rate",
        keys=(
            "usd_per_hour_decimal",
            "local_ssd_count",
            "evidence",
        ),
        code=code,
    )
    licensed_rate = _contract_decimal(
        rate["usd_per_hour_decimal"],
        field="handoff.rate.usd_per_hour_decimal",
        code=code,
    )
    if (
        isinstance(rate["local_ssd_count"], bool)
        or rate["local_ssd_count"] != 2
    ):
        raise F1KOpsError(
            code,
            "handoff rate does not bind two Local SSDs",
        )
    evidence = _closed_contract_object(
        rate["evidence"],
        field="handoff.rate.evidence",
        keys=(
            "path",
            "sha256",
            "schema",
            "observed_at_utc",
        ),
        code=code,
    )
    _contract_path(
        evidence["path"],
        field="handoff.rate.evidence.path",
        code=code,
    )
    _contract_sha256(
        evidence["sha256"],
        field="handoff.rate.evidence.sha256",
        code=code,
    )
    _contract_timestamp(
        evidence["observed_at_utc"],
        field="handoff.rate.evidence.observed_at_utc",
        code=code,
    )
    if (
        evidence["path"] != RATE_EVIDENCE_PATH
        or evidence["schema"] != RATE_EVIDENCE_SCHEMA
    ):
        raise F1KOpsError(
            code,
            "handoff rate-evidence reference is "
            "not canonical",
        )

    provider = _closed_contract_object(
        handoff["provider"],
        field="handoff.provider",
        keys=(
            "campaign_started_at_utc",
            "termination_time_utc",
            "termination_timestamp_utc",
            "instance_termination_action",
            "frozen_hours_max_decimal",
            "armed_hours_decimal",
            "non_compute_allowance_usd_decimal",
            "rate_headroom_usd_decimal",
            "compute_ceiling_usd_decimal",
            "total_envelope_usd_decimal",
            "budget",
        ),
        code=code,
    )
    for name in (
        "campaign_started_at_utc",
        "termination_time_utc",
        "termination_timestamp_utc",
    ):
        _contract_timestamp(
            provider[name],
            field="handoff.provider." + name,
            code=code,
        )
    if (
        provider["termination_time_utc"]
        != provider["termination_timestamp_utc"]
        or provider["instance_termination_action"]
        != "DELETE"
    ):
        raise F1KOpsError(
            code,
            "provider deletion is not read-back DELETE",
        )

    decimals = {}
    for name in (
        "frozen_hours_max_decimal",
        "armed_hours_decimal",
        "non_compute_allowance_usd_decimal",
        "rate_headroom_usd_decimal",
        "compute_ceiling_usd_decimal",
        "total_envelope_usd_decimal",
    ):
        decimals[name] = Decimal(
            _contract_decimal(
                provider[name],
                field="handoff.provider." + name,
                code=code,
            )
        )
    if (
        decimals["frozen_hours_max_decimal"]
        != Decimal("900")
        or decimals["armed_hours_decimal"]
        > Decimal("899")
    ):
        raise F1KOpsError(
            code,
            "provider wall-clock envelope exceeds "
            "lean-B limits",
        )
    with localcontext() as context:
        context.prec = 80
        compute_ceiling = (
            decimals["armed_hours_decimal"]
            * Decimal(licensed_rate)
        )
        total_envelope = (
            compute_ceiling
            + decimals[
                "non_compute_allowance_usd_decimal"
            ]
            + decimals[
                "rate_headroom_usd_decimal"
            ]
        )
    if (
        compute_ceiling
        != decimals["compute_ceiling_usd_decimal"]
        or total_envelope
        != decimals["total_envelope_usd_decimal"]
        or total_envelope > Decimal("300")
    ):
        raise F1KOpsError(
            code,
            "provider decimal accounting is "
            "incoherent or exceeds $300",
        )

    budget = _closed_contract_object(
        provider["budget"],
        field="handoff.provider.budget",
        keys=(
            "resource_name",
            "amount_usd_decimal",
            "project_id",
        ),
        code=code,
    )
    _contract_string(
        budget["resource_name"],
        field="handoff.provider.budget.resource_name",
        code=code,
    )
    if (
        _contract_decimal(
            budget["amount_usd_decimal"],
            field=(
                "handoff.provider.budget."
                "amount_usd_decimal"
            ),
            code=code,
        )
        != "300"
        or budget["project_id"]
        != identity["project_id"]
    ):
        raise F1KOpsError(
            code,
            "provider budget is not project-scoped $300",
        )

    paths = _closed_contract_object(
        handoff["paths"],
        field="handoff.paths",
        keys=("rundir", "workdir", "out"),
        code=code,
    )
    for name in paths:
        _contract_path(
            paths[name],
            field="handoff.paths." + name,
            code=code,
        )
    service = _closed_contract_object(
        handoff["service"],
        field="handoff.service",
        keys=(
            "manager",
            "unit_name",
            "user",
            "working_directory",
            "exec_argv",
            "restart_policy",
            "enabled_on_boot",
        ),
        code=code,
    )
    _contract_path(
        service["working_directory"],
        field="handoff.service.working_directory",
        code=code,
    )
    exec_argv = _contract_string_list(
        service["exec_argv"],
        field="handoff.service.exec_argv",
        code=code,
    )
    if (
        service["manager"] != "systemd"
        or service["unit_name"]
        != "kot-f1k-construction.service"
        or service["user"] != "ubuntu"
        or service["restart_policy"] != "no"
        or service["enabled_on_boot"] is not False
    ):
        raise F1KOpsError(
            code,
            "handoff service policy is not lean-B",
        )
    _contract_path(
        exec_argv[0],
        field="handoff.service.exec_argv[0]",
        code=code,
    )
    return copy.deepcopy(handoff)


def verify_artifact(
    path, expected_sha256, *, root=None, executable=False
):
    """Verify a regular, symlink-free artifact and its SHA pair."""
    code = "F1K_ARTIFACT"
    path_text = _contract_path(
        os.fspath(path),
        field="artifact.path",
        code=code,
    )
    expected = _contract_sha256(
        expected_sha256,
        field="artifact.sha256",
        code=code,
    )
    if root is not None:
        root_text = _contract_path(
            os.fspath(root),
            field="artifact.root",
            code=code,
        )
        _contract_contained(
            path_text,
            root_text,
            field="artifact.path",
            code=code,
        )
    else:
        root_text = None
    if not isinstance(executable, bool):
        raise F1KOpsError(
            code,
            "artifact executable flag must be boolean",
        )

    current = Path(Path(path_text).anchor)
    leaf = None
    try:
        for part in Path(path_text).parts[1:]:
            current /= part
            leaf = current.lstat()
            if stat.S_ISLNK(leaf.st_mode):
                raise F1KOpsError(
                    code,
                    "artifact path is symlinked: %s"
                    % current,
                )
        if leaf is None or not stat.S_ISREG(
            leaf.st_mode
        ):
            raise F1KOpsError(
                code, "artifact is not a regular file"
            )
        if root_text is not None:
            root_mode = Path(root_text).lstat().st_mode
            if not stat.S_ISDIR(root_mode):
                raise F1KOpsError(
                    code,
                    "artifact root is not a directory",
                )
    except F1KOpsError:
        raise
    except OSError as exc:
        raise F1KOpsError(
            code,
            "cannot lstat artifact path: %s" % exc,
        ) from exc

    flags = (
        os.O_RDONLY
        | getattr(os, "O_NOFOLLOW", 0)
    )
    try:
        fd = os.open(path_text, flags)
    except OSError as exc:
        raise F1KOpsError(
            code, "cannot open artifact: %s" % exc
        ) from exc
    try:
        before = os.fstat(fd)
        if not stat.S_ISREG(before.st_mode):
            raise F1KOpsError(
                code, "artifact is not a regular file"
            )
        if (
            executable
            and not before.st_mode & 0o111
        ):
            raise F1KOpsError(
                code, "artifact is not executable"
            )
        digest = hashlib.sha256()
        while True:
            chunk = os.read(fd, 1024 * 1024)
            if not chunk:
                break
            digest.update(chunk)
        after = os.fstat(fd)
    finally:
        os.close(fd)

    try:
        final = Path(path_text).lstat()
    except OSError as exc:
        raise F1KOpsError(
            code, "cannot re-stat artifact: %s" % exc
        ) from exc
    if (
        (
            before.st_dev,
            before.st_ino,
            before.st_size,
            before.st_mtime_ns,
        )
        != (
            after.st_dev,
            after.st_ino,
            after.st_size,
            after.st_mtime_ns,
        )
        or (after.st_dev, after.st_ino)
        != (final.st_dev, final.st_ino)
    ):
        raise F1KOpsError(
            code,
            "artifact changed during verification",
        )
    actual = digest.hexdigest()
    if actual != expected:
        raise F1KOpsError(
            code, "artifact SHA-256 mismatch"
        )
    return {
        "path": path_text,
        "sha256": actual,
    }


def build_runtime_license(ready, gate, handoff):
    """Build the normalized lean-B license used by launch and guard."""
    ready = validate_ready(ready)
    gate = validate_gate(gate)
    handoff = validate_handoff(handoff)
    binding = validate_ready_gate_binding(
        ready, gate
    )
    code = "F1K_RUNTIME_LICENSE"

    if handoff["instance"] != ready["instance"]:
        raise F1KOpsError(
            code,
            "handoff identity differs from READY",
        )
    if handoff["binding"] != binding:
        raise F1KOpsError(
            code,
            "handoff binding differs from READY/GREEN",
        )
    if (
        handoff["rate"]["usd_per_hour_decimal"]
        != gate["rate"]["usd_per_hour_decimal"]
    ):
        raise F1KOpsError(
            code, "handoff rate differs from GREEN"
        )
    if handoff["paths"] != ready["paths"]:
        raise F1KOpsError(
            code, "handoff paths differ from READY"
        )
    if (
        handoff["service"]["working_directory"]
        != ready["payload"]["root"]
    ):
        raise F1KOpsError(
            code,
            "service working directory differs from "
            "READY payload",
        )
    expected_exec = [
        ready["builder"]["argv_base"][0],
        os.path.join(
            ready["payload"]["root"],
            "f1k_bringup_gate.py",
        ),
        "guard",
        "--handoff",
        CONSTRUCTION_HANDOFF_PATH,
    ]
    if (
        handoff["service"]["exec_argv"]
        != expected_exec
    ):
        raise F1KOpsError(
            code,
            "service ExecStart is not the direct "
            "guard argv",
        )

    return {
        "schema": RUNTIME_LICENSE_SCHEMA,
        "instance":
            copy.deepcopy(ready["instance"]),
        "ready":
            copy.deepcopy(handoff["ready"]),
        "gate":
            copy.deepcopy(handoff["gate"]),
        "binding": binding,
        "rate":
            copy.deepcopy(handoff["rate"]),
        "provider":
            copy.deepcopy(handoff["provider"]),
        "payload":
            copy.deepcopy(ready["payload"]),
        "builder":
            copy.deepcopy(ready["builder"]),
        "engine":
            copy.deepcopy(ready["engine"]),
        "tokenizer":
            copy.deepcopy(ready["tokenizer"]),
        "dump_patch":
            copy.deepcopy(ready["dump_patch"]),
        "token_sidecar":
            copy.deepcopy(ready["token_sidecar"]),
        "pin":
            copy.deepcopy(ready["pin"]),
        "launch":
            copy.deepcopy(ready["launch"]),
        "paths":
            copy.deepcopy(ready["paths"]),
        "engine_tests":
            copy.deepcopy(ready["engine_tests"]),
        "service":
            copy.deepcopy(handoff["service"]),
    }


# --- governance layer (ledger/lease/attestation) pending issue #53 A/B/C ---


def selftest_b0() -> int:
    """Run the $0 pure/local lean-B contract oracle."""
    print(
        "SELFTEST-B0 SCOPE: $0 pure/local construction "
        "contracts; fixture files only; NO network, "
        "gcloud, GCP resources, or spend."
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

    def refuses(function):
        try:
            function()
        except (F1KOpsError, ValueError):
            return True
        return False

    def records():
        instance = {
            "instance_id":
                "1234567890123456789",
            "name": "kot-f1k-run",
            "project_id": "test-project",
            "project_number": "987654321",
            "zone": "us-central1-a",
            "machine_type": "n2d-highmem-8",
            "provisioning_model": "SPOT",
            "last_start_timestamp":
                "2026-07-18T12:00:00Z",
            "boot_id":
                "12345678-1234-5678-9234-567812345678",
        }
        root = "/home/ubuntu/f1k"
        python = "/usr/bin/python3"
        builder = (
            root
            + "/poc/glm52-probe/f1k-harness/"
            "build_carriers.py"
        )
        source_sha = "a" * 64
        bundle_sha = "b" * 64
        engine_sha = "c" * 64
        weights_sha = "d" * 64
        tokenizer_sha = "e" * 64
        dump_sha = "f" * 64
        tokens_sha = "1" * 64
        pin_sha = "2" * 64
        result_sha = "3" * 64
        tokenizer_artifact = (
            "/mnt/nvme/glm52_i4/tokenizer.json"
        )
        weights_artifact = (
            "/home/ubuntu/f1k-gate/"
            "glm52-weights-hash.json"
        )
        dump_artifact = (
            root
            + "/dump-patch/kot-f1k-dump.patch"
        )
        paths = {
            "rundir":
                "/home/ubuntu/f1k-gate/guard",
            "workdir":
                "/mnt/nvme/kot-f1k/construction/work",
            "out":
                "/mnt/nvme/kot-f1k/construction/out",
        }
        argv = [
            python,
            builder,
            "construct",
            "--mode",
            "real",
            "--layers",
            ",".join(
                str(layer)
                for layer in range(3, 78)
            ),
            "--tokenizer-sha",
            tokenizer_sha,
            "--tokenizer-artifact",
            tokenizer_artifact,
            "--engine-weights-sha",
            weights_sha,
            "--engine-weights-artifact",
            weights_artifact,
            "--dump-patch-sha",
            dump_sha,
            "--dump-patch-artifact",
            dump_artifact,
            "--out",
            paths["out"],
            "--workdir",
            paths["workdir"],
        ]
        ready = {
            "schema": CONSTRUCTION_READY_SCHEMA,
            "status": "READY",
            "created_at_utc":
                "2026-07-18T12:00:00Z",
            "instance": copy.deepcopy(instance),
            "timing_results": {
                "boot_id": instance["boot_id"],
                "result_set_sha256": result_sha,
                "pin_sha256": pin_sha,
                "t1_sample_ids": ["s000"],
                "t2_sample_ids": [
                    "s000",
                    "s001",
                ],
            },
            "payload": {
                "root": root,
                "source_manifest": {
                    "path": (
                        root
                        + "/data/f1k-carriers-v1/"
                        "generator/"
                        "construction-manifest.jsonl"
                    ),
                    "sha256": source_sha,
                },
                "bundle_manifest": {
                    "path":
                        root + "/bundle-manifest.json",
                    "sha256": bundle_sha,
                    "file_count": 12,
                },
            },
            "builder": {
                "path": builder,
                "sha256":
                    CONSTRUCTION_BUILDER_SHA256,
                "argv_base": argv,
            },
            "engine": {
                "argv": [
                    "/home/ubuntu/"
                    "colibri-construct/c/glm",
                    "64",
                    "4",
                    "8",
                ],
                "executable_path":
                    "/home/ubuntu/"
                    "colibri-construct/c/glm",
                "sha256": engine_sha,
                "weights_artifact_path":
                    weights_artifact,
                "weights_artifact_sha256":
                    weights_sha,
            },
            "tokenizer": {
                "argv": [
                    python,
                    root + "/tok_glm52.py",
                    tokenizer_artifact,
                ],
                "artifact_path": tokenizer_artifact,
                "sha256": tokenizer_sha,
            },
            "dump_patch": {
                "artifact_path": dump_artifact,
                "sha256": dump_sha,
            },
            "token_sidecar": {
                "path": (
                    "/home/ubuntu/f1k-gate/"
                    "gate-tokens/tokens-full.jsonl"
                ),
                "sha256": tokens_sha,
            },
            "pin": {
                "path": (
                    "/home/ubuntu/f1k-gate/"
                    "pin_bringup.stats"
                ),
                "sha256": pin_sha,
                "pin_gb": 40.0,
            },
            "launch": {
                "layers": list(range(3, 78)),
                "environment": {
                    "SNAP":
                        "/mnt/nvme/glm52_i4",
                    "TOK_SHA256": tokenizer_sha,
                    "OMP_NUM_THREADS": "8",
                    "OMP_DYNAMIC": "FALSE",
                    "OMP_PROC_BIND": "close",
                    "OMP_WAIT_POLICY": "active",
                    "COLI_OMP_TUNED": "1",
                },
            },
            "paths": copy.deepcopy(paths),
            "engine_tests": [
                {
                    "name": name,
                    "path": (
                        "/home/ubuntu/f1k-gate/"
                        + name
                        + ".evidence"
                    ),
                    "sha256":
                        format(index + 4, "x") * 64,
                    "verdict": "PASS",
                }
                for index, name in enumerate(
                    (
                        "kae",
                        "dump-a",
                        "dump-b",
                        "dump-c",
                        "functional-inertness",
                        "tokenizer-engine-agreement",
                    )
                )
            ],
        }

        gate = {
            "schema": BRINGUP_GATE_SCHEMA,
            "verdict": "GREEN",
            "reasons": [],
            "checks": {
                name: True
                for name in (
                    "rate_in_window",
                    "f_le_threshold",
                    "central_hours_in_window",
                    "central_usd_in_window",
                    "hi_band_below_caps",
                    "dump_preconditions_pass",
                    "functional_inertness_pass",
                    "lo_band_above_floors",
                    "prefills_ge_min",
                    "tokenizer_real",
                    "pin_regime_pinned",
                    "pin_engagement_pass",
                )
            },
            "f": {
                "blended": 1.45,
                "threshold": 1.6,
                "branch": "LE",
                "per_population": {
                    "construction": 1.45
                },
                "convention": "fixture",
            },
            "tokenizer": {
                "mode": "REAL",
                "mock_f": None,
                "sha256": tokenizer_sha,
            },
            "corpus_sha256": {
                "construction-manifest.jsonl":
                    source_sha,
                "test.jsonl": "a" * 64,
                "dev.jsonl": "b" * 64,
                "guard.jsonl": "c" * 64,
            },
            "sample": {
                "seed": 20260718,
                "rule": {
                    "quantile_edges": [0.0, 1.0],
                    "bin_alloc": [2],
                    "cont_tokens": 8,
                    "pop_floor": {
                        "construction": 1
                    },
                    "t1_n": 1,
                    "text": "fixture",
                },
                "realized_bin_edges_Tp": [10, 20],
                "n": 2,
                "t1_sample_ids": ["s000"],
                "entries": [
                    {
                        "sample_id": "s000",
                        "key":
                            "construction:0000",
                        "pop": "construction",
                        "bin": 0,
                        "W": 4,
                        "T": 6,
                        "Tp": 14,
                        "why": "stratified",
                    },
                    {
                        "sample_id": "s001",
                        "key":
                            "construction:0001",
                        "pop": "construction",
                        "bin": 0,
                        "W": 5,
                        "T": 7,
                        "Tp": 15,
                        "why": "campaign-max-T",
                    },
                ],
            },
            "model": {
                "type": "fixture",
                "knots_raw": [{"T": 14.0}],
                "knots_isotonic": [{"T": 14.0}],
                "isotonic_repairs": [],
                "se_rule": "fixture",
                "cont_tokens_addend": 8,
            },
            "pin": {
                "pin_file_sha256": pin_sha,
                "pin_gb": 40.0,
                "pin_file_path":
                    ready["pin"]["path"],
                "regime": "pinned-bringup",
                "derivation": {},
                "role": "fixture",
                "note": "fixture",
            },
            "model_bundle": {
                "add7_src_sha256": "9" * 64,
                "tokens_full_sha256": tokens_sha,
                "rule": "fixture",
            },
            "pin_engagement": {
                "pass": True,
                "problems": [],
                "rule": "fixture",
            },
            "rate": {
                "usd_per_hour": 0.219,
                "usd_per_hour_decimal": "0.219",
                "source": "fixture",
            },
            "projection": {
                "prefills": 11011,
                "replace_included": False,
                "instance_hours": {
                    "central": 700.0,
                    "hi": 750.0,
                    "lo": 650.0,
                },
                "usd_total": {
                    "central": 153.3,
                    "hi": 164.25,
                    "lo": 142.35,
                },
                "blended_s_per_prefill_central":
                    228.86,
                "hours_by_population_central": {
                    "construction": 100.0
                },
                "per_average_naive_hours_RETIRED":
                    690.0,
                "per_average_divergence_pct": 1.45,
                "reserve": {
                    "usd": 8.0,
                    "hours_at_rate": 36.53,
                    "rule": "fixture",
                    "usd_central_with_reserve":
                        161.3,
                    "hours_central_with_reserve":
                        736.5,
                },
            },
            "dump_gate": {
                "a": "PASS",
                "b": "PASS",
                "c": "PASS",
                "functional_inertness": "PASS",
                "rule": "fixture",
            },
            "thresholds": {
                "instance_hours": [260.6, 900.0],
                "usd_total": [73.0, 155.0],
                "rate_window": [0.0811, 0.5948],
                "prefills_min": 11011,
            },
            "semantics": "fixture",
        }

        binding = validate_ready_gate_binding(
            ready, gate
        )
        handoff = {
            "schema": CONSTRUCTION_HANDOFF_SCHEMA,
            "created_at_utc":
                "2026-07-18T12:01:00Z",
            "mode": "initial",
            "instance": copy.deepcopy(instance),
            "ready": {
                "path": CONSTRUCTION_READY_PATH,
                "sha256": hashlib.sha256(
                    canonical_json_bytes(ready)
                ).hexdigest(),
                "schema": CONSTRUCTION_READY_SCHEMA,
                "status": "READY",
            },
            "gate": {
                "path": BRINGUP_GATE_PATH,
                "sha256": hashlib.sha256(
                    canonical_json_bytes(gate)
                ).hexdigest(),
                "schema": BRINGUP_GATE_SCHEMA,
                "verdict": "GREEN",
            },
            "binding": binding,
            "rate": {
                "usd_per_hour_decimal": "0.219",
                "local_ssd_count": 2,
                "evidence": {
                    "path": RATE_EVIDENCE_PATH,
                    "sha256": "8" * 64,
                    "schema": RATE_EVIDENCE_SCHEMA,
                    "observed_at_utc":
                        "2026-07-18T12:00:30Z",
                },
            },
            "provider": {
                "campaign_started_at_utc":
                    "2026-07-18T12:00:00Z",
                "termination_time_utc":
                    "2026-08-24T23:00:00Z",
                "termination_timestamp_utc":
                    "2026-08-24T23:00:00Z",
                "instance_termination_action":
                    "DELETE",
                "frozen_hours_max_decimal": "900",
                "armed_hours_decimal": "899",
                "non_compute_allowance_usd_decimal":
                    "50",
                "rate_headroom_usd_decimal": "10",
                "compute_ceiling_usd_decimal":
                    "196.881",
                "total_envelope_usd_decimal":
                    "256.881",
                "budget": {
                    "resource_name":
                        "billingAccounts/123/"
                        "budgets/456",
                    "amount_usd_decimal": "300",
                    "project_id": "test-project",
                },
            },
            "paths": copy.deepcopy(paths),
            "service": {
                "manager": "systemd",
                "unit_name":
                    "kot-f1k-construction.service",
                "user": "ubuntu",
                "working_directory": root,
                "exec_argv": [
                    python,
                    root + "/f1k_bringup_gate.py",
                    "guard",
                    "--handoff",
                    CONSTRUCTION_HANDOFF_PATH,
                ],
                "restart_policy": "no",
                "enabled_on_boot": False,
            },
        }
        return ready, gate, handoff

    def happy():
        ready, gate, handoff = records()
        license_a = build_runtime_license(
            ready, gate, handoff
        )
        reordered = dict(
            reversed(list(ready.items()))
        )
        license_b = build_runtime_license(
            reordered, gate, handoff
        )
        return (
            license_a == license_b
            and license_a["schema"]
            == RUNTIME_LICENSE_SCHEMA
            and canonical_json_bytes(license_a)
            == canonical_json_bytes(license_b)
        )

    check(
        "landed-shaped READY + GREEN produce one "
        "deterministic runtime license",
        happy,
    )

    def ready_schema_refusals():
        ready, _, _ = records()
        missing = copy.deepcopy(ready)
        del missing["status"]
        unknown = copy.deepcopy(ready)
        unknown["unknown"] = {}
        wrong = copy.deepcopy(ready)
        wrong["schema"] = (
            "kot-f1k-construction-ready/2"
        )
        return all(
            refuses(
                lambda value=value:
                    validate_ready(value)
            )
            for value in (missing, unknown, wrong)
        )

    check(
        "READY wrong/missing/unknown schema fields "
        "refuse",
        ready_schema_refusals,
    )

    def identity_refusal():
        ready, _, _ = records()
        ready["timing_results"]["boot_id"] = (
            "00000000-0000-4000-8000-000000000000"
        )
        return refuses(
            lambda: validate_ready(ready)
        )

    check(
        "READY identity/timing mismatch refuses",
        identity_refusal,
    )

    def gate_schema_refusals():
        _, gate, _ = records()
        wrong = copy.deepcopy(gate)
        wrong["schema"] = (
            "kot-f1k-bringup-gate/1"
        )
        stopped = copy.deepcopy(gate)
        stopped["verdict"] = "STOP"
        unknown = copy.deepcopy(gate)
        unknown["unknown"] = {}
        return all(
            refuses(
                lambda value=value:
                    validate_gate(value)
            )
            for value in (
                wrong,
                stopped,
                unknown,
            )
        )

    check(
        "gate not closed /2 GREEN refuses",
        gate_schema_refusals,
    )

    def mismatch(path, value):
        ready, gate, _ = records()
        target = gate
        for key in path[:-1]:
            target = target[key]
        target[path[-1]] = value
        return refuses(
            lambda:
                validate_ready_gate_binding(
                    ready, gate
                )
        )

    check(
        "token-sidecar mismatch refuses",
        lambda: mismatch(
            (
                "model_bundle",
                "tokens_full_sha256",
            ),
            "0" * 64,
        ),
    )
    check(
        "tokenizer mismatch refuses",
        lambda: mismatch(
            ("tokenizer", "sha256"),
            "0" * 64,
        ),
    )
    check(
        "pin mismatch refuses",
        lambda: mismatch(
            ("pin", "pin_file_sha256"),
            "0" * 64,
        ),
    )
    check(
        "construction-corpus mismatch refuses",
        lambda: mismatch(
            (
                "corpus_sha256",
                "construction-manifest.jsonl",
            ),
            "0" * 64,
        ),
    )

    def sample_refusal():
        ready, gate, _ = records()
        ready["timing_results"][
            "t2_sample_ids"
        ] = ["s001", "s000"]
        return refuses(
            lambda:
                validate_ready_gate_binding(
                    ready, gate
                )
        )

    check(
        "timing sample-ID mismatch refuses",
        sample_refusal,
    )

    def layer_refusal():
        ready, _, _ = records()
        ready["launch"]["layers"] = list(
            range(3, 77)
        )
        return refuses(
            lambda: validate_ready(ready)
        )

    check(
        "layer drift refuses",
        layer_refusal,
    )

    def argv_path_refusal():
        ready, _, _ = records()
        ready["builder"]["argv_base"][1] = (
            "/tmp/alternate-builder.py"
        )
        return refuses(
            lambda: validate_ready(ready)
        )

    check(
        "builder/interpreter/path substitution seam "
        "refuses",
        argv_path_refusal,
    )

    def handoff_refusals():
        _, _, handoff = records()
        unknown = copy.deepcopy(handoff)
        unknown["unknown"] = {}
        floated = copy.deepcopy(handoff)
        floated["provider"][
            "armed_hours_decimal"
        ] = 899.0
        over = copy.deepcopy(handoff)
        over["provider"][
            "total_envelope_usd_decimal"
        ] = "300.001"
        return all(
            refuses(
                lambda value=value:
                    validate_handoff(value)
            )
            for value in (
                unknown,
                floated,
                over,
            )
        )

    check(
        "handoff closed schema and canonical-decimal "
        "accounting refuse drift",
        handoff_refusals,
    )

    def artifact_happy():
        with tempfile.TemporaryDirectory(
            prefix="kot-f1k-b0-"
        ) as raw:
            root = Path(raw)
            payload = root / "payload"
            payload.mkdir()
            artifact = payload / "tool"
            artifact.write_bytes(
                b"fixture artifact\n"
            )
            artifact.chmod(0o700)
            digest = hashlib.sha256(
                artifact.read_bytes()
            ).hexdigest()
            return (
                verify_artifact(
                    artifact,
                    digest,
                    root=payload,
                    executable=True,
                )
                == {
                    "path": os.fspath(artifact),
                    "sha256": digest,
                }
                and refuses(
                    lambda: verify_artifact(
                        artifact,
                        "0" * 64,
                        root=payload,
                    )
                )
            )

    check(
        "artifact verifier accepts exact SHA pair "
        "and refuses SHA drift",
        artifact_happy,
    )

    def artifact_refusals():
        with tempfile.TemporaryDirectory(
            prefix="kot-f1k-b0-"
        ) as raw:
            root = Path(raw)
            payload = root / "payload"
            payload.mkdir()
            outside = root / "outside"
            outside.write_bytes(b"outside\n")
            link = payload / "link"
            link.symlink_to(outside)
            fifo = payload / "fifo"
            os.mkfifo(fifo)
            digest = hashlib.sha256(
                outside.read_bytes()
            ).hexdigest()
            return (
                refuses(
                    lambda: verify_artifact(
                        link,
                        digest,
                        root=payload,
                    )
                )
                and refuses(
                    lambda: verify_artifact(
                        outside,
                        digest,
                        root=payload,
                    )
                )
                and refuses(
                    lambda: verify_artifact(
                        fifo,
                        digest,
                        root=payload,
                    )
                )
            )

    check(
        "artifact symlink, path escape, and special "
        "file refuse",
        artifact_refusals,
    )

    print(
        "SELFTEST-B0: %d/%d PASS"
        % (passed, total)
    )
    return 0 if passed == total else 2


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
            "usage: f1k_ops.py selftest | selftest-b0",
        )

    command = sys.argv[1]
    if command == "selftest":
        parser = argparse.ArgumentParser(
            prog="f1k_ops.py selftest"
        )
        parser.parse_args(sys.argv[2:])
        return selftest()
    if command == "selftest-b0":
        parser = argparse.ArgumentParser(
            prog="f1k_ops.py selftest-b0"
        )
        parser.parse_args(sys.argv[2:])
        return selftest_b0()

    _die(
        "F1K_OPS_USAGE",
        "unknown command %r "
        "(expected selftest or selftest-b0)"
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
