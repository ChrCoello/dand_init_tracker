"""Routes for managing creature libraries (PC uploads, monster library)."""
from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, Request, UploadFile
from fastapi.templating import Jinja2Templates

from app import state
from app.parsers.character_md import parse_character_md
from app.parsers.monster_md import parse_monster_md

router = APIRouter(prefix="/creatures", tags=["creatures"])
templates = Jinja2Templates(directory=Path(__file__).parent.parent / "templates")


@router.post("/upload-pc")
async def upload_pc(request: Request, file: UploadFile):
    """Upload a PC stat block markdown file."""
    content = (await file.read()).decode("utf-8")
    creature = parse_character_md(content)
    state.pc_library[creature.name] = creature

    return templates.TemplateResponse(
        "partials/library_lists.html",
        {
            "request": request,
            "pc_library": state.pc_library,
            "monster_library": state.monster_library,
        },
    )



@router.post("/upload-monster")
async def upload_monster(request: Request, file: UploadFile):
    """Upload a monster stat block markdown file."""
    content = (await file.read()).decode("utf-8")
    creature = parse_monster_md(content)
    state.monster_library[creature.name] = creature

    return templates.TemplateResponse(
        "partials/library_lists.html",
        {
            "request": request,
            "pc_library": state.pc_library,
            "monster_library": state.monster_library,
        },
    )
