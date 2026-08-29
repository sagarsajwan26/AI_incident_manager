from fastapi import FastAPI, APIRouter
from app.routes.api.v1.router import router as apiRoutes

app = FastAPI(title="ai incidence manger")

router = APIRouter()


app.include_router(apiRoutes)


@router.get("/health")
def health():
    return {"health": "ok"}


app.include_router(router)
