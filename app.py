from fastapi import FastAPI
from uvicorn import run
from routes.user import user
from routes.userDetail import userDetail
from fastapi.middleware.cors import CORSMiddleware

api_escu = FastAPI()


api_escu.include_router(user)
api_escu.include_router(userDetail)

api_escu.add_middleware(
   CORSMiddleware,
   allow_origins=["*"],
   allow_credentials=True,
   allow_methods=["GET", "POST", "PUT", "DELETE"],
   allow_headers=["*"],
)

