#!/usr/bin/env python3
"""
worldbuild — exportador do World City Map System.

Lê os dados canônicos do repositório (gazetteer + archetypes + dossiers + lenses)
e emite um único bundle navegável para o visualizador e para a engine.

    python3 tools/worldbuild.py            # gera build/world.json + build/report.md
    python3 tools/worldbuild.py --check    # só valida, não escreve (exit 1 se falhar)

Sem dependências externas — stdlib apenas.

A ideia central: o gazetteer para na cidade (nível 3), mas bairros e locais
existem nos dossiês em markdown. Este exportador junta os dois numa ÁRVORE ÚNICA
de contenção, do país até o edifício:

    0 região → 1 estado → 2 sub-região → 3 cidade → 4 bairro → 5 local

É essa árvore que o visualizador percorre, e é ela que responde "como o jogo
mantém cada localidade contida nas suas próprias interações" (ver docs/arquitetura-mapa.md).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from dataclasses import dataclass, field, asdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BUILD = ROOT / "build"

LEVEL_NAMES = ["region", "state", "subregion", "city", "district", "venue"]

# ─────────────────────────────────────────────────────────────────────────────
# utilidades
# ─────────────────────────────────────────────────────────────────────────────


def slugify(text: str) -> str:
    """Título de seção → slug ASCII estável. É o gerador de slug da §5 da lista de assets."""
    text = text.strip().lower()
    accents = {
        "á": "a", "à": "a", "ã": "a", "â": "a", "ä": "a",
        "é": "e", "ê": "e", "è": "e",
        "í": "i", "î": "i",
        "ó": "o", "õ": "o", "ô": "o", "ö": "o",
        "ú": "u", "ü": "u", "û": "u",
        "ç": "c", "ñ": "n",
    }
    text = "".join(accents.get(ch, ch) for ch in text)
    # corta em separadores editoriais comuns antes de slugificar
    text = re.split(r"[&(–—:,]", text)[0]
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return re.sub(r"-{2,}", "-", text).strip("-") or "item"


def hue_of(seed: str) -> int:
    return int(hashlib.sha1(seed.encode("utf-8")).hexdigest()[:8], 16) % 360


def tint(seed: str, sat: int = 30, light: int = 36, shift: int = 0) -> str:
    """Cor determinística a partir de um ID. Base dos placeholders gerados (§8.4).

    Saturação baixa de propósito: placeholder tem que ler como ausência de arte,
    não competir com a arte final. `shift` desloca o matiz para que os filhos de
    uma cidade formem uma família visível em vez de um arco-íris."""
    return f"hsl({(hue_of(seed) + shift) % 360}, {sat}%, {light}%)"


STOPWORDS = {
    "de", "da", "do", "das", "dos", "e", "the", "of", "a", "o", "as", "os",
    "edge", "hinge", "downtown", "port", "zone",
}


def tokens(text: str) -> set[str]:
    """Palavras significativas de um nome, sem acento e sem ruído editorial.
    Usado para casar a área citada num landmark com o bairro correspondente."""
    text = slugify_full(text)
    return {t for t in text.split("-") if len(t) > 2 and t not in STOPWORDS}


def slugify_full(text: str) -> str:
    """Como slugify(), mas sem cortar em separadores — preserva o nome inteiro."""
    text = text.strip().lower()
    accents = {
        "á": "a", "à": "a", "ã": "a", "â": "a", "ä": "a",
        "é": "e", "ê": "e", "è": "e",
        "í": "i", "î": "i",
        "ó": "o", "õ": "o", "ô": "o", "ö": "o",
        "ú": "u", "ü": "u", "û": "u",
        "ç": "c", "ñ": "n",
    }
    text = "".join(accents.get(ch, ch) for ch in text)
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return re.sub(r"-{2,}", "-", text).strip("-")


# Cadência e tipo são heurísticas por palavra-chave sobre o texto do dossiê.
# Não são inferência: são um mapeamento explícito e auditável, e o relatório
# mostra quais landmarks não casaram com nada (= escritos como prosa, não como
# mecânica). Esse "não casou" é sinal útil, não falha.
CADENCE_HINTS = [
    ("weekly", ("weekly", "tuesday", "weekday", "every week")),
    ("annual", ("annual", "january", "feb 2", "february", "new year", "carnival",
                "réveillon", "reveillon", "season")),
    ("daily", ("daily", "day/night", "daytime", "nighttime", "night ", "morning")),
]

KIND_HINTS = [
    ("commerce", ("commerce", "trade", "market", "selling", "buying", "economy",
                  "supply", "vendors", "stalls", "sourcing")),
    ("event", ("event", "festival", "procession", "mega-event", "match-day",
               "derby", "romaria", "lavagem", "parade")),
    ("skill", ("skill", "lesson", "training", "learning", "rehearsal", "building")),
    ("quest", ("quest", "collectible", "mini-quest", "oral-history", "restoration")),
    ("transit", ("transit", "ferry", "tram", "train", "link between", "shortcut",
                 "departures", "transport")),
    ("exploration", ("exploration", "hiking", "trail", "panorama", "spotting")),
    ("social", ("social", "npc", "relationship", "hub", "gathering", "roda",
                "nightlife", "hangout")),
]


def split_top_level(text: str, sep: str = ";") -> list[str]:
    """Divide em `sep` apenas fora de parênteses — senão '(Bahia home games; ...)'
    vira duas ações truncadas."""
    out, buf, depth = [], [], 0
    for ch in text:
        if ch in "([":
            depth += 1
        elif ch in ")]":
            depth = max(0, depth - 1)
        if ch == sep and depth == 0:
            out.append("".join(buf))
            buf = []
        else:
            buf.append(ch)
    out.append("".join(buf))
    return [p.strip(" .;—-") for p in out if p.strip(" .;—-")]


def derive_actions(gameplay: str) -> list[dict]:
    """Transforma o campo 'Gameplay Function' do dossiê em ações discretas.

    É o teste central do protótipo: o conteúdo já escrito gera jogo, ou é prosa
    bonita que ainda precisa ser convertida à mão?"""
    actions = []
    for i, part in enumerate(split_top_level(gameplay)):
        low = part.lower()
        cadence = next((c for c, keys in CADENCE_HINTS if any(k in low for k in keys)), "any")
        kind = next((k for k, keys in KIND_HINTS if any(x in low for x in keys)), None)
        # rótulo curto: primeira oração antes de travessão/parêntese
        label = re.split(r"[—(]", part)[0].strip(" .,-")
        actions.append(
            {
                "id": f"a{i}",
                "label": label[:58] or part[:58],
                "text": part,
                "cadence": cadence,
                "kind": kind or "unclassified",
            }
        )
    return actions


def strip_md(text: str) -> str:
    """Remove ênfase markdown, preservando o texto."""
    text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)
    text = re.sub(r"\*(.+?)\*", r"\1", text)
    text = re.sub(r"`(.+?)`", r"\1", text)
    return text.strip()


# ─────────────────────────────────────────────────────────────────────────────
# modelo
# ─────────────────────────────────────────────────────────────────────────────


@dataclass
class Node:
    """Um nó da árvore de contenção. Uma cidade, um bairro e um estádio são todos Node."""

    id: str
    name: str
    level: int
    kind: str                       # region|state|subregion|city|district|venue
    parentId: str | None = None
    childIds: list[str] = field(default_factory=list)

    tier: str | None = None
    signature: str | None = None
    isCapitalOf: str | None = None
    twinCity: str | None = None

    archetypeId: str | None = None          # declarado no próprio nó
    archetypeResolved: str | None = None     # herdado da árvore (§4 da lista de assets)
    archetypeInheritedFrom: str | None = None
    variantIds: list[str] = field(default_factory=list)

    summary: str = ""
    detail: dict = field(default_factory=dict)   # campos livres vindos do markdown
    lens: dict = field(default_factory=dict)     # overlays por lente (separável)
    assets: list[dict] = field(default_factory=list)
    color: str = ""
    sourceRef: str | None = None                 # de onde veio (arquivo#âncora)


@dataclass
class Report:
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    info: list[str] = field(default_factory=list)

    def error(self, m: str) -> None:
        self.errors.append(m)

    def warn(self, m: str) -> None:
        self.warnings.append(m)

    def note(self, m: str) -> None:
        self.info.append(m)


# ─────────────────────────────────────────────────────────────────────────────
# parsers
# ─────────────────────────────────────────────────────────────────────────────


def parse_archetypes(rep: Report) -> dict[str, dict]:
    """Lê archetypes/*.md. Cada arquivo tem um kit base e, opcionalmente,
    instâncias/variantes anexadas por passes posteriores (separadas por ---)."""
    out: dict[str, dict] = {}
    for path in sorted((ROOT / "archetypes").glob("*.md")):
        aid = path.stem
        if aid == "_template":
            continue
        raw = path.read_text(encoding="utf-8")

        fields: dict[str, str] = {}
        for m in re.finditer(r"^\*\*(.+?):?\*\*[ :]*(.*?)(?=\n\*\*|\n##|\n---|\Z)", raw, re.S | re.M):
            label = strip_md(m.group(1)).rstrip(":")
            body = m.group(2).strip()
            if label and body and label not in fields:
                fields[label] = body

        # variantes e instâncias declaradas dentro do arquivo
        variants = sorted(set(re.findall(r"NEW VARIANT: `([a-z0-9\-]+)`", raw)))
        instances = [strip_md(x) for x in re.findall(r"\(instance: (.+?)\)", raw)]

        palette = ""
        pm = re.search(r"^- Palette: (.+)$", raw, re.M)
        if pm:
            palette = pm.group(1).strip()

        signature = ""
        sm = re.search(r"[Bb]ird's-eye signature: (.+)$", raw, re.M)
        if sm:
            signature = sm.group(1).strip()

        prompts = [strip_md(p).strip('"') for p in re.findall(r"\*\"(.+?)\"\*", raw, re.S)]

        out[aid] = {
            "id": aid,
            "name": aid.replace("-", " ").title(),
            "identity": fields.get("Identity", ""),
            "palette": palette,
            "signature": signature,
            "soundscape": fields.get("Soundscape/culture", ""),
            "economy": fields.get("Economy hooks", ""),
            "fields": fields,
            "variants": variants,
            "instances": instances,
            "imagePrompts": prompts,
            "color": tint(aid),
            "source": f"archetypes/{aid}.md",
        }
        rep.note(f"archetype `{aid}`: {len(variants)} variante(s), {len(instances)} instância(s)")
    return out


def parse_dossier(path: Path, rep: Report) -> dict:
    """Extrai contexto, bairros, landmarks, notas de arte e a seção de overlay de lente.

    O parser é deliberadamente tolerante: os dossiês têm campos livres
    (ex.: 'Authenticity note' só existe no Rio). Qualquer '- **Label:** valor'
    vira uma chave, sem lista fixa.
    """
    raw = path.read_text(encoding="utf-8")
    doc: dict = {"source": str(path.relative_to(ROOT)), "districts": [], "landmarks": []}

    pos = re.search(r"\*\*(?:Vertical slice position|Position):\*\*\s*`([^`]+)`", raw)
    if pos:
        doc["declaredId"] = pos.group(1)

    # blocos de seção por heading de nível 2
    sections = re.split(r"^## ", raw, flags=re.M)[1:]
    for sec in sections:
        title = sec.splitlines()[0].strip()
        body = "\n".join(sec.splitlines()[1:])
        key = strip_md(re.sub(r"^[^\w]+", "", title)).lower()

        if key.startswith("cultural"):
            doc["context"] = body.strip()
        elif key.startswith("districts"):
            for m in re.finditer(r"^- \*\*(.+?):\*\*\s*(.+)$", body, re.M):
                name = strip_md(m.group(1))
                text = m.group(2).strip()
                zones = ""
                zm = re.search(r"(?:Gameplay zones|Zones):\s*(.+?)\.?$", text)
                if zm:
                    zones = zm.group(1).strip()
                    text = text[: zm.start()].strip()
                doc["districts"].append(
                    {"slug": slugify(name), "name": name, "description": text, "zones": zones}
                )
        elif key.startswith("landmark"):
            for lm in re.split(r"^### ", body, flags=re.M)[1:]:
                head = lm.splitlines()[0].strip()
                head = re.sub(r"^Location \d+:\s*", "", head)
                is_lens = bool(re.search(r"lens overlay", head, re.I))
                # marcador de lente em itálico não é área — remove antes de extrair
                head = re.sub(r"\*+\([^)]*lens overlay[^)]*\)\*+", "", head, flags=re.I).strip()
                area = ""
                am = re.search(r"\(([^)]+)\)\s*$", head)
                if am:
                    area = am.group(1)
                    head = head[: am.start()].strip()
                lm_fields: dict[str, str] = {}
                for fm in re.finditer(r"^- \*\*(.+?):\*\*\s*(.+)$", lm, re.M):
                    lm_fields[strip_md(fm.group(1))] = strip_md(fm.group(2))
                doc["landmarks"].append(
                    {
                        "slug": slugify(head),
                        "name": strip_md(head),
                        "area": area,
                        "isLensOverlay": is_lens,
                        "fields": lm_fields,
                    }
                )
        elif "overlay" in key and "applied" in key:
            doc["lensOverlay"] = body.strip()
        elif key.startswith("visual design"):
            doc["artNotes"] = body.strip()
        elif key.startswith("research notes"):
            doc["researchNotes"] = body.strip()

    if not doc["landmarks"]:
        rep.warn(f"{path.name}: nenhum landmark reconhecido — conferir formatação")
    return doc


def parse_lenses(rep: Report) -> dict[str, dict]:
    out = {}
    for path in sorted((ROOT / "lenses").glob("*.json")):
        out[path.stem] = json.loads(path.read_text(encoding="utf-8"))
    return out


# ─────────────────────────────────────────────────────────────────────────────
# construção da árvore
# ─────────────────────────────────────────────────────────────────────────────


def build_tree(rep: Report) -> tuple[dict[str, Node], dict, dict, dict]:
    gaz = json.loads((ROOT / "gazetteer" / "br.json").read_text(encoding="utf-8"))
    archetypes = parse_archetypes(rep)
    lenses = parse_lenses(rep)

    nodes: dict[str, Node] = {}
    for p in gaz["places"]:
        lvl = p["level"]
        nodes[p["id"]] = Node(
            id=p["id"],
            name=p["name"],
            level=lvl,
            kind=LEVEL_NAMES[lvl],
            parentId=p.get("parentId"),
            tier=p.get("tier"),
            signature=p.get("signature"),
            isCapitalOf=p.get("isCapitalOf"),
            twinCity=p.get("twinCity"),
            archetypeId=p.get("archetypeId"),
            variantIds=p.get("variantIds", []) or [],
            color=tint(p["id"]),
            sourceRef="gazetteer/br.json",
        )

    # V-estrutura: pai único e existente
    for n in nodes.values():
        if n.parentId:
            if n.parentId not in nodes:
                rep.error(f"nó `{n.id}` referencia parentId inexistente `{n.parentId}`")
            else:
                nodes[n.parentId].childIds.append(n.id)

    # herança de arquétipo: sobe a árvore até achar quem declara (§4 da lista de assets)
    def resolve_archetype(n: Node) -> None:
        cur, hops = n, 0
        while cur and hops < 8:
            if cur.archetypeId:
                n.archetypeResolved = cur.archetypeId
                n.archetypeInheritedFrom = None if cur.id == n.id else cur.id
                return
            cur = nodes.get(cur.parentId) if cur.parentId else None
            hops += 1

    for n in nodes.values():
        resolve_archetype(n)
        if n.archetypeResolved and n.archetypeResolved not in archetypes:
            rep.error(f"nó `{n.id}` referencia archetypeId inexistente `{n.archetypeResolved}`")

    # dossiês → bairros (nível 4) e locais (nível 5)
    dossiers: dict[str, dict] = {}
    declared_by_file: dict[str, str] = {}
    for path in sorted((ROOT / "dossiers").glob("*.md")):
        if path.stem == "_template":
            continue
        doc = parse_dossier(path, rep)
        target = doc.get("declaredId")
        if target and target in nodes:
            host = target
        elif path.stem in nodes:
            host = path.stem
            rep.warn(
                f"dossiê `{path.name}`: casado pelo nome do arquivo, não pelo ID declarado "
                f"(`{doc.get('declaredId')}`)"
            )
        else:
            rep.error(f"dossiê `{path.name}` não casa com nenhum nó do gazetteer")
            continue

        declared_by_file[path.stem] = host
        dossiers[host] = doc
        city = nodes[host]
        city.summary = doc.get("context", "").split("\n")[0][:400]
        city.detail = {
            "artNotes": doc.get("artNotes", ""),
            "researchNotes": doc.get("researchNotes", ""),
            "context": doc.get("context", ""),
        }
        city.sourceRef = doc["source"]

        if path.stem != host:
            rep.warn(
                f"convenção do README (filename = gazetteer ID) violada: "
                f"`dossiers/{path.stem}.md` hospeda `{host}`"
            )

        # bairros
        district_by_slug: dict[str, str] = {}
        district_tokens: dict[str, set[str]] = {}
        for d in doc["districts"]:
            did = f"{host}#{d['slug']}"
            district_by_slug[d["slug"]] = did
            district_tokens[did] = tokens(d["name"])
            nodes[did] = Node(
                id=did,
                name=d["name"],
                level=4,
                kind="district",
                parentId=host,
                summary=d["description"][:400],
                detail={"zones": d["zones"], "description": d["description"]},
                color=tint(host, sat=26, light=42, shift=18 * (len(district_by_slug))),
                sourceRef=f"{doc['source']}#districts",
            )
            city.childIds.append(did)

        # locais: pendurados no bairro quando o dossiê nomeia a área, senão na cidade
        for lm in doc["landmarks"]:
            parent = host
            if lm["area"]:
                # casa pela sobreposição de palavras significativas; empate = fica na cidade
                at = tokens(lm["area"])
                scored = sorted(
                    ((len(at & dt), did) for did, dt in district_tokens.items() if at & dt),
                    reverse=True,
                )
                if scored and (len(scored) == 1 or scored[0][0] > scored[1][0]):
                    parent = scored[0][1]
                elif scored:
                    rep.note(
                        f"landmark `{lm['name']}` cita área `{lm['area']}` que casa com "
                        f"{len(scored)} bairros — mantido no nível da cidade"
                    )
            vid = f"{host}#{lm['slug']}"
            f = lm["fields"]
            nodes[vid] = Node(
                id=vid,
                name=lm["name"],
                level=5,
                kind="venue",
                parentId=parent,
                summary=f.get("Cultural Significance", "")[:400],
                detail={
                    "type": f.get("Type", ""),
                    "significance": f.get("Cultural Significance", ""),
                    "gameplay": f.get("Gameplay Function", ""),
                    "visual": f.get("Visual Identity", ""),
                    "imagePrompt": f.get("Image Prompt", ""),
                    "extra": {
                        k: v
                        for k, v in f.items()
                        if k
                        not in {
                            "Type",
                            "Cultural Significance",
                            "Gameplay Function",
                            "Visual Identity",
                            "Image Prompt",
                        }
                    },
                    "area": lm["area"],
                    "fromLens": lm["isLensOverlay"],
                    "actions": derive_actions(f.get("Gameplay Function", "")),
                },
                color=tint(host, sat=34, light=47, shift=11 * (len(doc["landmarks"]) + 3)),
                sourceRef=f"{doc['source']}#landmarks",
            )
            nodes[parent].childIds.append(vid)

    # lentes: overlay separável, nunca gravado no nó canônico
    for lid, lens in lenses.items():
        alias_used: list[tuple[str, str]] = []
        for entry in lens.get("entries", []):
            cid = entry["cityId"]
            target = cid if cid in nodes else None
            if target is None:
                # tolerância a ID divergente: casa pelo sufixo (ver §8.6 da lista de assets)
                cands = [
                    n.id
                    for n in nodes.values()
                    if n.level == 3 and n.id.split(".")[-1] == cid.split(".")[-1]
                ]
                if len(cands) == 1:
                    target = cands[0]
                    alias_used.append((cid, target))
                else:
                    rep.error(
                        f"lente `{lid}`: cityId `{cid}` não existe no gazetteer "
                        f"e não foi possível resolver ({len(cands)} candidatos)"
                    )
                    continue
            node = nodes[target]
            node.lens.setdefault(lid, {"clubs": [], "derbies": []})
            node.lens[lid]["clubs"].append(
                {"club": entry["club"], "stadium": entry.get("stadium", "")}
            )

        for d in lens.get("derbies", []):
            cid = d["cityId"]
            target = cid if cid in nodes else next(
                (a[1] for a in alias_used if a[0] == cid), None
            )
            if target:
                nodes[target].lens.setdefault(lid, {"clubs": [], "derbies": []})
                nodes[target].lens[lid]["derbies"].append(
                    {"name": d["name"], "clubs": d["clubs"]}
                )

        for old, new in sorted(set(alias_used)):
            rep.warn(
                f"lente `{lid}`: `{old}` resolvido por alias para `{new}` — "
                f"IDs divergentes entre lente e gazetteer (ver docs/lista-de-assets.md §8.6)"
            )

    # segunda passada: bairros e locais só existem agora, e também herdam (§4)
    for n in nodes.values():
        if not n.archetypeResolved:
            resolve_archetype(n)

    return nodes, archetypes, lenses, dossiers


# ─────────────────────────────────────────────────────────────────────────────
# geometria: a árvore vira zonas no mapa
#
# O mapa não é um gráfico — é um espaço navegável. Cada nó ocupa um retângulo
# DENTRO do retângulo do pai, recursivamente, então o aninhamento da árvore é
# literalmente aninhamento espacial. O zoom é contínuo (viewBox do SVG), sem
# menu de seleção entre níveis.
#
# O layout é gerado quando não existe e PRESERVADO quando existe: map/layout.
# <país>.json é dado editável. Desenhar por cima e salvar é o fluxo previsto.
# ─────────────────────────────────────────────────────────────────────────────

WORLD_W, WORLD_H = 1600.0, 900.0

# folga interna por nível, para o aninhamento ser visível
PAD = {0: 10.0, 1: 8.0, 2: 7.0, 3: 6.0, 4: 5.0, 5: 0.0}

# peso relativo: resolução segue valor de gameplay, não área real
# (playbook, Parte 3 — "distorça a escala, nunca a identidade")
TIER_WEIGHT = {"hero": 6.0, "generic+signature": 2.5, "generic": 1.0}


def node_weight(nid: str, nodes: dict[str, "Node"]) -> float:
    n = nodes[nid]
    own = TIER_WEIGHT.get(n.tier or "", 1.0) if n.kind == "city" else 1.0
    if n.kind == "venue":
        own = 1.0
    return own + sum(node_weight(c, nodes) for c in n.childIds)


def grid_cells(n: int, x: float, y: float, w: float, h: float,
               gap: float) -> list[tuple[float, float, float, float]]:
    """Divide o retângulo em n células o mais quadradas possível.

    Grade, não treemap: um treemap empacota por peso e produz tiras finas com
    rótulos ilegíveis — testamos e ficou inutilizável. A grade sempre dá zonas
    de proporção saudável, é o que jogos de mapa por zonas usam, e é previsível
    de editar à mão depois."""
    if n <= 0 or w <= 0 or h <= 0:
        return []
    # escolhe colunas/linhas minimizando o desvio de proporção 1:1 das células
    best, best_cost = (1, n), float("inf")
    for cols in range(1, n + 1):
        rows = -(-n // cols)
        cw, ch = (w - gap * (cols - 1)) / cols, (h - gap * (rows - 1)) / rows
        if cw <= 0 or ch <= 0:
            continue
        cost = max(cw / ch, ch / cw) + 0.12 * (cols * rows - n)  # pune buraco
        if cost < best_cost:
            best, best_cost = (cols, rows), cost
    cols, rows = best
    cw = (w - gap * (cols - 1)) / cols
    ch = (h - gap * (rows - 1)) / rows
    out = []
    for i in range(n):
        r, c = divmod(i, cols)
        out.append((x + c * (cw + gap), y + r * (ch + gap), cw, ch))
    return out


def build_layout(nodes: dict[str, "Node"], roots: list[str],
                 saved: dict | None = None) -> dict[str, dict]:
    """Retângulos absolutos no espaço do mundo, um por nó. Retângulos salvos
    à mão vencem os gerados — é isso que torna o mapa desenhável."""
    saved = saved or {}
    rects: dict[str, dict] = {}

    def place(ids: list[str], box: tuple[float, float, float, float], depth: int) -> None:
        x, y, w, h = box
        pad = PAD.get(depth, 4.0)
        gap = max(1.5, pad * 0.55)
        ix, iy = x + pad, y + pad + (7.0 if depth > 0 else 4.0)   # espaço p/ o rótulo
        iw = max(0.0, w - 2 * pad)
        ih = max(0.0, h - 2 * pad - (7.0 if depth > 0 else 4.0))
        # maiores subárvores primeiro, para a leitura ficar estável
        ordered = sorted(ids, key=lambda i: (-node_weight(i, nodes), nodes[i].name))
        cells = grid_cells(len(ordered), ix, iy, iw, ih, gap)
        for nid, cell in zip(ordered, cells):
            if nid in saved:
                s_ = saved[nid]
                cell = (s_["x"], s_["y"], s_["w"], s_["h"])
                edited = True
            else:
                edited = False
            # local é pin, não zona: célula quadrada centrada, para o ícone
            # não ficar minúsculo quando o bairro tem um só local
            if nodes[nid].kind == "venue" and not edited:
                side = min(cell[2], cell[3])
                cell = (cell[0] + (cell[2] - side) / 2,
                        cell[1] + (cell[3] - side) / 2, side, side)
            rects[nid] = {"x": round(cell[0], 2), "y": round(cell[1], 2),
                          "w": round(cell[2], 2), "h": round(cell[3], 2),
                          "edited": edited}
            kids = nodes[nid].childIds
            if kids:
                place(kids, cell, depth + 1)

    place(roots, (0.0, 0.0, WORLD_W, WORLD_H), 0)
    return rects


# ─────────────────────────────────────────────────────────────────────────────
# slots de asset (§8 da lista de assets)
# ─────────────────────────────────────────────────────────────────────────────

SLOT_SPECS = {
    "city.plate.lod0": {"kind": "image-tiles", "width": 8192, "height": 4608, "tile": 512,
                        "format": "ktx2/bc7", "colorspace": "srgb", "phase": "P0"},
    "city.mask.districts": {"kind": "image", "width": 2048, "height": 1152,
                            "format": "png8", "colorspace": "none", "phase": "P0"},
    "city.crest": {"kind": "vector", "width": 256, "height": 256,
                   "format": "svg+png", "colorspace": "srgb", "phase": "P0"},
    "city.loading": {"kind": "image", "width": 2560, "height": 1440,
                     "format": "png", "colorspace": "srgb", "phase": "P0"},
    "city.audio.ambience": {"kind": "audio", "seconds": 120,
                            "format": "ogg", "phase": "P0"},
    "city.signature": {"kind": "image", "width": 1024, "height": 1024,
                       "format": "png32", "colorspace": "srgb", "phase": "P1"},
    "archetype.card": {"kind": "image", "width": 2048, "height": 512,
                       "format": "png", "colorspace": "srgb", "phase": "P0"},
    "archetype.terrain.albedo": {"kind": "image", "width": 1024, "height": 1024,
                                 "format": "png", "colorspace": "srgb", "phase": "P0"},
    "archetype.palette.lut": {"kind": "image", "width": 256, "height": 16,
                              "format": "png", "colorspace": "none", "phase": "P0"},
    "archetype.silhouette": {"kind": "image", "width": 1024, "height": 1024,
                             "format": "png32", "colorspace": "srgb", "phase": "P0"},
    "archetype.audio.ambience_day": {"kind": "audio", "seconds": 120,
                                     "format": "ogg", "phase": "P0"},
    "venue.card": {"kind": "image", "width": 1024, "height": 576,
                   "format": "png", "colorspace": "srgb", "phase": "P0"},
    "venue.pin": {"kind": "image", "width": 128, "height": 128,
                  "format": "png32", "colorspace": "srgb", "phase": "P0"},
    "district.mask.index": {"kind": "index", "phase": "P0"},
}


def asset_path(slot: str, node: Node) -> str:
    base = node.id.split("#")[0].replace(".", "/")
    leaf = node.id.split("#")[1] if "#" in node.id else None
    if slot.startswith("archetype."):
        return f"assets/archetype/{node.archetypeResolved}/{slot.split('.', 1)[1].replace('.', '/')}"
    if slot.startswith("venue."):
        return f"assets/city/{base}/landmark/{leaf}/{slot.split('.', 1)[1]}"
    if slot.startswith("district."):
        return f"assets/city/{base}/mask/districts.png#{leaf}"
    return f"assets/city/{base}/{slot.split('.', 1)[1].replace('.', '/')}"


def attach_assets(nodes: dict[str, Node]) -> dict:
    """Preenche os slots esperados por nó e devolve o manifest agregado."""
    manifest = {"generated": True, "slots": []}
    for n in nodes.values():
        wanted: list[str] = []
        if n.kind == "city":
            if n.tier == "hero":
                wanted = ["city.plate.lod0", "city.mask.districts", "city.crest",
                          "city.loading", "city.audio.ambience"]
            elif n.tier == "generic+signature":
                wanted = ["city.signature", "archetype.card"]
            else:
                wanted = ["archetype.card"]
        elif n.kind == "venue":
            wanted = ["venue.card", "venue.pin"]
        elif n.kind == "district":
            wanted = ["district.mask.index"]
        elif n.kind == "subregion":
            wanted = ["archetype.card", "archetype.terrain.albedo",
                      "archetype.palette.lut", "archetype.silhouette",
                      "archetype.audio.ambience_day"]

        for slot in wanted:
            inherited = slot.startswith("archetype.")
            path = asset_path(slot, n)
            entry = {
                "slotId": slot,
                "owner": n.id,
                "path": path,
                "spec": SLOT_SPECS.get(slot, {}),
                "status": "inherited" if inherited else "missing",
                "resolvedFrom": n.archetypeResolved if inherited else None,
                "brief": n.sourceRef,
                "phase": SLOT_SPECS.get(slot, {}).get("phase", "P1"),
            }
            n.assets.append(entry)
            manifest["slots"].append(entry)
    return manifest


# ─────────────────────────────────────────────────────────────────────────────
# validações (§8.5 da lista de assets)
# ─────────────────────────────────────────────────────────────────────────────


def validate(nodes: dict[str, Node], archetypes: dict, lenses: dict, rep: Report) -> None:
    for n in nodes.values():
        if n.kind == "city" and n.tier == "hero" and not n.detail.get("context"):
            queued = any(
                q["cityId"].split(".")[-1] == n.id.split(".")[-1]
                for lens in lenses.values()
                for q in lens.get("researchQueue", [])
            )
            (rep.note if queued else rep.warn)(
                f"cidade hero `{n.id}` sem dossiê"
                + (" (na fila de pesquisa)" if queued else " e fora da fila de pesquisa")
            )
        if n.tier == "generic+signature" and not n.signature:
            rep.error(f"cidade `{n.id}` é generic+signature mas não tem campo `signature`")
        if n.kind in {"city", "subregion"} and not n.archetypeResolved:
            rep.warn(f"nó `{n.id}` não resolve nenhum arquétipo")

    # prontidão de gameplay: o dossiê virou mecânica ou parou na prosa?
    venues = [n for n in nodes.values() if n.kind == "venue"]
    acts = [a for n in venues for a in n.detail.get("actions", [])]
    if venues:
        thin = [n.name for n in venues if len(n.detail.get("actions", [])) <= 1]
        uncl = [a["label"] for a in acts if a["kind"] == "unclassified"]
        rep.note(
            f"prontidão de gameplay: {len(acts)} ações derivadas de {len(venues)} locais "
            f"(média {len(acts) / len(venues):.1f})"
        )
        if thin:
            rep.warn(
                f"{len(thin)} local(is) renderam 1 ação ou menos — o campo "
                f"'Gameplay Function' está escrito como prosa corrida, não como mecânicas "
                f"separadas por ponto-e-vírgula: " + ", ".join(thin)
            )
        if uncl:
            rep.note(f"{len(uncl)} ação(ões) sem tipo reconhecido: " + ", ".join(uncl[:6]))

    # separabilidade da lente (invariante 3 do README)
    leaked = [
        n.id for n in nodes.values()
        if n.kind == "venue" and n.detail.get("fromLens") and n.level == 5
    ]
    if leaked:
        rep.note(
            f"{len(leaked)} local(is) marcado(s) como overlay de lente — "
            "removíveis sem quebrar o dossiê: " + ", ".join(leaked)
        )


# ─────────────────────────────────────────────────────────────────────────────
# saída
# ─────────────────────────────────────────────────────────────────────────────


def write_report(rep: Report, stats: dict) -> str:
    lines = ["# Relatório de build\n"]
    lines.append("## Contagens\n")
    for k, v in stats.items():
        lines.append(f"- **{k}**: {v}")
    for title, items, icon in (
        ("Erros", rep.errors, "❌"),
        ("Avisos", rep.warnings, "⚠️"),
        ("Notas", rep.info, "·"),
    ):
        lines.append(f"\n## {title} ({len(items)})\n")
        lines.extend(f"{icon} {m}" for m in items) if items else lines.append("_nenhum_")
    return "\n".join(lines) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser(description="Exportador do World City Map System")
    ap.add_argument("--check", action="store_true", help="valida sem escrever; exit 1 se houver erro")
    ap.add_argument("--out", default=str(BUILD), help="diretório de saída")
    args = ap.parse_args()

    rep = Report()
    nodes, archetypes, lenses, dossiers = build_tree(rep)
    manifest = attach_assets(nodes)
    validate(nodes, archetypes, lenses, rep)

    # geometria do mapa: edições salvas à mão vencem o layout gerado
    layout_file = ROOT / "map" / "layout.br.json"
    saved = {}
    if layout_file.exists():
        saved = json.loads(layout_file.read_text(encoding="utf-8")).get("rects", {})
        rep.note(f"layout: {len(saved)} zona(s) com posição editada à mão em {layout_file.name}")
    roots = sorted(n.id for n in nodes.values() if n.parentId is None)
    layout = build_layout(nodes, roots, saved)

    by_kind: dict[str, int] = {}
    for n in nodes.values():
        by_kind[n.kind] = by_kind.get(n.kind, 0) + 1

    stats = {
        "nós totais": len(nodes),
        **{f"nós · {k}": v for k, v in sorted(by_kind.items())},
        "arquétipos": len(archetypes),
        "lentes": len(lenses),
        "dossiês": len(dossiers),
        "slots de asset": len(manifest["slots"]),
        "slots faltando": sum(1 for s in manifest["slots"] if s["status"] == "missing"),
        "slots herdados": sum(1 for s in manifest["slots"] if s["status"] == "inherited"),
    }

    world = {
        "schema": 1,
        "country": json.loads((ROOT / "gazetteer" / "br.json").read_text(encoding="utf-8"))["country"],
        "levelNames": LEVEL_NAMES,
        "world": {"w": WORLD_W, "h": WORLD_H},
        "layout": layout,
        "roots": sorted(n.id for n in nodes.values() if n.parentId is None),
        "nodes": {nid: asdict(n) for nid, n in sorted(nodes.items())},
        "archetypes": archetypes,
        "lenses": {k: {"id": v["lens"]["id"], "description": v["lens"]["description"],
                       "coverage": v.get("coverage", {})} for k, v in lenses.items()},
        "manifest": manifest,
        "stats": stats,
        "report": {"errors": rep.errors, "warnings": rep.warnings, "info": rep.info},
    }

    report_md = write_report(rep, stats)

    if args.check:
        print(report_md)
        return 1 if rep.errors else 0

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "world.json").write_text(
        json.dumps(world, ensure_ascii=False, indent=1), encoding="utf-8"
    )
    (out / "report.md").write_text(report_md, encoding="utf-8")

    # bundle para o visualizador em tools/viewer/ (carrega via <script src>)
    data_js = "window.WORLD = " + json.dumps(world, ensure_ascii=False) + ";\n"
    (out / "world.data.js").write_text(data_js, encoding="utf-8")

    # páginas self-contained: um arquivo só, abre com duplo clique
    for src, dst in (("viewer", "viewer.html"), ("prototype", "prototype.html"),
                     ("mapper", "mapper.html")):
        tpl = ROOT / "tools" / src / "index.html"
        if tpl.exists():
            html = tpl.read_text(encoding="utf-8").replace(
                '<script src="../../build/world.data.js"></script>',
                "<script>" + data_js + "</script>",
            )
            (out / dst).write_text(html, encoding="utf-8")

    print(f"✓ build/world.json      {len(nodes)} nós ({stats['slots de asset']} slots)")
    print(f"✓ build/world.data.js   bundle p/ tools/viewer/index.html")
    print(f"✓ build/viewer.html     visualizador self-contained (abra com duplo clique)")
    print(f"✓ build/mapper.html     mapa espacial editável ({len(layout)} zonas)")
    print(f"✓ build/report.md       {len(rep.errors)} erro(s), {len(rep.warnings)} aviso(s)")
    return 1 if rep.errors else 0


if __name__ == "__main__":
    sys.exit(main())
