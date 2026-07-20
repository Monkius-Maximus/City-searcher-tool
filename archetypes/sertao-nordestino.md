# Archetype: `sertao-nordestino`

*Origin: Pernambuco pass. Cross-border tag — gazetteer nodes reference this file; see Instances below.*

## Archetype 4: `sertao-nordestino` (instance: Sertão Pernambucano)

**Identity:** The semi-arid interior — caatinga scrubland, cattle-and-leather culture, cangaço legend, deep Catholic-popular religiosity, resilience as cultural core. The single most reusable archetype in Brazil: spans PE, PB, CE, RN, BA, PI, AL, SE interiors.

**Visual kit:**
- Terrain: gray-silver caatinga scrub (turns explosively green after rain — a seasonal state change!), rocky hills, açudes (reservoirs) as blue mirrors in dry land, isolated green serras (Triunfo pattern)
- Architecture: whitewashed chapels on hilltops, low houses with platibanda painted facades, stone corrals, windmill/water-tank silhouettes
- Palette: silver-gray caatinga, ochre-red earth, intense blue sky and reservoir water, white chapels, leather browns
- Bird's-eye signature: emptiness with punctuation — vast texture broken by a white chapel, an açude, a lone town grid

**Soundscape/culture:** repente & viola, aboio (cattle call singing), xilogravura woodcut aesthetics, cordel, vaquejada, Padre Cícero-style pilgrimage culture, Lampião/cangaço mythology

**Economy hooks:** cattle/leather craft, drought-and-rain seasonal cycle driving all systems, pilgrimage events

**Landmark templates:**
1. Hilltop pilgrimage chapel with ex-voto room
2. Açude reservoir with fishing village edge
3. Vaquejada arena on a town's edge
4. Cangaço-era hideout in rocky hills (quest site)

**Image prompt template:** *"Bird's-eye view of a small town in semi-arid scrubland, grid of low whitewashed houses with colorful painted facades, hilltop white chapel, large blue reservoir nearby, silver-gray thorny caatinga vegetation stretching to rocky hills, harsh bright sunlight. Isometric game asset, stark and beautiful."*

**Variant sub-archetype:** `vale-do-sao-francisco` (Petrolina pattern) — the São Francisco river creates irrigated vineyards and mango orchards, a surreal geometric green grid inside the drylands, plus river-crossing culture. Worth splitting out if the game reaches the PE/BA border. (IBGE actually treats São Francisco Pernambucano as a fifth division — the archetype model absorbs this as a variant without touching the gazetteer.)

---

---

## REUSED: `sertao-nordestino` (instance: Sertão Baiano) — NO NEW ARCHETYPE

This is the payoff of the tag model. Bahia's node simply references the archetype written in the Pernambuco pass:

```
br.nordeste.ba.sertao  →  archetypeId: "sertao-nordestino"
```

**Bahia instance notes only (thin overlay, not a rewrite):**
- **Canudos**: site of the 1896-97 war, foundational to Brazilian identity (Os Sertões). Signature landmark: memorial + the eerie fact that the original village lies under the Cocorobó reservoir — the açude landmark template with a historical layer.
- **Sisal belt variant**: around Valente/Conceição do Coité, agave sisal fields and cooperative craft economy add a texture variant (blue-green agave rows) to the base caatinga kit.
- **`vale-do-sao-francisco` variant activates here**: Juazeiro (BA) is the twin city of Petrolina (PE) across the river — the variant defined in the Pernambuco pass now has both banks. Irrigated vineyards and mango grids in drylands; Brazil's tropical wine region. One of the few places on Earth producing two grape harvests a year. Cross-state twin-city bridge = natural map connection node.

Cost of Bahia's entire Sertão: this note. Everything else inherited.

---

---

## REUSED: `sertao-nordestino` (instance: Sertões Cearenses)

```
br.nordeste.ce.sertao  →  archetypeId: "sertao-nordestino"
```

**Instance notes (thin overlay):**
- **Quixadá monoliths**: field of colossal granite inselbergs (the famous "Galinha Choca" stone) — a terrain texture variant on the base rocky-hills kit; landmark-grade silhouette for free
- **Açude Castanhão**: one of Brazil's largest reservoirs — the açude landmark template at mega scale, with drought-level as a visible systemic indicator (water line rises/falls with the seasonal cycle already built into the archetype)
- **Canindé**: major St. Francis pilgrimage town — direct use of the hilltop-pilgrimage-chapel template, no new content needed

---

## NEW VARIANT: `cariri-romeiro` (variant of `sertao-nordestino`; instance: Cariri)

**Why a variant and not a full archetype:** the base is still sertão culture, but the Cariri inverts two fundamentals — it's GREEN (spring-fed valley at the foot of the Chapada do Araripe) and its economy runs on mass pilgrimage.

**Identity (present tense):** Juazeiro do Norte is one of Latin America's largest pilgrimage destinations — millions of romeiros annually visit the Padre Cícero sites; the pilgrimage economy (lodging, religious goods, transport) IS the urban economy. Crato and Barbalha share the valley; the Chapada do Araripe is a UNESCO Global Geopark (major fossil site).

**Visual kit deltas from base sertão:**
- Terrain: lush irrigated valley floor against the chapada's forested wall — green-in-the-drylands, the Cariri's own version of the São Francisco effect
- The Horto hill: giant Padre Cícero statue overlooking the city — instant landmark silhouette
- Streetscape: religious-goods commerce, pilgrim lodging (ranchos), constant flag-and-banner color

**Culture:** romarias as calendar mega-events (the city's population multiplies), bandas cabaçais, Pau da Bandeira festival (Barbalha), reisado; xilogravura and cordel production at their historic center — Juazeiro is where the base archetype's woodcut aesthetic is actually made

**Landmark templates (additions):**
1. Pilgrimage statue hill with ascending devotional path (Horto pattern)
2. Pilgrim quarter — lodging + religious market district that swells during romarias (population-surge event mechanic)
3. Geopark fossil site / chapada spring source (fonte) parks

**Image prompt template:** *"Bird's-eye view of a dense pilgrimage city in a green valley at the foot of a long forested plateau, a giant white statue on a hill overlooking the city with a winding devotional path, streets full of banners and religious market stalls, crowds of pilgrims, warm light. Isometric game asset."*

---
