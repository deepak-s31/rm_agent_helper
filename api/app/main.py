from fastapi import FastAPI
from .routers import crew as crew_router


def create_app() -> FastAPI:
    app = FastAPI(title="rm_agent_helper API", version="0.1.0")

    @app.get("/healthz")
    async def healthz() -> dict:
        return {"status": "ok"}

    app.include_router(crew_router.router, prefix="/crew", tags=["crew"])
    return app


app = create_app()


