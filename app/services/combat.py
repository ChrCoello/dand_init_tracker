"""Combat management: initiative, turns, HP logic."""
from __future__ import annotations

from app.models import CreatureType, Encounter
from app.services.dice import roll_d20


def roll_monster_initiative(encounter: Encounter) -> None:
    """Roll initiative for monsters only (PCs are set manually)."""
    for creature in encounter.creatures:
        if creature.creature_type == CreatureType.MONSTER:
            creature.initiative_roll = roll_d20() + creature.initiative_modifier


def start_combat(encounter: Encounter) -> None:
    """Start combat after all initiative values are set."""
    encounter.round_number = 1
    encounter.is_active = True
    order = encounter.initiative_order
    if order:
        encounter.current_creature_id = order[0].id


def next_turn(encounter: Encounter) -> None:
    """Advance to the next creature in initiative order."""
    if not encounter.is_active:
        return
    order = encounter.initiative_order
    if not order:
        return

    current_idx = 0
    for i, c in enumerate(order):
        if c.id == encounter.current_creature_id:
            current_idx = i
            break

    next_idx = (current_idx + 1) % len(order)
    if next_idx <= current_idx:
        encounter.round_number += 1

    encounter.current_creature_id = order[next_idx].id


def prev_turn(encounter: Encounter) -> None:
    """Go back to the previous creature in initiative order."""
    if not encounter.is_active:
        return
    order = encounter.initiative_order
    if not order:
        return

    current_idx = 0
    for i, c in enumerate(order):
        if c.id == encounter.current_creature_id:
            current_idx = i
            break

    prev_idx = (current_idx - 1) % len(order)
    if prev_idx >= current_idx and encounter.round_number > 1:
        encounter.round_number -= 1

    encounter.current_creature_id = order[prev_idx].id


def apply_damage(encounter: Encounter, creature_id: str, amount: int) -> None:
    """Apply damage to a creature, consuming temp HP first."""
    creature = encounter.get_creature(creature_id)
    if creature is None or amount <= 0:
        return

    remaining = amount
    if creature.temp_hp > 0:
        absorbed = min(creature.temp_hp, remaining)
        creature.temp_hp -= absorbed
        remaining -= absorbed

    creature.current_hp = max(0, creature.current_hp - remaining)


def apply_healing(encounter: Encounter, creature_id: str, amount: int) -> None:
    """Heal a creature, capped at max HP."""
    creature = encounter.get_creature(creature_id)
    if creature is None or amount <= 0:
        return

    creature.current_hp = min(creature.max_hp, creature.current_hp + amount)
    # Healing from 0 resets death saves
    if creature.current_hp > 0:
        creature.death_save_successes = 0
        creature.death_save_failures = 0


def set_temp_hp(encounter: Encounter, creature_id: str, amount: int) -> None:
    """Set temporary HP (doesn't stack, takes higher)."""
    creature = encounter.get_creature(creature_id)
    if creature is None:
        return
    creature.temp_hp = max(creature.temp_hp, amount)


def update_death_save(
    encounter: Encounter, creature_id: str, save_type: str, value: int
) -> None:
    """Update death save successes or failures."""
    creature = encounter.get_creature(creature_id)
    if creature is None or creature.creature_type != CreatureType.PC:
        return

    if save_type == "success":
        creature.death_save_successes = max(0, min(3, value))
    elif save_type == "failure":
        creature.death_save_failures = max(0, min(3, value))
