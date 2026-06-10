"""
Zevar Hardware Bridge — MOCK / DEVELOPMENT SERVER

A hardware-free WebSocket server that mirrors the wire protocol of
`scripts/hardware_bridge.py`. Use this for local development and for
the Settings → Hardware Test panel when no real printer/scanner/terminal
is attached.

What it does:
  - Listens on ws://localhost:8080 (same as the real bridge)
  - Accepts the same `action` messages as the real bridge
  - Renders ESC/POS bytes to a readable ASCII preview in the console
  - Logs ZPL to ./printed_tags/  (open .zpl files at labelary.com)
  - Logs cash-drawer kicks as console lines
  - Always reports status=ok so the UI shows a "connected" indicator

Run:
  python mock_bridge.py
  # or with custom port:
  ZEVAR_BRIDGE_PORT=8081 python mock_bridge.py

Stop with Ctrl+C. No external dependencies beyond `websockets`
(already required by the real bridge).
"""

from __future__ import annotations

import asyncio
import datetime as _dt
import json
import os
import sys
from pathlib import Path

try:
	import websockets
except ImportError:
	print("ERROR: websockets not installed. Run: pip install websockets")
	sys.exit(1)


BRIDGE_HOST = os.environ.get("ZEVAR_BRIDGE_HOST", "localhost")
BRIDGE_PORT = int(os.environ.get("ZEVAR_BRIDGE_PORT", "8080"))

# Where we dump "printed" artefacts so the dev can inspect them.
OUT_DIR = Path(__file__).resolve().parent / "mock_output"
OUT_DIR.mkdir(exist_ok=True)


# ---------------------------------------------------------------------------
# ESC/POS byte interpreter
# ---------------------------------------------------------------------------


def render_escpos(content: str | bytes) -> str:
	"""Best-effort render of ESC/POS content to readable ASCII.

	ESC/POS streams mix plain text with control bytes. We strip the well-known
	control sequences and keep the human-readable payload so a developer can
	eyeball receipt/tag layout in the terminal without a printer.
	"""
	if isinstance(content, bytes):
		try:
			text = content.decode("utf-8", errors="replace")
		except Exception:
			text = content.decode("latin-1", errors="replace")
	else:
		text = content

	# Drop common ESC/POS control sequences we don't want to display.
	# (We intentionally keep \n so layout is visible.)
	replacements = {
		"\x1b@": "",  # init
		"\x1bE": "",  # bold on
		"\x1bF": "",  # bold off
		"\x1d!": "",  # text size
		"\x1bM": "",  # font
		"\x1ba": "",  # align
		"\x1bd": "",  # align (legacy)
		"\x1d\x61": "",  # align (GS!)
		"\x1b\x21": "",  # print mode
		"\x1b--\x00": "",  # cancel underline
		"\x1b--\x01": "",  # underline 1-dot
		"\x1dV\x41": "",  # cut (partial)
		"\x1dV\x42": "",  # cut (full)
		"\x1dV\x00": "",  # cut
		"\x1b\x70\x00\x19\xfa": "",  # cash drawer pulse (we log it elsewhere)
		"\x1b=\x01": "",  # printer online
		"\x1b=\x00": "",  # printer offline
	}
	for k, v in replacements.items():
		text = text.replace(k, v)

	# Strip any remaining non-printable bytes (keep \n, \t, CR).
	cleaned = []
	for ch in text:
		o = ord(ch)
		if ch in ("\n", "\t", "\r") or 0x20 <= o < 0x7F:
			cleaned.append(ch)
		elif o == 0xA0:  # nbsp
			cleaned.append(" ")
	return "".join(cleaned).replace("\r", "")


# ---------------------------------------------------------------------------
# Action handlers (mirror hardware_bridge.py wire protocol exactly)
# ---------------------------------------------------------------------------


async def handle_request(websocket, _path):
	peer = getattr(websocket, "remote_address", None)
	print(f"[connect] {peer}")
	try:
		async for message in websocket:
			try:
				data = json.loads(message)
			except json.JSONDecodeError:
				await websocket.send(json.dumps({"status": "error", "message": "invalid json"}))
				continue

			action = data.get("action")
			ts = _dt.datetime.now().strftime("%H:%M:%S")
			print(f"[{ts}] action={action}")

			if action == "print":
				payload = data.get("payload", {}) or {}
				content = payload.get("content", "")
				printer_type = payload.get("type", "receipt")
				encoding = payload.get("encoding", "ESC/POS")

				# Save raw bytes for offline inspection
				ext = "zpl" if encoding == "ZPL" else "bin"
				outfile = OUT_DIR / f"{printer_type}_{_dt.datetime.now():%Y%m%d_%H%M%S}.{ext}"
				outfile.write_bytes(
					content.encode("utf-8", errors="replace") if isinstance(content, str) else content
				)

				if encoding == "ZPL":
					print(f"   -> ZPL written to {outfile.name}")
					print("   -> View at https://labelary.com/viewer.html  (paste file contents)")
					preview = (
						content if isinstance(content, str) else content.decode("utf-8", errors="replace")
					)
					print("   --- ZPL preview ---")
					for line in preview.splitlines()[:8]:
						print(f"   | {line}")
					print("   ---")
				else:
					preview = render_escpos(content)
					print(f"   -> {printer_type.upper()} rendered preview:")
					print("   --- ESC/POS preview ---")
					for line in preview.splitlines():
						print(f"   | {line}")
					print("   ---")

				await websocket.send(
					json.dumps(
						{
							"status": "success",
							"message": f"{printer_type.capitalize()} printed (mock)",
							"mock": True,
							"output_file": str(outfile),
						}
					)
				)

			elif action == "print_tag_zpl":
				tag_data = data.get("tag_data", {}) or {}
				# Reuse the real bridge's ZPL generator if importable; else inline.
				try:
					from hardware_bridge import generate_zpl_jewelry_tag  # type: ignore

					zpl = generate_zpl_jewelry_tag(tag_data)
				except Exception:
					zpl = _inline_zpl(tag_data)

				outfile = OUT_DIR / f"tag_{_dt.datetime.now():%Y%m%d_%H%M%S}.zpl"
				outfile.write_text(zpl)
				print(f"   -> ZPL tag written to {outfile.name}")
				print("   --- ZPL preview ---")
				for line in zpl.splitlines():
					print(f"   | {line}")
				print("   ---")

				await websocket.send(
					json.dumps(
						{
							"status": "success",
							"message": "ZPL tag printed (mock)",
							"mock": True,
							"zpl": zpl,
							"output_file": str(outfile),
						}
					)
				)

			elif action == "cash_drawer":
				print("   -> CASH DRAWER KICK  (\\x1b\\x70\\x00\\x19\\xfa)")
				print("   -> In production the receipt printer would emit the pulse.")
				await websocket.send(
					json.dumps(
						{
							"status": "success",
							"message": "Cash drawer opened (mock)",
							"mock": True,
						}
					)
				)

			elif action == "ping":
				await websocket.send(json.dumps({"status": "pong", "mock": True}))

			elif action == "status":
				await websocket.send(
					json.dumps(
						{
							"status": "ok",
							"receipt_printer": True,
							"tag_printer": True,
							"cash_drawer": True,
							"bridge_version": "mock-1.0",
							"mock": True,
						}
					)
				)

			else:
				await websocket.send(
					json.dumps(
						{
							"status": "error",
							"message": f"unknown action: {action!r}",
						}
					)
				)

	except websockets.exceptions.ConnectionClosed:
		print(f"[disconnect] {peer}")
	except Exception as e:
		print(f"[error] {e!r}")
		try:
			await websocket.send(json.dumps({"status": "error", "message": str(e)}))
		except Exception:
			pass


def _inline_zpl(tag: dict) -> str:
	"""Minimal ZPL fallback if the real bridge module isn't on the path."""
	item_code = (tag.get("item_code") or "")[:24]
	item_name = (tag.get("item_name") or "")[:28]
	rate = tag.get("rate") or 0
	metal = tag.get("metal_type") or ""
	weight = tag.get("weight_grams") or 0
	desc = f"{metal} {weight}g" if metal else item_name
	return (
		"^XA\n"
		"^PW400\n"
		"^LL200\n"
		"^FO20,10^A0N,25,25^FDZEVAR^FS\n"
		f"^FO20,40^A0N,18,18^FD{desc}^FS\n"
		f"^FO20,65^A0N,18,18^FD{item_name}^FS\n"
		f"^FO20,90^A0N,30,30^FD${rate:.2f}^FS\n"
		f"^FO20,130^BY2^BCN,40,Y,N,N^FD{item_code}^FS\n"
		"^XZ\n"
	)


async def main():
	print("=" * 70)
	print(" Zevar Hardware Bridge — MOCK SERVER")
	print(f" Listening on ws://{BRIDGE_HOST}:{BRIDGE_PORT}")
	print(f" Output dir:  {OUT_DIR}")
	print(" Stop with Ctrl+C")
	print("=" * 70)
	print(" This is NOT a real hardware bridge. It accepts the same wire")
	print(" protocol as hardware_bridge.py and renders output to console")
	print(" + files so you can develop and test without printers.")
	print("=" * 70)
	async with websockets.serve(handle_request, BRIDGE_HOST, BRIDGE_PORT):
		await asyncio.Future()


if __name__ == "__main__":
	try:
		asyncio.run(main())
	except KeyboardInterrupt:
		print("\nMock bridge stopped.")
