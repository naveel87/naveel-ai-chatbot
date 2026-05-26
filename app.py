from dotenv import load_dotenv
import os
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


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):

    if "user" not in request.session:

        return RedirectResponse(
            url="/login",
            status_code=303
        )

    chats = get_chat_history()

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "chats": chats
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

    response = client.chat.completions.create(
        model="openrouter/free",
        messages=[
            {
                "role": "user",
                "content": request.message
            }
        ]
    )

    ai_reply = response.choices[0].message.content

    # Save the chat to the database
    save_chat(request.message, ai_reply)
    
    return {
        "reply": ai_reply
    }
@app.get("/signup", response_class=HTMLResponse)
async def signup_page(request: Request):

    return templates.TemplateResponse(
        "signup.html",
        {
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
        "login.html",
        {
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