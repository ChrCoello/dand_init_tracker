"""Routes for encounter setup and combat management."""
from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app import state
from app.models import Encounter
from app.models import CreatureType
from app.services.combat import (
    apply_damage,
    apply_healing,
    next_turn,
    prev_turn,
    roll_monster_initiative,
    start_combat,
    set_temp_hp,
    update_death_save,
)

router = APIRouter(tags=["encounter"])
templates = Jinja2Templates(directory=Path(__file__).parent.parent / "templates")


@router.post("/encounter/add-pc")
async def add_pc(request: Request, pc_name: str = Form(...)):
    """Add a PC from library to the encounter."""
    if pc_name in state.pc_library:
        creature = state.pc_library[pc_name].copy()
        state.encounter.creatures.append(creature)

    return templates.TemplateResponse(
        "partials/encounter_creatures.html",
        {"request": request, "encounter": state.encounter},
    )


@router.post("/encounter/add-monster")
async def add_monster(
    request: Request,
    monster_name: str = Form(...),
    count: int = Form(1),
):
    """Add monsters from library to the encounter."""
    if monster_name in state.monster_library:
        template = state.monster_library[monster_name]
        for i in range(min(count, 20)):  # cap at 20
            creature = template.copy()
            if count > 1:
                creature.name = f"{template.name} {i + 1}"
            state.encounter.creatures.append(creature)

    return templates.TemplateResponse(
        "partials/encounter_creatures.html",
        {"request": request, "encounter": state.encounter},
    )


@router.post("/encounter/remove/{creature_id}")
async def remove_creature(request: Request, creature_id: str):
    """Remove a creature from the encounter."""
    state.encounter.creatures = [
        c for c in state.encounter.creatures if c.id != creature_id
    ]
    if state.encounter.is_active:
        return templates.TemplateResponse(
            "partials/creature_list.html",
            {"request": request, "encounter": state.encounter},
        )
    return templates.TemplateResponse(
        "partials/encounter_creatures.html",
        {"request": request, "encounter": state.encounter},
    )


@router.post("/encounter/roll-initiative")
async def roll_initiative(request: Request):
    """Show the initiative modal for PC rolls."""
    if not state.encounter.creatures:
        return HTMLResponse("<p>No creatures in encounter!</p>")
    return templates.TemplateResponse(
        "partials/initiative_modal.html",
        {"request": request, "encounter": state.encounter},
    )


@router.post("/encounter/start-combat")
async def start_combat_route(request: Request):
    """Process PC initiative inputs, roll for monsters, and start combat."""
    form = await request.form()

    # Apply PC initiative rolls from the form
    for creature in state.encounter.creatures:
        if creature.creature_type == CreatureType.PC:
            raw = form.get(f"roll_{creature.id}")
            is_total = form.get(f"total_{creature.id}")
            if raw is not None:
                value = int(raw)
                if is_total:
                    creature.initiative_roll = value
                else:
                    creature.initiative_roll = value + creature.initiative_modifier

    # Roll for monsters
    roll_monster_initiative(state.encounter)

    # Start combat
    start_combat(state.encounter)

    return templates.TemplateResponse(
        "encounter/tracker.html",
        {"request": request, "encounter": state.encounter},
    )


@router.post("/encounter/next-turn")
async def advance_turn(request: Request):
    """Advance to next turn."""
    next_turn(state.encounter)
    return templates.TemplateResponse(
        "partials/creature_list.html",
        {"request": request, "encounter": state.encounter},
    )


@router.post("/encounter/prev-turn")
async def go_back_turn(request: Request):
    """Go back one turn."""
    prev_turn(state.encounter)
    return templates.TemplateResponse(
        "partials/creature_list.html",
        {"request": request, "encounter": state.encounter},
    )


@router.post("/encounter/damage/{creature_id}")
async def damage_creature(
    request: Request, creature_id: str, amount: int = Form(0)
):
    """Apply damage to a creature."""
    apply_damage(state.encounter, creature_id, amount)
    return templates.TemplateResponse(
        "partials/creature_card.html",
        {
            "request": request,
            "creature": state.encounter.get_creature(creature_id),
            "encounter": state.encounter,
        },
    )


@router.post("/encounter/heal/{creature_id}")
async def heal_creature(
    request: Request, creature_id: str, amount: int = Form(0)
):
    """Heal a creature."""
    apply_healing(state.encounter, creature_id, amount)
    return templates.TemplateResponse(
        "partials/creature_card.html",
        {
            "request": request,
            "creature": state.encounter.get_creature(creature_id),
            "encounter": state.encounter,
        },
    )


@router.post("/encounter/temp-hp/{creature_id}")
async def temp_hp(
    request: Request, creature_id: str, amount: int = Form(0)
):
    """Set temporary HP."""
    set_temp_hp(state.encounter, creature_id, amount)
    return templates.TemplateResponse(
        "partials/creature_card.html",
        {
            "request": request,
            "creature": state.encounter.get_creature(creature_id),
            "encounter": state.encounter,
        },
    )


@router.post("/encounter/death-save/{creature_id}")
async def death_save(
    request: Request,
    creature_id: str,
    save_type: str = Form(...),
    value: int = Form(...),
):
    """Update death save."""
    update_death_save(state.encounter, creature_id, save_type, value)
    return templates.TemplateResponse(
        "partials/creature_card.html",
        {
            "request": request,
            "creature": state.encounter.get_creature(creature_id),
            "encounter": state.encounter,
        },
    )


@router.post("/encounter/set-initiative/{creature_id}")
async def set_initiative(
    request: Request, creature_id: str, value: int = Form(...)
):
    """Manually set a creature's initiative roll."""
    creature = state.encounter.get_creature(creature_id)
    if creature:
        creature.initiative_roll = value
    return templates.TemplateResponse(
        "partials/creature_list.html",
        {"request": request, "encounter": state.encounter},
    )


@router.post("/encounter/reset")
async def reset_encounter(request: Request):
    """End combat and reset the encounter."""
    state.encounter = Encounter()
    return templates.TemplateResponse(
        "encounter/setup.html",
        {
            "request": request,
            "monster_library": state.monster_library,
            "pc_library": state.pc_library,
            "encounter": state.encounter,
        },
    )
