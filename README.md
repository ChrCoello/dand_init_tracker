# D&D 5e Initiative & HP Tracker

A browser-based combat tracker for Dungeon Masters running D&D 5e sessions. Manage initiative order, hit points, death saves, and reference stat blocks — so you can focus on storytelling instead of bookkeeping.

## Features

- **Import PCs** from fillable PDF character sheets (WotC / TWC format)
- **Import monsters** from markdown stat block files
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

1. **Upload PC sheets** — drop in fillable PDF character sheets (like the included `assets/thomas_aurelius_cs.pdf`)
2. **Add monsters** — the app auto-loads markdown stat blocks from `assets/` on startup. Upload more via the UI
3. **Build encounter** — pick PCs and monsters (with count, e.g. "Wolf x3")
4. **Roll initiative** — enter each PC's d20 roll in the modal, monsters roll automatically
5. **Run combat** — advance turns, apply damage/healing, track death saves

## Sample Data

The `assets/` folder includes example files to get started:

| File | Description |
|------|-------------|
| `thomas_aurelius_cs.pdf` | Level 1 Human Wizard (fillable PDF) |
| `goblin_stats.md` | Goblin stat block (CR 1/4) |
| `wolf_stats.md` | Wolf stat block (CR 1/4) |

## Adding Monsters

Create a markdown file following this format and place it in `assets/` (loaded on startup) or upload via the UI:

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
