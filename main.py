from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import ALLOWED_ORIGINS
from routes import (
    auth_router,
    product_router,
    customer_router,
    invoice_router,
)

app = FastAPI(
    title="Ifiasoft ERP APIs",
    version="0.1.0",
    description="API endpoints for Ifiasoft ERP system",
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router)
app.include_router(product_router)
app.include_router(customer_router)
app.include_router(invoice_router)


# Root endpoint
@app.get("/")
def read_root():
    return {
        "name": "Ifiasoft ERP API",
        "version": "0.1.0",
    }
