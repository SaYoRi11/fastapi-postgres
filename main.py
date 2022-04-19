from typing import List
from fastapi import FastAPI, status, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_login.exceptions import InvalidCredentialsException
from pydantic import BaseModel
from db import database, notes, users
from fastapi_login import LoginManager
import os
import datetime

class User(BaseModel):
    email: str

class UserDB(User):
    password: str

class NoteIn(BaseModel):
    text: str
    completed: bool

class Note(BaseModel):
    id: int
    text: str
    completed: bool

app = FastAPI(title="REST API using FastAPI PostgreSQL Async EndPoints")
manager = LoginManager('secretkey', token_url='/auth/token')
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

@manager.user_loader()
async def load_user(email: str):
    query = users.select().where(users.c.email == email)
    return await database.fetch_one(query)

@app.on_event("startup")
async def startup():
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

@app.post('/auth/token')
async def login(data: OAuth2PasswordRequestForm = Depends()):
    email = data.username
    password = data.password

    user = await load_user(email)
    if not user:
        raise InvalidCredentialsException
    elif password != user['password']:
        raise InvalidCredentialsException
    
    access_token = manager.create_access_token(
        data=dict(sub=email)
    )
    return {'access_token': access_token, 'token_type': 'bearer'}

@app.post('/register', response_model=User, status_code = status.HTTP_201_CREATED)
async def register(user: UserDB):
    query = users.insert().values(email=user.email, password=user.password)
    last_user_id = await database.execute(query)
    return {**user.dict(), "id": last_user_id}

@app.post("/notes/", response_model=Note, status_code = status.HTTP_201_CREATED)
async def create_note(note: NoteIn, user = Depends(manager)):
    query = notes.insert().values(text=note.text, completed=note.completed)
    last_record_id = await database.execute(query)
    return {**note.dict(), "id": last_record_id}

@app.put("/notes/{note_id}/", response_model=Note, status_code = status.HTTP_200_OK)
async def update_note(note_id: int, payload: NoteIn, user = Depends(manager)):
    query = notes.update().where(notes.c.id == note_id).values(text=payload.text, completed=payload.completed)
    await database.execute(query)
    return {**payload.dict(), "id": note_id}

@app.get("/notes/", response_model=List[Note], status_code = status.HTTP_200_OK)
async def read_notes(skip: int = 0, take: int = 20, user = Depends(manager)):
    query = notes.select().offset(skip).limit(take)
    return await database.fetch_all(query)

@app.get("/notes/{note_id}/", response_model=Note, status_code = status.HTTP_200_OK)
async def read_notes(note_id: int, user = Depends(manager)):
    query = notes.select().where(notes.c.id == note_id)
    return await database.fetch_one(query)

@app.delete("/notes/{note_id}/", status_code = status.HTTP_200_OK)
async def update_note(note_id: int, user = Depends(manager)):
    query = notes.delete().where(notes.c.id == note_id)
    await database.execute(query)
    return {"message": "Note with id: {} deleted successfully!".format(note_id)}