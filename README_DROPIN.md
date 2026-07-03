# Agentic Perspective Capture v1.1 Drop-in Replacement

Copy these files over your existing `agentic_perspective_capture` project.

## Files replaced

```text
agentic_perspective_capture/perspective_capture/models.py
agentic_perspective_capture/perspective_capture/prompts.py
agentic_perspective_capture/perspective_capture/capture.py
agentic_perspective_capture/perspective_capture/serializers.py
tests/test_perspective_capture.py
```

## What changes

The Perspective Pack contract is simplified:

```json
{
  "persona": "Harry",
  "source_file": "Harry.md",
  "initial_perspective": "..."
}
```

No fixed sections. No discussion. No synthesis. No hand-off.

## Suggested workflow

```powershell
git checkout -b feature/short-initial-perspectives
# copy files over existing project
pytest
git status
git diff
git add .
git commit -m "Simplify perspective capture to short initial positions"
python -m agentic_perspective_capture "What is philosophy?"
```
