from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from enum import Enum


class CreatureType(str, Enum):
    PC = "PC"
    MONSTER = "MONSTER"


@dataclass
class AbilityScores:
    strength: int = 10
    dexterity: int = 10
    constitution: int = 10
    intelligence: int = 10
    wisdom: int = 10
    charisma: int = 10

    @staticmethod
    def modifier(score: int) -> int:
        return (score - 10) // 2


@dataclass
class Creature:
    name: str
    creature_type: CreatureType
    description: str = ""
    armor_class: int = 10
    max_hp: int = 1
    current_hp: int = 0
    temp_hp: int = 0
    speed: str = "30 ft."
    abilities: AbilityScores = field(default_factory=AbilityScores)
    initiative_modifier: int = 0
    initiative_roll: int | None = None
    passive_perception: int = 10
    challenge_rating: str = ""
    death_save_successes: int = 0
    death_save_failures: int = 0
    traits: str = ""
    actions: str = ""
    id: str = field(default_factory=lambda: uuid.uuid4().hex[:8])

    def __post_init__(self) -> None:
        if self.current_hp == 0:
            self.current_hp = self.max_hp

    @property
    def dex_modifier(self) -> int:
        return AbilityScores.modifier(self.abilities.dexterity)

    @property
    def hp_percentage(self) -> int:
        if self.max_hp <= 0:
            return 0
        return max(0, int(self.current_hp / self.max_hp * 100))

    @property
    def is_unconscious(self) -> bool:
        return self.current_hp <= 0 and self.creature_type == CreatureType.PC

    @property
    def is_dead(self) -> bool:
        if self.creature_type == CreatureType.MONSTER:
            return self.current_hp <= 0
        return self.death_save_failures >= 3

    def copy(self) -> Creature:
        """Create a copy with a new ID."""
        import dataclasses
        new = dataclasses.replace(self)
        new.id = uuid.uuid4().hex[:8]
        new.abilities = dataclasses.replace(self.abilities)
        new.initiative_roll = None
        new.current_hp = new.max_hp
        new.temp_hp = 0
        new.death_save_successes = 0
        new.death_save_failures = 0
        return new


@dataclass
class Encounter:
    creatures: list[Creature] = field(default_factory=list)
    current_creature_id: str | None = None
    round_number: int = 0
    is_active: bool = False

    @property
    def initiative_order(self) -> list[Creature]:
        return sorted(
            self.creatures,
            key=lambda c: (
                c.initiative_roll if c.initiative_roll is not None else -100,
                c.dex_modifier,
            ),
            reverse=True,
        )

    @property
    def current_creature(self) -> Creature | None:
        if self.current_creature_id is None:
            return None
        for c in self.creatures:
            if c.id == self.current_creature_id:
                return c
        return None

    def get_creature(self, creature_id: str) -> Creature | None:
        for c in self.creatures:
            if c.id == creature_id:
                return c
        return None
