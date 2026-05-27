from dotenv import load_dotenv
import os
import uuid
from database import get_chat_history
from database import save_chat
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from fastapi.responses import RedirectResponse
from fastapi import Form
from database import create_user
from database import check_user
from starlette.middleware.sessions import SessionMiddleware
from openai import OpenAI
app = FastAPI()
load_dotenv()
# conversation_history = []
chat_sessions = {}
# app.add_middleware(SessionMiddleware, secret_key=os.getenv("SECRET_KEY"))
app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("SECRET_KEY")
)
client = OpenAI(
   api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1"
)

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")


class ChatRequest(BaseModel):
   message: str
   chat_id: str


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):

    if "user" not in request.session:

        return RedirectResponse(
            url="/login",
            status_code=303
        )

    chats = get_chat_history()

    chat_id = str(uuid.uuid4())

    chat_sessions[chat_id] = []

    return templates.TemplateResponse(

        request=request,

        name="index.html",

        context={
            "request": request,
            "chats": chats,
            "chat_id": chat_id
        }
    )
@app.get("/logout")
async def logout(request: Request):

    request.session.clear()

    return RedirectResponse(
        url="/login",
        status_code=303
    )
@app.post("/chat")
async def chat(request: ChatRequest):

    conversation_history = chat_sessions.get(
        request.chat_id,
        []
    )

    conversation_history.append({
        "role": "user",
        "content": request.message
    })

    response = client.chat.completions.create(

        model="openrouter/free",

        messages=conversation_history

    )

    ai_reply = response.choices[0].message.content

    conversation_history.append({
        "role": "assistant",
        "content": ai_reply
    })

    chat_sessions[request.chat_id] = conversation_history

    save_chat(
        request.message,
        ai_reply
    )

    return {
        "reply": ai_reply
    }
@app.get("/signup", response_class=HTMLResponse)
async def signup_page(request: Request):

  return templates.TemplateResponse(
    request=request,
    name="signup.html",
    context={
        "request": request
    }
)

@app.post("/signup")
async def signup(

    username: str = Form(...),
    password: str = Form(...)

):

    create_user(
        username,
        password
    )

    return RedirectResponse(
        url="/login",
        status_code=303
    )
@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):

   return templates.TemplateResponse(
    request=request,
    name="login.html",
    context={
        "request": request
    }
)

@app.post("/login")
async def login(

    request: Request,
    username: str = Form(...),
    password: str = Form(...)

):

    user = check_user(
        username,
        password
    )

    if user:

        request.session["user"] = username

        return RedirectResponse(
            url="/",
            status_code=303
        )

    return {
        "message": "Invalid credentials"
    }