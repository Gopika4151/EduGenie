# EduGenie — Google Gemini Powered Learning Assistant

EduGenie is a lightweight FastAPI web application based on the supplied project documentation. It provides:

- Question & Answer (`/qa`)
- Concept explanation (`/explain`)
- Quiz generation with exactly 3 MCQs and 4 options each (`/quiz`)
- Educational summarization (`/summarize`)
- Beginner-to-advanced learning recommendations (`/learn/recommendations`)

## Architecture

```text
Browser
  │
  ├── HTML/CSS/JS
  │
  ▼
FastAPI (main.py)
  │
  ├── qna.py ───────────────┐
  ├── quiz_module.py ───────┤
  ├── summary_module.py ────┤──> gemini_client.py ──> Gemini API
  ├── learning_path.py ─────┤
  └── explanation_module.py ┘
             │
             └── optional LaMini-Flan-T5 local model
```

The project keeps the module separation described in the source document while adding validation, environment-based configuration, a browser-side integration layer, health checking, and tests.

## 1. Prerequisites

- Python 3.10+
- VS Code
- A Gemini API key

The default application uses Gemini for the explanation endpoint too, so it starts with a smaller dependency footprint. The optional local LaMini model is available when `USE_LOCAL_EXPLANATION=true`.

## 2. Create a virtual environment

### Windows PowerShell

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## 3. Configure Gemini

Copy `.env.example` to `.env`:

```text
GEMINI_API_KEY=your_real_key_here
GEMINI_MODEL=gemini-3.8-flash
USE_LOCAL_EXPLANATION=false
```

Do not commit `.env` to Git.

## 4. Run

```bash
uvicorn main:app --reload
```

Open:

```text
http://127.0.0.1:8000
```

FastAPI API documentation:

```text
http://127.0.0.1:8000/docs
```

## 5. Test

Run the automated tests:

```bash
pytest -q
```

These tests verify that the application loads, the health endpoint works, and request validation rejects empty questions.

## 6. Test the AI features manually

### Q&A

Ask:

```text
Which is the largest ocean?
```

### Explain

Enter:

```text
Explain the Pythagoras theorem.
```

### Quiz

Paste a paragraph about any educational topic. The app asks Gemini for exactly 3 MCQs with 4 options each and provides browser-side answer checking.

### Summary

Paste a long educational passage.

### Learning path

Enter:

```text
SQL
```

and select a level.

## 7. Optional local LaMini explanation

The source documentation specifies `LaMini-Flan-T5-783M` for concept explanations. To use that local model:

```bash
pip install -r requirements-local.txt
```

Then set:

```text
USE_LOCAL_EXPLANATION=true
```

The first explanation request downloads the Hugging Face model if it is not already cached. CPU inference can be slower and requires substantially more disk/RAM than the default Gemini-backed explanation.

If the local model cannot be loaded, the endpoint returns a clear configuration error rather than silently producing an unrelated response.

## API request examples

### Q&A

```bash
curl -X POST http://127.0.0.1:8000/qa ^
  -H "Content-Type: application/json" ^
  -d "{\"question\":\"What is photosynthesis?\"}"
```

On macOS/Linux:

```bash
curl -X POST http://127.0.0.1:8000/qa \
  -H "Content-Type: application/json" \
  -d '{"question":"What is photosynthesis?"}'
```

### Quiz

```bash
curl -X POST http://127.0.0.1:8000/quiz \
  -H "Content-Type: application/json" \
  -d '{"text":"Photosynthesis is the process by which green plants convert light energy into chemical energy."}'
```

## Troubleshooting

### `GEMINI_API_KEY is not configured`

Check that `.env` exists in the project root and contains:

```text
GEMINI_API_KEY=...
```

Restart Uvicorn after changing `.env`.

### Model not found / unavailable

Change `GEMINI_MODEL` in `.env` to a model currently available to your Gemini API project. The application does not hard-code a historical Gemini model.

### Quiz JSON error

The quiz module requests JSON, strips Markdown fences if a model returns them, parses the JSON, and validates the exact three-question/four-option contract. A provider response that violates that contract is returned as an API error instead of being displayed as malformed quiz data.

### PowerShell blocks activation

Use:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Then activate the environment again.

## Project structure

```text
EduGenie/
├── main.py
├── config.py
├── gemini_client.py
├── qna.py
├── explanation_module.py
├── quiz_module.py
├── summary_module.py
├── learning_path.py
├── requirements.txt
├── requirements-local.txt
├── .env.example
├── .gitignore
├── README.md
├── templates/
│   └── index.html
├── static/
│   ├── style.css
│   └── app.js
└── tests/
    └── test_api.py
```
