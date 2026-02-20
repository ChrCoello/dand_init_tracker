from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.parsers.monster_md import load_all_monsters
from app.routers import creatures, encounter

APP_DIR = Path(__file__).parent
ASSETS_DIR = APP_DIR.parent / "assets"

app = FastAPI(title="D&D Initiative Tracker")
app.mount("/static", StaticFiles(directory=APP_DIR / "static"), name="static")

templates = Jinja2Templates(directory=APP_DIR / "templates")

app.include_router(encounter.router)
app.include_router(creatures.router)


@app.on_event("startup")
async def startup() -> None:
    load_all_monsters(ASSETS_DIR)


@app.get("/")
async def index(request: Request):
    from app import state

    return templates.TemplateResponse(
        "encounter/setup.html",
        {
            "request": request,
            "monster_library": state.monster_library,
            "pc_library": state.pc_library,
            "encounter": state.encounter,
        },
    )
