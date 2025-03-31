import uvicorn
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from app.api import routers
import uuid
from app.services.database_service import database_service
from datetime import datetime

app = FastAPI()

@app.middleware("http")
async def add_user_id_header(request: Request, call_next):
    existing_user_id = request.headers.get("userid")  # FastAPI normalizes header names to lowercase
    if not existing_user_id:
        _id = await database_service.insert_one("users", { "created_at": str(datetime.utcnow())})
        request.scope["headers"] = [
            (name, value) for name, value in request.scope["headers"]
            if name.lower() != b"userid"
        ] + [(b"userid", str(_id).encode())]

        response = await call_next(request)
        response.headers["x-user-id"] = str(_id)
        return response
    return await call_next(request)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
    expose_headers=["x-user-id"],  # Expose custom header
)

app.include_router(routers.router, prefix='/api')

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)