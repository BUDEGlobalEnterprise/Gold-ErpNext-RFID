import asyncio
import json
import os

import websockets

# Configuration
BRIDGE_HOST = "localhost"
BRIDGE_PORT = 8080


async def handle_hardware_request(websocket, path):
	print(f"Client connected from {websocket.remote_address}")
	try:
		async for message in websocket:
			data = json.loads(message)
			action = data.get("action")

			if action == "print":
				payload = data.get("payload", {})
				content = payload.get("content", "")
				printer_type = payload.get("type", "receipt")

				print(f"Printing {printer_type}...")
				print("-" * 20)
				print(content)
				print("-" * 20)

				# In a real environment, you would use a library like python-escpos
				# to send 'content' to the USB/Network printer.
				# Example:
				# from escpos.printer import Usb
				# p = Usb(0x04b8, 0x0202) # Epson TM-T88V
				# p.text(content)
				# p.cut()

				await websocket.send(
					json.dumps(
						{"status": "success", "message": f"{printer_type.capitalize()} printed successfully."}
					)
				)

			elif action == "ping":
				await websocket.send(json.dumps({"status": "pong"}))

	except websockets.exceptions.ConnectionClosed:
		print("Client disconnected")
	except Exception as e:
		print(f"Error: {e}")
		await websocket.send(json.dumps({"status": "error", "message": str(e)}))


async def main():
	print(f"Starting Zevar Hardware Bridge on ws://{BRIDGE_HOST}:{BRIDGE_PORT}")
	async with websockets.serve(handle_hardware_request, BRIDGE_HOST, BRIDGE_PORT):
		await asyncio.Future()  # run forever


if __name__ == "__main__":
	try:
		asyncio.run(main())
	except KeyboardInterrupt:
		print("\nBridge stopped.")
