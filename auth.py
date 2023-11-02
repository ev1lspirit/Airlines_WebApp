from jose import JWTError, jwt
from db import Connector
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi import Depends, HTTPException, status, APIRouter
from pydantic import BaseModel
from typing import Annotated
from additional import make_json
import uuid


SECRET_KEY = uuid.uuid4().hex
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 120

auth_router = APIRouter(prefix="/auth", tags=["auth"])
connector = Connector.get(dbase="WebAirlines")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")


class CreateUserRequest(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str
