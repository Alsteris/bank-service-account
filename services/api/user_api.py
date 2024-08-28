from fastapi import Depends, FastAPI, HTTPException, status, APIRouter, Header, Query
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import NoResultFound
from security import decode_access_token
from security.auth import JWTBearer
from jose import JWTError
from security import token_blacklist, decode_access_token


from app import user_crud, verify_nomorRekening
from utils import RespApp, get_async_session
from schema import regisAccount, login



router = APIRouter()


@router.post("/regis-new-account")
async def RegistNewAccount(
    request: regisAccount,
    db: AsyncSession = Depends(get_async_session)
    ):
    out_resp, e = await user_crud.create_new_account(request, db)
    if e != None:
        return RespApp(status="400", message=f"{e}", data=None)
    
    return RespApp(status="200", message="Berhasil registrasi akun", data=out_resp)

@router.post("/login")
async def LoginAccount(
    request: login,
    db: AsyncSession = Depends(get_async_session)
    ):
    out_resp, e = await user_crud.login_user(request, db)
    if e != None:
        return RespApp(status="400", message=f"{e}", data=None)
    
    return RespApp(status="200", message="success", data=out_resp)

@router.post("/transaksi")
async def Tabung(token: str = Depends(JWTBearer()),
                pilih_transaksi: str = Query(enum=["Setor Tunai", "Tarik Tunai", "Transfer"]),
                Nominal: float = "masukkan nominal",
                rekening_tujuan: str = "masukkan rekening tujuan",
                db: AsyncSession = Depends(get_async_session)):
    try:
        out_resp, e = await user_crud.transaksi_rekening(token, pilih_transaksi, Nominal, db, rekening_tujuan)
        if e:
            return RespApp(status="400", message=f"{e}", data=None)
        
        return RespApp(status="200", message=f"Anda telah melakukan transaksi {pilih_transaksi}", data=out_resp)
    
    
    except Exception as e:
        return RespApp(status="400", message=f"{e}", data=None)


    
@router.get("/saldo/{no_rekening}")
async def get_saldo(token: str = Depends(JWTBearer()), db_session: AsyncSession = Depends(get_async_session)):
    try:
        saldo, e = await user_crud.cek_saldo(token, db_session)
        if e:
            return RespApp(status="400", message=f"{e}", data=None)
    
        return RespApp(status="200", message=f"Saldo anda sekarang: {saldo}", data=saldo)

    except Exception as e:
            return RespApp(status="400", message=f"{e}", data=None)

@router.get("/mutasi/{no_rekening}")
async def get_mutasi(token: str = Depends(JWTBearer()), db_session: AsyncSession = Depends(get_async_session)):
    try:
        saldo, e = await user_crud.cek_mutasi(token, db_session)
        if e:
            return RespApp(status="400", message=f"{e}", data=None)
    
        return RespApp(status="200", message=f"Success", data=saldo)

    except Exception as e:
            return RespApp(status="400", message=f"{e}", data=None)

@router.post("/logout")
async def logout(token: str = Depends(JWTBearer())):
    try:
        token_blacklist.add(token)
        return RespApp(status="200", message="Logout successful. Token invalidated.", data=None)
    except Exception as e:
        return RespApp(status="400", message=f"{e}", data=None)
