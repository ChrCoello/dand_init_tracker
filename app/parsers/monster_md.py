"""Parse D&D 5e monster stat blocks from markdown files."""
from __future__ import annotations

import re
from pathlib import Path

from app.models import AbilityScores, Creature, CreatureType


def parse_monster_md(text: str) -> Creature:
    """Parse a markdown stat block into a Creature."""
    # Name from ## heading
    name_match = re.search(r"^##\s+(.+)$", text, re.MULTILINE)
    name = name_match.group(1).strip() if name_match else "Unknown"

    # AC
    ac_match = re.search(r"\*\*Armor Class:\*\*\s*(\d+)", text)
    ac = int(ac_match.group(1)) if ac_match else 10

    # HP (first number)
    hp_match = re.search(r"\*\*Hit Points:\*\*\s*(\d+)", text)
    hp = int(hp_match.group(1)) if hp_match else 1

    # Speed
    speed_match = re.search(r"\*\*Speed:\*\*\s*(.+?)(?:\n|$)", text)
    speed = speed_match.group(1).strip() if speed_match else "30 ft."

    # Ability scores from table row: | 12 (+1) | 15 (+2) | ...
    abilities = AbilityScores()
    score_row = re.search(
        r"^\|.*\(\s*[+-]\d+\s*\).*\|$", text, re.MULTILINE
    )
    if score_row:
        scores = [int(s) for s in re.findall(r"(\d+)\s*\([+-]", score_row.group())]
        if len(scores) == 6:
            abilities = AbilityScores(*scores)

    # Passive Perception
    pp_match = re.search(r"Passive Perception\s+(\d+)", text)
    passive = int(pp_match.group(1)) if pp_match else 10 + AbilityScores.modifier(abilities.wisdom)

    # Challenge Rating
    cr_match = re.search(r"\*\*Challenge:\*\*\s*([^\s(]+)", text)
    cr = cr_match.group(1).strip() if cr_match else ""

    # Traits (between ### Traits and ### Actions)
    traits = ""
    traits_match = re.search(
        r"###\s*Traits\s*\n(.*?)(?=###|$)", text, re.DOTALL
    )
    if traits_match:
        traits = traits_match.group(1).strip()

    # Actions (after ### Actions)
    actions = ""
    actions_match = re.search(r"###\s*Actions\s*\n(.*?)(?=###|$)", text, re.DOTALL)
    if actions_match:
        actions = actions_match.group(1).strip()

    return Creature(
        name=name,
        creature_type=CreatureType.MONSTER,
        armor_class=ac,
        max_hp=hp,
        speed=speed,
        abilities=abilities,
        initiative_modifier=AbilityScores.modifier(abilities.dexterity),
        passive_perception=passive,
        challenge_rating=cr,
        traits=traits,
        actions=actions,
    )


def load_all_monsters(assets_dir: Path) -> None:
    """Load all .md files from assets directory into monster library."""
    from app import state

    for md_file in assets_dir.glob("*_stats.md"):
        text = md_file.read_text()
        creature = parse_monster_md(text)
        state.monster_library[creature.name] = creature
