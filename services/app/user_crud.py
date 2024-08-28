from sqlalchemy.ext.asyncio import AsyncSession
from datastore import user_datastore
from schema import regisAccount, user_schema
from fastapi import FastAPI, Depends, HTTPException, status
from models import user_models
from security import verify_password, create_access_token
from datetime import timedelta

async def create_new_account(data: regisAccount, db_session:AsyncSession):
    async with db_session as session:
        try:  
            if data.email == "" :
                raise Exception("email harus di isi")
            
            if data.password == "" :
                raise Exception("password harus di isi")
        
            if data.nik == "" :
                raise Exception("nik harus di isi")

            if data.nama_lengkap == "" :
                raise Exception("nama lengkap harus di isi")

            if data.nomor_telepon == "" :
                raise Exception("nomor telepom harus di isi")

            if data.role == "" :
                raise Exception("role harus di isi")
            
            verify_email,e = await user_datastore.GetUserDetailByEmail(data.email, session)
            verify_nomor_telepon,e = await user_datastore.GetUserDetailByNoTelepon(data.nomor_telepon, session)
            verify_nik,e = await user_datastore.GetUserDetailByNik(data.nik, session)
            if verify_email or verify_nomor_telepon or verify_nik not in (None,{}):
                raise Exception("Email/Nomor Telepon/Nik sudah digunakan! silahkan masukkan data yang baru")

            resCreateAccount, e = await user_datastore.registNewAccount(data, session)
            if e != None:
                raise Exception(f"{e}")
            
            await session.commit()
            

            return resCreateAccount, None


        except Exception as e:
            return data, e
        
async def login_user(data: user_schema.login, db_session: AsyncSession):
    async with db_session as session:
        try:
            # Fetch user by email
            user, e = await user_datastore.GetUserDetailByEmail(data.email, session)
            if user is None or not verify_password(data.password, user.password):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="password atau email salah!",
                    headers={"WWW-Authenticate": "Bearer"},
                )

            # Create JWT token
            access_token_expires = timedelta(minutes=30)
            access_token = create_access_token(
                data={"sub": user.email, "nomor_rekening": user.nomor_rekening}, expires_delta=access_token_expires
            )

            return {"access_token": access_token, "token_type": "bearer"}, None

        except Exception as e:
            return None, e


async def get_list_user_detail_by_email(keyword:str, db_session:AsyncSession):
    async with db_session as session:
        try:  

            resgetUserDetailByEmail, e = await user_datastore.GetUserDetailByEmail(keyword, session)
            if e != None:
                raise Exception(f"{e}")
            
            await session.commit()

            return resgetUserDetailByEmail, None


        except Exception as e:
            return None, e


async def verify_nomorRekening(keyword:str, db_session:AsyncSession):
    async with db_session as session:
        try:  

            resgetUserNomorRekening, e = await user_datastore.GetUserNomorRekening(keyword, session)
            if e != None:
                raise Exception(f"{e}")
            
            await session.commit()

            return resgetUserNomorRekening, None


        except Exception as e:
            return None, e
        
async def transaksi_rekening(token: str, jenis_transaksi: str, saldo: float, db_session: AsyncSession, rekening_tujuan: None):
    async with db_session as session:
        try:
            resTransaksi, e = await user_datastore.transaksiRekening(token, jenis_transaksi, saldo, session, rekening_tujuan)
            if e is not None:
                raise Exception(f"{e}")
            
            await session.commit()

            return resTransaksi, None

        except Exception as e:
            await session.rollback()
            return None, e

async def cek_saldo(token: str, db_session: AsyncSession):
    async with db_session as session:
        try:
            resCekSaldo, e = await user_datastore.cekSaldo(token, session)
            if e is not None:
                raise Exception(f"{e}")
            
            await session.commit()

            return resCekSaldo, None

        except Exception as e:
            await session.rollback()
            return None, e
        
async def cek_mutasi(token: str, db_session: AsyncSession):
    async with db_session as session:
        try:
            resCekMutasi, e = await user_datastore.cek_mutasi(token, session)
            if e is not None:
                raise Exception(f"{e}")
            
            await session.commit()

            return resCekMutasi, None

        except Exception as e:
            await session.rollback()
            return None, e