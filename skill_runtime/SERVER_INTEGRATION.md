# Server Integration Notes

`server.py` can connect DeepSeek to indexed skills by loading context before the Ollama request.

Add this import near the top of `server.py` after the standard imports:

```python
from pathlib import Path
import sys

SKILL_RUNTIME = Path(r"C:\Users\Kausar\Documents\Codex\2026-07-29\i-want-you-to-redesign-saturnalia\work\skill_runtime")
if str(SKILL_RUNTIME) not in sys.path:
    sys.path.insert(0, str(SKILL_RUNTIME))

from luminary_skill_context import requires_approval, select_skill_context
```

Then inside the `/chat` handler, before building `full_prompt`, add:

```python
if requires_approval(prompt):
    self._set_cors(200)
    self.wfile.write(json.dumps({
        "response": "That request may affect files, accounts, credentials, installs, or system settings. Please confirm the exact action you want me to take before I proceed."
    }).encode("utf-8"))
    return

skill_context = select_skill_context(prompt)
```

Finally include the context in the prompt:

```python
full_prompt = f"""### Instruction:
{system_instruction}

Relevant Luminary skill context:
{skill_context}

User request:
{prompt}

### Response:
"""
```

This keeps DeepSeek grounded in the indexed skills while preventing skill text from authorizing unsafe actions.
