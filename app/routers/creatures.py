"""Routes for managing creature libraries (PC uploads, monster library)."""
from __future__ import annotations

from pathlib import Path
from tempfile import NamedTemporaryFile

from fastapi import APIRouter, Request, UploadFile
from fastapi.templating import Jinja2Templates

from app import state
from app.parsers.character_pdf import parse_character_pdf
from app.parsers.monster_md import parse_monster_md

router = APIRouter(prefix="/creatures", tags=["creatures"])
templates = Jinja2Templates(directory=Path(__file__).parent.parent / "templates")


@router.post("/upload-pc")
async def upload_pc(request: Request, file: UploadFile):
    """Upload a PC character sheet PDF."""
    content = await file.read()
    with NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        tmp.write(content)
        tmp_path = tmp.name

    try:
        creature = parse_character_pdf(tmp_path)
        state.pc_library[creature.name] = creature
    finally:
        Path(tmp_path).unlink(missing_ok=True)

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
