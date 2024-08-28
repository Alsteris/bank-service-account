from models import user_models
from sqlalchemy.orm import Session
from fastapi import HTTPException
from sqlalchemy import select, or_, and_, update, delete
from api import user_api
from datetime import timedelta
from security import get_password_hash, create_access_token, decode_access_token
from sqlalchemy.exc import NoResultFound
import random

async def registNewAccount(data, session):
    try:
        generate_nomorRekening = str(random.randint(1000000000, 9999999999))
        hashed_password = get_password_hash(data.password)
        paramsInsert = user_models.Users(
            email = data.email,
            password=hashed_password,
            nik = data.nik,
            nama_lengkap = data.nama_lengkap,
            nomor_telepon = data.nomor_telepon,
            nomor_rekening = generate_nomorRekening,
            role = data.role
        )

        session.add(paramsInsert)
        session.commit()
        session.refresh(paramsInsert)
        # Create a JWT token for the new user
        access_token = create_access_token(
            data={"sub": paramsInsert.email, "role": paramsInsert.role}, expires_delta=timedelta(minutes=30)
        )
        
        return {"user": paramsInsert, "access_token": access_token, "token_type": "bearer"}, None

    except Exception as e:
        session.rollback()
        return None, e
    

async def GetUserDetailByEmail(keyword, session):
    try:
        sql = select(user_models.Users).where(user_models.Users.email == keyword)
        proxy_rows = await session.execute(sql)
        data = proxy_rows.scalars().first()
        
        return data, None
    except Exception as e:
        return None, e

async def GetUserDetailByNik(keyword, session):
    try:
        sql = select(user_models.Users).where(user_models.Users.nik == keyword)
        proxy_rows = await session.execute(sql)
        data = proxy_rows.scalars().first()
        
        return data, None
    except Exception as e:
        return None, e

async def GetUserDetailByNoTelepon(keyword, session):
    try:
        sql = select(user_models.Users).where(user_models.Users.nomor_telepon == keyword)
        proxy_rows = await session.execute(sql)
        data = proxy_rows.scalars().first()
        
        return data, None
    except Exception as e:
        return None, e

async def GetUserNomorRekening(keyword, session):
    try:
        sql = select(user_models.Users).where(user_models.Users.nomor_rekening == keyword)
        proxy_rows = await session.execute(sql)
        data = proxy_rows.scalars().first()
        
        return data, None
    except Exception as e:
        return None, e

async def transaksiRekening(token, pilih_transaksi, Nominal, session, rekening_tujuan=None):
    try:
        access_token = decode_access_token(token)
        nomor_rekening = access_token["nomor_rekening"]
        
        # Unpack the result from GetUserNomorRekening
        cek_nomor_rekening, error = await GetUserNomorRekening(nomor_rekening, session)
        
        if error:
            return {"error": error}, None
        
        if not cek_nomor_rekening:
            return {"error": "nomor rekening tidak ditemukan"}, None
        
        #Transaksi setor tunai
        if pilih_transaksi == "Setor Tunai":
            cek_nomor_rekening.saldo += Nominal
            await session.commit()
            await session.refresh(cek_nomor_rekening)

            await simpan_mutasi(nomor_rekening, "Setor Tunai", Nominal, cek_nomor_rekening.saldo, session)
            
            return {"message": "Setor tunai berhasil", "saldo anda sekarang": cek_nomor_rekening.saldo}, None

        #Transaksi tarik tunai
        if pilih_transaksi == "Tarik Tunai":
            if cek_nomor_rekening.saldo < 20000:
                return {"error": "Saldo tidak mencukupi untuk penarikan tunai. Minimal saldo yang harus tersisa di rekening adalah 20.000.","Saldo anda saat ini":cek_nomor_rekening.saldo }, None
    
            cek_nomor_rekening.saldo -= Nominal
            await session.commit()
            await session.refresh(cek_nomor_rekening)

            await simpan_mutasi(nomor_rekening, "Tarik Tunai", Nominal, cek_nomor_rekening.saldo, session)
            
            return {"message": "Tarik tunai berhasil", "saldo anda sekarang": cek_nomor_rekening.saldo}, None

        #Transaksi transfer
        if pilih_transaksi == "Transfer":
            if cek_nomor_rekening.saldo < Nominal:
                return {"error": "Saldo tidak mencukupi untuk transfer. Saldo anda saat ini: {}".format(cek_nomor_rekening.saldo)}, None
            
            if rekening_tujuan is None:
                return {"error": "Rekening tujuan harus diisi untuk transfer"}, None
            
            if nomor_rekening == rekening_tujuan:
                return {"error": "Tidak dapat melakukan transfer ke rekening yang sama"}, None
            
            # Cek rekening tujuan
            rekening_tujuan_data, error_tujuan = await GetUserNomorRekening(rekening_tujuan, session)
            if error_tujuan:
                return {"error": error_tujuan}, None

            if not rekening_tujuan_data:
                return {"error": "Rekening tujuan tidak ditemukan"}, None

            # Lakukan transfer
            cek_nomor_rekening.saldo -= Nominal
            rekening_tujuan_data.saldo += Nominal

            await session.commit()

            # Simpan mutasi untuk pengirim
            await simpan_mutasi(nomor_rekening, "Transfer Keluar", Nominal, cek_nomor_rekening.saldo, session)

            # Simpan mutasi untuk penerima
            await simpan_mutasi(rekening_tujuan, "Transfer Masuk", Nominal, rekening_tujuan_data.saldo, session)

            return {"message": "Transfer berhasil", "saldo anda sekarang": cek_nomor_rekening.saldo}, None


        else:
            return {"error": "Jenis transaksi tidak valid"}, None

    except NoResultFound:
        return {"error": "Nomor rekening tidak ditemukan"}, None
    except Exception as e:
        await session.rollback()
        return None, str(e)
    

async def cekSaldo(token, session):
    access_token = decode_access_token(token)
    nomor_rekening = access_token["nomor_rekening"]
    cek_nomor_rekening, error = await GetUserNomorRekening(nomor_rekening, session)
    if error:
        return None, error
    
    if not cek_nomor_rekening:
        return None, "Nomor rekening tidak ditemukan"

    return cek_nomor_rekening.saldo, None

async def simpan_mutasi(nomor_rekening: str, jenis_transaksi: str, nominal: float, saldo: float, session):
    mutasi = user_models.Mutasi(
        nomor_rekening=nomor_rekening,
        jenis_transaksi=jenis_transaksi,
        nominal=nominal,
        saldo=saldo,
        keterangan = f"Berhasil {jenis_transaksi}"
    )
    session.add(mutasi)
    await session.commit()
    await session.refresh(mutasi)

async def cek_mutasi(token: str, session):
    try:
        access_token = decode_access_token(token)
        nomor_rekening = access_token["nomor_rekening"]
        
        sql = select(user_models.Mutasi).where(user_models.Mutasi.nomor_rekening == nomor_rekening)
        proxy_rows = await session.execute(sql)
        data = proxy_rows.scalars().all()

        return data, None
    except Exception as e:
        return None, e

async def DeleteAccount(email, session) :
    try:
        sql =(
        delete(user_models.Users)
        .where(user_models.Users.email == email)
        )
        await session.execute(sql)
        await session.commit()
        
        return email, None
    except Exception as e:
        return None, e
    

