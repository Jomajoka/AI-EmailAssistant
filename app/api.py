from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware
from fastapi.middleware.cors import CORSMiddleware
from app.database.db import init_db
from app.routers.process import router as process_router
from app.routers.data import router as data_router


def create_app():
    # Initialize database
    init_db()

    app = FastAPI()

    # Session Middleware (required for OAuth login state)
    app.add_middleware(
    SessionMiddleware,
    secret_key="dev-secret-change-this",
    same_site="lax",
    https_only=False
    )

    # CORS (required if frontend runs on different port later)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Import and register routers
    from app.auth.routes import router as auth_router
    app.include_router(auth_router)
    @app.get("/")
    def root():
        return {"message": "API v2 - OAuth Debug Build"}
    
    from app.auth.routes import router as auth_router
    from app.routers.sync import router as sync_router

    app.include_router(auth_router)
    app.include_router(sync_router)
    app.include_router(process_router)
    app.include_router(data_router)

    return app