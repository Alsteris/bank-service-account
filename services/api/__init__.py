from fastapi import APIRouter

from .user_api import *

api_router = APIRouter()

api_router.include_router(user_api.router, tags=['Daftar Akun'])
