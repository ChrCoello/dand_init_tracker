from app.models import Creature, Encounter

# Monster library: name -> template Creature (copied when adding to encounter)
monster_library: dict[str, Creature] = {}

# PC library: name -> Creature
pc_library: dict[str, Creature] = {}

# Active encounter (single encounter at a time for MVP)
encounter: Encounter = Encounter()
