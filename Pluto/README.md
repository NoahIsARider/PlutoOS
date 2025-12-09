# PlutoOS (demo)

Pluto is a minimal, demonstrative "OS"-like project that emphasizes two themes:

- Mystery & Privacy: a `PrivacyVault` for encrypted local storage.
- Cooperation & Coordination: a simple `CollabServer` and `CollabClient` for peer messaging.

Quick start

1. Create a Python virtual environment and install dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Run demo:

```bash
python3 demo.py
```

Or run the CLI module:

```bash
python3 -m Pluto.cli --demo
```

Notes

- This is a demonstration project, not a production OS. The design focuses on structure and primitives that reflect Pluto's themes.
- The vault uses `cryptography`'s Fernet; if not available, a fallback XOR cipher is used for demo purposes only.
