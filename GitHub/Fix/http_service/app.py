from fastapi import FastAPI

from http_service.routes import bonus_routes

app = FastAPI()

app.include_router(bonus_routes.router)