# D&D 5e Initiative & HP Tracker

A browser-based combat tracker for Dungeon Masters running D&D 5e sessions. Manage initiative order, hit points, death saves, and reference stat blocks — so you can focus on storytelling instead of bookkeeping.

## Features

- **Auto-load PCs & monsters** from markdown stat blocks in `assets/pcs/` and `assets/monsters/`
- **Monster descriptions** — annotate individual monsters (e.g. "the one under the table") to tell multiples apart
- **Initiative modal** — enter each PC's d20 roll, monsters are auto-rolled
- **Combat tracker** — initiative-ordered cards with HP bars, damage/heal/temp HP controls
- **Death saves** — appear automatically when a PC drops to 0 HP
- **Manual overrides** — edit initiative mid-combat, add/remove creatures
- **Zero JS build step** — server-rendered with HTMX, no npm needed

## Quick Start

Requires [uv](https://docs.astral.sh/uv/getting-started/installation/) and Python 3.11+.

```bash
git clone git@github.com:ChrCoello/dand_init_tracker.git
cd dand_init_tracker
uv sync
uv run uvicorn app.main:app --reload
```

Open [http://localhost:8000](http://localhost:8000).

## Usage

1. **Add PCs** — place markdown stat blocks in `assets/pcs/` (auto-loaded on startup). See [Converting PDF sheets](#adding-pcs) below
2. **Add monsters** — place markdown stat blocks in `assets/monsters/` (auto-loaded on startup)
3. **Build encounter** — pick PCs and monsters (with count, e.g. "Wolf x3"), add descriptions to tell multiples apart
4. **Roll initiative** — enter each PC's d20 roll in the modal, monsters roll automatically
5. **Run combat** — advance turns, apply damage/healing, track death saves

## Sample Data

The `assets/` folder includes example files to get started:

| File | Description |
|------|-------------|
| `assets/pcs/thomas_aurelius_lvl1_stats.md` | Level 1 Human Wizard |
| `assets/pcs/penda_of_mercia_lvl2_stats.md` | Level 2 Fighter |
| `assets/monsters/goblin_stats.md` | Goblin stat block (CR 1/4) |
| `assets/monsters/wolf_stats.md` | Wolf stat block (CR 1/4) |

When a character has multiple level files (e.g. `penda_of_mercia_lvl1_stats.md` and `penda_of_mercia_lvl2_stats.md`), only the highest level is loaded.

## Adding PCs

Create a markdown file and place it in `assets/pcs/`:

```markdown
## Character Name

**Class:** Wizard 1
**Armor Class:** 12
**Hit Points:** 8
**Speed:** 30 ft.

| STR | DEX | CON | INT | WIS | CHA |
|:---:|:---:|:---:|:---:|:---:|:---:|
| 9 (-1) | 14 (+2) | 14 (+2) | 18 (+4) | 10 (+0) | 10 (+0) |

**Initiative Modifier:** +2
**Passive Perception:** 12
```

To convert an existing PDF character sheet, see the conversion prompt in [`docs/pc_conversion_prompt.md`](docs/pc_conversion_prompt.md).

## Adding Monsters

Create a markdown file following this format and place it in `assets/monsters/`:

```markdown
## Monster Name

**Armor Class:** 13 (natural armor)
**Hit Points:** 11 (2d8 + 2)
**Speed:** 40 ft.

| STR | DEX | CON | INT | WIS | CHA |
|:---:|:---:|:---:|:---:|:---:|:---:|
| 12 (+1) | 15 (+2) | 12 (+1) | 3 (-4) | 12 (+1) | 6 (-2) |

**Senses:** Passive Perception 13
**Challenge:** 1/4 (50 XP)

### Traits

**Pack Tactics.** Description here.

### Actions

**Bite.** *Melee Weapon Attack:* +4 to hit, reach 5 ft., one target. *Hit:* 7 (2d4 + 2) piercing damage.
```

## License

GPLv3 — see [LICENSE](LICENSE).
