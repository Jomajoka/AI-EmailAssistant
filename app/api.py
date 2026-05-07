from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware
from fastapi.middleware.cors import CORSMiddleware
from app.database.db import init_db
from app.routers.process import router as process_router
from app.routers.data import router as data_router
from app.auth.routes import router as auth_router
from app.routers.sync import router as sync_router
from app.security.encryption import validate_encryption_config
import os

def create_app():
    validate_encryption_config()
    init_db()

    app = FastAPI()

    is_production = os.getenv("ENVIRONMENT") == "production"

    app.add_middleware(
        SessionMiddleware,
        secret_key=os.getenv("SECRET_KEY"),
        same_site="none" if is_production else "lax",
        https_only=is_production,
        max_age=3600
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:3000",
            os.getenv("FRONTEND_URL", "")
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/")
    def root():
        return {"message": "EmailAssist API"}

    app.include_router(auth_router)
    app.include_router(sync_router)
    app.include_router(process_router)
    app.include_router(data_router)

    return app  
