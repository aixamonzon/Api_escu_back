from fastapi import FastAPI
from uvicorn import run
from routes.user import user
from routes.carrera import carrera_router
from routes.pago import pago
from routes.userCarrera import user_carrera_router
from fastapi.middleware.cors import CORSMiddleware

api_escu = FastAPI()


api_escu.include_router(user)
api_escu.include_router(carrera_router)
api_escu.include_router(pago)
api_escu.include_router(user_carrera_router)

api_escu.add_middleware(
   CORSMiddleware,
   allow_origins=["*"],
   allow_credentials=True,
   allow_methods=["GET", "POST", "PUT", "DELETE"],
   allow_headers=["*"],
)

