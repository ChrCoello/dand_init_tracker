"""Parse D&D 5e PC stat blocks from markdown files."""
from __future__ import annotations

import re
from pathlib import Path

from app.models import AbilityScores, Creature, CreatureType


def parse_character_md(text: str) -> Creature:
    """Parse a PC markdown stat block into a Creature."""
    # Name from ## heading
    name_match = re.search(r"^##\s+(.+)$", text, re.MULTILINE)
    name = name_match.group(1).strip() if name_match else "Unknown PC"

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

    # Initiative modifier (explicit for PCs — may differ from DEX mod)
    init_match = re.search(r"\*\*Initiative Modifier:\*\*\s*([+-]?\d+)", text)
    initiative = int(init_match.group(1)) if init_match else AbilityScores.modifier(abilities.dexterity)

    # Passive Perception
    pp_match = re.search(r"\*\*Passive Perception:\*\*\s*(\d+)", text)
    passive = int(pp_match.group(1)) if pp_match else 10 + AbilityScores.modifier(abilities.wisdom)

    return Creature(
        name=name,
        creature_type=CreatureType.PC,
        armor_class=ac,
        max_hp=hp,
        speed=speed,
        abilities=abilities,
        initiative_modifier=initiative,
        passive_perception=passive,
    )


def _extract_level(filename: str) -> int:
    """Extract level number from filename like 'penda_of_mercia_lvl2_stats.md'."""
    match = re.search(r"_lvl(\d+)_", filename)
    return int(match.group(1)) if match else 0


def load_all_pcs(pcs_dir: Path) -> None:
    """Load all .md files from pcs directory into PC library.

    When multiple files share the same character name (## heading),
    only the highest-level file is kept.
    """
    from app import state

    # Track the level loaded per character name
    loaded_levels: dict[str, int] = {}

    for md_file in pcs_dir.glob("*_stats.md"):
        level = _extract_level(md_file.name)
        text = md_file.read_text()
        creature = parse_character_md(text)

        if creature.name not in loaded_levels or level > loaded_levels[creature.name]:
            state.pc_library[creature.name] = creature
            loaded_levels[creature.name] = level
