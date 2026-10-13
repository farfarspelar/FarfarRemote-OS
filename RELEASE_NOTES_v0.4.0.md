# FarfarRemote 0.4.0

FarfarRemote 0.4.0 introduced two APK variants built from one shared source tree.

- **FarfarRemote App** (`org.farfarremote.app`) is a normal Android app with no HOME intent.
- **FarfarRemote OS** (`org.farfarremote`) retains HOME launcher behavior for dedicated devices. It remains an Android app, not a separate ROM.

Both support Android 4.4 / API 19 or newer. Find My Kodi searches for Kodi's HTTP JSON-RPC DNS-SD service when requested, verifies the endpoint, and asks before saving. Manual host, port, username, and password entry remains available. See [README.md](README.md) and [TEST_REPORT.md](TEST_REPORT.md) for setup and test details.
