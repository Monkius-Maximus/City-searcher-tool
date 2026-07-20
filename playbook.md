# World City Map System – Replication Playbook

The transferable "know-how" behind the Brazil build. Everything here is country-agnostic; Brazil examples are illustrations, not requirements.

---

## Part 1 — The Architecture (what you're building, always)

Three independent layers + a tier system. This never changes between countries; only the data does.

```
LAYER 1: GAZETTEER      one canonical place tree per country (stable, boring, permanent)
LAYER 2: CONTENT         dossiers & archetypes attached to places (researched once, context-free)
LAYER 3: LENSES          project-specific selectors + overlays (time-stamped, disposable)

TIERS:   hero → generic+signature → generic → player/sandbox   (content LOD)
TAGS:    archetypes are ORTHOGONAL to the tree — they cross admin borders
```

**The five governing rules, learned the hard way:**

1. **One tree, single parent.** Every place has exactly one position in the hierarchy. Anything that doesn't fit the tree (cultural zones, biomes, project groupings) is a tag or a lens — never force it into the hierarchy.
2. **Archetypes are tags, not nodes.** Cultural identity ignores administrative borders (the Sertão spans 8+ states). A gazetteer node *references* an archetype; many nodes reference the same one. This is where all the cost savings come from.
3. **Lenses are snapshots; the gazetteer is forever.** A league season, a heritage route, a franchise list — these change yearly. Never bake lens data into dossiers. (Proof: Fortaleza is a permanent hero city but absent from the 2026 lens because its clubs were relegated.)
4. **Resolution follows gameplay value, not geographic size.** The LOD tiers exist so research effort lands where players actually go. A metropolis of 12M can be "generic" if no project touches it; a town of 60k can matter because a lens selected it (Mirassol).
5. **Tiers are metadata, not identity.** Promotion path: any generic city can become hero later without changing its ID or breaking references.

---

## Part 2 — The Replication Process (per new country)

### Step 0: Find the country's "IBGE equivalent"
Every country has an official statistical/administrative geography — the problem is only finding it:
- **National statistics institutes**: INEGI (Mexico), INDEC (Argentina), INSEE (France), Istat (Italy), ONS (UK), Statistics Bureau (Japan), Census Bureau (USA)...
- **Universal fallbacks when the local system is unclear**: ISO 3166-2 (subdivision codes for every country), NUTS (harmonized EU levels 1-3), and open boundary datasets (GADM, geoBoundaries) that encode each country's real levels.
- **Rule**: use the country's own official divisions as the tree. Never invent hierarchy; never import another country's model.

### Step 1: Declare the levels
Fill the generic schema — nothing else changes:
```
Brazil:   ["região", "estado", "sub-região", "cidade"]
France:   ["région", "département", "commune"]
Japan:    ["region", "prefecture", "municipality"]
Germany:  ["Land", "Regierungsbezirk", "Kreis", "Gemeinde"]
USA:      ["region*", "state", "county", "city"]     *statistical only — see Step 2
```

### Step 2: Find the CULTURAL GRAIN — the most important judgment call
Ask: *at what scale do places actually share identity — architecture, music, food, economy, landscape?* This is where archetypes live, and **it is not always an administrative level**:
- Brazil: sub-state mesoregions (Sertão, Agreste) — below the state
- USA: cultural regions CROSS state lines (New England, the Deep South, the Mountain West) — pure tags with no admin counterpart
- Italy: the regioni themselves are strong cultural units — the admin level and cultural grain coincide
- Japan: regional blocks (Kansai, Tōhoku) above prefectures, plus the omote/ura (Pacific/Sea-of-Japan) coast split that crosses everything
Because archetypes are orthogonal tags (Rule 2), all of these fit without changing the schema. The tree stores the country's official truth; the tags store the cultural truth; they only sometimes align.

### Step 3: Build the lens from the project dataset
Take the project's entity list (league clubs, franchise sites, tour stops), map each entity → home city, **deduplicate**, and record relationships that emerge (shared-city rivalries, twin cities). Output: `lens.json` with entries, overlay rules, and a coverage report (which regions the lens reaches / misses).

### Step 4: Sort the research queue by value
Priority = (entities per city) × (project importance). Mark existing dossiers. The queue tells you what to research next and what to skip.

### Step 5: Archetype passes, one region at a time
For each pass: identify the sub-regions → for each, check the library first (**reuse > variant > new**, in that order) → write only what's missing. Per archetype, produce the standard kit: identity (present tense), visual kit + palette + bird's-eye signature, soundscape/culture, economy hooks, 2-4 landmark templates, an image-prompt template, and generic-city parameters.

**The variant-vs-new rule:** if a candidate shares the base's culture but inverts 1-2 fundamentals (Cariri = sertão but green + pilgrimage-driven), it's a variant. If its visual kit, economy AND culture are all different, it's new.

### Step 6: Hero dossiers where the lens demands them
Full brief per hero city (context → districts → 5-6 landmarks → art direction → notes), then apply the lens overlay in a **clearly separated section** — the dossier must remain complete if the overlay is deleted.

### Step 7: Measure saturation
Track per pass: new archetypes / variants / pure reuses. Healthy curve: each pass in the same macro-region costs less than the last (Brazil: PE full price → BA ~60% → CE ~35%). When a pass is nearly all instance notes, that macro-region is saturated — move to the next one, where costs reset (new biome/culture families) but the method doesn't.

---

## Part 3 — The Paradox Lesson: Distort Geography, Never Identity

Paradox maps openly distort reality for gameplay: province density follows strategic importance rather than land area, and the whole hierarchy exists so content can be scripted once at the group level. Their model, translated into this system's rules:

1. **Distort SCALE freely.** Compress travel distances, shrink dull terrain, enlarge landmark districts. Players never measure kilometers; they read identity.
2. **Distort DENSITY by value.** More map resolution where more gameplay lives — that's the hero/generic tier system spatially applied. Their Europe-vs-elsewhere province density is our hero-vs-generic split.
3. **Never distort IDENTITY.** The wrong palette, the wrong music, colonial-era framing of a living place, a sacred practice turned into a minigame — these break the contract with players from that place. Scale is negotiable; truth is not.
4. **Exaggerate SILHOUETTES.** Bird's-eye readability beats fidelity: make the reef line darker, the pivot circles more perfect, the elevator taller. Every location needs a one-glance identity (the "signature" field in every archetype exists for this).
5. **Script to the GROUP.** Paradox scopes events to areas/regions so one script covers many provinces; we scope mechanics to archetypes (caatinga green-up, feira weekday cycle, wind-season tourism) so one system animates dozens of cities.

---

## Part 4 — Quality Gates (run on every archetype and dossier)

**Modernity checklist** — describe the place in the present tense; ask "what changed in the last 30 years?" (crisis, conversion, new economy); prefer living culture over heritage pageantry; include at least one element that could not exist in a period map (wind farms, kite tourism, agro grid cities, tech districts).

**Dignity checklist** — communities are hosts and protagonists of their own spaces, never scenery; religions are living practices: devotional adjacency is playable, ceremonies are not player-performable; painful histories (slavery, massacres, displacement) are sites of memory with descendant voices, not flavor text; economically marginalized areas show complexity, never danger-zone set dressing.

**Structure checklist** — single parent in the tree? Cross-border identity moved to a tag? Lens data out of the dossier? Overlay separable? Variant justified vs. new archetype? Promotion path preserved (no ID changes)?

---

## Part 5 — File Inventory (the whole system on disk)

```
/gazetteer/{country}.json          levels + places tree            (Layer 1)
/archetypes/{archetype-id}.md      shared cultural kits + variants (Layer 2, tags)
/dossiers/{city-id}.md             hero city briefs                (Layer 2)
/lenses/{project-id}.json          selector + overlay + queue      (Layer 3)
/playbook.md                       this document
```

Plain files, human-readable, diffable, engine-agnostic — the same property that makes Paradox's `area.txt`/`region.txt` files endlessly moddable. Any future tool (a map painter, a generator pipeline, a wiki) reads these; none of them owns the data.

---

## Quick-Start Card (new country in 7 moves)

1. Find the official divisions (statistics institute → ISO 3166-2 fallback)
2. Declare `levels`, load the tree
3. Locate the cultural grain; list candidate archetypes (check library for cross-border reuse FIRST)
4. Build the project lens; deduplicate; write the coverage report
5. Research queue by value; archetype passes (reuse > variant > new)
6. Hero dossiers + separable lens overlays
7. Track saturation; when a macro-region is mostly instance notes, move on
```
