import uvicorn as uv
from fastapi import FastAPI

# import modul from another folder
from api import api_router
from utils import engine, settings, Base


# base standart default
app = FastAPI(
    title=settings.PROJECT_NAME,
    docs_url="/api/docs"
)

app.include_router(api_router, prefix="/api/v1")

async def startup():
    async with engine.begin() as conn:
        print("do migration data database ....")
        #await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

        print("do migration database done !....")

app.add_event_handler("startup", startup)

if __name__ == "__main__":
    uv.run(app, host="0.0.0.0") 