# PC Character Sheet → Markdown Conversion Prompt

Copy-paste the prompt below into Claude Haiku along with a character sheet PDF or image.

---

I am going to give you a D&D 5e character sheet (as a PDF or image).
Extract the character's stats and produce a markdown stat block in
exactly this format:

```
## [Character Name]

**Class:** [Class and Level, e.g. "Wizard 1"]
**Armor Class:** [number only]
**Hit Points:** [max HP, number only]
**Speed:** [e.g. "30 ft."]

| STR | DEX | CON | INT | WIS | CHA |
|:---:|:---:|:---:|:---:|:---:|:---:|
| [score] ([modifier]) | [score] ([modifier]) | [score] ([modifier]) | [score] ([modifier]) | [score] ([modifier]) | [score] ([modifier]) |

**Initiative Modifier:** [modifier, e.g. "+2"]
**Passive Perception:** [number]
```

Rules:
- Modifiers are formatted as (+N) or (-N), with +0 shown as (+0)
- Initiative modifier is usually the DEX modifier, unless the character
  has a feat like Alert that adds a bonus — check the character sheet
- Output ONLY the markdown block, nothing else
- The file should be saved as [character_name]_lvl[level]_stats.md
  (lowercase, underscores for spaces, e.g. thomas_aurelius_lvl1_stats.md)
