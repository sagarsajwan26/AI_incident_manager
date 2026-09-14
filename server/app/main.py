from fastapi import FastAPI, APIRouter
from app.routes.api.v1.router import router as apiRoutes
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="ai incidence manger")


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
router = APIRouter()


app.include_router(apiRoutes, prefix="/api/v1")


@router.get("/health")
def health():
    return {"health": "ok"}


app.include_router(router)
