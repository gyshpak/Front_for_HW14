from fastapi import FastAPI, Form, HTTPException, Header, Request, Depends, status
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
import httpx

app = FastAPI()

# Підключення папки зі статичними файлами (стилі, скрипти)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Підключення папки з шаблонами Jinja2
templates = Jinja2Templates(directory="templates")

base_url = "https://web-hw13.onrender.com/api"  # URL локального сервера FastAPI


# Базовий шаблон з кнопками для запуску різних функцій
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("base.html", {"request": request})


@app.get("/signup", response_class=HTMLResponse)
async def signup_form(request: Request):
    return templates.TemplateResponse("signup.html", {"request": request})


# Функція реєстрації нового користувача
@app.post("/signup")
async def signup_user(
    request: Request,
    name: str = Form(...),
    email: str = Form(...),
    phone: str = Form(...),
    birthday: str = Form(...),
    password: str = Form(...),
):
    data = {
        "name": name,
        "email": email,
        "phone": phone,
        "birthday": birthday,
        "password": password,
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(f"{base_url}/auth/signup", json=data)
            response.raise_for_status()  # Перевірка статусу відповіді
            return {"message": "User registered successfully", "data": response.json()}
        except httpx.HTTPStatusError as e:
            raise Exception(f"Registration failed: {e}")


@app.get("/login", response_class=HTMLResponse)
async def login_form(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


# Функція входу користувача
@app.post("/login", response_class=HTMLResponse)
async def login_user(
    request: Request, username: str = Form(...), password: str = Form(...)
):
    data = {"username": username, "password": password}
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(f"{base_url}/auth/login", data=data)
            response.raise_for_status()
            tokens = response.json()

            # Передача токенів через HTTP заголовок
            access_token = tokens["access_token"]
            headers = {"Authorization": f"Bearer {access_token}"}
            ##########################
            # Виконати GET запит на /contacts з токеном авторизації
            response_contacts = await client.get(
                f"{base_url}/contacts", headers=headers, follow_redirects=True
            )
            response_contacts.raise_for_status()
            contacts = response_contacts.json()

            return templates.TemplateResponse(
                "contacts.html", {"request": request, "contacts": contacts}
            )
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to fetch contacts: {e}")

#############################
#     return RedirectResponse(url="/contacts", headers=headers)
#     # return templates.TemplateResponse("login.html",{"request": request, "message": f"Login successful {access_token}"},)
# except httpx.HTTPStatusError as e:
#     return templates.TemplateResponse(
#         "login.html",
#         {"request": request, "error_message": f"Login failed: {e}"},
#     )


# Функція отримання списку контактів
# @app.get("/contacts", response_class=JSONResponse)
# async def get_contacts(request: Request, authorization: str = Header(None)):
#     if not authorization or not authorization.startswith("Bearer "):
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Invalid authorization header",
#         )

#     access_token = authorization.split(" ")[1]

#     async with httpx.AsyncClient() as client:
#         try:
#             headers = {"Authorization": f"Bearer {access_token}"}
#             response = await client.get(f"{base_url}/contacts/", headers=headers)
#             response.raise_for_status()  # Перевірка статусу відповіді
#             contacts = response.json()

#             return contacts
#             # return templates.TemplateResponse(
#             #     "contacts.html", {"request": request, "contacts": contacts}
#             # )
#         except httpx.HTTPStatusError as e:
#             raise HTTPException(
#                 status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#                 detail=f"Failed to fetch contacts: {e}",
#             )


# @app.get("/contacts", response_class=HTMLResponse)
# async def get_contacts(authorization: str = Depends()):
#     if not authorization or not authorization.startswith("Bearer "):
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authorization header")

#     access_token = authorization.split(" ")[1]

#     async with httpx.AsyncClient() as client:
#         try:
#             response = await client.get(f"{base_url}/contacts/")
#             response.raise_for_status()  # Перевірка статусу відповіді
#             return {"message": "Contacts fetched successfully", "data": response.json()}
#         except httpx.HTTPStatusError as e:
#             raise Exception(f"Failed to fetch contacts: {e}")


#     # Тут має бути ваша логіка для використання access_token у запиті до захищеного ендпоінту (наприклад, /contacts)

#     return {"message": "Contacts retrieved successfully"}
