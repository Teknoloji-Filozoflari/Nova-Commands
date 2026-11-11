#!/usr/bin/env python3
"""Validate committed/generated catalog artifacts (hard gate).

Checks:
  - metadata/catalog.json conforms to catalog.schema.json (and nested command /
    concept / task / profile schemas via $ref) — missing required fields fail;
    validators never invent or guess values
  - catalog.json / manifest.json / search-index.json content_sha256 agree
  - basic shape / count coherence across the three artifacts

Does not rewrite files. Invoked via sys.executable from validate_catalog / tests.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from jsonschema import Draft202012Validator
from referencing import Registry, Resource

ROOT = Path(__file__).resolve().parents[1]
META = ROOT / "metadata"
SCHEMA = ROOT / "schema"

CATALOG_DEPS = (
    "catalog.schema.json",
    "command.schema.json",
    "concept.schema.json",
    "task.schema.json",
    "profile.schema.json",
)


def load_catalog_validator(schema_dir: Path) -> Draft202012Validator:
    resources: list[tuple[str, Resource]] = []
    for name in CATALOG_DEPS:
        path = schema_dir / name
        doc = json.loads(path.read_text(encoding="utf-8"))
        Draft202012Validator.check_schema(doc)
        resources.append((doc["$id"], Resource.from_contents(doc)))
    registry = Registry().with_resources(resources)
    catalog_schema = json.loads(
        (schema_dir / "catalog.schema.json").read_text(encoding="utf-8")
    )
    return Draft202012Validator(catalog_schema, registry=registry)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--meta-dir", type=Path, default=META)
    parser.add_argument("--schema-dir", type=Path, default=SCHEMA)
    args = parser.parse_args()
    meta: Path = args.meta_dir
    schema_dir: Path = args.schema_dir

    errors: list[str] = []
    paths = {
        "catalog": meta / "catalog.json",
        "manifest": meta / "manifest.json",
        "search": meta / "search-index.json",
    }
    for path in paths.values():
        if not path.is_file():
            errors.append(f"missing {path}")

    if errors:
        print(f"FAIL: {len(errors)} generated-artifact issue(s)", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        return 1

    cat = json.loads(paths["catalog"].read_text(encoding="utf-8"))
    man = json.loads(paths["manifest"].read_text(encoding="utf-8"))
    idx = json.loads(paths["search"].read_text(encoding="utf-8"))

    try:
        validator = load_catalog_validator(schema_dir)
    except Exception as exc:  # noqa: BLE001 — surface schema load failures
        print(f"FAIL: cannot load catalog schema: {exc}", file=sys.stderr)
        return 1

    for err in sorted(validator.iter_errors(cat), key=lambda e: list(e.path)):
        loc = "/".join(str(p) for p in err.absolute_path) or "(root)"
        errors.append(f"catalog.json schema {loc}: {err.message}")

    for label, doc, kind in (
        ("catalog.json", cat, "nova-commands-bank"),
        ("manifest.json", man, "nova-commands-manifest"),
        ("search-index.json", idx, "nova-commands-search-index"),
    ):
        if doc.get("schema_version") != 2:
            errors.append(f"{label}: schema_version must be 2 (no auto-guess)")
        if doc.get("kind") != kind:
            errors.append(f"{label}: kind must be {kind!r}")
        sha = doc.get("content_sha256")
        if not isinstance(sha, str) or len(sha) != 64:
            errors.append(f"{label}: content_sha256 missing or malformed")

    sha_cat = cat.get("content_sha256")
    sha_man = man.get("content_sha256")
    sha_idx = idx.get("content_sha256")
    if sha_cat != sha_man or sha_cat != sha_idx:
        errors.append(
            "content_sha256 mismatch across catalog/manifest/search-index "
            f"(catalog={sha_cat!r}, manifest={sha_man!r}, search={sha_idx!r})"
        )

    if cat.get("command_count") != len(cat.get("commands") or []):
        errors.append("catalog.json: command_count != len(commands)")
    if cat.get("concept_count") != len(cat.get("concepts") or []):
        errors.append("catalog.json: concept_count != len(concepts)")
    if cat.get("task_count") != len(cat.get("tasks") or []):
        errors.append("catalog.json: task_count != len(tasks)")
    if cat.get("profile_count") != len(cat.get("profiles") or []):
        errors.append("catalog.json: profile_count != len(profiles)")

    for key in ("command_count", "concept_count", "task_count", "profile_count"):
        if man.get(key) != cat.get(key):
            errors.append(f"manifest.json: {key} != catalog.json")
        if idx.get(key) != cat.get(key):
            errors.append(f"search-index.json: {key} != catalog.json")

    if idx.get("entry_count") != len(idx.get("entries") or []):
        errors.append("search-index.json: entry_count != len(entries)")

    if errors:
        print(f"FAIL: {len(errors)} generated-artifact issue(s)", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        return 1

    print(
        f"OK: generated artifacts — catalog schema + matching content_sha256 "
        f"({sha_cat[:12]}…) "
        f"commands={cat.get('command_count')} concepts={cat.get('concept_count')} "
        f"tasks={cat.get('task_count')} profiles={cat.get('profile_count')}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
