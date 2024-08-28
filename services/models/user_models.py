from sqlalchemy import Column, String, BigInteger, Text, DateTime, Integer, Numeric, Float
from datetime import datetime
from utils import Base
from pydantic import BaseModel
from sqlalchemy.orm import relationship



class Users(Base):
    __tablename__ = 'accounts'
    id = Column(BigInteger, primary_key=True)
    email = Column(String(50))
    password = Column(Text)
    nik = Column(String(50))
    nama_lengkap = Column(String(100))
    nomor_telepon = Column(String(13))
    nomor_rekening = Column(String(10), foreign_key=True)
    saldo = Column(Float, default =0.0)
    role = Column(String(5))
    create_at = Column(DateTime, default=datetime.now())


class Mutasi (Base):
    __tablename__ = 'mutasi'
    id = Column(BigInteger, primary_key=True)
    nomor_rekening = Column(String(10), index= True)
    jenis_transaksi = Column(String())
    tanggal_transaksi = Column(DateTime, default=datetime.now())
    nominal = Column(Float)
    saldo= Column(Float)
    keterangan = Column(String())


