# Agentic Perspective Capture v1.0

Module 1 of Agentic Co-Emergence.

Its contract is deliberately boring:

```text
Question + Persona Library → Perspective Pack
```

It captures each persona's independent initial framing of a question. It does not conduct discussion, synthesis, hand-off, memory update, or semantic graph work.

## Install

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e .[test]
copy .env.example .env
```

Add your `OPENAI_API_KEY` to `.env`.

## Run

```powershell
python -m agentic_perspective_capture "What is philosophy?"
```

This creates:

```text
outputs/
└── Q000001/
    ├── perspective_pack.json
    └── perspective_pack.md
```

## Persona Library

The expected deterministic order is:

```text
Ada.md
Aletheia.md
Alison.md
Harry.md
joan.md
lyla.md
Sael.md
Synaia.md
tenzing.md
```

Replace the placeholder files in `personas/` with the canonical persona files from `agentic_co_emergence_v0_1`.

## Tests

```powershell
pytest
```
