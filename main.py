from fastapi import FastAPI
from routes import auth_routes, user_routes, contact_routes

app = FastAPI()

app.include_router(auth_routes.router)
app.include_router(user_routes.router)
app.include_router(contact_routes.router)