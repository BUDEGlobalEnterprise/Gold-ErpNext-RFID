"""
Zevar Hardware Bridge — WebSocket server for POS hardware communication.

Handles: ESC/POS thermal printers, Zebra ZPL tag printers, cash drawers,
barcode scanners (via keyboard wedge), and RFID readers.

Requires: python-escpos (pip install python-escpos)
Optional: libusb for USB printer support

Run: python hardware_bridge.py
"""

import asyncio
import json
import os
import sys

try:
	import websockets
except ImportError:
	print("ERROR: websockets not installed. Run: pip install websockets")
	sys.exit(1)

# Configuration from environment or defaults
BRIDGE_HOST = os.environ.get("ZEVAR_BRIDGE_HOST", "localhost")
BRIDGE_PORT = int(os.environ.get("ZEVAR_BRIDGE_PORT", "8080"))

# Printer config (set via env vars or config file)
RECEIPT_PRINTER_TYPE = os.environ.get("ZEVAR_RECEIPT_PRINTER_TYPE", "usb")  # usb, network, cups
RECEIPT_PRINTER_USB_VENDOR = int(os.environ.get("ZEVAR_RECEIPT_PRINTER_USB_VENDOR", "0x04b8"), 16)  # Epson
RECEIPT_PRINTER_USB_PRODUCT = int(os.environ.get("ZEVAR_RECEIPT_PRINTER_USB_PRODUCT", "0x0202"), 16)
RECEIPT_PRINTER_NETWORK_IP = os.environ.get("ZEVAR_RECEIPT_PRINTER_NETWORK_IP", "")
RECEIPT_PRINTER_NETWORK_PORT = int(os.environ.get("ZEVAR_RECEIPT_PRINTER_NETWORK_PORT", "9100"))

TAG_PRINTER_TYPE = os.environ.get("ZEVAR_TAG_PRINTER_TYPE", "usb")  # usb, network
TAG_PRINTER_USB_VENDOR = int(os.environ.get("ZEVAR_TAG_PRINTER_USB_VENDOR", "0x0a5f"), 16)  # Zebra
TAG_PRINTER_USB_PRODUCT = int(os.environ.get("ZEVAR_TAG_PRINTER_USB_PRODUCT", "0x0161"), 16)
TAG_PRINTER_NETWORK_IP = os.environ.get("ZEVAR_TAG_PRINTER_NETWORK_IP", "")
TAG_PRINTER_NETWORK_PORT = int(os.environ.get("ZEVAR_TAG_PRINTER_NETWORK_PORT", "9100"))


def get_receipt_printer():
	"""Get ESC/POS printer instance for receipts."""
	try:
		from escpos.printer import Network, Usb

		if RECEIPT_PRINTER_TYPE == "network" and RECEIPT_PRINTER_NETWORK_IP:
			return Network(RECEIPT_PRINTER_NETWORK_IP, port=RECEIPT_PRINTER_NETWORK_PORT)
		else:
			return Usb(RECEIPT_PRINTER_USB_VENDOR, RECEIPT_PRINTER_USB_PRODUCT, in_ep=0x81, out_ep=0x03)
	except ImportError:
		print("WARNING: python-escpos not installed. Install with: pip install python-escpos")
		return None
	except Exception as e:
		print(f"WARNING: Could not connect to receipt printer: {e}")
		return None


def get_tag_printer():
	"""Get ZPL printer instance for jewelry tags (raw socket)."""
	import socket

	ip = TAG_PRINTER_NETWORK_IP or "192.168.1.50"
	port = TAG_PRINTER_NETWORK_PORT or 9100

	try:
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.settimeout(5)
		s.connect((ip, port))
		return s
	except Exception as e:
		print(f"WARNING: Could not connect to tag printer at {ip}:{port}: {e}")
		return None


def print_receipt_escpos(content):
	"""Print ESC/POS formatted content to thermal receipt printer."""
	p = get_receipt_printer()
	if p is None:
		print("[FALLBACK] No receipt printer connected, printing to console:")
		print(content)
		return True

	try:
		p.text(content)
		p.cut()
		print("Receipt printed successfully")
		return True
	except Exception as e:
		print(f"ERROR: Receipt print failed: {e}")
		return False


def print_tag_zpl(content, printer_type="escpos"):
	"""Print tag content — either ESC/POS or ZPL format."""
	if printer_type == "zpl":
		return _print_zpl(content)
	else:
		return _print_tag_escpos(content)


def _print_tag_escpos(content):
	"""Print ESC/POS formatted tag to tag printer."""
	p = get_receipt_printer()
	if p is None:
		print("[FALLBACK] No tag printer connected, printing to console:")
		print(content)
		return True

	try:
		p.text(content)
		p.cut()
		print("Tag printed successfully")
		return True
	except Exception as e:
		print(f"ERROR: Tag print failed: {e}")
		return False


def _print_zpl(zpl_content):
	"""Send ZPL commands directly to Zebra printer via raw socket."""
	sock = get_tag_printer()
	if sock is None:
		print("[FALLBACK] No ZPL printer connected, ZPL output:")
		print(zpl_content)
		return True

	try:
		sock.sendall(zpl_content.encode("ascii"))
		sock.close()
		print("ZPL tag printed successfully")
		return True
	except Exception as e:
		print(f"ERROR: ZPL print failed: {e}")
		return False


def open_cash_drawer():
	"""Send cash drawer kick signal via receipt printer."""
	p = get_receipt_printer()
	if p is None:
		print("[FALLBACK] No printer connected to trigger cash drawer")
		return False

	try:
		# ESC/POS cash drawer kick: ESC p m t1 t2
		# m=0, t1=25*2ms, t2=25*2ms (standard kick)
		p._raw(b"\x1b\x70\x00\x19\x19")
		print("Cash drawer opened")
		return True
	except Exception as e:
		print(f"ERROR: Cash drawer failed: {e}")
		return False


def generate_zpl_jewelry_tag(data):
	"""Generate ZPL for a jewelry tag. Returns ZPL string.

	Tag size: 50mm x 25mm (2" x 1") — standard jewelry tag
	Density: 8 dots/mm
	"""
	item_code = data.get("item_code", "")
	item_name = data.get("item_name", "")[:30]
	price = data.get("rate", 0)
	metal = data.get("metal_type", "")
	weight = data.get("weight_grams", 0)

	price_str = f"${price:.2f}" if price else ""
	desc = f"{metal} {weight}g" if metal else item_name

	zpl = "^XA\n"
	zpl += "^PW400\n"  # Print width: 400 dots (50mm)
	zpl += "^LL200\n"  # Label length: 200 dots (25mm)

	# Store name
	zpl += "^FO20,10^A0N,25,25^FDZEVAR^FS\n"
	# Item description
	zpl += "^FO20,40^A0N,20,20^FD{0}^FS\n".format(desc)
	# SKU
	zpl += "^FO20,70^A0N,18,18^FDSKU: {0}^FS\n".format(item_code)
	# Price
	zpl += "^FO20,100^A0N,30,30^FD{0}^FS\n".format(price_str)
	# Barcode
	zpl += "^FO20,140^BY2^BCN,40,Y,N,N^FD{0}^FS\n".format(item_code)
	zpl += "^XZ\n"

	return zpl


async def handle_hardware_request(websocket, path):
	client_addr = websocket.remote_address
	print(f"Client connected from {client_addr}")
	try:
		async for message in websocket:
			data = json.loads(message)
			action = data.get("action")

			if action == "print":
				payload = data.get("payload", {})
				content = payload.get("content", "")
				printer_type = payload.get("type", "receipt")
				encoding = payload.get("encoding", "ESC/POS")

				if printer_type == "tag" and encoding == "ZPL":
					success = _print_zpl(content)
				elif printer_type == "receipt":
					success = print_receipt_escpos(content)
				elif printer_type == "tag":
					success = print_tag_zpl(content)
				else:
					success = print_receipt_escpos(content)

				await websocket.send(
					json.dumps(
						{
							"status": "success" if success else "error",
							"message": f"{printer_type.capitalize()} printed {'successfully' if success else 'failed'}.",
						}
					)
				)

			elif action == "print_tag_zpl":
				tag_data = data.get("tag_data", {})
				zpl_content = generate_zpl_jewelry_tag(tag_data)
				success = _print_zpl(zpl_content)
				await websocket.send(
					json.dumps(
						{
							"status": "success" if success else "error",
							"message": "ZPL tag printed",
							"zpl": zpl_content if not success else None,
						}
					)
				)

			elif action == "cash_drawer":
				success = open_cash_drawer()
				await websocket.send(
					json.dumps(
						{
							"status": "success" if success else "error",
							"message": "Cash drawer " + ("opened" if success else "failed"),
						}
					)
				)

			elif action == "ping":
				await websocket.send(json.dumps({"status": "pong"}))

			elif action == "status":
				receipt_ok = get_receipt_printer() is not None
				tag_ok = get_tag_printer() is not None
				await websocket.send(
					json.dumps(
						{
							"status": "ok",
							"receipt_printer": receipt_ok,
							"tag_printer": tag_ok,
							"bridge_version": "2.0",
						}
					)
				)

	except websockets.exceptions.ConnectionClosed:
		print("Client disconnected")
	except Exception as e:
		print(f"Error: {e}")
		try:
			await websocket.send(json.dumps({"status": "error", "message": str(e)}))
		except Exception:
			pass


async def main():
	print(f"Starting Zevar Hardware Bridge v2.0 on ws://{BRIDGE_HOST}:{BRIDGE_PORT}")
	print(f"  Receipt printer: {RECEIPT_PRINTER_TYPE}")
	print(f"  Tag printer: {TAG_PRINTER_TYPE}")
	async with websockets.serve(handle_hardware_request, BRIDGE_HOST, BRIDGE_PORT):
		await asyncio.Future()


if __name__ == "__main__":
	try:
		asyncio.run(main())
	except KeyboardInterrupt:
		print("\nBridge stopped.")
