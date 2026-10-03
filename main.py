from pathlib import Path
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field

from qna import answer_question
from explanation_module import explain_topic
from quiz_module import generate_quiz
from summary_module import summarize_text
from learning_path import get_learning_recommendations

BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(
    title="EduGenie",
    description="Google Gemini powered learning assistant",
    version="1.0.0",
)

app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


class TextRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=30000)
    model: str | None = Field(default=None, max_length=100)


class QuestionRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=10000)
    model: str | None = Field(default=None, max_length=100)


class LearningPathRequest(BaseModel):
    topic: str = Field(..., min_length=1, max_length=500)
    level: str = Field(default="beginner", max_length=50)
    model: str | None = Field(default=None, max_length=100)


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")


@app.get("/health")
async def health():
    return {"status": "ok", "service": "EduGenie"}


@app.post("/qa")
async def qa(payload: QuestionRequest):
    try:
        return {"answer": answer_question(payload.question, model=payload.model)}
    except Exception as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@app.post("/explain")
async def explain(payload: TextRequest):
    try:
        return {"explanation": explain_topic(payload.text, model=payload.model)}
    except Exception as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@app.post("/quiz")
async def quiz(payload: TextRequest):
    try:
        return {"quiz": generate_quiz(payload.text, model=payload.model)}
    except Exception as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@app.post("/summarize")
async def summarize(payload: TextRequest):
    try:
        return {"summary": summarize_text(payload.text, model=payload.model)}
    except Exception as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@app.post("/learn/recommendations")
async def learning_recommendations(payload: LearningPathRequest):
    try:
        return {
            "recommendations": get_learning_recommendations(
                payload.topic, payload.level, model=payload.model
            )
        }
    except Exception as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

