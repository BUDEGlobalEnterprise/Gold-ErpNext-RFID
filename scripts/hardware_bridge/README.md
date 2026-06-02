# Zevar Hardware Bridge

Two WebSocket servers live here. Both speak the same wire protocol on
`ws://localhost:8080`, so the frontend (`HardwareService.js`) cannot tell
them apart. Pick the one that matches the moment:

| Server            | When to use                              |
| ----------------- | ---------------------------------------- |
| `hardware_bridge.py` | Production — talks to real USB/network printers and the cash drawer |
| `mock_bridge.py`     | Development & client onboarding — renders to console + files |

## Quick start

```bash
# Mock (no hardware needed — works on a fresh checkout)
cd frappe-bench/apps/zevar_core/scripts/hardware_bridge
python mock_bridge.py

# Real (requires printers wired up + `pip install python-escpos`)
python hardware_bridge.py
```

Both bind to `ws://localhost:8080` by default. Override with env vars:

```bash
ZEVAR_BRIDGE_HOST=0.0.0.0 ZEVAR_BRIDGE_PORT=8081 python mock_bridge.py
```

## Wire protocol

Messages are JSON. The mock and the real bridge respond identically to
these actions:

| `action`         | Payload                                          | Response                             |
| ---------------- | ------------------------------------------------ | ------------------------------------ |
| `print`          | `{type, encoding, content}`                      | `{status, message}`                  |
| `print_tag_zpl`  | `{tag_data: {item_code, item_name, rate, ...}}`  | `{status, message, zpl?}`            |
| `cash_drawer`    | —                                                | `{status, message}`                  |
| `ping`           | —                                                | `{status: 'pong'}`                   |
| `status`         | —                                                | `{status: 'ok', receipt_printer, tag_printer, bridge_version}` |

The frontend uses `bridge_version` starting with `mock-` to display the
"(mock)" badge in the Settings → Hardware Test panel.

## Mock output

`mock_bridge.py` writes "printed" artefacts to `./mock_output/`:

```
mock_output/
├── receipt_20260602_143012.bin   # raw ESC/POS bytes
└── tag_20260602_143045.zpl       # ZPL text
```

ESC/POS content is also rendered to the terminal in ASCII so you can
eyeball receipt layout without a printer. ZPL previews open at
[https://labelary.com/viewer.html](https://labelary.com/viewer.html) —
paste the `.zpl` file contents to see the rendered label.

## Settings → Hardware Test panel

Path: `/settings` → **Hardware Test** tab.

| Test                    | What it does                                                                                                          |
| ----------------------- | --------------------------------------------------------------------------------------------------------------------- |
| Scanner input           | Focused text field — a hardware scanner (keyboard wedge) types the value and presses Enter. Camera fallback works too.|
| Print Test Receipt      | Calls `build_test_receipt` on the backend, sends sample ESC/POS to bridge. Falls back to browser print if offline.    |
| Print Test Tag          | Calls `build_test_tag`, sends ZPL to bridge. Preview button renders at labelary.com.                                  |
| Open Cash Drawer        | Sends `\\x1b\\x70\\x00\\x19\\xfa` to bridge.                                                                          |
| Stripe Quick Check      | Loads Stripe Terminal SDK, lists readers. No charge.                                                                  |
| Stripe Full Test ($0.50) | Calls `stripe_terminal.api.run_test_payment` — test mode charge + auto refund.                                       |
| Square Quick / Full     | Same pattern against the Square sandbox.                                                                              |

The activity log at the bottom records every test action so a client can
share the trace during onboarding.

## Backend test endpoints

Located in `zevar_core/integrations/hardware/api.py`:

- `get_hardware_bridge_status()` — reports bridge URL + device protocol map
- `build_test_receipt()` — sample ESC/POS payload (no Sales Invoice needed)
- `build_test_tag()` — sample ESC/POS tag + ZPL payload (no Item needed)
- `build_test_zpl()` — sample ZPL only (for labelary preview)

All gated by `frappe.only_for(["Sales User", "Sales Manager", "System Manager", "POS User"])`.

## Troubleshooting

**Bridge won't connect from the browser.**
Browsers refuse `ws://localhost` from an `https://` parent page. Either
serve the site over `http://` during dev, or run the bridge with a TLS
wrapper (HAProxy / Caddy) — and switch the URL to `wss://`.

**`websockets` import error.**
```bash
pip install websockets
```
The real bridge additionally needs `python-escpos` and (for USB) `libusb`.

**Stripe Full Test fails with "no such customer".**
You're running against live Stripe keys. Switch to `sk_test_...` keys in
**Zevar POS Settings** before retrying — the test endpoint expects test mode.
