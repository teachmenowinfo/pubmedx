from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.api.routes.home import router as home_router
from app.utils.paths import get_static_dir


app = FastAPI(title="pubmedx")


app.mount("/static", StaticFiles(directory=str(get_static_dir())), name="static")


app.include_router(home_router)


