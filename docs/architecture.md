# Architecture

## Tech Stack

| Component | Choice | Rationale |
|-----------|--------|-----------|
| Backend | **FastAPI** | Async, modern Python, automatic OpenAPI docs |
| Templating | **Jinja2** | Server-rendered HTML, built-in FastAPI support |
| Interactivity | **HTMX** (CDN) | Partial page swaps without writing JavaScript |
| CSS | **Pico CSS** (CDN) | Classless framework, dark mode out of the box |
| PDF parsing | **pypdf** | Extracts form fields from fillable character sheet PDFs |
| State | In-memory Python dicts | No database needed — session-scoped, single DM use case |
| Package manager | **uv** | Fast dependency resolution, lockfile included |

## Project Structure

```
app/
  main.py                        # FastAPI app, startup, static mount
  models.py                      # Dataclasses: Creature, Encounter, AbilityScores
  state.py                       # Global in-memory state (monster/PC libraries, encounter)
  routers/
    encounter.py                 # Encounter setup, combat actions (damage, heal, turns)
    creatures.py                 # PC/monster upload endpoints
  parsers/
    monster_md.py                # Regex-based markdown stat block parser
    character_pdf.py             # pypdf form field extraction from fillable PDFs
  services/
    combat.py                    # Initiative rolling, turn management, HP logic
    dice.py                      # d20 roller
  templates/
    base.html                    # Layout: Pico CSS + HTMX from CDN
    encounter/
      setup.html                 # Encounter building page
      tracker.html               # Active combat view
    partials/                    # HTMX swap targets
      creature_card.html         # Single creature: HP bar, stats, controls
      creature_list.html         # Initiative-ordered list + turn controls
      encounter_creatures.html   # Setup table of chosen creatures
      initiative_modal.html      # PC initiative input dialog
      library_lists.html         # Available PCs and monsters
  static/
    style.css                    # HP bar colors, active turn highlight, layout
assets/                          # Monster markdown files, sample PDFs
```

## Data Model

**Creature** — flat dataclass, `creature_type` enum (`PC` / `MONSTER`) distinguishes behavior:
- Core stats: `armor_class`, `max_hp`, `current_hp`, `temp_hp`, `speed`
- Initiative: `initiative_modifier` (DEX mod), `initiative_roll` (final d20 + mod)
- Ability scores: nested `AbilityScores` dataclass (STR/DEX/CON/INT/WIS/CHA)
- PC-only: `death_save_successes` / `death_save_failures` (0–3)
- Monster-only: `traits`, `actions` (raw text), `challenge_rating`

**Encounter** — holds the creature list and combat state:
- `initiative_order` property sorts by roll descending, DEX mod as tiebreaker
- `current_creature_id` tracks the active turn by ID (stable across list mutations)
- `round_number` increments when the turn wraps around

## HTMX Interaction Pattern

All user actions return HTML partials that HTMX swaps into the DOM:

| Action | Endpoint | Swaps |
|--------|----------|-------|
| Add/remove creature | `POST /encounter/add-*`, `remove` | `#encounter-creatures` |
| Roll initiative | `POST /encounter/roll-initiative` | Appends modal to `<body>` |
| Start combat | `POST /encounter/start-combat` | Replaces `<main>` with tracker |
| Damage/heal/temp HP | `POST /encounter/damage/{id}` | `#creature-{id}` (single card) |
| Next/prev turn | `POST /encounter/next-turn` | `#combat-tracker` (full list) |
| Death save toggle | `POST /encounter/death-save/{id}` | `#creature-{id}` |

No custom JavaScript. The only client-side JS is the HTMX library and one `onclick` to close the initiative modal on cancel.

## Parsers

**Monster MD**: Regex extraction matching the format in `assets/*.md`. Pulls name (## heading), AC, HP, speed, ability scores (from the markdown table row), passive perception, CR, traits, and actions.

**Character PDF**: Uses `pypdf.PdfReader.get_fields()` to read form field values. Field names match both WotC standard and TWC variant sheets (e.g. `CharacterName`, `AC`, `HPMax`, `DEX`, `Initiative`, `Passive`). A helper `_get_field()` tries multiple field name aliases for robustness.

## Initiative Flow

1. DM clicks "Roll Initiative" — server returns a `<dialog>` modal listing each PC
2. DM enters each PC's raw d20 roll (modifier added server-side) or final total (toggle)
3. On submit: server auto-rolls d20 + modifier for all monsters, applies PC values, starts combat
4. Tracker displays creatures sorted by final initiative (descending), DEX mod breaks ties
