/* ══════════════════════════════════════════════════════════════════════════
   City Searcher — editor de mundo
   ══════════════════════════════════════════════════════════════════════════
   Gerador de localidades com mapa espacial. Tudo roda no navegador, no modelo
   do Azgaar: o estado vive em memória + localStorage, e você exporta um arquivo
   para levar de volta ao repositório.

   Camadas:
     WORLD (build/world.json)  base gerada por worldbuild.py — pesquisa + dossiês
     ed    (localStorage)      suas edições pendentes: added / patched / removed / rects
     N     (derivado)          a árvore final que a tela desenha

   Exportar produz map/edits.json, que o worldbuild.py mescla no próximo build.
   A pesquisa em markdown nunca é sobrescrita — as duas fontes compõem.
   ══════════════════════════════════════════════════════════════════════════ */
(function () {
'use strict';

const W = window.WORLD;
if (!W) { document.body.innerHTML =
  '<p style="padding:24px;font:14px system-ui">Rode <code>python3 tools/worldbuild.py</code>.</p>';
  return; }

const SVG = document.getElementById('svg');
const NS = 'http://www.w3.org/2000/svg';
const KEY = 'city-searcher-edits-v2';

const KIND = {region:'região', state:'estado', subregion:'sub-região',
              city:'cidade', district:'bairro', venue:'local'};
const KIND_ORDER = ['region','state','subregion','city','district','venue'];
const TIERS = ['', 'hero', 'generic+signature', 'generic'];
const CAT = {
  commerce:{c:'--gold', g:'▤', n:'Comércio'},   event:{c:'--pink', g:'★', n:'Evento'},
  skill:{c:'--accent', g:'◆', n:'Perícia'},     quest:{c:'--violet', g:'❖', n:'Missão'},
  transit:{c:'--blue', g:'⇄', n:'Transporte'},  exploration:{c:'--teal', g:'▲', n:'Exploração'},
  social:{c:'--orange', g:'●', n:'Social'},     unclassified:{c:'--faint', g:'○', n:'Sem tipo'}
};
const css = v => getComputedStyle(document.documentElement).getPropertyValue(v).trim();

/* ── geometria (porte fiel do grid_cells/place do worldbuild.py) ─────────── */
const PAD = {0:10, 1:8, 2:7, 3:6, 4:5, 5:0};
const TIER_WEIGHT = {'hero':6, 'generic+signature':2.5, 'generic':1};

function gridCells(n, x, y, w, h, gap) {
  if (n <= 0 || w <= 0 || h <= 0) return [];
  let best = [1, n], bestCost = Infinity;
  for (let cols = 1; cols <= n; cols++) {
    const rows = Math.ceil(n / cols);
    const cw = (w - gap * (cols - 1)) / cols, ch = (h - gap * (rows - 1)) / rows;
    if (cw <= 0 || ch <= 0) continue;
    const cost = Math.max(cw / ch, ch / cw) + 0.12 * (cols * rows - n);
    if (cost < bestCost) { best = [cols, rows]; bestCost = cost; }
  }
  const [cols, rows] = best;
  const cw = (w - gap * (cols - 1)) / cols, ch = (h - gap * (rows - 1)) / rows;
  const out = [];
  for (let i = 0; i < n; i++) {
    const r = Math.floor(i / cols), c = i % cols;
    out.push([x + c * (cw + gap), y + r * (ch + gap), cw, ch]);
  }
  return out;
}

function weightOf(id, N, memo) {
  if (memo[id] != null) return memo[id];
  const n = N[id];
  let own = 1;
  if (n.kind === 'city') own = TIER_WEIGHT[n.tier] || 1;
  let t = own;
  for (const c of n.childIds) t += weightOf(c, N, memo);
  return memo[id] = t;
}

function computeLayout(N, roots, fixed) {
  const rects = {}, memo = {};
  (function place(ids, box, depth) {
    const [x, y, w, h] = box;
    const pad = PAD[depth] != null ? PAD[depth] : 4;
    const gap = Math.max(1.5, pad * 0.55);
    const lab = depth > 0 ? 7 : 4;
    const cells = gridCells(ids.length, x + pad, y + pad + lab,
      Math.max(0, w - 2 * pad), Math.max(0, h - 2 * pad - lab), gap);
    const ordered = ids.slice().sort((a, b) =>
      (weightOf(b, N, memo) - weightOf(a, N, memo)) || N[a].name.localeCompare(N[b].name, 'pt-BR'));
    ordered.forEach((id, i) => {
      let cell = cells[i]; if (!cell) return;
      const edited = !!fixed[id];
      if (edited) { const s = fixed[id]; cell = [s.x, s.y, s.w, s.h]; }
      else if (N[id].kind === 'venue') {
        const side = Math.min(cell[2], cell[3]);
        cell = [cell[0] + (cell[2] - side) / 2, cell[1] + (cell[3] - side) / 2, side, side];
      }
      rects[id] = {x: cell[0], y: cell[1], w: cell[2], h: cell[3], edited};
      if (N[id].childIds.length) place(N[id].childIds, cell, depth + 1);
    });
  })(roots, [0, 0, W.world.w, W.world.h], 0);
  return rects;
}

/* ── estado editável ────────────────────────────────────────────────────── */
const blank = () => ({added: [], patched: {}, removed: [], rects: {}});
let ed = blank();
try { const raw = localStorage.getItem(KEY); if (raw) ed = Object.assign(blank(), JSON.parse(raw)); }
catch (e) { console.warn('estado local ilegível, recomeçando', e); }

const save = () => { try { localStorage.setItem(KEY, JSON.stringify(ed)); } catch (e) {} };

let N = {}, ROOTS = [], LAY = {};

function rebuild() {
  N = {};
  for (const [k, v] of Object.entries(W.nodes)) N[k] = Object.assign({}, v, {childIds: v.childIds.slice()});

  // remoções, com descendentes
  for (const id of ed.removed) {
    if (!N[id]) continue;
    const stack = [id];
    while (stack.length) { const cur = N[stack.pop()]; if (!cur) continue;
      stack.push(...cur.childIds); delete N[cur.id]; }
    for (const n of Object.values(N)) {
      const i = n.childIds.indexOf(id); if (i >= 0) n.childIds.splice(i, 1);
    }
  }
  // adições (ignora as que o build já absorveu, para não duplicar)
  for (const a of ed.added) {
    if (N[a.id]) continue;
    if (a.parentId && !N[a.parentId]) continue;
    N[a.id] = {
      id: a.id, name: a.name, level: a.level, kind: a.kind, parentId: a.parentId || null,
      childIds: [], tier: a.tier || null, signature: a.signature || null,
      archetypeId: a.archetypeId || null, archetypeResolved: null,
      archetypeInheritedFrom: null, variantIds: [],
      detail: a.detail || {}, lens: {}, assets: [],
      color: a.color || tintOf(a.id), sourceRef: 'map/edits.json (local)'
    };
    if (a.parentId) N[a.parentId].childIds.push(a.id);
  }
  // alterações
  for (const [id, p] of Object.entries(ed.patched)) {
    if (!N[id]) continue;
    for (const k of ['name', 'tier', 'signature', 'archetypeId']) if (k in p) N[id][k] = p[k];
    if (p.detail) N[id].detail = Object.assign({}, N[id].detail, p.detail);
  }
  // herança de arquétipo, subindo a árvore (mesma regra do exportador)
  for (const n of Object.values(N)) {
    let cur = n, hops = 0;
    n.archetypeResolved = null; n.archetypeInheritedFrom = null;
    while (cur && hops++ < 8) {
      if (cur.archetypeId) { n.archetypeResolved = cur.archetypeId;
        n.archetypeInheritedFrom = cur.id === n.id ? null : cur.id; break; }
      cur = cur.parentId ? N[cur.parentId] : null;
    }
  }
  ROOTS = Object.values(N).filter(n => !n.parentId).map(n => n.id);
  LAY = computeLayout(N, ROOTS, ed.rects);
}

function tintOf(seed) {
  let h = 0; for (let i = 0; i < seed.length; i++) h = (h * 31 + seed.charCodeAt(i)) >>> 0;
  return `hsl(${h % 360}, 30%, 36%)`;
}

/* ── navegação ──────────────────────────────────────────────────────────── */
let scope = null, sel = null, lens = true, editing = false, tab = 'map', query = '';
let view = {x: 0, y: 0, w: W.world.w, h: W.world.h}, target = Object.assign({}, view);

const kidsOf = id => (id === null ? ROOTS : (N[id] ? N[id].childIds : []));
const chain = id => { const o = []; let c = id; while (c && N[c]) { o.unshift(c); c = N[c].parentId; } return o; };
const rectOf = id => LAY[id];
const actsOf = id => (N[id] && N[id].detail && N[id].detail.actions) || [];
const subActs = id => { let t = actsOf(id).length; for (const c of N[id].childIds) t += subActs(c); return t; };
const catOf = n => { const a = (n.detail && n.detail.actions) || [];
  return a.length ? (CAT[a[0].kind] || CAT.unclassified) : CAT.unclassified; };

const el = (t, a) => { const e = document.createElementNS(NS, t);
  for (const k in (a || {})) e.setAttribute(k, a[k]); return e; };
const h = (t, cls, txt) => { const e = document.createElement(t);
  if (cls) e.className = cls; if (txt != null) e.textContent = txt; return e; };

function frame(id) {
  const r = id === null ? {x: 0, y: 0, w: W.world.w, h: W.world.h} : rectOf(id);
  if (!r) return;
  const m = Math.max(r.w, r.h) * 0.06;
  target = {x: r.x - m, y: r.y - m, w: r.w + 2 * m, h: r.h + 2 * m};
}
const applyView = () => SVG.setAttribute('viewBox', `${view.x} ${view.y} ${view.w} ${view.h}`);
function tick() {
  const d = ['x','y','w','h'].reduce((s, p) => s + Math.abs(target[p] - view[p]), 0);
  if (d > 0.4) { for (const p of ['x','y','w','h']) view[p] += (target[p] - view[p]) * 0.2;
    applyView(); renderMap(); requestAnimationFrame(tick); }
  else { view = Object.assign({}, target); applyView(); renderMap(); }
}
function enter(id) { scope = id; sel = null; frame(id); tick(); drawChrome(); drawSide(); }

/* ── mapa ───────────────────────────────────────────────────────────────── */
function renderMap() {
  SVG.innerHTML = '';
  const scale = view.w / (SVG.clientWidth || SVG.getBoundingClientRect().width || 1200);
  const anc = chain(scope);

  for (const id of anc) { if (id === scope) continue; const r = rectOf(id); if (!r) continue;
    SVG.appendChild(el('rect', {x: r.x, y: r.y, width: r.w, height: r.h, rx: 2,
      class: 'zone ghost', stroke: N[id].color})); }
  if (scope !== null) { const r = rectOf(scope); if (r)
    SVG.appendChild(el('rect', {x: r.x, y: r.y, width: r.w, height: r.h, rx: 2,
      class: 'zone scope', stroke: css('--accent'), 'stroke-opacity': .5})); }

  for (const id of kidsOf(scope)) {
    const n = N[id], r = rectOf(id); if (!r) continue;
    if (n.kind === 'venue') { if (lens) drawPin(id, r, scale, false); continue; }

    const z = el('rect', {x: r.x, y: r.y, width: r.w, height: r.h, rx: 2,
      class: 'zone child' + (sel === id ? ' sel' : '') + (ed.rects[id] ? ' edited' : ''),
      stroke: sel === id ? css('--accent') : n.color});
    z.dataset.id = id; SVG.appendChild(z);

    const lp = 9 * scale;
    const lab = el('text', {x: r.x + lp * .45, y: r.y + lp * 1.15, class: 'zlabel',
      fill: n.color, 'fill-opacity': .95, 'font-size': lp});
    lab.textContent = (n.signature ? '◆ ' : '') + n.name.toUpperCase().slice(0, 26);
    SVG.appendChild(lab);

    if (r.w / scale > 96) {
      const fit = (r.w * 0.92) / Math.max(6, n.name.length) * 1.85;
      const fs = Math.min(fit, r.h * 0.2, 26 * scale);
      const nm = el('text', {x: r.x + r.w / 2, y: r.y + r.h / 2, class: 'zname',
        fill: css('--ink'), 'text-anchor': 'middle', 'dominant-baseline': 'central', 'font-size': fs});
      nm.textContent = n.name; SVG.appendChild(nm);
      const na = subActs(id), inner = n.childIds.length;
      if ((inner || na) && r.w / scale > 140) {
        const mt = el('text', {x: r.x + r.w / 2, y: r.y + r.h / 2 + fs * .95, class: 'zmeta',
          'text-anchor': 'middle', 'font-size': Math.min(fs * .42, 9 * scale)});
        mt.textContent = [inner ? inner + ' dentro' : '', na ? na + ' interações' : '']
          .filter(Boolean).join('  ·  ');
        SVG.appendChild(mt);
      }
    }
    if (editing) { const hs = Math.max(3, 6 * scale);
      const hd = el('rect', {x: r.x + r.w - hs, y: r.y + r.h - hs, width: hs, height: hs, class: 'handle'});
      hd.dataset.id = id; hd.dataset.resize = '1'; SVG.appendChild(hd); }

    if (lens) for (const g of n.childIds) {
      if (N[g].kind !== 'venue') continue;
      const gr = rectOf(g); if (gr) drawPin(g, gr, scale, true);
    }
  }
}

function drawPin(id, r, scale, small) {
  const n = N[id], cat = catOf(n), col = css(cat.c);
  const s = Math.min(Math.min(r.w, r.h) * (small ? .5 : .68), (small ? 24 : 46) * scale);
  const cx = r.x + r.w / 2, cy = r.y + r.h / 2;
  const g = el('g', {class: 'pin'}); g.dataset.id = id;
  g.appendChild(el('rect', {x: cx - s / 2, y: cy - s / 2, width: s, height: s, rx: s * .2,
    fill: 'rgba(0,0,0,.55)', stroke: col, 'stroke-opacity': sel === id ? 1 : .85}));
  const t = el('text', {x: cx, y: cy, fill: col, 'font-size': s * .55}); t.textContent = cat.g;
  g.appendChild(t);
  const na = actsOf(id).length;
  if (na > 1) {
    g.appendChild(el('circle', {cx: cx + s / 2, cy: cy - s / 2, r: s * .17, fill: col}));
    const bt = el('text', {x: cx + s / 2, y: cy - s / 2, fill: '#08120e', 'font-size': s * .22,
      'text-anchor': 'middle', 'dominant-baseline': 'central'});
    bt.textContent = String(na); g.appendChild(bt);
  }
  SVG.appendChild(g);
  if (!small && s / scale > 20) {
    const lb = el('text', {x: cx, y: cy + s / 2 + 7 * scale, class: 'pinlabel', fill: col,
      'font-size': 8 * scale});
    lb.textContent = n.name.slice(0, 22).toUpperCase(); SVG.appendChild(lb);
  }
}

/* ── CRUD ───────────────────────────────────────────────────────────────── */
function slug(s) {
  return s.toLowerCase()
    .normalize('NFD').replace(/[̀-ͯ]/g, '')
    .replace(/[^a-z0-9]+/g, '-').replace(/-{2,}/g, '-').replace(/^-|-$/g, '') || 'item';
}
function newId(parentId, name) {
  const s = slug(name);
  let base;
  if (!parentId) base = (W.country.code || 'xx').toLowerCase() + '.' + s;
  else {
    const p = N[parentId];
    base = p.level >= 3 ? (parentId.split('#')[0] + '#' + s) : (parentId + '.' + s);
  }
  let id = base, i = 2;
  while (N[id] || ed.added.some(a => a.id === id)) id = base + '-' + (i++);
  return id;
}

function addNode(parentId, name, extra) {
  const lvl = parentId ? N[parentId].level + 1 : 0;
  if (lvl > 5) return null;
  const id = newId(parentId, name);
  ed.added.push(Object.assign({
    id, parentId: parentId || null, name: name.trim(), level: lvl,
    kind: KIND_ORDER[lvl], color: tintOf(id)
  }, extra || {}));
  save(); rebuild();
  return id;
}
function patchNode(id, patch) {
  if (ed.added.some(a => a.id === id)) {
    const a = ed.added.find(a => a.id === id); Object.assign(a, patch);
  } else {
    ed.patched[id] = Object.assign({}, ed.patched[id], patch);
  }
  save(); rebuild();
}
function removeNode(id) {
  ed.added = ed.added.filter(a => a.id !== id);
  delete ed.patched[id]; delete ed.rects[id];
  if (W.nodes[id] && !ed.removed.includes(id)) ed.removed.push(id);
  save(); rebuild();
}

/* ── painel lateral ─────────────────────────────────────────────────────── */
function drawSide() {
  const s = document.getElementById('side'); s.innerHTML = '';

  const head = h('div', 'sh');
  head.appendChild(h('h3', null, scope === null ? W.country.name : N[scope].name));
  head.appendChild(h('p', null, scope === null
    ? (W.country.levels || []).join(' › ')
    : KIND[N[scope].kind] + ' · nível ' + N[scope].level + ' · ' + scope));
  s.appendChild(head);

  const sb = h('div', 'searchbox');
  const inp = h('input'); inp.placeholder = 'Buscar em todas as localidades…'; inp.value = query;
  inp.oninput = e => { query = e.target.value; drawSide();
    const f = document.querySelector('.searchbox input');
    if (f) { f.focus(); f.setSelectionRange(f.value.length, f.value.length); } };
  sb.appendChild(inp); s.appendChild(sb);

  if (tab === 'list' || query) {
    const q = query.trim().toLowerCase();
    const hits = Object.keys(N)
      .filter(i => !q || N[i].name.toLowerCase().includes(q) || i.toLowerCase().includes(q))
      .sort((a, b) => (N[a].level - N[b].level) || N[a].name.localeCompare(N[b].name, 'pt-BR'))
      .slice(0, 120);
    s.appendChild(h('div', 'slab', (q ? 'resultados' : 'todas as localidades') + ' · ' + hits.length));
    for (const id of hits) s.appendChild(itemFor(id, true));
    if (sel) s.appendChild(editorFor(sel));
    return;
  }

  // criar filho do escopo atual — é aqui que se constrói o mapa interno
  if (scope !== null && N[scope].level < 5) s.appendChild(creatorFor(scope));
  else if (scope === null) s.appendChild(creatorFor(null));

  const kids = kidsOf(scope);
  s.appendChild(h('div', 'slab', 'contido aqui · ' + kids.length));
  if (!kids.length) {
    const e = h('div', 'empty');
    e.textContent = scope !== null && N[scope].kind === 'city'
      ? 'Esta cidade ainda não tem mapa interno. Adicione bairros acima e eles aparecem no mapa na hora.'
      : 'Vazio. Adicione localidades acima.';
    s.appendChild(e);
  }
  for (const id of kids.slice().sort((a, b) =>
      (N[a].level - N[b].level) || N[a].name.localeCompare(N[b].name, 'pt-BR')))
    s.appendChild(itemFor(id));

  if (sel) s.appendChild(editorFor(sel));
}

function creatorFor(parentId) {
  const lvl = parentId === null ? 0 : N[parentId].level + 1;
  const box = h('div', 'creator');
  const lbl = h('div', 'slab', '+ adicionar ' + KIND[KIND_ORDER[lvl]]);
  lbl.style.padding = '0 0 6px'; box.appendChild(lbl);
  const ta = h('textarea');
  ta.placeholder = 'Um nome por linha…\nEx.: Boa Viagem\n     Recife Antigo';
  ta.rows = 2;
  box.appendChild(ta);
  const row = h('div', 'crow');
  const btn = h('button', 'primary', 'Adicionar');
  btn.onclick = () => {
    const names = ta.value.split('\n').map(x => x.trim()).filter(Boolean);
    if (!names.length) { ta.focus(); return; }
    let last = null;
    for (const nm of names) last = addNode(parentId, nm) || last;
    sel = last; ta.value = '';
    frame(scope); tick(); drawChrome(); drawSide();
  };
  ta.onkeydown = e => { if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) btn.click(); };
  row.appendChild(btn);
  const hint = h('span', 'hintxt', 'Ctrl+Enter');
  row.appendChild(hint);
  box.appendChild(row);
  return box;
}

function itemFor(id, withPath) {
  const n = N[id], b = h('button', 'item');
  if (sel === id) b.setAttribute('aria-current', 'true');
  const isV = n.kind === 'venue', cat = catOf(n);
  const ic = h('div', 'ic');
  ic.style.borderColor = isV ? css(cat.c) : n.color;
  ic.style.color = isV ? css(cat.c) : n.color;
  ic.textContent = isV ? cat.g : (n.tier === 'hero' ? '◈' : '▢');
  b.appendChild(ic);
  const tx = h('div', 'tx');
  tx.appendChild(h('b', null, n.name));
  tx.appendChild(h('span', null, [KIND[n.kind], n.tier,
    n.archetypeResolved && ('↳' + n.archetypeResolved)].filter(Boolean).join(' · ').slice(0, 44)));
  b.appendChild(tx);
  if (withPath) b.appendChild(h('span', 'n', chain(n.parentId).map(a => N[a].name).join(' ▸ ').slice(-26)));
  else {
    const na = subActs(id);
    b.appendChild(h('span', 'n', n.childIds.length ? ('▸' + n.childIds.length) : (na ? na + '×' : '')));
  }
  b.onclick = () => {
    // resultado de busca: navega até o pai E mantém o item selecionado
    // (enter() zera a seleção, então ela é reposta depois)
    if (withPath) { enter(n.parentId); sel = id; renderMap(); drawSide(); return; }
    if (sel === id && n.childIds.length) enter(id); else { sel = id; renderMap(); drawSide(); }
  };
  b.ondblclick = () => { if (n.childIds.length || n.level < 5) enter(id); };
  return b;
}

function field(parent, label, value, onChange, opts) {
  const w = h('div', 'fld');
  w.appendChild(h('label', null, label));
  let input;
  if (opts && opts.options) {
    input = h('select');
    for (const o of opts.options) {
      const op = h('option', null, o === '' ? '—' : o); op.value = o;
      if ((value || '') === o) op.selected = true; input.appendChild(op);
    }
  } else {
    input = h('input'); input.value = value || '';
    if (opts && opts.placeholder) input.placeholder = opts.placeholder;
  }
  input.onchange = () => onChange(input.value);
  w.appendChild(input); parent.appendChild(w);
  return input;
}

function editorFor(id) {
  const n = N[id];
  const d = h('div', 'detail');
  const hd = h('div', 'dh');
  hd.appendChild(h('h4', null, 'editar · ' + KIND[n.kind]));
  const x = h('button', 'x', '✕'); x.title = 'fechar';
  x.onclick = () => { sel = null; renderMap(); drawSide(); };
  hd.appendChild(x); d.appendChild(hd);
  d.appendChild(h('code', 'idline', n.id));

  field(d, 'Nome', n.name, v => { if (v.trim()) { patchNode(id, {name: v.trim()}); renderMap(); drawSide(); } });

  if (n.kind === 'city')
    field(d, 'Tier', n.tier, v => { patchNode(id, {tier: v || null}); renderMap(); drawChrome(); drawSide(); },
      {options: TIERS});
  if (n.kind === 'city' || n.kind === 'district')
    field(d, 'Assinatura', n.signature, v => { patchNode(id, {signature: v || null}); renderMap(); drawSide(); },
      {placeholder: 'identidade de um relance'});
  if (n.level <= 3)
    field(d, 'Arquétipo', n.archetypeId, v => { patchNode(id, {archetypeId: v || null}); renderMap(); drawSide(); },
      {options: [''].concat(Object.keys(W.archetypes).sort())});

  if (n.archetypeResolved) {
    const t = h('div', 'inh');
    t.textContent = n.archetypeInheritedFrom
      ? '↳ herda ' + n.archetypeResolved + ' de ' + N[n.archetypeInheritedFrom].name
      : '◆ define ' + n.archetypeResolved;
    d.appendChild(t);
  }

  // interações — só fazem sentido na folha
  if (n.kind === 'venue') {
    d.appendChild(h('div', 'slab2', 'interações · ' + actsOf(id).length));
    const list = h('div', 'acts');
    actsOf(id).forEach((a, i) => {
      const row = h('div', 'acti');
      const sel2 = h('select');
      for (const k of Object.keys(CAT)) {
        const op = h('option', null, CAT[k].g + ' ' + CAT[k].n); op.value = k;
        if (a.kind === k) op.selected = true; sel2.appendChild(op);
      }
      sel2.onchange = () => { const acts = actsOf(id).slice();
        acts[i] = Object.assign({}, acts[i], {kind: sel2.value});
        patchNode(id, {detail: {actions: acts}}); renderMap(); drawSide(); };
      row.appendChild(sel2);
      const inp = h('input'); inp.value = a.label;
      inp.onchange = () => { const acts = actsOf(id).slice();
        acts[i] = Object.assign({}, acts[i], {label: inp.value, text: inp.value});
        patchNode(id, {detail: {actions: acts}}); drawSide(); };
      row.appendChild(inp);
      const rm = h('button', 'x', '−'); rm.title = 'remover';
      rm.onclick = () => { const acts = actsOf(id).slice(); acts.splice(i, 1);
        patchNode(id, {detail: {actions: acts}}); renderMap(); drawSide(); };
      row.appendChild(rm);
      list.appendChild(row);
    });
    d.appendChild(list);
    const add = h('button', 'ghostbtn', '+ interação');
    add.onclick = () => { const acts = actsOf(id).slice();
      acts.push({id: 'a' + acts.length, label: 'Nova interação', text: 'Nova interação',
                 cadence: 'any', kind: 'social'});
      patchNode(id, {detail: {actions: acts}}); renderMap(); drawSide(); };
    d.appendChild(add);
  }

  const foot = h('div', 'dfoot');
  if (n.level < 5) {
    const go = h('button', 'ghostbtn', '↳ abrir mapa interno');
    go.onclick = () => enter(id); foot.appendChild(go);
  }
  const del = h('button', 'danger', '🗑 excluir');
  del.onclick = () => {
    const kids = subCount(id);
    const msg = kids ? `Excluir "${n.name}" e ${kids} descendente(s)?` : `Excluir "${n.name}"?`;
    if (!confirm(msg)) return;
    removeNode(id); sel = null;
    if (chain(scope).indexOf(id) >= 0 || scope === id) scope = n.parentId;
    frame(scope); tick(); drawChrome(); drawSide();
  };
  foot.appendChild(del);
  d.appendChild(foot);
  return d;
}
function subCount(id) { let c = 0; for (const k of N[id].childIds) c += 1 + subCount(k); return c; }

/* ── cromo: trilha, abas, números, legenda ─────────────────────────────── */
function drawChrome() {
  const c = document.getElementById('crumbs'); c.innerHTML = '';
  const mk = (lv, nm, t, here) => { const b = h('button');
    if (here) b.setAttribute('aria-current', 'true');
    b.appendChild(h('span', 'lv', lv)); b.appendChild(document.createTextNode(nm));
    b.onclick = () => enter(t); return b; };
  c.appendChild(mk('—', 'MUNDO', null, scope === null));
  for (const id of chain(scope)) {
    c.appendChild(h('i', null, '▸'));
    c.appendChild(mk(String(N[id].level), N[id].name, id, id === scope));
  }

  const tb = document.getElementById('tabs'); tb.innerHTML = '';
  for (const [k, lbl] of [['map', '◱ Mapa'], ['list', '☰ Localidades']]) {
    const b = h('button', null, lbl);
    b.setAttribute('aria-pressed', String(k === tab));
    b.onclick = () => { tab = k; if (k === 'map') query = ''; drawChrome(); drawSide(); };
    tb.appendChild(b);
  }

  const hs = document.getElementById('hudstats'); hs.innerHTML = '';
  const add = (v, l, cls) => { const d = h('div', 'st' + (cls ? ' ' + cls : ''));
    d.appendChild(h('b', null, v)); d.appendChild(h('span', null, l)); hs.appendChild(d); };
  const cnt = k => Object.values(N).filter(n => n.kind === k).length;
  const pend = ed.added.length + Object.keys(ed.patched).length + ed.removed.length
             + Object.keys(ed.rects).length;
  add(Object.keys(N).length, 'zonas');
  add(cnt('city'), 'cidades');
  add(cnt('district'), 'bairros');
  add(Object.values(N).reduce((a, n) => a + actsOf(n.id).length, 0), 'interações');
  add(pend, 'edições', pend ? 'warn' : '');

  const lg = document.getElementById('legend'); lg.innerHTML = '';
  lg.appendChild(h('h4', null, 'Categorias de interação'));
  for (const k of Object.keys(CAT)) {
    if (k === 'unclassified') continue;
    const d = h('div'); const i = h('i'); i.style.background = css(CAT[k].c);
    d.appendChild(i); d.appendChild(document.createTextNode(CAT[k].g + '  ' + CAT[k].n));
    lg.appendChild(d);
  }
}

/* ── ponteiro: clique, pan, zoom, arrasto de zona ───────────────────────── */
const pt = ev => { const r = SVG.getBoundingClientRect();
  return {x: view.x + (ev.clientX - r.left) / r.width * view.w,
          y: view.y + (ev.clientY - r.top) / r.height * view.h}; };
let drag = null;

SVG.addEventListener('pointerdown', ev => {
  const t = ev.target.closest('[data-id]');
  if (editing && t) { const id = t.dataset.id;
    drag = {id, r: Object.assign({}, rectOf(id)), start: pt(ev), resize: t.dataset.resize === '1'};
    SVG.setPointerCapture(ev.pointerId); return; }
  drag = {pan: true, start: pt(ev), v: Object.assign({}, view)};
  SVG.setPointerCapture(ev.pointerId);
});
SVG.addEventListener('pointermove', ev => {
  if (!drag) return;
  const p = pt(ev), dx = p.x - drag.start.x, dy = p.y - drag.start.y;
  if (drag.pan) { target = {x: drag.v.x - dx, y: drag.v.y - dy, w: view.w, h: view.h};
    view = Object.assign({}, target); applyView(); return; }
  const r = drag.r;
  ed.rects[drag.id] = drag.resize
    ? {x: r.x, y: r.y, w: Math.max(8, r.w + dx), h: Math.max(8, r.h + dy)}
    : {x: r.x + dx, y: r.y + dy, w: r.w, h: r.h};
  rebuild(); renderMap();
});
SVG.addEventListener('pointerup', ev => {
  if (!drag) return;
  const moved = Math.abs(pt(ev).x - drag.start.x) + Math.abs(pt(ev).y - drag.start.y);
  if (!drag.pan) { save(); drawChrome(); drawSide(); }
  if (moved < 2) {
    const t = ev.target.closest('[data-id]');
    const id = drag.id || (t && t.dataset.id);
    if (id && N[id]) { if (sel === id && N[id].childIds.length) enter(id);
      else { sel = id; renderMap(); drawSide(); } }
  }
  drag = null;
});
SVG.addEventListener('wheel', ev => {
  ev.preventDefault();
  const p = pt(ev), k = ev.deltaY > 0 ? 1.13 : 1 / 1.13;
  const nw = Math.min(W.world.w * 2.5, Math.max(20, view.w * k)), s = nw / view.w;
  target = {x: p.x - (p.x - view.x) * s, y: p.y - (p.y - view.y) * s, w: nw, h: view.h * s};
  view = Object.assign({}, target); applyView(); renderMap();
}, {passive: false});

document.addEventListener('keydown', ev => {
  if (ev.target.matches('input,textarea,select')) return;
  if (ev.key === 'Escape') {
    if (sel) { sel = null; renderMap(); drawSide(); }
    else if (scope !== null) enter(N[scope].parentId);
  }
});

/* ── barra de ferramentas ───────────────────────────────────────────────── */
document.getElementById('lens').onclick = e => {
  lens = !lens; e.currentTarget.setAttribute('aria-pressed', String(lens)); renderMap(); };
document.getElementById('edit').onclick = e => {
  editing = !editing; e.currentTarget.setAttribute('aria-pressed', String(editing));
  document.getElementById('map').classList.toggle('editing', editing); renderMap(); };

document.getElementById('export').onclick = () => {
  const out = {
    note: 'Gerado pelo editor de mapa. Salve como map/edits.json — worldbuild.py mescla no próximo build.',
    world: W.world,
    added: ed.added, patched: ed.patched, removed: ed.removed,
    rects: Object.fromEntries(Object.entries(ed.rects).map(([k, r]) =>
      [k, {x: +r.x.toFixed(2), y: +r.y.toFixed(2), w: +r.w.toFixed(2), h: +r.h.toFixed(2), edited: true}]))
  };
  const a = document.createElement('a');
  a.href = URL.createObjectURL(new Blob([JSON.stringify(out, null, 1)], {type: 'application/json'}));
  a.download = 'edits.json'; a.click();
};
document.getElementById('import').onclick = () => document.getElementById('file').click();
document.getElementById('file').onchange = e => {
  const f = e.target.files[0]; if (!f) return;
  const r = new FileReader();
  r.onload = () => { try {
    const j = JSON.parse(r.result);
    ed = Object.assign(blank(), {added: j.added || [], patched: j.patched || {},
      removed: j.removed || [], rects: j.rects || {}});
    save(); rebuild(); frame(scope); tick(); drawChrome(); drawSide();
  } catch (err) { alert('Arquivo inválido: ' + err.message); } };
  r.readAsText(f); e.target.value = '';
};
document.getElementById('reset').onclick = () => {
  if (!confirm('Descartar todas as edições locais? O que já está no repositório permanece.')) return;
  ed = blank(); save(); rebuild(); scope = null; sel = null;
  frame(null); tick(); drawChrome(); drawSide();
};
window.addEventListener('resize', renderMap);

/* ── partida ────────────────────────────────────────────────────────────── */
rebuild(); frame(null); tick(); drawChrome(); drawSide();
})();
