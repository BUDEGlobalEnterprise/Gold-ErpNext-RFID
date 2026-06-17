#!/usr/bin/env python3
"""Generate frontend/zevar_ui/src/types/realtime-events.ts from events_schema.py.

Single source of truth: ``zevar_core/api/realtime/events_schema.py``. Both the
Python publishers and this generated TypeScript read it, so a field added there
appears on both sides with no hand-sync.

Usage:
    python scripts/gen_realtime_types.py            # write the .ts
    python scripts/gen_realtime_types.py --check    # CI gate: exit 1 on drift
"""

from __future__ import annotations

import argparse
import importlib.util
import pathlib
import sys

_APP_ROOT = pathlib.Path(__file__).resolve().parents[1]


def _load_schema():
	"""Load events_schema.py directly by path.

	zevar_core/api/__init__.py imports frappe-dependent modules, so we must NOT
	go through the package import system. events_schema.py is frappe-free, so a
	standalone file load works under any python (CI doesn't need the bench env).
	"""
	schema_path = _APP_ROOT / "zevar_core" / "api" / "realtime" / "events_schema.py"
	spec = importlib.util.spec_from_file_location("zevar_events_schema", schema_path)
	mod = importlib.util.module_from_spec(spec)
	spec.loader.exec_module(mod)
	return mod


_schema = _load_schema()
CHANNELS = _schema.CHANNELS
EVENT_TYPES = _schema.EVENT_TYPES
TYPE_MAP = _schema.TYPE_MAP
SCHEMA_VERSION = _schema.SCHEMA_VERSION
envelope_fields = _schema.envelope_fields

_HEADER = (
	"// AUTO-GENERATED from zevar_core/api/realtime/events_schema.py\n"
	"// by scripts/gen_realtime_types.py. Do not edit by hand —\n"
	"// edit events_schema.py and re-run the generator.\n\n"
)


def _ts_interface(name: str, fields: dict) -> str:
	lines = [f"export interface {name} {{"]
	for fname, tlabel in fields.items():
		t = TYPE_MAP.get(tlabel, tlabel)
		optional = "null" in t
		lines.append(f"\t{fname}{'?' if optional else ''}: {t};")
	lines.append("}")
	return "\n".join(lines)


def _data_name(event_type: str) -> str:
	return "".join(p.capitalize() for p in event_type.split(".")) + "Data"


def render() -> str:
	out = [_HEADER, f"export const SCHEMA_VERSION = '{SCHEMA_VERSION}';\n"]
	out.append(_ts_interface("EventEnvelope", envelope_fields()))
	out.append("")
	for event_type, spec in EVENT_TYPES.items():
		out.append(_ts_interface(_data_name(event_type), spec["fields"]))
		out.append("")
	out.append("export const EVENT_TYPES = {")
	for event_type, spec in EVENT_TYPES.items():
		out.append(
			f"\t'{event_type}': {{ channel: '{spec['channel']}', dataType: '{_data_name(event_type)}' }},"
		)
	out.append("} as const;\n")
	out.append("export const CHANNELS = {")
	for channel, spec in CHANNELS.items():
		out.append(f"\t'{channel}': {{ scope: '{spec['scope']}' }},")
	out.append("} as const;\n")
	return "\n".join(out)


def main() -> None:
	ap = argparse.ArgumentParser()
	ap.add_argument("--check", action="store_true", help="fail if the .ts drifted")
	ap.add_argument(
		"--out",
		default="frontend/zevar_ui/src/types/realtime-events.ts",
		help="output path relative to the app root",
	)
	args = ap.parse_args()

	content = render() + "\n"
	out_path = _APP_ROOT / args.out

	if args.check:
		existing = out_path.read_text() if out_path.exists() else ""
		if existing != content:
			print(
				f"DRIFT: {out_path} differs from events_schema.py. "
				f"Run: python scripts/gen_realtime_types.py",
				file=sys.stderr,
			)
			sys.exit(1)
		print("OK: realtime-events.ts is up to date with events_schema.py.")
		return

	out_path.parent.mkdir(parents=True, exist_ok=True)
	out_path.write_text(content)
	print(f"wrote {out_path} ({len(content)} chars)")


if __name__ == "__main__":
	main()
