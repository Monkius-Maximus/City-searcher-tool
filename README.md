# World City Map System

A three-layer geographic content system for bird's-eye game maps: research once, reuse everywhere, distort geography — never identity.

Built and stress-tested on Brazil (3 state passes + 2 hero cities + 1 project lens); designed to replicate for any country. **Read `playbook.md` first** — it is the method; everything else is data produced by it.

## Repository layout

```
playbook.md                  THE method: architecture, replication steps, Paradox lessons, quality gates
gazetteer/br.json            Layer 1 — canonical place tree (IBGE levels, archetype refs, city tiers)
archetypes/{id}.md           Layer 2 — cross-border cultural kits (tags). Instances/variants appended per pass
dossiers/{city-id}.md        Layer 2 — handcrafted hero city briefs (filename = gazetteer ID)
lenses/{project}.json        Layer 3 — time-stamped project selectors + overlays + research queue
docs/saturation-log.md       cost tracking per pass (the reuse curve)
archetypes/_template.md      blank kit for new archetypes
dossiers/_template.md        blank structure for new hero dossiers
```

## Current status (Brazil)

- **Gazetteer:** 5 regions, 10 states loaded, sub-regions for PE / BA / CE
- **Archetype library:** 10 archetypes + 3 variants; ~5 multi-state. Nordeste near saturation (PE full price → BA ~60% → CE ~35%)
- **Hero dossiers:** Rio de Janeiro, Salvador (full vertical slice: gazetteer → archetype → dossier → lens overlay)
- **Lenses:** Brasileirão Série A 2026 (20 clubs → 11 cities; Centro-Oeste coverage gap documented)
- **Next frontiers:** São Paulo dossier (3 lens clubs), Amazônia archetype family (Belém), Sul family (Porto Alegre)

## How to add a new country

Follow the Quick-Start Card at the end of `playbook.md`: find the official divisions → declare levels → locate the cultural grain → build the lens → archetype passes (reuse > variant > new) → hero dossiers → track saturation.

## Invariants (do not break)

1. One tree, single parent — everything else is a tag or a lens
2. Archetypes are tags, not nodes — they cross admin borders
3. Lenses are snapshots; gazetteer and dossiers are permanent
4. Resolution follows gameplay value, not geographic size
5. Tiers are metadata — promotion never changes an ID
