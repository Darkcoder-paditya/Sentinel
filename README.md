# Sentinel Backend (Flask)

Local-only internal mail + credential vault.

## Quickstart

1. Create venv and install deps:
```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

2. Configure env:
```bash
cp .env.example .env
```

3. Run dev server:
```bash
python run.py
```

Default admin is created from env on first run.

## API Overview
- Auth: login, bootstrap admin
- Mail: send, inbox, sent
- Vault: CRUD encrypted credentials

## Tech
- Flask, SQLAlchemy (SQLite), JWT, CORS, cryptography
