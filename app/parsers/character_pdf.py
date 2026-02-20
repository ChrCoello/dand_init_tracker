"""Parse D&D 5e character sheets from fillable PDF files."""
from __future__ import annotations

from pathlib import Path

from pypdf import PdfReader

from app.models import AbilityScores, Creature, CreatureType


def _get_field(fields: dict, *names: str, default: str = "") -> str:
    """Try multiple field names, return first non-empty value."""
    for name in names:
        if name in fields:
            val = fields[name].get("/V", "")
            if val and str(val).strip():
                return str(val).strip()
    return default


def _parse_int(value: str, default: int = 0) -> int:
    """Parse an integer from a string, handling +/- prefixes and parens."""
    if not value:
        return default
    # Handle formats like "9(-1)", "+2", "14"
    cleaned = value.split("(")[0].strip().lstrip("+")
    try:
        return int(cleaned)
    except ValueError:
        return default


def parse_character_pdf(pdf_path: str | Path) -> Creature:
    """Parse a fillable PDF character sheet into a Creature."""
    reader = PdfReader(str(pdf_path))
    fields = reader.get_fields() or {}

    name = _get_field(fields, "CharacterName", "CharacterName 2") or "Unknown PC"

    # Ability scores - field names are uppercase abbreviations
    str_val = _parse_int(_get_field(fields, "STR"), 10)
    dex_val = _parse_int(_get_field(fields, "DEX"), 10)
    con_val = _parse_int(_get_field(fields, "CON"), 10)
    int_val = _parse_int(_get_field(fields, "INT"), 10)
    wis_val = _parse_int(_get_field(fields, "WIS"), 10)
    cha_val = _parse_int(_get_field(fields, "CHA"), 10)

    # STRmod field sometimes has the score instead (e.g. "9(-1)")
    # If STR is empty but STRmod has the score, extract it
    if str_val == 10:
        strmod_raw = _get_field(fields, "STRmod")
        if strmod_raw:
            str_val = _parse_int(strmod_raw, 10)

    abilities = AbilityScores(str_val, dex_val, con_val, int_val, wis_val, cha_val)

    ac = _parse_int(_get_field(fields, "AC"), 10)
    max_hp = _parse_int(_get_field(fields, "HPMax"), 1)
    speed = _get_field(fields, "Speed", default="30 ft.")
    initiative = _parse_int(_get_field(fields, "Initiative"), AbilityScores.modifier(dex_val))
    passive = _parse_int(_get_field(fields, "Passive"), 10 + AbilityScores.modifier(wis_val))

    return Creature(
        name=name,
        creature_type=CreatureType.PC,
        armor_class=ac,
        max_hp=max_hp,
        speed=speed,
        abilities=abilities,
        initiative_modifier=initiative,
        passive_perception=passive,
    )
