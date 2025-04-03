from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes import auth_router

app = FastAPI(title="FastAPI RBAC Project", version="0.1.0")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router)
# app.include_router(organization_router)
