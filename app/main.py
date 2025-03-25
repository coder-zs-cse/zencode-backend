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
    if not request.headers.get("userId"):
        user_id = str(uuid.uuid4())
        await database_service.insert_one("users", {"_id": user_id, "created_at": str(datetime.utcnow())})
        request.headers.__dict__["_list"].append(
            (b"userId", user_id.encode())
        )
        response = await call_next(request)
        response.headers["x-user-id"] = user_id
        return response
    return await call_next(request)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

app.include_router(routers.router, prefix='/api')

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)