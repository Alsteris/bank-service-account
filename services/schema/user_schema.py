from pydantic import BaseModel

class regisAccount(BaseModel):
    email : str = "lewishamilton44@gmail.com"
    password : str = "mercedesamg44"
    nik : str = "012390"
    nama_lengkap : str = "Max Verstappen"
    nomor_telepon: str = "08213819379"
    role : str = "user"

class regisUserDetail(BaseModel):
    email : str = "maxverstappen01@gmail.com"
    nik : str = "012390"
    nama_lengkap : str = "Max Verstappen"
    tanggal_lahir : str = " 1 Januari 1995"
    alamat : str = "Netherland"
    nomor_telepon: str = "08213819379"

class login(BaseModel):
    email : str = " "
    password : str = " "




