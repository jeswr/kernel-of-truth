#!/usr/bin/env python3
"""Fork-independent F1-K operational foundations.

Includes the option-B lean provider-native spend-cap backstop (maintainer
ruling #53: build B, not the full-rigor option-A durable-ledger controller).
Its selftests are pure/local and never contact GCP or another network service.
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
# Cloud Billing budget resource name: billingAccounts/<id>/budgets/<id>
# (LC-8v3 / R3.3 — the handoff must carry the EXACT budget resource, not a
# free-form string; "any $300 budget" never validates).
_BUDGET_RESOURCE_RE = re.compile(
    r"billingAccounts/[A-Za-z0-9-]{3,60}/budgets/[A-Za-z0-9-]{1,64}\Z"
)

CONSTRUCTION_READY_SCHEMA = "kot-f1k-construction-ready/1"
BRINGUP_GATE_SCHEMA = "kot-f1k-bringup-gate/2"
# Rev4/variant-B: the construction handoff is /2 — the provider block carries
# a live-STOP `cap` sub-object (native GCE terminationTime) and a `cleanup`
# sub-object (verified post-cap deletion). The /1 literal-DELETE form is the
# rejected variant-A record and is REFUSED by validate_handoff.
CONSTRUCTION_HANDOFF_SCHEMA = "kot-f1k-construction-handoff/2"
CONSTRUCTION_HANDOFF_SCHEMA_V1 = "kot-f1k-construction-handoff/1"
# The unified provider action for BOTH Spot preemption and the runtime-limit
# cap (GCE treats instanceTerminationAction as one field — R3.1/R3.2).
CAP_MECHANISM = "gce-termination-time"
CAP_ACTION = "STOP"
CLEANUP_MECHANISM = "control-box-reaper"
CLEANUP_ACTION = "DELETE"
# DESIGN QUESTION (flagged for the CAP-PROBE, PROPOSED-CC-13): the exact GCE
# scheduling field that reflects "discard Local SSD at STOP-termination" is
# doc-inferred, not yet API-confirmed. verify_provider_cap reads THIS key from
# the live scheduling block and requires a truthy value. The CAP-PROBE settles
# the real field name before build freeze; the fake supplies this key in the
# $0 oracle. If the probe finds a different field, change this one constant.
DISCARD_LOCAL_SSD_KEY = "discardLocalSsdsAtTermination"
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


def _resolve_boot_id(bootid_transport=None) -> str:
    """LC-9: resolve the boot id from an injected transport or the local /proc.

    bootid_transport() -> str (a raw boot_id). Default = the local read
    (on-VM path). The control box injects an SSH guest read so the boot id
    compared is the GUEST's, not the control box's.
    """
    if bootid_transport is None:
        return _read_boot_id()
    try:
        raw = bootid_transport()
    except F1KOpsError:
        raise
    except Exception as exc:  # noqa: BLE001 — fail closed
        raise F1KOpsError(
            "F1K_IDENTITY", "boot_id transport failed: %s" % exc
        ) from exc
    if not isinstance(raw, str):
        raise F1KOpsError(
            "F1K_IDENTITY", "boot_id transport did not return a string"
        )
    raw = raw.strip()
    try:
        parsed = uuid.UUID(raw)
    except ValueError as exc:
        raise F1KOpsError(
            "F1K_IDENTITY", "transport boot_id is not a valid UUID"
        ) from exc
    canonical = str(parsed)
    if raw.lower() != canonical:
        raise F1KOpsError(
            "F1K_IDENTITY", "transport boot_id is not canonical"
        )
    return canonical


def resolve_live_instance_identity(
    *, metadata_transport=None, compute_transport=None, bootid_transport=None
) -> dict:
    """Resolve and cross-bind local metadata to Compute instances.get.

    compute_transport is called with keyword arguments project_id, zone, and
    instance_name. It must return a full Compute instance object.

    LC-9: bootid_transport is injectable. Default = the LOCAL /proc read (the
    on-VM READY writer path, unchanged). The control box injects an SSH guest
    read (`cat /proc/sys/kernel/random/boot_id` as ubuntu@<vm>) so a
    control-box-side identity resolution compares the GUEST boot id, not the
    control box's own — otherwise every continue launch would false-refuse.
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
    boot_id = _resolve_boot_id(bootid_transport)

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


def validate_handoff(record, *, now_utc=None):
    """Validate the closed variant-B construction handoff /2 (LC-8v3).

    now_utc (RFC3339, default = real current UTC) anchors the freshness rule
    (R3.4/R4.4): campaign_started_at_utc <= now_utc STRICTLY (no skew) AND
    campaign_started_at_utc <= created_at_utc <= now_utc — so a hand-built
    FUTURE campaign start cannot understate exposure by any amount. The guard
    repeats this with its OWN fresh clock at license load.
    """
    code = "F1K_HANDOFF"
    now_ts = _utc_timestamp(
        now_utc if now_utc is not None else _utc_now_z(),
        field="now_utc", code=code,
    )
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
    if handoff["schema"] == CONSTRUCTION_HANDOFF_SCHEMA_V1:
        raise F1KOpsError(
            code,
            "handoff schema is the rejected variant-A /1 (literal DELETE); "
            "variant B requires /2 with a live-STOP cap block",
        )
    if (
        handoff["schema"]
        != CONSTRUCTION_HANDOFF_SCHEMA
        or handoff["mode"] != "initial"
    ):
        raise F1KOpsError(
            code,
            "handoff schema/mode is not variant-B "
            "initial /2",
        )
    created_at_ts = _contract_timestamp(
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
            "cap",
            "cleanup",
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
    campaign_started = _contract_timestamp(
        provider["campaign_started_at_utc"],
        field="handoff.provider.campaign_started_at_utc",
        code=code,
    )

    # /2 cap block (variant B, R3.2): the native STOP runtime-limit cap. Its
    # fields are populated ONLY from the LC-5 verify_cap_armed composite; a
    # hand-built cap block echoing a provisioning flag is refused structurally
    # (the composite cannot exist unless every live leg verified).
    cap = _closed_contract_object(
        provider["cap"],
        field="handoff.provider.cap",
        keys=(
            "mechanism",
            "action",
            "termination_time_utc",
            "termination_timestamp_utc",
        ),
        code=code,
    )
    cap_intended = _contract_timestamp(
        cap["termination_time_utc"],
        field="handoff.provider.cap.termination_time_utc",
        code=code,
    )
    cap_readback = _contract_timestamp(
        cap["termination_timestamp_utc"],
        field="handoff.provider.cap.termination_timestamp_utc",
        code=code,
    )
    if (
        cap["mechanism"] != CAP_MECHANISM
        or cap["action"] != CAP_ACTION
        or cap_intended != cap_readback
    ):
        raise F1KOpsError(
            code,
            "provider cap is not the read-back native STOP terminationTime "
            "(mechanism=%s action=STOP intended==read-back)" % CAP_MECHANISM,
        )

    cleanup = _closed_contract_object(
        provider["cleanup"],
        field="handoff.provider.cleanup",
        keys=("mechanism", "action", "verified"),
        code=code,
    )
    if (
        cleanup["mechanism"] != CLEANUP_MECHANISM
        or cleanup["action"] != CLEANUP_ACTION
        or cleanup["verified"] != "delete-poll-done-absence"
    ):
        raise F1KOpsError(
            code,
            "provider cleanup block is not the verified reaper deletion "
            "(mechanism/action/verified)",
        )

    # Freshness + ordering (R3.4/R4.4): campaign_started <= created_at <= now,
    # strict, no skew allowance. The producer captures the start strictly
    # before writing the handoff, so legitimate ordering always holds; a
    # hand-built FUTURE start refuses.
    started_dt = _utc_datetime(
        campaign_started, field="campaign_started_at_utc", code=code
    )
    created_dt = _utc_datetime(
        created_at_ts, field="created_at_utc", code=code
    )
    now_dt = _utc_datetime(now_ts, field="now_utc", code=code)
    if not (started_dt <= created_dt <= now_dt):
        raise F1KOpsError(
            code,
            "provider campaign start / handoff creation / now are not "
            "ordered campaign_started <= created_at <= now (future-start or "
            "clock-ahead exposure understatement)",
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
            "variant-B limits",
        )
    # LC-8: RECOMPUTE armed_hours from campaign_started -> cap.termination_time
    # under the producer's ROUND_CEILING / 6 dp rule and require exact equality
    # plus strict timestamp ordering — an understated "armed_hours_decimal"
    # can no longer satisfy the $300 arithmetic.
    cap_deadline_dt = _utc_datetime(
        cap_intended, field="cap.termination_time_utc", code=code
    )
    if not (started_dt < cap_deadline_dt):
        raise F1KOpsError(
            code,
            "provider campaign start is not strictly before the cap "
            "termination time",
        )
    recomputed_armed = _hours_ceiling(started_dt, cap_deadline_dt)
    if recomputed_armed != decimals["armed_hours_decimal"]:
        raise F1KOpsError(
            code,
            "provider armed_hours_decimal %s != recomputed %s (LC-8)"
            % (decimals["armed_hours_decimal"], recomputed_armed),
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
    if not _BUDGET_RESOURCE_RE.fullmatch(budget["resource_name"]):
        raise F1KOpsError(
            code,
            "provider budget.resource_name is not a "
            "billingAccounts/<id>/budgets/<id> resource (LC-8)",
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


def build_runtime_license(ready, gate, handoff, *, now_utc=None):
    """Build the normalized variant-B license used by launch and guard.

    now_utc is threaded to validate_handoff's freshness rule (R3.4); the guard
    passes its OWN fresh clock at license load so a stale/future campaign start
    refuses at the spend authority, not only at production.
    """
    ready = validate_ready(ready)
    gate = validate_gate(gate)
    handoff = validate_handoff(handoff, now_utc=now_utc)
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


PRIOR_SPEND_SCHEMA = "kot-f1k-prior-spend/1"


def build_prior_spend(*, launch_epoch_utc, campaign_started_at_utc,
                      licensed_rate, instance_id) -> dict:
    """Build the kot-f1k-prior-spend/1 record (Rev2 R2.6-#8 / LC-13).

    Carries the bring-up epoch, campaign start, ROUND_CEILING 6-dp elapsed
    hours, the licensed rate, and bringup_cost = elapsed x rate (ROUND_CEILING),
    self-hashed. LC-13 makes `cmd_config_cost` REQUIRE this record and refuse
    manual prior dollars/hours, so bring-up spend is BOUND as evidence with an
    enforcing consumer — it can never vanish from the 900 h analysis basis.
    """
    from decimal import ROUND_CEILING
    launch_dt = _utc_datetime(
        launch_epoch_utc, field="launch_epoch_utc", code="F1K_PRIOR")
    started_dt = _utc_datetime(
        campaign_started_at_utc, field="campaign_started_at_utc",
        code="F1K_PRIOR")
    if not (launch_dt < started_dt):
        raise F1KOpsError(
            "F1K_PRIOR",
            "campaign start must be strictly after the launch epoch")
    elapsed = _hours_ceiling(launch_dt, started_dt)
    rate = canonical_decimal(licensed_rate, field="licensed_rate")
    with localcontext() as ctx:
        ctx.prec = 80
        cost = (elapsed * Decimal(rate)).quantize(
            Decimal("0.000001"), rounding=ROUND_CEILING)
    ident = _strict_string(
        instance_id, field="instance_id", pattern=_NUMERIC_ID_RE)
    record = {
        "schema": PRIOR_SPEND_SCHEMA,
        "launch_epoch_utc": _utc_timestamp(
            launch_epoch_utc, field="launch_epoch_utc", code="F1K_PRIOR"),
        "campaign_started_at_utc": _utc_timestamp(
            campaign_started_at_utc, field="campaign_started_at_utc",
            code="F1K_PRIOR"),
        "bringup_elapsed_hours_decimal": str(elapsed),
        "licensed_rate_usd_per_hour_decimal": rate,
        "bringup_cost_usd_decimal": str(cost),
        "instance_id": ident,
    }
    record["sha256"] = hashlib.sha256(
        canonical_json_bytes(record)).hexdigest()
    return record


def validate_prior_spend(record, *, rate=None, instance_id=None) -> dict:
    """Validate a kot-f1k-prior-spend/1 record: schema/sha/arithmetic/binding
    (LC-13). Returns the DERIVED {prior_usd, prior_hours} as canonical strings.
    Fails closed on any tamper; manual override is impossible by construction —
    the derived values come only from the self-consistent record."""
    code = "F1K_PRIOR"
    obj = _closed_contract_object(
        record, field="prior-spend", keys=(
            "schema", "launch_epoch_utc", "campaign_started_at_utc",
            "bringup_elapsed_hours_decimal",
            "licensed_rate_usd_per_hour_decimal", "bringup_cost_usd_decimal",
            "instance_id", "sha256"), code=code)
    if obj["schema"] != PRIOR_SPEND_SCHEMA:
        raise F1KOpsError(code, "prior-spend schema is not %s"
                          % PRIOR_SPEND_SCHEMA)
    unhashed = {k: obj[k] for k in obj if k != "sha256"}
    expected = hashlib.sha256(canonical_json_bytes(unhashed)).hexdigest()
    if not isinstance(obj["sha256"], str) or obj["sha256"] != expected:
        raise F1KOpsError(code, "prior-spend sha256 does not recompute")
    rebuilt = build_prior_spend(
        launch_epoch_utc=obj["launch_epoch_utc"],
        campaign_started_at_utc=obj["campaign_started_at_utc"],
        licensed_rate=obj["licensed_rate_usd_per_hour_decimal"],
        instance_id=obj["instance_id"])
    if (rebuilt["bringup_elapsed_hours_decimal"]
            != obj["bringup_elapsed_hours_decimal"]
            or rebuilt["bringup_cost_usd_decimal"]
            != obj["bringup_cost_usd_decimal"]):
        raise F1KOpsError(
            code, "prior-spend arithmetic (elapsed/cost) does not recompute")
    if rate is not None and canonical_decimal(rate, field="rate") != \
            obj["licensed_rate_usd_per_hour_decimal"]:
        raise F1KOpsError(
            code, "prior-spend rate %s != config rate %s"
            % (obj["licensed_rate_usd_per_hour_decimal"], rate))
    if instance_id is not None and obj["instance_id"] != instance_id:
        raise F1KOpsError(
            code, "prior-spend instance_id %s != expected %s"
            % (obj["instance_id"], instance_id))
    return {
        "prior_usd": obj["bringup_cost_usd_decimal"],
        "prior_hours": obj["bringup_elapsed_hours_decimal"],
        "instance_id": obj["instance_id"],
        "licensed_rate": obj["licensed_rate_usd_per_hour_decimal"],
    }


# --- governance layer (ledger/lease/attestation) pending issue #53 A/B/C ---


def build_construction_fixture():
    """Shared valid variant-B (ready, gate) fixture — the b0 records()
    triple, exposed module-level so the construction-continue $0 oracle reuses
    the exact canonical shapes (no divergent hand-rolled fixture)."""
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
            "cap": {
                "mechanism":
                    "gce-termination-time",
                "action": "STOP",
                "termination_time_utc":
                    "2026-08-24T23:00:00Z",
                "termination_timestamp_utc":
                    "2026-08-24T23:00:00Z",
            },
            "cleanup": {
                "mechanism":
                    "control-box-reaper",
                "action": "DELETE",
                "verified":
                    "delete-poll-done-absence",
            },
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
    return ready, gate



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
                "cap": {
                    "mechanism":
                        "gce-termination-time",
                    "action": "STOP",
                    "termination_time_utc":
                        "2026-08-24T23:00:00Z",
                    "termination_timestamp_utc":
                        "2026-08-24T23:00:00Z",
                },
                "cleanup": {
                    "mechanism":
                        "control-box-reaper",
                    "action": "DELETE",
                    "verified":
                        "delete-poll-done-absence",
                },
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


# ----------------------------------------------------------------------------
# Option-B governance layer — lean provider-native construction spend backstop.
#
# Maintainer ruling #53 (2026-07-19): build B, NOT the full-rigor option-A
# durable ledger/lease/attestation-CAS controller. The governance job is a HARD
# SPEND CAP, nothing more (pinning was refuted on #55 so speed is irrelevant).
# The hard bound is achieved provider-side: the VM self-deletes at the 900 h
# wall-clock cap, and because a GCP Spot instance resumes as the SAME instance,
# instance-hours <= wall-clock <= cap. A $300 billing budget and a pre-spend
# live-rate guard are backstops. No bespoke ledger/lease/CAS lives here.
#
# All transports are injectable. Every transport-bearing entry point either
# fails closed when its transport is absent (write_launch_epoch, verify/assure,
# guard, preflight) or is an explicitly-named local recovery read
# (read_elapsed_hours with mirror_transport=None). Nothing here reaches a
# network at import or during selftest_b1 (pure/local, $0).
#
# Revised 2026-07-19 after the GPT-5.6 cross-vendor review returned MUST-FIX:
# deadline now derives from the persisted epoch (not a caller value); the
# rate*s product is computed exactly; guard/preflight fail closed on an absent
# catalog transport; the $300 ceiling is not caller-overridable; the timer
# verifier binds Persistent + triggered Unit + the delete ExecStart target;
# transport/parse failures normalize to F1K_B_* and preflight fails closed on
# any error. Residual single-writer/durable-mirror assumptions are documented.
# ----------------------------------------------------------------------------

# Frozen anchors (do not edit without the frozen record). The 900 h wall-clock
# cap is the upper bound of instance_hours in [260.6, 900] h
# (analysis/f1k.py, pinned) and registry/experiments/f1k.json (ASM-2405 context).
SELFDELETE_CAP_HOURS = Decimal("900")
# Rev4 R4.1 (PROPOSED-CC-14): the provider may take up to 30 s AFTER the
# configured terminationTime to begin STOPPING, so a raw epoch+900h cannot
# support a hard <=900 h compute bound. T_cap = epoch + 900 h - 10 min. The
# 10 min margin exceeds the documented worst case by >1 order of magnitude and
# costs 0.019% of the window; CPU charges cease at STOPPING, so the
# RUNNING-billable window is provably < 900 h. compute_selfdelete_deadline is
# the SINGLE deadline derivation, so L1/L2/handoff/preflight/re-probe/guard all
# share this one conservative value.
SELFDELETE_MARGIN_MINUTES = 10
# $300 is the maintainer's protective GCE billing ceiling (a superset of the
# $155 frozen construction-compute cap, ASM-2374). NOT caller-overridable.
BILLING_CEILING_USD = "300"
# Spot rate window (poc/gcp/f1k_gcp.py): [$0.081, $0.595]/h.
RATE_MIN_USD_PER_HOUR = Decimal("0.081")
RATE_MAX_USD_PER_HOUR = Decimal("0.595")
# Two-sided construction gate (poc/gcp/f1k_gcp.py): s/prefill in [47.0, 162.3] s
# AND s/prefill * rate in [13.16, 27.95] $*s/h.
SPP_MIN_SECONDS = Decimal("47.0")
SPP_MAX_SECONDS = Decimal("162.3")
RATE_SPP_PRODUCT_MIN = Decimal("13.16")
RATE_SPP_PRODUCT_MAX = Decimal("27.95")

LAUNCH_EPOCH_SCHEMA = "kot-f1k-launch-epoch/1"
LAUNCH_EPOCH_KEY = "launch-epoch/%s" % LAUNCH_EPOCH_SCHEMA
SELFDELETE_TIMER_UNIT = "f1k-selfdelete.timer"
SELFDELETE_SERVICE_UNIT = "f1k-selfdelete.service"


def _utc_datetime(value, *, field: str, code: str) -> datetime:
    """Validate an RFC3339 value and return an aware UTC datetime.

    Reuses _utc_timestamp for validation/normalization, then parses the
    canonical Z form for arithmetic. No binary float is involved. Rejects
    sub-microsecond precision rather than silently truncating it.
    """
    normalized = _utc_timestamp(value, field=field, code=code)
    body = normalized[:-1]  # drop trailing Z
    if "." in body:
        base, fraction = body.split(".", 1)
        if len(fraction) > 6:
            raise F1KOpsError(
                code,
                "%s has sub-microsecond precision: %r" % (field, value),
            )
        micro = int((fraction + "000000")[:6])
    else:
        base, micro = body, 0
    parsed = datetime.strptime(base, "%Y-%m-%dT%H:%M:%S")
    return parsed.replace(microsecond=micro, tzinfo=timezone.utc)


def _elapsed_hours(start: datetime, end: datetime) -> Decimal:
    """Exact Decimal hours between two aware datetimes (end - start).

    The numerator is an exact integer count of microseconds; the quotient is
    taken at high precision (ample for the whole-hour 900 h cap comparison).
    """
    delta = end - start
    total_us = (
        (delta.days * 86400 + delta.seconds) * 1_000_000
        + delta.microseconds
    )
    with localcontext() as ctx:
        ctx.prec = 50
        return Decimal(total_us) / Decimal(3_600_000_000)


def _utc_now_z() -> str:
    """Current UTC as a second-resolution RFC3339 Z string."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S") + "Z"


def _hours_ceiling(start: datetime, end: datetime, *, dp: int = 6) -> Decimal:
    """Exact hours between two aware datetimes, quantized UP to `dp` decimals.

    ROUND_CEILING so the armed-hours envelope OVER-states exposure — the
    conservative direction for a spend cap (LC-8 recompute).
    """
    from decimal import ROUND_CEILING
    exact = _elapsed_hours(start, end)
    quant = Decimal(1).scaleb(-dp)
    with localcontext() as ctx:
        ctx.prec = 80
        return exact.quantize(quant, rounding=ROUND_CEILING)


def _exact_product(a: Decimal, b: Decimal) -> Decimal:
    """Return a*b with no context rounding (exact for any finite operands)."""
    need = len(a.as_tuple().digits) + len(b.as_tuple().digits) + 2
    with localcontext() as ctx:
        ctx.prec = max(need, 28)
        return a * b


def _build_launch_epoch(launch_utc_z: str) -> dict:
    record = {
        "schema": LAUNCH_EPOCH_SCHEMA,
        "launch_utc": launch_utc_z,
    }
    record["sha256"] = hashlib.sha256(
        canonical_json_bytes(record)
    ).hexdigest()
    return record


def _parse_launch_epoch(record, *, source: str) -> str:
    """Validate a launch-epoch record and return its normalized launch_utc.

    The SHA is an integrity check against accidental corruption / unrecomputed
    edits; it is not authentication (anyone able to rewrite the record can
    recompute it). Durability, not authenticity, is B's threat model.
    """
    if not isinstance(record, dict):
        raise F1KOpsError(
            "F1K_B_EPOCH_SHAPE", "%s epoch is not an object" % source
        )
    if set(record) != {"schema", "launch_utc", "sha256"}:
        raise F1KOpsError(
            "F1K_B_EPOCH_SHAPE", "%s epoch has unexpected keys" % source
        )
    if record["schema"] != LAUNCH_EPOCH_SCHEMA:
        raise F1KOpsError(
            "F1K_B_EPOCH_SCHEMA", "%s epoch has wrong schema" % source
        )
    unhashed = {
        "schema": record["schema"],
        "launch_utc": record["launch_utc"],
    }
    expected = hashlib.sha256(
        canonical_json_bytes(unhashed)
    ).hexdigest()
    if not isinstance(record["sha256"], str) or record["sha256"] != expected:
        raise F1KOpsError(
            "F1K_B_EPOCH_SHA", "%s epoch sha256 does not recompute" % source
        )
    return _utc_timestamp(
        record["launch_utc"],
        field="%s launch_utc" % source,
        code="F1K_B_EPOCH_TIME",
    )


def _load_epoch_bytes(data, *, source: str) -> str:
    try:
        record = json.loads(data.decode("utf-8"))
    except (ValueError, AttributeError, UnicodeDecodeError) as exc:
        raise F1KOpsError(
            "F1K_B_EPOCH_SHAPE",
            "%s epoch is not JSON: %s" % (source, exc),
        ) from exc
    return _parse_launch_epoch(record, source=source)


def _mirror_get(mirror_transport):
    """Fetch the durable epoch blob, normalizing transport failure."""
    try:
        return mirror_transport(action="get", key=LAUNCH_EPOCH_KEY)
    except F1KOpsError:
        raise
    except Exception as exc:  # noqa: BLE001 — normalize to fail-closed
        raise F1KOpsError(
            "F1K_B_MIRROR_TRANSPORT", "mirror get failed: %s" % exc
        ) from exc


def write_launch_epoch(
    *, launch_utc, local_path, mirror_transport=None
) -> dict:
    """Persist the launch timestamp durably; write-once.

    Writes the epoch to a local file AND a durable mirror (injectable
    mirror_transport). A GCP Spot instance loses Local SSD contents on a
    preemption stop, so the mirror (e.g. GCS) is the authoritative copy that
    survives preemption; the local file is a fast-path cache. A resume must
    NOT reset the clock, so an existing epoch with a different launch is
    refused. Re-writing the identical epoch is idempotent.

    LIMITATION (documented, not enforceable here): write-once holds only while
    at least one durable source survives. If BOTH the mirror and local copy
    are gone, there is no record to compare against and a fresh launch will set
    a new clock — this is why the mirror must be genuinely durable (GCS). The
    get-then-put is non-atomic, so write-once also assumes a single writer.

    mirror_transport(action, key, data=None):
        action="get" -> bytes or None (absent)
        action="put" -> persist data bytes durably; raise on failure
    """
    normalized = _utc_timestamp(
        launch_utc, field="launch_utc", code="F1K_B_EPOCH_TIME"
    )
    if mirror_transport is None:
        raise F1KOpsError(
            "F1K_B_MIRROR",
            "write_launch_epoch requires a durable mirror_transport",
        )
    record = _build_launch_epoch(normalized)
    payload = canonical_json_bytes(record)

    existing = _mirror_get(mirror_transport)
    if existing is not None:
        prior = _load_epoch_bytes(existing, source="mirror")
        if prior != normalized:
            raise F1KOpsError(
                "F1K_B_EPOCH_OVERWRITE",
                "refusing to reset the launch clock: mirror holds %r"
                % prior,
            )
    if os.path.exists(local_path):
        try:
            with open(local_path, "rb") as handle:
                prior_local = _load_epoch_bytes(
                    handle.read(), source="local"
                )
        except OSError as exc:
            raise F1KOpsError(
                "F1K_B_EPOCH_SHAPE",
                "cannot read existing local epoch: %s" % exc,
            ) from exc
        if prior_local != normalized:
            raise F1KOpsError(
                "F1K_B_EPOCH_OVERWRITE",
                "refusing to reset the launch clock: local holds %r"
                % prior_local,
            )

    local_sha = atomic_write_json(local_path, record)
    try:
        mirror_transport(action="put", key=LAUNCH_EPOCH_KEY, data=payload)
    except F1KOpsError:
        raise
    except Exception as exc:  # noqa: BLE001
        raise F1KOpsError(
            "F1K_B_MIRROR_TRANSPORT", "mirror put failed: %s" % exc
        ) from exc
    return {
        "launch_utc": normalized,
        "sha256": record["sha256"],
        "local_sha256": local_sha,
        "mirror_key": LAUNCH_EPOCH_KEY,
    }


def _resolve_epoch_launch(
    *, local_path, mirror_transport, require_mirror=False
) -> str:
    """Return the single authoritative launch_utc from the durable sources.

    The mirror (when supplied) is authoritative because it survives Spot
    preemption; a present local copy must agree with it. Fails closed if no
    durable source exists or the sources disagree.

    LC-12: in `require_mirror` mode (the launch context) a mirror object that
    is ABSENT while a local copy EXISTS is a durability failure, not a
    fallback — it REFUSES (F1K_B_MIRROR_REQUIRED). Mirror loss must never be
    silently papered over by the fast-path local cache when spend is at stake.
    """
    launches = {}
    mirror_present = False
    if mirror_transport is not None:
        data = _mirror_get(mirror_transport)
        if data is not None:
            mirror_present = True
            launches["mirror"] = _load_epoch_bytes(data, source="mirror")
    if require_mirror and mirror_transport is None:
        raise F1KOpsError(
            "F1K_B_MIRROR_REQUIRED",
            "launch context requires a durable mirror_transport",
        )
    if os.path.exists(local_path):
        try:
            with open(local_path, "rb") as handle:
                launches["local"] = _load_epoch_bytes(
                    handle.read(), source="local"
                )
        except OSError as exc:
            raise F1KOpsError(
                "F1K_B_EPOCH_SHAPE", "cannot read local epoch: %s" % exc
            ) from exc
    if require_mirror and "local" in launches and not mirror_present:
        raise F1KOpsError(
            "F1K_B_MIRROR_REQUIRED",
            "launch context: a local epoch exists but the durable mirror is "
            "ABSENT — mirror loss is not a fallback (LC-12)",
        )
    if not launches:
        raise F1KOpsError(
            "F1K_B_EPOCH_MISSING", "no durable launch epoch is available"
        )
    if len(set(launches.values())) != 1:
        raise F1KOpsError(
            "F1K_B_EPOCH_SPLIT",
            "launch epoch sources disagree: %r" % (launches,),
        )
    return next(iter(launches.values()))


def read_elapsed_hours(
    *, now_utc, local_path, mirror_transport=None
) -> Decimal:
    """Return exact wall-clock hours since the persisted launch epoch.

    With mirror_transport=None this is an explicitly local-only recovery read;
    the preflight gate always supplies the mirror so its cap is anchored to the
    preemption-surviving copy. Fails closed on a future epoch.
    """
    now_dt = _utc_datetime(now_utc, field="now_utc", code="F1K_B_NOW_TIME")
    launch = _resolve_epoch_launch(
        local_path=local_path, mirror_transport=mirror_transport
    )
    launch_dt = _utc_datetime(
        launch, field="launch_utc", code="F1K_B_EPOCH_TIME"
    )
    if now_dt < launch_dt:
        raise F1KOpsError(
            "F1K_B_EPOCH_FUTURE",
            "launch epoch is in the future relative to now",
        )
    return _elapsed_hours(launch_dt, now_dt)


def compute_selfdelete_deadline(*, launch_utc) -> str:
    """Return T_cap = epoch + 900 h - 10 min as a UTC Z timestamp (Rev4 R4.1).

    The single, authoritative provider deadline. The 10 min conservative margin
    (SELFDELETE_MARGIN_MINUTES) absorbs the documented up-to-30 s
    termination-start delay so the running-billable window is provably < 900 h.
    Second granularity (systemd OnCalendar is second-resolved). A fractional-
    second launch is floored, so the deadline is at most one second early —
    conservative for a spend cap.
    """
    launch_dt = _utc_datetime(
        launch_utc, field="launch_utc", code="F1K_B_EPOCH_TIME"
    )
    deadline = launch_dt.replace(microsecond=0) + timedelta(
        hours=int(SELFDELETE_CAP_HOURS),
        minutes=-int(SELFDELETE_MARGIN_MINUTES),
    )
    return deadline.strftime("%Y-%m-%dT%H:%M:%S") + "Z"


def _oncalendar(deadline_utc: str) -> str:
    dt = _utc_datetime(
        deadline_utc, field="deadline_utc", code="F1K_B_DEADLINE_TIME"
    )
    return dt.strftime("%Y-%m-%d %H:%M:%S UTC")


# LC-1: the L2 guest fallback is defense-in-depth beneath the native L1 cap.
# The retry loop is EXTENDED (20 attempts x 30 s ~= 10 min) and, on exhaustion,
# a terminal `poweroff -f` needs NO cloud credentials and stops COMPUTE billing
# even under total IAM/API failure (PROPOSED-CC-8). Residual (disclosed): boot
# PD + attached Local SSDs keep billing until the L1 cap / reaper deletes the
# instance. The ExecStart is verified BYTE-EXACT by verify_selfdelete_armed, so
# any drift between this string and the rendered unit fails closed.
_SELFDELETE_ATTEMPTS = 20


def _selfdelete_exec_start(name, zone_text, project_id) -> str:
    seq = " ".join(str(i) for i in range(1, _SELFDELETE_ATTEMPTS + 1))
    return (
        "/bin/bash -c 'for i in %s; do "
        "/usr/bin/gcloud compute instances delete %s "
        "--zone %s --project %s --quiet && exit 0; sleep 30; "
        "done; /usr/sbin/poweroff -f; exit 1'"
        % (seq, name, zone_text, project_id)
    )


def render_selfdelete_unit(
    *, instance_name, zone, project_id, deadline_utc
) -> dict:
    """Render the on-VM systemd timer+service that self-deletes at the cap.

    Persistent=true catches a deadline missed across a preemption/reboot on the
    next boot; AccuracySec=1s keeps the fire time tight against the cap. The
    delete is bound to instance + zone + project and wrapped in a retry loop
    with network-online ordering. Nothing is executed here.
    """
    name = _strict_string(
        instance_name, field="instance_name", pattern=_INSTANCE_NAME_RE
    )
    zone_text = _strict_string(zone, field="zone", pattern=_ZONE_RE)
    project = _strict_string(
        project_id, field="project_id", pattern=_PROJECT_ID_RE
    )
    oncalendar = _oncalendar(deadline_utc)
    exec_start = _selfdelete_exec_start(name, zone_text, project)
    # LC-1: Restart=on-failure with StartLimitIntervalSec=0 (never rate-limited
    # out) hardens the guest fallback; the ExecStart already ends in
    # `poweroff -f`, so an exhausted-retry oneshot exits nonzero and is
    # restarted, and the poweroff terminal stops compute billing with no auth.
    service_text = (
        "[Unit]\n"
        "Description=F1-K wall-clock spend-cap self-delete "
        "(guest defense-in-depth beneath the native cap)\n"
        "Wants=network-online.target\n"
        "After=network-online.target\n"
        "StartLimitIntervalSec=0\n"
        "[Service]\n"
        "Type=oneshot\n"
        "Restart=on-failure\n"
        "RestartSec=30\n"
        "ExecStart=%s\n" % exec_start
    )
    timer_text = (
        "[Unit]\n"
        "Description=F1-K wall-clock spend-cap self-delete timer\n"
        "[Timer]\n"
        "OnCalendar=%s\n"
        "Persistent=true\n"
        "AccuracySec=1s\n"
        "Unit=%s\n"
        "[Install]\n"
        "WantedBy=timers.target\n" % (oncalendar, SELFDELETE_SERVICE_UNIT)
    )
    return {
        "timer_unit": SELFDELETE_TIMER_UNIT,
        "timer_path": "/etc/systemd/system/%s" % SELFDELETE_TIMER_UNIT,
        "timer_text": timer_text,
        "service_unit": SELFDELETE_SERVICE_UNIT,
        "service_path": "/etc/systemd/system/%s" % SELFDELETE_SERVICE_UNIT,
        "service_text": service_text,
        "exec_start": exec_start,
        "deadline_utc": _utc_timestamp(
            deadline_utc, field="deadline_utc", code="F1K_B_DEADLINE_TIME"
        ),
        "oncalendar": oncalendar,
    }


def _systemctl_query(systemctl_transport, *, action, unit) -> str:
    try:
        value = systemctl_transport(action=action, unit=unit)
    except F1KOpsError:
        raise
    except Exception as exc:  # noqa: BLE001
        raise F1KOpsError(
            "F1K_B_SYSTEMCTL_TRANSPORT",
            "systemctl %s failed: %s" % (action, exc),
        ) from exc
    if not isinstance(value, str):
        raise F1KOpsError(
            "F1K_B_SYSTEMCTL_TRANSPORT",
            "systemctl %s did not return a string" % action,
        )
    return value


def verify_selfdelete_armed(
    *, deadline_utc, instance_name, zone, project_id,
    systemctl_transport=None,
) -> dict:
    """Confirm the self-delete timer is active, persistent, armed at the exact
    deadline, and that its triggered service actually deletes THIS instance.

    systemctl_transport(action, unit) -> str:
        action="is-active"      -> "active" iff running
        action="oncalendar"     -> the timer's OnCalendar string
        action="persistent"     -> "yes"/"true"/"1" iff Persistent set
        action="triggered-unit" -> the service the timer triggers
        action="exec-start"     -> the service's ExecStart command line
        action="restart-policy" -> the service's Restart= value (LC-2)

    LC-2: also verifies the hardened Restart=on-failure policy and — via the
    byte-exact ExecStart match — the terminal `poweroff -f` fallback, and
    returns a CLOSED attestation carrying `action`/`mechanism` so the LC-5
    composite has a real value to compose (no fiction — the wonu lesson).
    """
    if systemctl_transport is None:
        raise F1KOpsError(
            "F1K_B_SYSTEMCTL",
            "verify_selfdelete_armed requires a systemctl_transport",
        )
    name = _strict_string(
        instance_name, field="instance_name", pattern=_INSTANCE_NAME_RE
    )
    zone_text = _strict_string(zone, field="zone", pattern=_ZONE_RE)
    project = _strict_string(
        project_id, field="project_id", pattern=_PROJECT_ID_RE
    )
    expected = _oncalendar(deadline_utc)

    active = _systemctl_query(
        systemctl_transport, action="is-active", unit=SELFDELETE_TIMER_UNIT
    )
    if active.strip() != "active":
        raise F1KOpsError(
            "F1K_B_SELFDELETE_INACTIVE",
            "self-delete timer is not active: %r" % (active,),
        )
    armed = _systemctl_query(
        systemctl_transport, action="oncalendar", unit=SELFDELETE_TIMER_UNIT
    )
    if armed.strip() != expected:
        raise F1KOpsError(
            "F1K_B_SELFDELETE_DRIFT",
            "self-delete armed at %r, expected %r" % (armed, expected),
        )
    persistent = _systemctl_query(
        systemctl_transport, action="persistent", unit=SELFDELETE_TIMER_UNIT
    )
    if persistent.strip().lower() not in ("yes", "true", "1"):
        raise F1KOpsError(
            "F1K_B_SELFDELETE_NOT_PERSISTENT",
            "self-delete timer is not Persistent: %r" % (persistent,),
        )
    triggered = _systemctl_query(
        systemctl_transport,
        action="triggered-unit", unit=SELFDELETE_TIMER_UNIT,
    )
    if triggered.strip() != SELFDELETE_SERVICE_UNIT:
        raise F1KOpsError(
            "F1K_B_SELFDELETE_UNIT",
            "self-delete timer triggers %r, expected %r"
            % (triggered, SELFDELETE_SERVICE_UNIT),
        )
    exec_start = _systemctl_query(
        systemctl_transport,
        action="exec-start", unit=SELFDELETE_SERVICE_UNIT,
    )
    # Exact match against the re-rendered command — a substring check would
    # accept a confusable superstring target (kot-f1k-run-other) or a
    # non-gcloud command that merely contains the tokens.
    expected_exec = _selfdelete_exec_start(name, zone_text, project)
    if exec_start.strip() != expected_exec:
        raise F1KOpsError(
            "F1K_B_SELFDELETE_TARGET",
            "self-delete ExecStart is not the exact bound delete of "
            "%s/%s/%s: %r" % (project, zone_text, name, exec_start),
        )
    # LC-2: the byte-exact ExecStart above proves the terminal `poweroff -f`
    # fallback is present (it is part of _selfdelete_exec_start); the restart
    # policy is verified independently here — a unit lacking Restart=on-failure
    # refuses (defect #1: a give-up single-shot left the VM billable).
    if "/usr/sbin/poweroff -f" not in expected_exec:  # invariant guard
        raise F1KOpsError(
            "F1K_B_SELFDELETE_TARGET",
            "self-delete fallback is not the terminal poweroff -f",
        )
    restart = _systemctl_query(
        systemctl_transport,
        action="restart-policy", unit=SELFDELETE_SERVICE_UNIT,
    )
    if restart.strip() != "on-failure":
        raise F1KOpsError(
            "F1K_B_SELFDELETE_RESTART",
            "self-delete service Restart policy is %r, expected "
            "on-failure (LC-2 hardening)" % (restart,),
        )
    return {
        "armed": True,
        "action": "DELETE",
        "mechanism": "systemd-selfdelete",
        "restart_policy": "on-failure",
        "fallback": "poweroff-f",
        "deadline_utc": _utc_timestamp(
            deadline_utc, field="deadline_utc", code="F1K_B_DEADLINE_TIME"
        ),
        "oncalendar": expected,
        "target": "%s/%s/%s" % (project, zone_text, name),
    }


def verify_provider_cap(
    *, instance_name, zone, project_id, deadline_utc, compute_transport=None,
) -> dict:
    """LC-3v3: verify the NATIVE GCE runtime-limit cap (variant B, the hard
    cap) via a live `instances.get` scheduling read-back.

    Requires scheduling.terminationTime == T_cap (the conservative
    epoch+900h-10min deadline), instanceTerminationAction == STOP (the unified
    action shared with Spot preemption), provisioningModel == SPOT, and the
    discard-local-SSD-at-termination flag set. The cap is READ from live
    scheduling — never inferred from a provisioning flag we set (the wonu
    two-axes rule, R3.2). Fails closed on any drift or transport error.

    compute_transport(project_id, zone, instance_name) -> full instance dict
    (the same shape resolve_live_instance_identity consumes).
    """
    if compute_transport is None:
        raise F1KOpsError(
            "F1K_B_CAP", "verify_provider_cap requires a compute_transport"
        )
    name = _strict_string(
        instance_name, field="instance_name", pattern=_INSTANCE_NAME_RE
    )
    zone_text = _strict_string(zone, field="zone", pattern=_ZONE_RE)
    project = _strict_string(
        project_id, field="project_id", pattern=_PROJECT_ID_RE
    )
    expected_deadline = _utc_timestamp(
        deadline_utc, field="deadline_utc", code="F1K_B_DEADLINE_TIME"
    )
    try:
        instance = compute_transport(
            project_id=project, zone=zone_text, instance_name=name
        )
    except F1KOpsError:
        raise
    except Exception as exc:  # noqa: BLE001 — fail closed on any transport error
        raise F1KOpsError(
            "F1K_B_CAP_TRANSPORT",
            "live scheduling read-back failed: %s" % exc,
        ) from exc
    if not isinstance(instance, dict):
        raise F1KOpsError(
            "F1K_B_CAP", "compute transport returned a non-object"
        )
    scheduling = instance.get("scheduling")
    if not isinstance(scheduling, dict):
        raise F1KOpsError(
            "F1K_B_CAP", "instance scheduling block is missing"
        )
    provisioning = scheduling.get("provisioningModel")
    if provisioning != "SPOT":
        raise F1KOpsError(
            "F1K_B_CAP_MODEL",
            "scheduling.provisioningModel %r != SPOT" % (provisioning,),
        )
    action = scheduling.get("instanceTerminationAction")
    if action != CAP_ACTION:
        raise F1KOpsError(
            "F1K_B_CAP_ACTION",
            "scheduling.instanceTerminationAction %r != %s (the unified cap "
            "action); a DELETE mis-provision would delete on every preemption"
            % (action, CAP_ACTION),
        )
    live_deadline = _utc_timestamp(
        scheduling.get("terminationTime"),
        field="scheduling.terminationTime", code="F1K_B_CAP_TIME",
    )
    if live_deadline != expected_deadline:
        raise F1KOpsError(
            "F1K_B_CAP_DRIFT",
            "live terminationTime %r != T_cap %r"
            % (live_deadline, expected_deadline),
        )
    discard = scheduling.get(DISCARD_LOCAL_SSD_KEY)
    if discard is not True:
        raise F1KOpsError(
            "F1K_B_CAP_DISCARD",
            "scheduling.%s is not set true — a STOP cap on a local-SSD VM "
            "requires discard-local-SSD-at-termination" % DISCARD_LOCAL_SSD_KEY,
        )
    return {
        "armed": True,
        "mechanism": CAP_MECHANISM,
        "action": CAP_ACTION,
        "provisioning_model": "SPOT",
        "termination_time_utc": expected_deadline,
        "termination_timestamp_utc": live_deadline,
        "discard_local_ssd": True,
        "target": "%s/%s/%s" % (project, zone_text, name),
    }


def verify_delete_iam(
    *, instance_name, zone, project_id, iam_transport=None,
) -> dict:
    """LC-4: guest-side dry-run proving compute.instances.delete IS permitted.

    An end-to-end auth + API-reachability + permission check via
    instances.testIamPermissions, executed with the VM's own credentials, that
    DELETES NOTHING — capability, not config. Backs the cleanup/teardown
    deletion path under Rev3. Fails closed if the permission is not granted or
    the transport errors.

    iam_transport(project_id, zone, instance_name, permissions) ->
        {"permissions": [<granted subset>]}
    """
    if iam_transport is None:
        raise F1KOpsError(
            "F1K_B_IAM", "verify_delete_iam requires an iam_transport"
        )
    name = _strict_string(
        instance_name, field="instance_name", pattern=_INSTANCE_NAME_RE
    )
    zone_text = _strict_string(zone, field="zone", pattern=_ZONE_RE)
    project = _strict_string(
        project_id, field="project_id", pattern=_PROJECT_ID_RE
    )
    required = ["compute.instances.delete"]
    try:
        response = iam_transport(
            project_id=project, zone=zone_text, instance_name=name,
            permissions=list(required),
        )
    except F1KOpsError:
        raise
    except Exception as exc:  # noqa: BLE001 — fail closed
        raise F1KOpsError(
            "F1K_B_IAM_TRANSPORT",
            "testIamPermissions dry-run failed: %s" % exc,
        ) from exc
    if not isinstance(response, dict):
        raise F1KOpsError(
            "F1K_B_IAM", "testIamPermissions returned a non-object"
        )
    granted = response.get("permissions")
    if (
        not isinstance(granted, list)
        or "compute.instances.delete" not in granted
    ):
        raise F1KOpsError(
            "F1K_B_IAM_DELETE",
            "compute.instances.delete is not granted (dry-run): %r"
            % (granted,),
        )
    return {
        "verified": True,
        "permissions": ["compute.instances.delete"],
        "target": "%s/%s/%s" % (project, zone_text, name),
    }


def verify_cap_armed(
    *, instance_name, zone, project_id, deadline_utc,
    compute_transport=None, systemctl_transport=None, iam_transport=None,
) -> dict:
    """LC-5: the composite CLOSED cap attestation.

    Composes L1 (native scheduling read-back, verify_provider_cap), L2 (the
    hardened guest self-delete timer, verify_selfdelete_armed) and the
    deletion-IAM dry-run (verify_delete_iam). It EXISTS only if every leg
    succeeds THIS run and the L1 terminationTime and L2 OnCalendar deadlines
    are identical. It is the ONLY lawful source for the handoff `cap` block
    (wonu, /2 form) — the handoff producer copies action/deadline FROM here,
    never from an echoed provisioning flag.
    """
    l1 = verify_provider_cap(
        instance_name=instance_name, zone=zone, project_id=project_id,
        deadline_utc=deadline_utc, compute_transport=compute_transport,
    )
    l2 = verify_selfdelete_armed(
        deadline_utc=deadline_utc, instance_name=instance_name,
        zone=zone, project_id=project_id,
        systemctl_transport=systemctl_transport,
    )
    iam = verify_delete_iam(
        instance_name=instance_name, zone=zone, project_id=project_id,
        iam_transport=iam_transport,
    )
    if l1["termination_time_utc"] != l2["deadline_utc"]:
        raise F1KOpsError(
            "F1K_B_CAP_DEADLINE_SPLIT",
            "L1 native cap deadline %s != L2 guest timer deadline %s — the "
            "layers must arm the ONE T_cap"
            % (l1["termination_time_utc"], l2["deadline_utc"]),
        )
    return {
        "armed": True,
        "mechanism": CAP_MECHANISM,
        "action": CAP_ACTION,
        "termination_time_utc": l1["termination_time_utc"],
        "termination_timestamp_utc": l1["termination_timestamp_utc"],
        "deadline_utc": l1["termination_time_utc"],
        "target": l1["target"],
        "l1": l1,
        "l2": l2,
        "iam": iam,
        "cleanup": {
            "mechanism": CLEANUP_MECHANISM,
            "action": CLEANUP_ACTION,
            "verified": "delete-poll-done-absence",
        },
    }


# Narrowing budgetFilter keys that MUST be absent (R3.3): a budget scoped to
# specific services / labels / resource ancestors / subaccounts / specific
# credit types is NOT a project-wide $300 tripwire and is REFUSED.
_BUDGET_NARROWING_KEYS = (
    "services",
    "labels",
    "resourceAncestors",
    "subaccountsBudgetScope",
    "creditTypes",
    "calendarPeriodBudgetScope",
)
_BUDGET_DEFAULT_CREDIT_TREATMENT = "INCLUDE_ALL_CREDITS"


def assure_billing_budget(
    *, billing_account, budget_resource_name=None, project_id=None,
    budget_transport=None, channel_transport=None, linkage_transport=None,
) -> dict:
    """LC-6v3: verify the EXACT $300 project-scoped Cloud Billing budget.

    Billing data lags hours, so a budget is a DELAYED-ALERT tripwire, NEVER a
    spending cap (vendor-documented). The point of this attestation is that the
    named resource is exactly the protective tripwire we think it is:

      - `budget_resource_name` is the EXACT billingAccounts/<id>/budgets/<id>
        (env KOT_F1K_BUDGET_RESOURCE); its parent account == `billing_account`;
      - amount USD, exactly 300 units / 0 nanos (BILLING_CEILING_USD);
      - budgetFilter names EXACTLY this one project (`projects/<project_id>`) and
        carries NO narrowing filter (services/labels/ancestors/subaccounts/
        credit types) and the default all-credits treatment (R3.3);
      - an explicit period (calendarPeriod XOR customPeriod);
      - non-empty thresholdRules;
      - EFFECTIVE notifications: every monitoringNotificationChannel fetched and
        in a VERIFIED + enabled state (Monitoring API read);
      - the project is LIVE-LINKED to `billing_account` with billing enabled.

    Fails closed on ANY defect. Returns a closed attestation preflight passes
    through for direct handoff population.

    budget_transport(action="get", resource_name=<name>) -> budgets.get object
    linkage_transport(project_id=<id>) -> projects.getBillingInfo object
    channel_transport(name=<channel>) -> notificationChannels.get object
    """
    if budget_transport is None:
        raise F1KOpsError(
            "F1K_B_BUDGET",
            "assure_billing_budget requires a budget_transport",
        )
    account = _strict_string(billing_account, field="billing_account")
    if budget_resource_name is None or project_id is None:
        raise F1KOpsError(
            "F1K_B_BUDGET",
            "assure_billing_budget requires budget_resource_name + project_id "
            "(LC-6v3: 'any $300 budget' never validates)",
        )
    resource = _strict_string(
        budget_resource_name, field="budget_resource_name",
        pattern=_BUDGET_RESOURCE_RE,
    )
    project = _strict_string(
        project_id, field="project_id", pattern=_PROJECT_ID_RE
    )
    if not resource.startswith(account + "/budgets/"):
        raise F1KOpsError(
            "F1K_B_BUDGET_RESOURCE",
            "budget resource %r is not a budget of billing account %r"
            % (resource, account),
        )
    expected = canonical_decimal(BILLING_CEILING_USD, field="billing ceiling")
    if channel_transport is None or linkage_transport is None:
        raise F1KOpsError(
            "F1K_B_BUDGET",
            "assure_billing_budget requires channel_transport + "
            "linkage_transport (verified channels + live project linkage)",
        )

    try:
        budget = budget_transport(action="get", resource_name=resource)
    except F1KOpsError:
        raise
    except Exception as exc:  # noqa: BLE001 — fail closed on any transport error
        raise F1KOpsError(
            "F1K_B_BUDGET_TRANSPORT", "budget get failed: %s" % exc
        ) from exc
    if budget is None:
        raise F1KOpsError(
            "F1K_B_BUDGET_ABSENT",
            "budget %r does not exist" % resource,
        )
    if not isinstance(budget, dict):
        raise F1KOpsError("F1K_B_BUDGET_SHAPE", "budget is not an object")
    if budget.get("name") != resource:
        raise F1KOpsError(
            "F1K_B_BUDGET_RESOURCE",
            "fetched budget name %r != requested resource %r"
            % (budget.get("name"), resource),
        )

    # amount: specifiedAmount USD 300 / 0 nanos
    amount_block = budget.get("amount")
    specified = (
        amount_block.get("specifiedAmount")
        if isinstance(amount_block, dict) else None
    )
    if not isinstance(specified, dict):
        raise F1KOpsError(
            "F1K_B_BUDGET_AMOUNT",
            "budget has no specifiedAmount (a last-period/dynamic budget is "
            "not a fixed $300 tripwire)",
        )
    if specified.get("currencyCode") != "USD":
        raise F1KOpsError(
            "F1K_B_BUDGET_CURRENCY",
            "budget currency %r != USD" % (specified.get("currencyCode"),),
        )
    nanos = specified.get("nanos", 0)
    if isinstance(nanos, bool) or not isinstance(nanos, int) or nanos != 0:
        raise F1KOpsError(
            "F1K_B_BUDGET_AMOUNT",
            "budget amount nanos %r != 0" % (nanos,),
        )
    try:
        amount = canonical_decimal(
            specified.get("units"), field="budget amount units"
        )
    except (ValueError, TypeError) as exc:
        raise F1KOpsError(
            "F1K_B_BUDGET_AMOUNT",
            "budget amount units is malformed: %s" % exc,
        ) from exc
    if amount != expected:
        raise F1KOpsError(
            "F1K_B_BUDGET_AMOUNT",
            "budget amount %s != required %s" % (amount, expected),
        )

    # budgetFilter: EXACTLY this one project, no narrowing, explicit period.
    bfilter = budget.get("budgetFilter")
    if not isinstance(bfilter, dict):
        raise F1KOpsError(
            "F1K_B_BUDGET_FILTER", "budget has no budgetFilter"
        )
    projects = bfilter.get("projects")
    if (
        not isinstance(projects, list)
        or projects != ["projects/%s" % project]
    ):
        raise F1KOpsError(
            "F1K_B_BUDGET_SCOPE",
            "budgetFilter.projects %r != exactly ['projects/%s'] — an "
            "account-wide or other-project budget is not this tripwire"
            % (projects, project),
        )
    present_narrowing = [
        key for key in _BUDGET_NARROWING_KEYS if bfilter.get(key)
    ]
    if present_narrowing:
        raise F1KOpsError(
            "F1K_B_BUDGET_FILTER",
            "budgetFilter carries narrowing filters %r — a narrowed budget "
            "does not tripwire the whole project" % (present_narrowing,),
        )
    treatment = bfilter.get("creditTypesTreatment")
    if treatment not in (None, _BUDGET_DEFAULT_CREDIT_TREATMENT):
        raise F1KOpsError(
            "F1K_B_BUDGET_FILTER",
            "budgetFilter.creditTypesTreatment %r != default all-credits"
            % (treatment,),
        )
    has_calendar = bool(bfilter.get("calendarPeriod"))
    has_custom = bool(bfilter.get("customPeriod"))
    if has_calendar == has_custom:
        raise F1KOpsError(
            "F1K_B_BUDGET_PERIOD",
            "budgetFilter must carry exactly one explicit period "
            "(calendarPeriod XOR customPeriod)",
        )

    thresholds = budget.get("thresholdRules")
    if not isinstance(thresholds, list) or not thresholds:
        raise F1KOpsError(
            "F1K_B_BUDGET_ALERT", "budget has no threshold rules"
        )
    for rule in thresholds:
        if not isinstance(rule, dict):
            raise F1KOpsError(
                "F1K_B_BUDGET_ALERT",
                "budget threshold rule is not an object: %r" % (rule,),
            )

    # notifications: non-empty AND every channel VERIFIED + enabled.
    notifications = budget.get("notificationsRule")
    channels = (
        notifications.get("monitoringNotificationChannels")
        if isinstance(notifications, dict) else None
    )
    if not isinstance(channels, list) or not channels:
        raise F1KOpsError(
            "F1K_B_BUDGET_NOTIFY",
            "budget has no monitoringNotificationChannels",
        )
    verified_channels = []
    for channel in channels:
        if not isinstance(channel, str) or not channel:
            raise F1KOpsError(
                "F1K_B_BUDGET_NOTIFY",
                "notification channel is malformed: %r" % (channel,),
            )
        try:
            info = channel_transport(name=channel)
        except F1KOpsError:
            raise
        except Exception as exc:  # noqa: BLE001 — fail closed
            raise F1KOpsError(
                "F1K_B_BUDGET_NOTIFY",
                "channel %r fetch failed: %s" % (channel, exc),
            ) from exc
        if not isinstance(info, dict):
            raise F1KOpsError(
                "F1K_B_BUDGET_NOTIFY",
                "channel %r returned a non-object" % (channel,),
            )
        if (
            info.get("verificationStatus") != "VERIFIED"
            or info.get("enabled") is not True
        ):
            raise F1KOpsError(
                "F1K_B_BUDGET_NOTIFY",
                "channel %r is not VERIFIED+enabled (status=%r enabled=%r)"
                % (channel, info.get("verificationStatus"),
                   info.get("enabled")),
            )
        verified_channels.append(channel)

    # live project-to-billing-account linkage + billing enabled.
    try:
        linkage = linkage_transport(project_id=project)
    except F1KOpsError:
        raise
    except Exception as exc:  # noqa: BLE001 — fail closed
        raise F1KOpsError(
            "F1K_B_BUDGET_LINKAGE",
            "project billing-info fetch failed: %s" % exc,
        ) from exc
    if not isinstance(linkage, dict):
        raise F1KOpsError(
            "F1K_B_BUDGET_LINKAGE", "billing-info returned a non-object"
        )
    if (
        linkage.get("billingAccountName") != account
        or linkage.get("billingEnabled") is not True
    ):
        raise F1KOpsError(
            "F1K_B_BUDGET_LINKAGE",
            "project %s is not live-linked to %s with billing enabled "
            "(account=%r enabled=%r)"
            % (project, account, linkage.get("billingAccountName"),
               linkage.get("billingEnabled")),
        )

    return {
        "present": True,
        "resource_name": resource,
        "billing_account": account,
        "project_id": project,
        "amount_usd": amount,
        "period": "calendar" if has_calendar else "custom",
        "threshold_count": len(thresholds),
        "verified_channel_count": len(verified_channels),
        "linkage_verified": True,
    }


def _check_rate_window(rate_value, spp_value) -> tuple:
    """Refuse (fail closed) unless rate, s/prefill, and their EXACT product are
    all inside the frozen two-sided construction window. Accept-at-equal."""
    try:
        rate = _decimal_value(rate_value, field="rate")
        spp = _decimal_value(spp_value, field="s_per_prefill")
    except ValueError as exc:
        raise F1KOpsError(
            "F1K_B_RATE_INPUT", "rate/s_per_prefill malformed: %s" % exc
        ) from exc
    if not (RATE_MIN_USD_PER_HOUR <= rate <= RATE_MAX_USD_PER_HOUR):
        raise F1KOpsError(
            "F1K_B_RATE_WINDOW",
            "rate %s outside [%s, %s]/h"
            % (rate, RATE_MIN_USD_PER_HOUR, RATE_MAX_USD_PER_HOUR),
        )
    if not (SPP_MIN_SECONDS <= spp <= SPP_MAX_SECONDS):
        raise F1KOpsError(
            "F1K_B_SPP_WINDOW",
            "s/prefill %s outside [%s, %s] s"
            % (spp, SPP_MIN_SECONDS, SPP_MAX_SECONDS),
        )
    product = _exact_product(rate, spp)
    if not (RATE_SPP_PRODUCT_MIN <= product <= RATE_SPP_PRODUCT_MAX):
        raise F1KOpsError(
            "F1K_B_PRODUCT_WINDOW",
            "rate*s %s outside [%s, %s] $*s/h"
            % (product, RATE_SPP_PRODUCT_MIN, RATE_SPP_PRODUCT_MAX),
        )
    return rate, spp, product


def guard_rate_within_window(
    *, project_id, zone, machine_type, local_ssd_count, s_per_prefill,
    catalog_transport, observed_at_utc=None,
) -> dict:
    """Quote the live all-in Spot rate and refuse if it would bust the window.

    catalog_transport is REQUIRED (no default): the guard must not silently
    fall through to resolve_live_rate's live HTTP path; production passes the
    live catalog transport explicitly, tests pass a fake. This is the pre-spend
    guard: it must PASS before any construction dollar.
    """
    if catalog_transport is None:
        raise F1KOpsError(
            "F1K_B_RATE_TRANSPORT",
            "guard_rate_within_window requires an explicit catalog_transport",
        )
    try:
        rate_str, evidence = resolve_live_rate(
            project_id=project_id,
            zone=zone,
            machine_type=machine_type,
            local_ssd_count=local_ssd_count,
            observed_at_utc=observed_at_utc,
            catalog_transport=catalog_transport,
        )
    except F1KOpsError as exc:
        # Normalize any live-quote failure into the B namespace so the guard
        # and preflight surface a single fail-closed error family.
        raise F1KOpsError(
            "F1K_B_RATE_QUOTE", "live rate quote failed (%s)" % exc.code
        ) from exc
    except Exception as exc:  # noqa: BLE001
        raise F1KOpsError(
            "F1K_B_RATE_QUOTE", "live rate quote failed: %s" % exc
        ) from exc
    rate, spp, product = _check_rate_window(rate_str, s_per_prefill)
    return {
        "pass": True,
        "rate_usd_per_hour": rate_str,
        "s_per_prefill": canonical_decimal(spp, field="s_per_prefill"),
        "rate_spp_product": canonical_decimal(product, field="product"),
        "rate_evidence_sha256": evidence["sha256"],
    }


def preflight_launch_gate(
    *, now_utc, local_epoch_path, instance_name, zone, project_id,
    deadline_utc, billing_account, machine_type, local_ssd_count,
    s_per_prefill, budget_resource_name=None,
    mirror_transport=None, systemctl_transport=None,
    compute_transport=None, iam_transport=None,
    budget_transport=None, channel_transport=None, linkage_transport=None,
    catalog_transport=None, observed_at_utc=None,
) -> dict:
    """Single pre-spend gate: GO only if EVERY provider-native check passes.

    Fails closed on ANY error (returns NO-GO, never raises). Checks (LC-7):
    (1) the durable launch epoch resolves (mirror REQUIRED, LC-12) and elapsed
        wall-clock < 900 h;
    (2) deadline_utc == T_cap derived from the PERSISTED epoch — never a caller
        value;
    (3) the COMPOSITE cap (verify_cap_armed, LC-5): live native scheduling
        read-back (terminationTime==T_cap, unified STOP, SPOT, discard flag) +
        the hardened L2 guest timer + the deletion-IAM dry-run, with the L1/L2
        deadlines equal;
    (4) the EXACT $300 project-scoped budget (LC-6v3); (5) the live Spot rate is
        in-window. The cap + budget closed attestations are passed through in
        the result for direct handoff population.
    """
    result = {}
    try:
        launch = _resolve_epoch_launch(
            local_path=local_epoch_path, mirror_transport=mirror_transport,
            require_mirror=True,
        )
        launch_dt = _utc_datetime(
            launch, field="launch_utc", code="F1K_B_EPOCH_TIME"
        )
        now_dt = _utc_datetime(
            now_utc, field="now_utc", code="F1K_B_NOW_TIME"
        )
        if now_dt < launch_dt:
            raise F1KOpsError(
                "F1K_B_EPOCH_FUTURE", "launch epoch is in the future"
            )
        elapsed = _elapsed_hours(launch_dt, now_dt)
        if elapsed >= SELFDELETE_CAP_HOURS:
            raise F1KOpsError(
                "F1K_B_CAP_ELAPSED",
                "elapsed wall-clock %s h has reached the 900 h cap"
                % elapsed,
            )
        expected_deadline = compute_selfdelete_deadline(launch_utc=launch)
        if _utc_timestamp(
            deadline_utc, field="deadline_utc", code="F1K_B_DEADLINE_TIME"
        ) != expected_deadline:
            raise F1KOpsError(
                "F1K_B_DEADLINE_MISMATCH",
                "deadline %r != persisted-launch T_cap %r"
                % (deadline_utc, expected_deadline),
            )
        cap = verify_cap_armed(
            instance_name=instance_name,
            zone=zone,
            project_id=project_id,
            deadline_utc=deadline_utc,
            compute_transport=compute_transport,
            systemctl_transport=systemctl_transport,
            iam_transport=iam_transport,
        )
        budget = assure_billing_budget(
            billing_account=billing_account,
            budget_resource_name=budget_resource_name,
            project_id=project_id,
            budget_transport=budget_transport,
            channel_transport=channel_transport,
            linkage_transport=linkage_transport,
        )
        rate = guard_rate_within_window(
            project_id=project_id,
            zone=zone,
            machine_type=machine_type,
            local_ssd_count=local_ssd_count,
            s_per_prefill=s_per_prefill,
            catalog_transport=catalog_transport,
            observed_at_utc=observed_at_utc,
        )
        result = {
            "elapsed_hours": canonical_decimal(
                elapsed, field="elapsed_hours"
            ) if elapsed > 0 else "0",
            "deadline_utc": cap["deadline_utc"],
            "cap": cap,
            "cap_target": cap["target"],
            "budget": budget,
            "budget_amount_usd": budget["amount_usd"],
            "budget_resource_name": budget["resource_name"],
            "rate_usd_per_hour": rate["rate_usd_per_hour"],
            "rate_evidence_sha256": rate["rate_evidence_sha256"],
        }
    except F1KOpsError as exc:
        return {"go": False, "reason": str(exc)}
    except Exception as exc:  # noqa: BLE001 — a spend gate fails closed on ANY error
        return {"go": False, "reason": "ERR_F1K_B_GATE: %s" % exc}

    out = {"go": True}
    out.update(result)
    return out


def selftest_b1() -> int:
    """Run the $0 pure/local option-B spend-cap oracle."""
    print(
        "SELFTEST-B1 SCOPE: $0 pure/local option-B spend-cap "
        "backstop; injectable fakes only; NO network, gcloud, "
        "GCP resources, or spend."
    )
    passed = 0
    total = 0

    def check(label, function):
        nonlocal passed, total
        total += 1
        try:
            ok = bool(function())
            detail = ""
        except Exception as exc:  # noqa: BLE001 — oracle reports all failures
            ok = False
            detail = " (%s: %s)" % (type(exc).__name__, exc)
        print("  %s%s%s" % ("ok:  " if ok else "FAIL: ", label, detail))
        passed += int(ok)

    def refuses(code, function):
        try:
            function()
        except F1KOpsError as exc:
            return exc.code == code
        return False

    class FakeMirror:
        def __init__(self):
            self.store = {}

        def __call__(self, *, action, key, data=None):
            if action == "put":
                self.store[key] = data
                return None
            if action == "get":
                return self.store.get(key)
            raise AssertionError("bad mirror action %r" % action)

    launch = "2026-07-20T00:00:00Z"
    deadline = compute_selfdelete_deadline(launch_utc=launch)

    def fake_systemctl(
        active="active", oncal=None, persistent="yes",
        triggered=None, exec_start=None, restart="on-failure",
    ):
        t_oncal = oncal if oncal is not None else _oncalendar(deadline)
        t_trig = triggered if triggered is not None else SELFDELETE_SERVICE_UNIT
        t_exec = exec_start if exec_start is not None else _selfdelete_exec_start(
            "kot-f1k-run", "us-central1-a", "test-project"
        )

        def transport(*, action, unit):
            return {
                "is-active": active,
                "oncalendar": t_oncal,
                "persistent": persistent,
                "triggered-unit": t_trig,
                "exec-start": t_exec,
                "restart-policy": restart,
            }[action]
        return transport

    # LC-3v3: a fake live scheduling read-back (variant-B native cap).
    def fake_compute(
        term=None, action="STOP", model="SPOT", discard=True,
    ):
        t_term = term if term is not None else deadline

        def transport(*, project_id, zone, instance_name):
            sched = {
                "provisioningModel": model,
                "instanceTerminationAction": action,
            }
            if t_term is not None:
                sched["terminationTime"] = t_term
            if discard is not None:
                sched[DISCARD_LOCAL_SSD_KEY] = discard
            return {"scheduling": sched}
        return transport

    # LC-4: a fake deletion-IAM dry-run.
    def fake_iam(granted=("compute.instances.delete",)):
        def transport(*, project_id, zone, instance_name, permissions):
            return {"permissions": list(granted)}
        return transport

    # LC-6v3: a fake budgets.get object (exact $300 project-scoped budget).
    def budget(
        name="billingAccounts/012345-6789AB-CDEF01/budgets/f1k",
        units="300", nanos=0, currency="USD",
        projects=("projects/test-project",), narrowing=None,
        treatment=None, period="calendar", rules=None,
        channels=("projects/test-project/notificationChannels/ch0",),
        absent=False,
    ):
        rules = ({"thresholdPercent": 0.5},) if rules is None else rules

        def transport(*, action, resource_name):
            if action != "get":
                raise AssertionError("bad budget action")
            if absent:
                return None
            bfilter = {}
            if projects is not None:
                bfilter["projects"] = list(projects)
            if period == "calendar":
                bfilter["calendarPeriod"] = "MONTH"
            elif period == "custom":
                bfilter["customPeriod"] = {
                    "startDate": {"year": 2026, "month": 7, "day": 1}
                }
            if treatment is not None:
                bfilter["creditTypesTreatment"] = treatment
            if narrowing:
                bfilter.update(narrowing)
            obj = {
                "name": name,
                "budgetFilter": bfilter,
                "thresholdRules": list(rules),
            }
            amt = {"currencyCode": currency}
            if units is not False:
                amt["units"] = units
            amt["nanos"] = nanos
            obj["amount"] = {"specifiedAmount": amt}
            if channels is not None:
                obj["notificationsRule"] = {
                    "monitoringNotificationChannels": list(channels)
                }
            return obj
        return transport

    def fake_channel(status="VERIFIED", enabled=True):
        def transport(*, name):
            return {
                "name": name,
                "verificationStatus": status,
                "enabled": enabled,
            }
        return transport

    def fake_linkage(account="billingAccounts/012345-6789AB-CDEF01",
                     enabled=True):
        def transport(*, project_id):
            return {"billingAccountName": account, "billingEnabled": enabled}
        return transport

    BUDGET_RESOURCE = "billingAccounts/012345-6789AB-CDEF01/budgets/f1k"
    BILLING_ACCOUNT = "billingAccounts/012345-6789AB-CDEF01"

    def min_catalog():
        def make_sku(sku_id, desc, fam, grp, usage, unit, nanos):
            return {
                "name": "%s/skus/%s" % (_COMPUTE_SERVICE, sku_id),
                "skuId": sku_id, "description": desc,
                "category": {
                    "serviceDisplayName": "Compute Engine",
                    "resourceFamily": fam, "resourceGroup": grp,
                    "usageType": usage,
                },
                "serviceRegions": ["us-central1"],
                "serviceProviderName": "Google",
                "geoTaxonomy": {
                    "type": "MULTI_REGIONAL", "regions": ["us-central1"]
                },
                "pricingInfo": [{
                    "effectiveTime": "2026-07-01T00:00:00Z",
                    "currencyConversionRate": 1,
                    "pricingExpression": {
                        "usageUnit": unit,
                        "tieredRates": [{
                            "startUsageAmount": 0,
                            "unitPrice": {
                                "currencyCode": "USD",
                                "units": "0", "nanos": nanos,
                            },
                        }],
                    },
                }],
            }
        skus = [
            make_sku("1111-AAAA-0001", "Spot Preemptible N2D AMD Instance "
                     "Core running in Americas", "Compute", "N2DAMDCore",
                     "Preemptible", "h", 10000000),
            make_sku("2222-BBBB-0002", "Spot Preemptible N2D AMD Instance "
                     "Ram running in Americas", "Compute", "N2DAMDram",
                     "Preemptible", "GiBy.h", 1000000),
            make_sku("3333-CCCC-0003", "SSD backed Local Storage attached "
                     "to Spot Preemptible VMs", "Storage", "LocalSSD",
                     "Preemptible", "GiBy.h", 100000),
        ]

        def catalog(**kwargs):
            return {"skus": copy.deepcopy(skus)}
        return catalog

    # --- B1: launch epoch -------------------------------------------------
    def b1_happy():
        mirror = FakeMirror()
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "launch-epoch.json")
            write_launch_epoch(
                launch_utc=launch, local_path=path, mirror_transport=mirror,
            )
            return read_elapsed_hours(
                now_utc="2026-07-20T12:00:00Z", local_path=path,
                mirror_transport=mirror,
            ) == Decimal("12")
    check("B1 persist epoch + read elapsed = 12 h", b1_happy)

    def b1_idempotent():
        mirror = FakeMirror()
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "e.json")
            write_launch_epoch(launch_utc=launch, local_path=path,
                               mirror_transport=mirror)
            write_launch_epoch(launch_utc=launch, local_path=path,
                               mirror_transport=mirror)
            return True
    check("B1 re-write identical epoch is idempotent", b1_idempotent)

    def b1_overwrite():
        mirror = FakeMirror()
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "e.json")
            write_launch_epoch(launch_utc=launch, local_path=path,
                               mirror_transport=mirror)
            return refuses("F1K_B_EPOCH_OVERWRITE", lambda: write_launch_epoch(
                launch_utc="2026-07-21T00:00:00Z", local_path=path,
                mirror_transport=mirror,
            ))
    check("B1 refuses resetting the clock (overwrite)", b1_overwrite)

    check("B1 write refuses without a durable mirror", lambda: refuses(
        "F1K_B_MIRROR",
        lambda: write_launch_epoch(
            launch_utc=launch, local_path="/tmp/never", mirror_transport=None),
    ))

    def b1_missing():
        with tempfile.TemporaryDirectory() as tmp:
            return refuses("F1K_B_EPOCH_MISSING", lambda: read_elapsed_hours(
                now_utc="2026-07-20T12:00:00Z",
                local_path=os.path.join(tmp, "absent.json"),
                mirror_transport=FakeMirror(),
            ))
    check("B1 read refuses when no epoch exists", b1_missing)

    def b1_future():
        mirror = FakeMirror()
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "e.json")
            write_launch_epoch(launch_utc=launch, local_path=path,
                               mirror_transport=mirror)
            return refuses("F1K_B_EPOCH_FUTURE", lambda: read_elapsed_hours(
                now_utc="2026-07-19T00:00:00Z", local_path=path,
                mirror_transport=mirror,
            ))
    check("B1 read refuses a future epoch", b1_future)

    def b1_split():
        mirror = FakeMirror()
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "e.json")
            write_launch_epoch(launch_utc=launch, local_path=path,
                               mirror_transport=mirror)
            other = FakeMirror()
            other.store[LAUNCH_EPOCH_KEY] = canonical_json_bytes(
                _build_launch_epoch("2026-07-25T00:00:00Z")
            )
            return refuses("F1K_B_EPOCH_SPLIT", lambda: read_elapsed_hours(
                now_utc="2026-07-26T00:00:00Z", local_path=path,
                mirror_transport=other,
            ))
    check("B1 read refuses local/mirror disagreement", b1_split)

    def b1_tamper():
        mirror = FakeMirror()
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "e.json")
            write_launch_epoch(launch_utc=launch, local_path=path,
                               mirror_transport=mirror)
            with open(path, "r+b") as handle:
                blob = json.loads(handle.read())
                blob["launch_utc"] = "2026-07-25T00:00:00Z"
                handle.seek(0)
                handle.truncate()
                handle.write(canonical_json_bytes(blob))
            return refuses("F1K_B_EPOCH_SHA", lambda: read_elapsed_hours(
                now_utc="2026-07-26T00:00:00Z", local_path=path,
                mirror_transport=None,
            ))
    check("B1 read refuses a tampered epoch (sha mismatch)", b1_tamper)

    check("B1 refuses sub-microsecond epoch precision", lambda: refuses(
        "F1K_B_EPOCH_TIME",
        lambda: compute_selfdelete_deadline(
            launch_utc="2026-07-20T00:00:00.0000001Z")))

    # --- B2: self-delete (T_cap = launch + 900 h - 10 min) ----------------
    check("B2 deadline = launch + 900 h - 10 min (T_cap, Rev4 R4.1)", lambda: (
        compute_selfdelete_deadline(launch_utc="2026-07-20T00:00:00Z")
        == "2026-08-26T11:50:00Z"))

    check("B2 render binds instance/zone/project + persistent + accuracy",
          lambda: (
        "Persistent=true" in render_selfdelete_unit(
            instance_name="kot-f1k-run", zone="us-central1-a",
            project_id="test-project", deadline_utc=deadline)["timer_text"]
        and "AccuracySec=1s" in render_selfdelete_unit(
            instance_name="kot-f1k-run", zone="us-central1-a",
            project_id="test-project", deadline_utc=deadline)["timer_text"]
        and "instances delete kot-f1k-run" in render_selfdelete_unit(
            instance_name="kot-f1k-run", zone="us-central1-a",
            project_id="test-project", deadline_utc=deadline)["service_text"]
        and "--project test-project" in render_selfdelete_unit(
            instance_name="kot-f1k-run", zone="us-central1-a",
            project_id="test-project", deadline_utc=deadline)["service_text"]))

    def verify(**kw):
        return verify_selfdelete_armed(
            deadline_utc=deadline, instance_name="kot-f1k-run",
            zone="us-central1-a", project_id="test-project",
            systemctl_transport=fake_systemctl(**kw),
        )
    check("B2 verify accepts a fully-armed timer",
          lambda: verify()["armed"] is True)
    check("B2 verify refuses an inactive timer", lambda: refuses(
        "F1K_B_SELFDELETE_INACTIVE", lambda: verify(active="inactive")))
    check("B2 verify refuses a drifted deadline", lambda: refuses(
        "F1K_B_SELFDELETE_DRIFT",
        lambda: verify(oncal="2030-01-01 00:00:00 UTC")))
    check("B2 verify refuses a non-persistent timer", lambda: refuses(
        "F1K_B_SELFDELETE_NOT_PERSISTENT", lambda: verify(persistent="no")))
    check("B2 verify refuses a wrong triggered unit", lambda: refuses(
        "F1K_B_SELFDELETE_UNIT", lambda: verify(triggered="harmless.service")))
    check("B2 verify refuses an unbound delete target", lambda: refuses(
        "F1K_B_SELFDELETE_TARGET",
        lambda: verify(exec_start=_selfdelete_exec_start(
            "some-other-vm", "us-central1-a", "test-project"))))
    check("B2 verify refuses a confusable superstring instance name",
          lambda: refuses(
        "F1K_B_SELFDELETE_TARGET",
        lambda: verify(exec_start=_selfdelete_exec_start(
            "kot-f1k-run-other", "us-central1-a", "test-project"))))
    check("B2 verify refuses a non-gcloud delete command", lambda: refuses(
        "F1K_B_SELFDELETE_TARGET",
        lambda: verify(exec_start=(
            "/bin/true instances delete kot-f1k-run "
            "--zone us-central1-a --project test-project"))))
    check("B2 verify refuses without a systemctl transport", lambda: refuses(
        "F1K_B_SYSTEMCTL",
        lambda: verify_selfdelete_armed(
            deadline_utc=deadline, instance_name="kot-f1k-run",
            zone="us-central1-a", project_id="test-project",
            systemctl_transport=None)))
    # LC-1/LC-2 hardening: Restart=on-failure + terminal poweroff fallback.
    check("B2 (LC-2) attestation carries action/mechanism/restart/fallback",
          lambda: (verify()["action"] == "DELETE"
                   and verify()["restart_policy"] == "on-failure"
                   and verify()["fallback"] == "poweroff-f"))
    check("B2 (LC-2) refuses a service missing Restart=on-failure",
          lambda: refuses("F1K_B_SELFDELETE_RESTART",
                          lambda: verify(restart="no")))
    check("B2 (LC-1) rendered unit carries Restart=on-failure + poweroff -f",
          lambda: ("Restart=on-failure"
                   in render_selfdelete_unit(
                       instance_name="kot-f1k-run", zone="us-central1-a",
                       project_id="test-project",
                       deadline_utc=deadline)["service_text"]
                   and "/usr/sbin/poweroff -f"
                   in render_selfdelete_unit(
                       instance_name="kot-f1k-run", zone="us-central1-a",
                       project_id="test-project",
                       deadline_utc=deadline)["service_text"]))

    # --- LC-3v3: native provider cap (live scheduling read-back) ----------
    def prov_cap(**kw):
        return verify_provider_cap(
            instance_name="kot-f1k-run", zone="us-central1-a",
            project_id="test-project", deadline_utc=deadline,
            compute_transport=fake_compute(**kw))
    check("LC-3 accepts a live STOP terminationTime==T_cap SPOT+discard cap",
          lambda: (prov_cap()["armed"] is True
                   and prov_cap()["action"] == "STOP"
                   and prov_cap()["mechanism"] == "gce-termination-time"))
    check("LC-3 refuses a DELETE unified action (deletes on preemption)",
          lambda: refuses("F1K_B_CAP_ACTION",
                          lambda: prov_cap(action="DELETE")))
    check("LC-3 refuses a non-SPOT model", lambda: refuses(
        "F1K_B_CAP_MODEL", lambda: prov_cap(model="STANDARD")))
    check("LC-3 refuses a drifted terminationTime", lambda: refuses(
        "F1K_B_CAP_DRIFT", lambda: prov_cap(term="2030-01-01T00:00:00Z")))
    check("LC-3 refuses a raw epoch+900h (non-conservative) deadline",
          lambda: refuses("F1K_B_CAP_DRIFT",
                          lambda: prov_cap(term="2026-08-26T12:00:00Z")))
    check("LC-3 refuses a missing discard-local-SSD flag", lambda: refuses(
        "F1K_B_CAP_DISCARD", lambda: prov_cap(discard=None)))
    check("LC-3 refuses without a compute transport", lambda: refuses(
        "F1K_B_CAP",
        lambda: verify_provider_cap(
            instance_name="kot-f1k-run", zone="us-central1-a",
            project_id="test-project", deadline_utc=deadline,
            compute_transport=None)))

    # --- LC-4: deletion-IAM dry-run ---------------------------------------
    def del_iam(**kw):
        return verify_delete_iam(
            instance_name="kot-f1k-run", zone="us-central1-a",
            project_id="test-project", iam_transport=fake_iam(**kw))
    check("LC-4 accepts a granted compute.instances.delete dry-run",
          lambda: del_iam()["verified"] is True)
    check("LC-4 refuses when delete permission is not granted", lambda: refuses(
        "F1K_B_IAM_DELETE",
        lambda: del_iam(granted=("compute.instances.get",))))
    check("LC-4 refuses a raising iam transport", lambda: refuses(
        "F1K_B_IAM_TRANSPORT",
        lambda: verify_delete_iam(
            instance_name="kot-f1k-run", zone="us-central1-a",
            project_id="test-project",
            iam_transport=lambda **k: (_ for _ in ()).throw(OSError("down")))))

    # --- LC-5: composite closed cap attestation ---------------------------
    def cap_armed(**kw):
        common = dict(
            compute_transport=fake_compute(),
            systemctl_transport=fake_systemctl(),
            iam_transport=fake_iam(),
        )
        common.update(kw)
        return verify_cap_armed(
            instance_name="kot-f1k-run", zone="us-central1-a",
            project_id="test-project", deadline_utc=deadline, **common)
    check("LC-5 composite attests STOP cap + guest + IAM at the one T_cap",
          lambda: (cap_armed()["armed"] is True
                   and cap_armed()["action"] == "STOP"
                   and cap_armed()["deadline_utc"] == deadline
                   and cap_armed()["cleanup"]["action"] == "DELETE"))
    check("LC-5 refuses if the L1 leg (native cap) is broken", lambda: refuses(
        "F1K_B_CAP_ACTION",
        lambda: cap_armed(compute_transport=fake_compute(action="DELETE"))))
    check("LC-5 refuses if the L2 leg (guest timer) is broken", lambda: refuses(
        "F1K_B_SELFDELETE_INACTIVE",
        lambda: cap_armed(systemctl_transport=fake_systemctl(
            active="inactive"))))
    check("LC-5 refuses if the IAM leg is broken", lambda: refuses(
        "F1K_B_IAM_DELETE",
        lambda: cap_armed(iam_transport=fake_iam(
            granted=("compute.instances.get",)))))

    # --- B3: billing budget (LC-6v3 exact-resource attestation) -----------
    def assure(**kw):
        return assure_billing_budget(
            billing_account=BILLING_ACCOUNT,
            budget_resource_name=BUDGET_RESOURCE, project_id="test-project",
            budget_transport=budget(**kw), channel_transport=fake_channel(),
            linkage_transport=fake_linkage())
    check("B3 accepts an exact $300 project-scoped budget",
          lambda: (assure()["present"] is True
                   and assure()["verified_channel_count"] == 1
                   and assure()["linkage_verified"] is True))
    check("B3 accepts a custom-period budget",
          lambda: assure(period="custom")["period"] == "custom")
    check("B3 refuses an absent budget", lambda: refuses(
        "F1K_B_BUDGET_ABSENT", lambda: assure(absent=True)))
    check("B3 refuses a wrong-amount budget", lambda: refuses(
        "F1K_B_BUDGET_AMOUNT", lambda: assure(units="500")))
    check("B3 refuses nonzero nanos", lambda: refuses(
        "F1K_B_BUDGET_AMOUNT", lambda: assure(nanos=1)))
    check("B3 refuses a non-USD currency", lambda: refuses(
        "F1K_B_BUDGET_CURRENCY", lambda: assure(currency="EUR")))
    check("B3 refuses an account-wide budget (no project filter)",
          lambda: refuses("F1K_B_BUDGET_SCOPE",
                          lambda: assure(projects=None)))
    check("B3 refuses a wrong-project filter", lambda: refuses(
        "F1K_B_BUDGET_SCOPE",
        lambda: assure(projects=("projects/other-project",))))
    check("B3 refuses a services-narrowed budget", lambda: refuses(
        "F1K_B_BUDGET_FILTER",
        lambda: assure(narrowing={"services": ["services/6F81-5844-456A"]})))
    check("B3 refuses a non-default credit treatment", lambda: refuses(
        "F1K_B_BUDGET_FILTER",
        lambda: assure(treatment="EXCLUDE_ALL_CREDITS")))
    check("B3 refuses a budget with no explicit period", lambda: refuses(
        "F1K_B_BUDGET_PERIOD", lambda: assure(period=None)))
    check("B3 refuses a budget with no threshold rules", lambda: refuses(
        "F1K_B_BUDGET_ALERT", lambda: assure(rules=())))
    check("B3 refuses a budget with no notification channels", lambda: refuses(
        "F1K_B_BUDGET_NOTIFY", lambda: assure(channels=())))
    check("B3 refuses an unverified notification channel", lambda: refuses(
        "F1K_B_BUDGET_NOTIFY",
        lambda: assure_billing_budget(
            billing_account=BILLING_ACCOUNT,
            budget_resource_name=BUDGET_RESOURCE, project_id="test-project",
            budget_transport=budget(),
            channel_transport=fake_channel(status="UNVERIFIED"),
            linkage_transport=fake_linkage())))
    check("B3 refuses a project not live-linked to the billing account",
          lambda: refuses("F1K_B_BUDGET_LINKAGE",
                          lambda: assure_billing_budget(
                              billing_account=BILLING_ACCOUNT,
                              budget_resource_name=BUDGET_RESOURCE,
                              project_id="test-project",
                              budget_transport=budget(),
                              channel_transport=fake_channel(),
                              linkage_transport=fake_linkage(enabled=False))))
    check("B3 refuses a budget resource not under the billing account",
          lambda: refuses("F1K_B_BUDGET_RESOURCE",
                          lambda: assure_billing_budget(
                              billing_account=BILLING_ACCOUNT,
                              budget_resource_name=(
                                  "billingAccounts/999999-999999-999999/"
                                  "budgets/f1k"),
                              project_id="test-project",
                              budget_transport=budget(),
                              channel_transport=fake_channel(),
                              linkage_transport=fake_linkage())))
    check("B3 refuses without budget_resource_name + project_id", lambda: refuses(
        "F1K_B_BUDGET",
        lambda: assure_billing_budget(
            billing_account=BILLING_ACCOUNT, budget_transport=budget())))
    check("B3 refuses without a budget transport", lambda: refuses(
        "F1K_B_BUDGET",
        lambda: assure_billing_budget(
            billing_account=BILLING_ACCOUNT,
            budget_resource_name=BUDGET_RESOURCE, project_id="test-project",
            budget_transport=None)))

    # --- B4: rate window --------------------------------------------------
    check("B4 window accepts interior rate/spp", lambda: (
        _check_rate_window("0.219", "100")[2] == Decimal("21.9")))
    check("B4 accept-at-equal at spp-min + product-min", lambda: (
        _check_rate_window("0.28", "47.0")[2] == Decimal("13.16")))
    check("B4 accept-at-equal at product-max", lambda: (
        _check_rate_window("0.2", "139.75")[2] == Decimal("27.95")))
    check("B4 accept-at-equal at spp-max", lambda: (
        _check_rate_window("0.12", "162.3")[1] == Decimal("162.3")))
    check("B4 refuses rate just under $0.081", lambda: refuses(
        "F1K_B_RATE_WINDOW", lambda: _check_rate_window("0.0809", "100")))
    check("B4 refuses rate just over $0.595", lambda: refuses(
        "F1K_B_RATE_WINDOW", lambda: _check_rate_window("0.5951", "50")))
    check("B4 refuses spp just under 47.0", lambda: refuses(
        "F1K_B_SPP_WINDOW", lambda: _check_rate_window("0.28", "46.9")))
    check("B4 refuses spp just over 162.3", lambda: refuses(
        "F1K_B_SPP_WINDOW", lambda: _check_rate_window("0.12", "162.4")))
    check("B4 refuses product just over 27.95", lambda: refuses(
        "F1K_B_PRODUCT_WINDOW", lambda: _check_rate_window("0.2", "140")))
    check("B4 refuses product just under 13.16", lambda: refuses(
        "F1K_B_PRODUCT_WINDOW", lambda: _check_rate_window("0.27", "48")))
    # Exact-product regression (the reviewer's rounding false-accept).
    check("B4 refuses a product that only ROUNDS into range", lambda: refuses(
        "F1K_B_PRODUCT_WINDOW",
        lambda: _check_rate_window(
            "0.2", "139.750000000000000000000000001")))

    def b4_end_to_end():
        result = guard_rate_within_window(
            project_id="test-project", zone="us-central1-a",
            machine_type="n2d-highmem-8", local_ssd_count=2,
            s_per_prefill="120", observed_at_utc="2026-07-18T00:00:00Z",
            catalog_transport=min_catalog(),
        )
        return (result["pass"] is True
                and result["rate_usd_per_hour"] == "0.219"
                and result["rate_spp_product"] == "26.28")
    check("B4 guard passes end-to-end through resolve_live_rate", b4_end_to_end)
    check("B4 guard refuses an absent catalog transport", lambda: refuses(
        "F1K_B_RATE_TRANSPORT",
        lambda: guard_rate_within_window(
            project_id="test-project", zone="us-central1-a",
            machine_type="n2d-highmem-8", local_ssd_count=2,
            s_per_prefill="120", catalog_transport=None)))
    check("B4 guard normalizes a raising catalog to F1K_B_RATE_QUOTE",
          lambda: refuses(
        "F1K_B_RATE_QUOTE",
        lambda: guard_rate_within_window(
            project_id="test-project", zone="us-central1-a",
            machine_type="n2d-highmem-8", local_ssd_count=2,
            s_per_prefill="120",
            catalog_transport=lambda **k: (_ for _ in ()).throw(
                OSError("catalog down")))))

    # --- B5: preflight gate (LC-7 composite cap + exact budget) -----------
    def b5_gate(**overrides):
        mirror = FakeMirror()
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "epoch.json")
            write_launch_epoch(launch_utc=launch, local_path=path,
                               mirror_transport=mirror)
            common = dict(
                now_utc="2026-07-20T06:00:00Z", local_epoch_path=path,
                instance_name="kot-f1k-run", zone="us-central1-a",
                project_id="test-project", deadline_utc=deadline,
                billing_account=BILLING_ACCOUNT,
                budget_resource_name=BUDGET_RESOURCE,
                machine_type="n2d-highmem-8", local_ssd_count=2,
                s_per_prefill="120", mirror_transport=mirror,
                systemctl_transport=fake_systemctl(),
                compute_transport=fake_compute(), iam_transport=fake_iam(),
                budget_transport=budget(), channel_transport=fake_channel(),
                linkage_transport=fake_linkage(),
                catalog_transport=min_catalog(),
                observed_at_utc="2026-07-18T00:00:00Z",
            )
            common.update(overrides)
            return preflight_launch_gate(**common)

    check("B5 gate GO when all checks pass", lambda: (
        b5_gate()["go"] is True
        and b5_gate()["rate_usd_per_hour"] == "0.219"
        and b5_gate()["cap"]["action"] == "STOP"
        and b5_gate()["cap_target"]
        == "test-project/us-central1-a/kot-f1k-run"))
    check("B5 NO-GO on an inactive timer", lambda: (
        b5_gate(systemctl_transport=fake_systemctl(active="inactive"))["go"]
        is False))
    check("B5 NO-GO on a DELETE unified cap action (L1 leg)", lambda: (
        "F1K_B_CAP_ACTION" in b5_gate(
            compute_transport=fake_compute(action="DELETE"))["reason"]))
    check("B5 NO-GO on a drifted live terminationTime (L1 leg)", lambda: (
        "F1K_B_CAP_DRIFT" in b5_gate(
            compute_transport=fake_compute(term="2030-01-01T00:00:00Z"))
        ["reason"]))
    check("B5 NO-GO on a missing delete-IAM grant (IAM leg)", lambda: (
        "F1K_B_IAM_DELETE" in b5_gate(
            iam_transport=fake_iam(granted=("compute.instances.get",)))
        ["reason"]))
    check("B5 NO-GO on a wrong self-delete deadline (derived from epoch)",
          lambda: (
        "F1K_B_DEADLINE_MISMATCH" in b5_gate(
            deadline_utc="2030-01-01T00:00:00Z")["reason"]))
    check("B5 NO-GO on an unbound delete target (L2 leg)", lambda: (
        "F1K_B_SELFDELETE_TARGET" in b5_gate(
            systemctl_transport=fake_systemctl(
                exec_start=_selfdelete_exec_start(
                    "other-vm", "us-central1-a", "test-project")))["reason"]))
    check("B5 NO-GO on a wrong-project budget filter", lambda: (
        "F1K_B_BUDGET_SCOPE" in b5_gate(
            budget_transport=budget(projects=("projects/other-project",)))
        ["reason"]))
    check("B5 NO-GO (fail-closed) on a raising budget transport", lambda: (
        b5_gate(budget_transport=lambda **k: (_ for _ in ()).throw(
            OSError("api down")))["go"] is False))
    check("B5 NO-GO on an absent catalog transport", lambda: (
        b5_gate(catalog_transport=None)["go"] is False))
    check("B5 NO-GO (fail-closed) on a raising catalog transport", lambda: (
        b5_gate(catalog_transport=lambda **k: (_ for _ in ()).throw(
            OSError("catalog down")))["go"] is False))
    check("B5 NO-GO (LC-12) when the mirror is absent but a local exists",
          lambda: b5_gate(mirror_transport=FakeMirror())["go"] is False)

    print("SELFTEST-B1: %d/%d PASS" % (passed, total))
    return 0 if passed == total else 2


def _main() -> int:
    if len(sys.argv) < 2:
        _die(
            "F1K_OPS_USAGE",
            "usage: f1k_ops.py selftest | selftest-b0 | selftest-b1",
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
    if command == "selftest-b1":
        parser = argparse.ArgumentParser(
            prog="f1k_ops.py selftest-b1"
        )
        parser.parse_args(sys.argv[2:])
        return selftest_b1()

    _die(
        "F1K_OPS_USAGE",
        "unknown command %r "
        "(expected selftest, selftest-b0, or selftest-b1)"
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
