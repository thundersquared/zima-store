#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = [
#   "ruamel.yaml==0.19.1",
#   "semver==3.1.0",
# ]
# ///
"""Reconcile ZimaOS store app versions, release notes, and update timestamps.

Each app is loaded as a round-trip YAML document, so comments, quoting style,
and block-scalar prose survive an edit. Dependencies are declared above, so
`uv run scripts/reconcile_versions.py <subcommand>` is the only entry point
needed.

Subcommands:
  reconcile          rewrite x-casaos.version / release_notes / update_at
  check              fail when a source version is not semver
  check-index        fail when a built index.json is missing app versions
"""

import argparse
import io
import json
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

import semver
from ruamel.yaml import YAML

APPS_DIR = Path("Apps")
X_CASAOS = "x-casaos"

DIGEST_MARKER = "sha256:"
DIGEST_PREFIX_LEN = len(DIGEST_MARKER) + 12
FALLBACK_VERSION = "1.0.0"
LINE_WIDTH = 4096


def parse_version(text):
    if not isinstance(text, str):
        return None
    try:
        return semver.Version.parse(text)
    except ValueError:
        return None


def canonical_version(text):
    parsed = parse_version(text)
    return str(parsed) if parsed else ""


def bump_patch(text):
    parsed = parse_version(text)
    return str(parsed.bump_patch()) if parsed else ""


@dataclass
class App:
    path: Path
    data: dict
    reference: str
    repo: str
    tag: str
    digest: str
    current: str
    prefix: str
    suffix: str
    note: str


def yaml_engine():
    engine = YAML()
    engine.preserve_quotes = True
    engine.width = LINE_WIDTH
    engine.indent(mapping=2, sequence=4, offset=2)
    return engine


def app_files(root):
    return sorted(Path(root).glob("*/docker-compose.yml"))


def text_of(value):
    return value if isinstance(value, str) else ""


def split_ref(reference):
    digest = ""
    if "@" in reference:
        reference, digest = reference.split("@", 1)
    head, separator, tail = reference.rpartition(":")
    if separator and "/" not in tail:
        return head, tail, digest
    return reference, "", digest


def main_reference(data):
    services = data.get("services") or {}
    main = (data.get(X_CASAOS) or {}).get("main")
    if main and isinstance(services.get(main), dict) and services[main].get("image"):
        return services[main]["image"]
    for service in services.values():
        if isinstance(service, dict) and service.get("image"):
            return service["image"]
    return ""


def first_text(mapping):
    if isinstance(mapping, dict):
        for value in mapping.values():
            if isinstance(value, str) and value:
                return value
    return ""


def app_from_data(data, path):
    block = data.get(X_CASAOS) or {}
    reference = main_reference(data)
    repo, tag, digest = split_ref(reference)
    return App(
        path=path,
        data=data,
        reference=reference,
        repo=repo,
        tag=tag,
        digest=digest,
        current=text_of(block.get("version")),
        prefix=text_of(block.get("version_prefix")),
        suffix=text_of(block.get("version_suffix")),
        note=first_text(block.get("release_notes")),
    )


def load_app(path, text=None):
    return app_from_data(yaml_engine().load(text if text is not None else path.read_text()), path)


def normalize_tag(tag, prefix, suffix):
    candidate = tag
    if prefix and candidate.startswith(prefix):
        candidate = candidate[len(prefix) :]
    if suffix and candidate.endswith(suffix):
        candidate = candidate[: -len(suffix)]
    return canonical_version(candidate)


def release_note(repo, tag, digest):
    reference = "{}:{}".format(repo, tag) if tag else repo
    if digest:
        return "Pinned {} at {}.".format(reference, digest[:DIGEST_PREFIX_LEN])
    return "Pinned {}.".format(reference)


def claimed_digest(note):
    start = note.find(DIGEST_MARKER)
    if start < 0:
        return ""
    return note[start : start + DIGEST_PREFIX_LEN]


def note_is_stale(note, tag, digest):
    claimed = claimed_digest(note)
    if claimed:
        return claimed != digest[:DIGEST_PREFIX_LEN]
    return bool(tag) and tag not in note


def desired_version(app, base):
    normalized = normalize_tag(app.tag, app.prefix, app.suffix)
    previous_reference = base.reference if base else ""
    previous_version = base.current if base else ""
    changed = bool(previous_reference) and previous_reference != app.reference
    version_touched = bool(previous_version) and previous_version != app.current

    if normalized:
        desired = normalized
    elif parse_version(app.current):
        desired = app.current if version_touched or not changed else bump_patch(app.current)
    else:
        desired = FALLBACK_VERSION

    return None if desired == app.current else desired


def git_load(ref, path):
    result = subprocess.run(
        ["git", "show", "{}:{}".format(ref, path)],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        return None
    return load_app(path, text=result.stdout)


def set_update_at(block, stamp):
    if "update_at" in block:
        block["update_at"] = stamp
        return
    keys = list(block.keys())
    block.insert(keys.index("version") + 1, "update_at", stamp)


def reconcile(path, base_ref, stamp):
    app = load_app(path)
    base = git_load(base_ref, path) if base_ref else None
    if base_ref and base is None:
        print(
            "warning: cannot read {} at {}; treating images as unchanged".format(path, base_ref),
            file=sys.stderr,
        )

    desired = desired_version(app, base)
    note = release_note(app.repo, app.tag, app.digest)
    if desired is None and not note_is_stale(app.note, app.tag, app.digest):
        return None

    block = app.data[X_CASAOS]
    block["version"] = desired or app.current
    set_update_at(block, stamp)
    if isinstance(block.get("release_notes"), dict):
        for locale in block["release_notes"]:
            block["release_notes"][locale] = note

    buffer = io.StringIO()
    yaml_engine().dump(app.data, buffer)
    path.write_text(buffer.getvalue())

    return "{}: version {} ({}:{})".format(
        path, desired or app.current, app.repo, app.tag or "untagged"
    )


def cmd_reconcile(args):
    stamp = args.stamp or datetime.now(timezone.utc).strftime("%Y-%m-%d")
    changes = []
    for path in app_files(args.root):
        result = reconcile(path, args.base, stamp)
        if result:
            changes.append(result)
    for change in changes:
        print(change)
    if not changes:
        print("versions already reconciled")
    return 0


def cmd_check(args):
    failures = []
    warnings = []
    for path in app_files(args.root):
        app = load_app(path)
        if not parse_version(app.current):
            failures.append("{}: version {!r} is not semver".format(path, app.current))
            continue
        if app.prefix and not app.tag.startswith(app.prefix):
            warnings.append(
                "{}: version_prefix {!r} does not match image tag {!r}".format(
                    path, app.prefix, app.tag
                )
            )
        if app.suffix and not app.tag.endswith(app.suffix):
            warnings.append(
                "{}: version_suffix {!r} does not match image tag {!r}".format(
                    path, app.suffix, app.tag
                )
            )
        normalized = normalize_tag(app.tag, app.prefix, app.suffix)
        if normalized and normalized != app.current:
            warnings.append(
                "{}: version {!r} overrides cleaned image tag {!r}".format(
                    path, app.current, normalized
                )
            )
    for failure in failures:
        print("error: {}".format(failure), file=sys.stderr)
    for warning in warnings:
        print("warning: {}".format(warning))
    if failures:
        print(
            "\nRun scripts/reconcile_versions.py reconcile and commit the result. "
            "A valid semver version that intentionally differs from the cleaned image "
            "tag is allowed, for example a hand-set major bump.",
            file=sys.stderr,
        )
        return 1
    print("all app versions are semver")
    return 0


def cmd_check_index(args):
    index = json.loads(Path(args.path).read_text())
    failures = []
    for app in index.get("apps", []):
        version = app.get("version", "")
        if not parse_version(version):
            failures.append("{}: index.json version {!r}".format(app.get("id"), version))
    for failure in failures:
        print("error: {}".format(failure), file=sys.stderr)
    if failures:
        print(
            "\nThe ZimaOS client cannot detect updates for apps without a semver "
            "version in index.json.",
            file=sys.stderr,
        )
        return 1
    print("index.json exposes a semver version for all {} apps".format(len(index.get("apps", []))))
    return 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=APPS_DIR, help="app source directory")
    sub = parser.add_subparsers(dest="command", required=True)

    reconcile_parser = sub.add_parser("reconcile")
    reconcile_parser.add_argument("--base", default="", help="git ref holding the previous state")
    reconcile_parser.add_argument("--stamp", default="", help="update_at date, YYYY-MM-DD")
    reconcile_parser.set_defaults(func=cmd_reconcile)

    check_parser = sub.add_parser("check")
    check_parser.set_defaults(func=cmd_check)

    index_parser = sub.add_parser("check-index")
    index_parser.add_argument("path")
    index_parser.set_defaults(func=cmd_check_index)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
