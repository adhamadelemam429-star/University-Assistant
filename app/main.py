from __future__ import annotations

from fastapi import FastAPI

from app.api.routes import router
from app.config import settings


app = FastAPI(title=settings.app_name, version='1.0.0')
app.include_router(router)


@app.get('/')
def root() -> dict:
    return {'message': f'{settings.app_name} is running.', 'mode': settings.app_env}
