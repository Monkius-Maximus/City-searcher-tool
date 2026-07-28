# Lista de Assets — Etapa 1 (fatia vertical: exportador de mapa + duas cidades hero)

> **O que este documento é:** o contrato de produção de arte/áudio da Etapa 1. Cada item tem: o que é, formato, dimensão em pixels (ou unidade equivalente), quantidade na Etapa 1, e o *slot* que o exportador vai preencher.
>
> **O que este documento não é:** design de sistemas. Onde um asset depende de uma mecânica ainda não definida (ex.: quais "prédios" uma cidade tem), o slot está marcado `TBD-design` com a contagem estimada — a especificação técnica (tamanho/formato) já vale, só a lista de ícones muda.
>
> **Idioma:** o documento está em pt-BR porque vai para artistas e fornecedores. Todos os **IDs, nomes de arquivo, chaves de slot e caminhos permanecem em inglês/ASCII**, iguais aos de `gazetteer/`, `archetypes/` e `lenses/`.

---

## 0. Como usar este documento

1. **Sistemas / engine:** leia §1 (resoluções), §2 (as duas camadas), §8 (contrato do exportador).
2. **Artistas:** leia §3 (pipeline), §5 (nomes), §6 (specs por categoria), §10 (checklist de entrega).
3. **Produção:** leia §9 (escopo P0/P1/P2 com contagens e ordem de ataque).

A regra de ouro do repositório vale para arte igual vale para pesquisa: **reutilizar > variar > criar novo** (playbook, Parte 2, Passo 5). A §4 descreve como isso vira herança de assets.

---

## 1. Premissas de exibição — de onde saem os números

Base: Steam Hardware & Software Survey (levantamento contínuo; recorte de jun/2026). Os percentuais abaixo são **ordens de grandeza**, não valores contratuais — o que importa aqui é a hierarquia, e ela é estável há anos.

| Resolução primária | Participação aprox. | Consequência de produção |
|---|---|---|
| 1920×1080 (16:9) | ~51% | **Canvas de design da UI.** Tudo é desenhado e revisado aqui primeiro. |
| 2560×1440 (16:9) | ~21% e subindo | Precisa de assets @2x nítidos; é onde a UI @1x começa a "borrar". |
| 3840×2160 (16:9) | ~3% | Atendido por escala 2.0 da UI + mip de topo das artes. Não justifica arte dedicada. |
| 1366×768 (16:9) | poucos % | Notebooks de entrada — **peso relevante no mercado brasileiro.** Define o piso de legibilidade. |
| 1280×800 (16:10) | Steam Deck | Define a *safe area* vertical e o tamanho mínimo de alvo clicável. |
| 2560×1080 / 3440×1440 (21:9) | nicho | Não ganha arte própria, mas **as artes de fundo precisam cobrir 21:9 sem borda vazia.** |

**VRAM:** a faixa dominante é 8 GB, com 16 GB em crescimento. Todo o orçamento de textura da §7 assume **8 GB como alvo confortável e 6 GB como piso**.

### 1.1 Decisões derivadas (valem para todo o projeto)

| Decisão | Valor | Racional |
|---|---|---|
| Canvas de design da UI | **1920×1080** | Maioria absoluta dos jogadores. |
| Autoria dos assets de UI | **@2x (equivalente a 3840×2160)** | Downscale é limpo; upscale não é. Um único conjunto @2x serve 1080p, 1440p e 4K. |
| Atlas exportados | `@1x` e `@2x` | `@1x` para 1080p e abaixo; `@2x` acima de 1080p. Sem `@1.5x` (não compensa). |
| Resolução mínima suportada | **1280×720** | Abaixo disso a UI não é legível sem redesenho. |
| Escalas de UI oferecidas | 1.0 / 1.25 / 1.5 / 2.0 | Manual + auto por altura de tela. |
| Safe area de HUD | 5% das bordas | Protege 16:10 e 21:9. |
| Alvo clicável mínimo | **44×44 px @1080p** | Legível em 1366×768 e tocável no Deck. |
| Razão de referência do mundo | **16:9**, com fundo cobrindo até **21:9** | Ver §6.3: as artes de cidade são autoradas mais largas do que 16:9 de propósito. |
| Fonte | Latin Extended-A obrigatório | Acentuação PT-BR (ã, ç, õ, é) + nomes indígenas/africanos nos dossiês. Fonte sem esse subset é rejeitada na entrega. |

---

## 2. As duas camadas de visualização (EU4 → The Sims 4)

A referência que você trouxe define exatamente duas camadas com **necessidades de asset completamente diferentes**. Elas não compartilham pipeline.

### Camada A — Mapa Nacional ("província") · referência EU4

Um mapa do Brasil inteiro, navegável, onde cada unidade clicável é um nó do `gazetteer/br.json`. O EU4 resolve isso com **bitmaps de dados**, não com cenário: `provinces.bmp` (cada província é uma cor RGB única), `terrain.bmp`, `heightmap.bmp`, `rivers.bmp`, mais `definition.csv` (cor → ID), `adjacencies.csv` e `positions.txt` (onde fica o ícone da cidade, o rótulo, o porto). O mundo inteiro cabe em ~5632×2048 px.

Isso é **exatamente** o que o exportador precisa emitir. E é a parte barata: são máscaras de dados, não pinturas.

O painel de província do EU4 (o print que você mandou) é a segunda metade da camada A, e ela revela a economia de assets mais importante do projeto:

- a **faixa de arte no topo do painel** (a foto da floresta) não é da província — é do **tipo de terreno**. O EU4 tem dezenas de províncias compartilhando a mesma imagem.
- **No nosso sistema, esse slot é do arquétipo.** 13 ilustrações cobrem todas as ~5.570 cidades do Brasil. Essa é a "curva de saturação" do `docs/saturation-log.md` aplicada à arte.
- a grade de prédios, os ícones de status, o painel de Grandes Projetos e o tooltip são **UI pura** (§6.6), reutilizada em 100% das localidades.

### Camada B — Vista de Cidade ("entrar na cidade") · referência The Sims 4

Ao selecionar uma cidade hero, o jogo troca para uma vista aérea daquela cidade: um mapa-ilustração com **pins de local** (o "Municipal Muses / Museum" do print), rótulos, estados de hover/seleção e um **card de tooltip** ("Starter Home… click this lot to Move In"). O Sims 4 dessatura o que não é interativo e colore o que é — economia de leitura, não de arte.

Traduzido para o nosso jogo de futebol, entrar em Salvador mostra: o recorte Cidade Alta/Cidade Baixa, quatro distritos clicáveis, e 6 pins de landmark (Pelourinho, Elevador Lacerda, Feira de São Joaquim, Bonfim, Rio Vermelho, Dique do Tororó + Fonte Nova) — **que já estão escritos, com direção de arte e image prompt, em `dossiers/br.nordeste.ba.salvador.md`.** O dossiê já é o briefing de arte; ele só precisa de dimensões, e é isso que este documento adiciona.

### 2.1 O que muda entre as camadas

| | Camada A (nacional) | Camada B (cidade) |
|---|---|---|
| Unidade de dado | nó do gazetteer (região → estado → sub-região → cidade) | distrito + landmark do dossiê |
| Asset dominante | máscaras de ID + terreno + relevo | placa ilustrada + pins |
| Quem paga | **arquétipo** (13 kits cobrem o país) | **cidade hero** (uma a uma) |
| Custo marginal por cidade nova | ~zero (herda arquétipo) | alto (é conteúdo autoral) |
| Escala | 1 px ≈ 1 km | 1 px ≈ 1,5 m |

---

## 3. Decisão de pipeline: 2.5D pintado × 3D real

**Esta é a decisão que mais muda o orçamento da Etapa 1. Recomendação abaixo; se você discordar, só a §6.3 e a §6.9 mudam — o resto do documento vale igual.**

| | Trilha A — 2.5D pintado (recomendada) | Trilha B — 3D isométrico real |
|---|---|---|
| O que é a cidade | uma imagem aérea autorada + máscara de distritos + pins | cena 3D com kit modular de prédios |
| Custo por cidade hero | 1 ilustração + 1 máscara + 6 pins | 200-400 módulos, materiais, iluminação, otimização |
| Rotação de câmera | não (zoom e pan apenas) | sim |
| Hora do dia / estações | por variante de imagem ou LUT | dinâmico e grátis |
| Risco de cronograma | baixo | alto |

**Recomendo a Trilha A para a Etapa 1**, por três motivos concretos:

1. As duas referências que você escolheu **são 2.5D pintado**. O mapa-mundo do Sims 4 é uma ilustração com modelos pousados em cima; o mapa do EU4 é bitmap + shader. Nenhuma das duas é uma cidade 3D navegável.
2. **O repositório já está escrito para a Trilha A.** Todo arquétipo tem campo *"bird's-eye signature"* e um *image prompt template* terminando em `"Isometric game asset"`; todo landmark de dossiê tem seu próprio image prompt. Os briefings de arte da Trilha A já existem — só falta produzir.
3. A Trilha B só se paga quando o jogador desce **abaixo** da vista de cidade (dentro do CT, dentro do estádio). Isso é outro escopo; e a Trilha A não impede — os pins da §6.4 já são o ponto de entrada para essa descida no futuro.

> **Assunção registrada:** o restante deste documento assume Trilha A. A §6.9 lista o que a Trilha B exigiria a mais, para você comparar antes de fechar.

---

## 4. Princípio de herança de assets (o que barateia tudo)

Todo slot de asset resolve na seguinte ordem, e o **exportador implementa exatamente isso**:

```
cidade (específico)  →  variante de arquétipo  →  arquétipo base  →  padrão do país  →  placeholder gerado
```

Consequências práticas:

- Uma cidade `generic` **não recebe nenhum asset próprio**. Ela renderiza com o kit do arquétipo da sua sub-região (`archetypeId` já está no gazetteer). Mirassol, Bragança Paulista e Chapecó custam zero em arte.
- Uma cidade `generic+signature` recebe **exatamente um** asset próprio: a silhueta assinatura já descrita no gazetteer (`"signature": "hill-top colonial skyline"` para Olinda). Todo o resto herda.
- Uma cidade `hero` recebe o pacote completo da §6.3.
- Promover uma cidade de `generic` para `hero` **não quebra nada**: o ID não muda (invariante 5 do README), só passam a existir arquivos onde antes havia herança.

**Isto significa que o número de assets não cresce com o número de cidades — cresce com o número de arquétipos e de cidades hero.** 10 arquétipos + 3 variantes cobrem hoje 3 estados inteiros; 27 estados devem caber em ~25-30 arquétipos.

---

## 5. Convenção de nomes e pastas

Regra única: **o caminho do asset é derivado do ID do gazetteer, trocando `.` por `/`.** Nada de nomes livres.

```
assets/
  country/br/
    map/            provinces.png  terrain.png  heightmap.png  rivers.png  water.png
    paint/          albedo/{lod}/{x}_{y}.ktx2
  archetype/<archetype-id>/
    card/           base.png  wet.png  dry.png          # a faixa do painel (§6.2)
    terrain/        albedo.png  normal.png  rough.png
    palette/        lut.png
    silhouette/     signature.png
    audio/          ambience_day.ogg  ambience_night.ogg
  city/br/nordeste/ba/salvador/
    plate/          lod0/{x}_{y}.ktx2  lod1/…  lod2/…  lod3.png
    mask/           districts.png
    crest/          crest.svg  crest_256.png
    loading/        loading.png
    audio/          ambience.ogg
    landmark/<landmark-slug>/  card.png  icon.png
  lens/brasileirao-serie-a-2026/
    club/<club-slug>/    crest.svg  crest_256.png
    stadium/<stadium-slug>/  card.png  pin.png
    audio/          chant_<club-slug>.ogg
  ui/
    atlas/          hud@1x.png  hud@2x.png  hud.json
    icon/           …
    font/           …
    sfx/            …
```

Regras de nomenclatura:

- **minúsculas, ASCII, `-` como separador de palavra, `_` como separador de campo.** Sem espaço, sem acento, sem maiúscula. `sao-paulo`, nunca `São Paulo`.
- O slug de cidade é **o último segmento do ID do gazetteer**, idêntico, sem exceção.
- O slug de landmark sai do título da seção no dossiê, slugificado: *"Elevador Lacerda, Praça Tomé de Souza & Mercado Modelo"* → `elevador-lacerda`. **O exportador gera esse slug e grava no manifest** — o artista nunca inventa slug (§8).
- Sufixos reservados: `@1x`, `@2x`, `_lod0..3`, `_n` (normal), `_r` (roughness), `_m` (mask).

---

## 6. Especificações por categoria

### 6.1 Camada A — bitmaps de dados do mapa nacional

O Brasil tem bounding box quase quadrada (~4.400 km norte-sul × ~4.320 km leste-oeste), então textura quadrada é o encaixe natural.

| Asset | Formato | Dimensão | Bits/canal | Notas |
|---|---|---|---|---|
| `provinces.png` | **PNG-24 sem perda** | **4096×4096** | 8 RGB | Uma cor RGB única por nó clicável. **Nunca JPEG/WebP com perda. Nunca antialiasing. Nunca redimensionar com interpolação — só nearest.** Um pixel errado = província errada. |
| `terrain.png` | PNG-8 indexado | 4096×4096 | 8 (índice) | Índice → arquétipo/terreno. Paleta declarada no manifest. |
| `heightmap.png` | PNG grayscale **16-bit** | 4096×4096 | 16 | O EU4 usa 8-bit e sofre com banding em terreno plano; usamos 16-bit (custa 32 MB, resolve o problema de vez). |
| `rivers.png` | PNG-8 indexado | 4096×4096 | 8 | São Francisco é gameplay (arquétipo `vale-do-sao-francisco`, ponte gêmea Petrolina↔Juazeiro), não decoração. |
| `water.png` | PNG-8 | 4096×4096 | 8 | Máscara oceano/baía/açude. Baía de Todos os Santos e açudes do sertão precisam ser distinguíveis. |
| `normal.png` | derivado | 4096×4096 | 8 RGB | **Gerado pelo exportador a partir do heightmap.** Não é entrega de artista. |
| Pintura/albedo do mapa | KTX2/BC7 em tiles | **8192×8192** total, tiles de **512×512** (16×16 = 256 tiles) | — | Única camada "bonita" da camada A. Autorada em 8192² para o zoom máximo do mapa nacional. |

**Escala resultante:** 4096 px / 4.400 km ≈ **1,07 km por pixel**.

**Regra de província mínima:** um nó clicável precisa de **≥ 24×24 px** na máscara (≈ 26×26 km). Abaixo disso ele não vira polígono — vira **pin** na camada de UI (§6.6), com a mesma hitbox de 44×44 px em tela. Isso evita o problema clássico do EU4 com cidades-estado minúsculas e resolve Jericoacoara, Olinda e afins sem distorcer o mapa.

**Espaço de cor:** as máscaras (`provinces`, `terrain`, `rivers`, `water`, `heightmap`) são **dados, não imagem**. Entregar sem perfil ICC embutido, sem gamma, sem color management. Só o albedo é sRGB.

**Arquivos de dado que acompanham** (emitidos pelo exportador, §8, não pelo artista): `definition.csv`, `adjacency.csv`, `positions.json`.

### 6.2 Camada de arquétipo — o kit que paga o país inteiro

Por arquétipo (**10 base + 3 variantes = 13**). As variantes só entregam o que difere da base (`cariri-romeiro` é verde e tem o Horto; herda o resto do `sertao-nordestino`).

| Asset | Formato | Dimensão | Qtd/arquétipo | Notas |
|---|---|---|---|---|
| **Card de província** | PNG sRGB | **2048×512** (@2x) → exporta 1024×256 | 1 base | É a faixa de arte do painel (a "foto da floresta" do print do EU4). Proporção 4:1. Fonte direta: campo *bird's-eye signature* + *image prompt template* do arquivo do arquétipo. |
| Card — variantes sazonais | PNG sRGB | 2048×512 | 0-2 | Só onde a estação **é mecânica**: caatinga verde pós-chuva (`sertao-nordestino`), safra da cana (`zona-da-mata-canavieira`), ciclo da feira (`agreste-feirante`). Já listadas no `saturation-log.md`. |
| Terreno — albedo | PNG/KTX2, **tileável** | **1024×1024** | 1 | Tileável sem costura visível em 4 rotações. |
| Terreno — normal | PNG/KTX2 | 1024×1024 | 1 | |
| Terreno — roughness/AO | PNG/KTX2 grayscale | 1024×1024 | 1 | Empacotável em canais junto do normal. |
| **LUT de paleta** | PNG sem perda | **256×16** (LUT 3D 16³ desdobrada) | 1 | Materializa o campo *Palette* do arquétipo (prata-cinza da caatinga, ocre, azul do açude). Aplicada como grade de correção de cor — muda a identidade da região inteira num arquivo de 12 KB. |
| **Silhueta assinatura** | PNG-32 com alpha | **1024×1024** | 1 | O "one-glance identity" da regra 4 do playbook (Parte 3). Capela branca no morro, açude, grade irrigada. |
| Ambiência dia | OGG Vorbis q6, estéreo, 48 kHz | loop de **90-120 s** | 1 | |
| Ambiência noite | OGG Vorbis q6, estéreo, 48 kHz | loop de 90-120 s | 1 | |

**Total do kit de arquétipo (13 arquétipos):** ~13 cards + ~30 texturas de terreno + 13 LUTs + 13 silhuetas + 20 loops de ambiência ≈ **89 arquivos** cobrindo os 3 estados já mapeados e pré-pagando PB, RN, PI, MA, AL, SE e o MATOPIBA.

### 6.3 Camada B — vista de cidade

#### 6.3.1 Cidade `hero` (pacote completo)

Enquadramento: cada cidade hero cobre uma pegada de **~12 × 6,75 km** do território real, comprimida conforme a regra "distorça a escala, nunca a identidade" (playbook, Parte 3).

| Asset | Formato | Dimensão | Qtd | Notas |
|---|---|---|---|---|
| **Placa da cidade — LOD0** | KTX2/BC7 em tiles de 512×512 | **8192×4608** (16×9 = 144 tiles) | 1 | ≈ **1,46 m/px**. Um estádio de 250 m mede ~171 px — legível. |
| Placa — LOD1 / LOD2 | KTX2/BC7 | 4096×2304 / 2048×1152 | 2 | Pirâmide de mip por nível de zoom. |
| Placa — LOD3 / thumbnail | PNG | 1024×576 | 1 | Serve também de miniatura no seletor de cidade. |
| **Extensão 21:9** | — | a placa é autorada em **8192×4608 útil dentro de um canvas de 9728×4608** | — | Os 768 px de cada lado só aparecem em ultrawide. Sem isso, 21:9 mostra borda vazia. Custo de arte: baixo (é periferia da cidade). |
| **Máscara de distritos** | PNG-8 indexado, sem perda, sem AA | **2048×1152** | 1 | Um índice por distrito, 3-4 por cidade, **já listados nos dossiês**: Salvador tem 4 (Centro Histórico, Liberdade/Curuzu, Itapagipe, Orla Atlântica), Rio tem 3 (Centro & Zona Portuária, Lapa & Santa Teresa, Zona Sul). Mesmas regras da §6.1: nearest, sem ICC. |
| Brasão / ícone da cidade | **SVG** + PNG 256/128/64/32 | vetorial | 1 | 32 px é o pin no mapa nacional; 256 px é o painel. |
| Arte de loading | PNG sRGB | **2560×1440** | 1 | Cobre até 1440p; downscale para 1080p. |
| Ambiência da cidade | OGG Vorbis q6, estéreo | loop 120 s | 1 | Sobrepõe (não substitui) a ambiência do arquétipo. |
| Camadas de evento *(P1)* | PNG-32 com alpha, mesmo enquadramento da placa | 4096×2304 | 0-3 | O dossiê de Salvador pede explicitamente: "Jan-Fev a cidade se transforma visualmente (Lavagem → Iemanjá → Carnaval) — planejar skins de distrito". São overlays sobre a placa, não placas novas. |

#### 6.3.2 Cidade `generic+signature`

| Asset | Formato | Dimensão | Qtd |
|---|---|---|---|
| Silhueta assinatura | PNG-32 com alpha | **1024×1024** | 1 |
| Card de província (override) | PNG sRGB | 2048×512 | 1 |

Nada mais. São 6 cidades hoje (Olinda, Caruaru, Petrolina, Juazeiro, Jericoacoara, Juazeiro do Norte) — **12 arquivos no total**, e o campo `"signature"` de cada uma no gazetteer já é o briefing.

#### 6.3.3 Cidade `generic`

**Zero assets.** Renderiza 100% herdado do arquétipo da sub-região (§4).

### 6.4 Landmarks (os "lotes" da vista de cidade)

Um por landmark de dossiê. Rio tem 5-6, Salvador tem 6 — **e os 12 já vêm com image prompt escrito.**

| Asset | Formato | Dimensão | Notas |
|---|---|---|---|
| **Card de landmark** | PNG sRGB | **1024×576** (16:9) | A arte do tooltip/painel ao selecionar o pin. Equivalente ao painel "Great Projects" do EU4 e ao card "Starter Home" do Sims. |
| **Ícone de pin** | PNG-32 com alpha | **128×128** (@2x) → exporta 64×64 | Desenhado dentro de um círculo seguro de 96 px; a "gota" do pin é do template de UI (§6.6), não do ícone. |
| Recorte destacado *(opcional, P1)* | PNG-32 com alpha | 2048×2048 | Para landmarks que ganham realce em cima da placa quando selecionados (Elevador Lacerda, Cristo, Horto). |

**Estados do pin** (assets de UI, autorados uma vez e usados por todos os landmarks — é o que o Sims faz com dessaturado/colorido):

`default` · `hover` · `selected` · `locked` · `has-event` — 5 estados × 1 template = 5 assets, não 5 por landmark.

### 6.5 Camada de lente — Brasileirão Série A 2026

Descartável por temporada (invariante 3 do README: lentes são snapshots). Nunca misturar com assets de cidade.

| Asset | Formato | Dimensão | Qtd total | Notas |
|---|---|---|---|---|
| Escudo de clube | **SVG** + PNG 512/256/128/64/32 | vetorial | **20** | 20 clubes na lente. Escudos são marcas registradas — ver §10.3. |
| Paleta de torcida | dado (JSON), não arte | 2-3 cores hex | 20 | Alimenta a mecânica de "cores da torcida tomam as ruas" do dossiê de Salvador. |
| Card de estádio | PNG sRGB | **1024×576** | **19** | 19 estádios únicos para 20 clubes (Fla e Flu dividem o Maracanã). |
| Pin de estádio | PNG-32 alpha | 128×128 | 19 | |
| Bed de multidão | OGG Vorbis, estéreo | loop 60 s | **4** | Genéricos por intensidade (vazio / normal / cheio / decisivo). Servem os 19 estádios. |
| Canto de torcida | OGG Vorbis, estéreo | one-shot 10-20 s | 6 na P0 | Só os clubes das 2 cidades hero da P0: Flamengo, Fluminense, Botafogo, Vasco, Bahia, Vitória. |
| Overlay de clássico | PNG-32 alpha | 1920×1080 | 6 *(P1)* | Um por clássico já mapeado no `lenses/*.json` (Fla-Flu, Paulistas, Mineiro, Grenal, Atletiba, Ba-Vi). |

### 6.6 UI

Autorada **@2x**, exportada em `@1x` e `@2x`. Atlas de **2048×2048** (4096×4096 só se estourar), com JSON de recorte.

| Grupo | Itens | Dimensão (@1x) | Notas |
|---|---|---|---|
| **Molduras nine-slice** | ~10 | bordas de 24-48 px | O visual "painel ornamentado" das duas referências. Nine-slice é obrigatório: um painel serve de 320 px a 1200 px de largura sem esticar o ornamento. |
| Barra superior / HUD | ~8 | altura 48 px | Ancorada na safe area de 5%. |
| **Painel de localidade** | 1 layout + ~12 partes | 640×900 (base) | O painel do print do EU4, traduzido: nome + trilha (região › estado › sub-região), card de arquétipo 1024×256, linhas de estatística, grade de prédios. |
| Ícones de estatística | ~12 `TBD-design` | 32×32 e 64×64 | Espec. técnica fechada; a lista depende do design de sistemas. |
| **Ícones de "prédio"** | ~16-24 `TBD-design` | 64×64 | A grade 4-colunas do print. Para futebol: CT, base, centro médico, arquibancada, escola… a definir. Precisam de estado "não construído" (overlay X) — 1 overlay, não 24. |
| Ícones de ação/navegação | ~18 | 32×32 | Zoom, camadas de mapa, entrar/sair da cidade, voltar. |
| Estados de pin | 5 | 128×128 | Ver §6.4. |
| Placa de rótulo | 1 nine-slice | altura 28 px | O rótulo "Municipal Muses / Museum" do print do Sims. |
| Card de tooltip | 1 nine-slice + 3 variantes | 360×220 | |
| Cursores | 4 | 32×32 e 64×64 | |
| **Fontes** | 2 famílias, 3 pesos cada | — | **Latin Extended-A obrigatório.** Uma display (títulos/painéis) e uma UI (números/listas, precisa de algarismos tabulares para as colunas de estatística). Licença para jogo comercial verificada antes do uso. |

### 6.7 Áudio — resumo consolidado

| Tipo | Formato de entrega | Fonte | Qtd P0 |
|---|---|---|---|
| Ambiência de arquétipo (dia/noite) | OGG Vorbis q6 estéreo 48 kHz, loop sem clique | WAV 48 kHz/24-bit | 20 |
| Ambiência de cidade hero | OGG Vorbis q6 estéreo, loop 120 s | WAV 48/24 | 2 (P0) |
| Bed de multidão | OGG Vorbis q6 estéreo, loop 60 s | WAV 48/24 | 4 |
| Canto de torcida | OGG Vorbis q6 estéreo, one-shot | WAV 48/24 | 6 |
| Tema musical por macrorregião | OGG Vorbis q8 estéreo, 2-3 min | WAV 48/24, **stems separados** | 5 *(P1)* |
| SFX de UI | WAV 48 kHz/24-bit **mono** (a engine comprime) | — | ~25 |

Regras: **-16 LUFS** integrado para música e ambiência, **-1 dBTP** de pico. Loops entregues com o ponto de emenda validado (sem clique, sem respiro fantasma). Nada de MP3 em nenhuma etapa da cadeia.

> **Nota de dignidade (playbook, Parte 4):** ambiência de terreiro, romaria e ritual entra como **presença sonora do entorno**, gravada/licenciada com consentimento e crédito — nunca como sample de cerimônia recortado. Vale a mesma regra do dossiê: adjacência devocional é jogável, cerimônia não é performável pelo jogador.

### 6.8 Vídeo

Vídeo é o formato mais caro e o menos necessário nesta etapa. **Na P0: nenhum.**

A transição "mapa nacional → entrar na cidade" deve ser **efeito de engine** (zoom + cross-fade entre o LOD3 da placa e a máscara de distritos), não vídeo pré-renderizado — vídeo quebra em resoluções diferentes, não pode partir da província que o jogador clicou, e pesa 100× mais.

| Asset | Formato | Dimensão | Fase |
|---|---|---|---|
| Loop "cartão-postal" da cidade | WebM VP9, ou H.264 MP4 alto perfil | 1280×720 @30 fps, 6-10 s, **loop perfeito, sem áudio** | P2 |
| Abertura / logo | WebM VP9 + MP4 fallback | 1920×1080 @30 fps | P2 |

Se a engine for Unreal, adicionar entrega paralela em **Bink**; se for Unity, **VP8/VP9 em WebM** é o caminho seguro multiplataforma.

### 6.9 3D — só se a Trilha B for escolhida (§3)

Não faz parte da P0 na recomendação. Registrado para comparação de orçamento:

| Asset | Formato | Orçamento |
|---|---|---|
| Módulos de prédio por arquétipo | **glTF 2.0 (.glb)**, Y-up, **escala em metros**, PBR metal-rough | 300-800 tris/módulo · textura 512² · **~40-80 módulos por arquétipo** |
| Props | .glb | 100-400 tris · atlas 1024² compartilhado · ~60 por arquétipo |
| Landmark herói | .glb | 8-20k tris · textura 2048² · LOD0-2 · 1 por landmark de dossiê |
| Estádio | .glb | 15-30k tris · 2048² · 1 por estádio da lente |

Ordem de grandeza: a Trilha B multiplica a contagem de assets da Etapa 1 por **~8-10×**. É por isso que a recomendação é A.

---

## 7. Tabela mestre de regras técnicas

| Regra | Valor |
|---|---|
| Espaço de cor — arte | sRGB, 8 bits/canal na entrega, **16 bits no arquivo-fonte** |
| Espaço de cor — máscara/dado | **nenhum**. Sem ICC, sem gamma, sem color management |
| Reamostragem de máscara | **nearest neighbor apenas.** Bilinear/bicúbico corrompe IDs |
| Compressão com perda em máscara | **proibida** (JPEG, WebP lossy, DXT em máscara de ID) |
| Potência de dois | obrigatória para tudo que vira textura de GPU |
| Compressão de GPU | **BC7** (albedo/UI desktop), **BC5** (normal), **BC4** (grayscale). Container **KTX2/BasisU** |
| Mipmaps | gerados no build, não entregues |
| Alpha | **premultiplied não** — alpha reto (straight), a engine converte |
| Arquivo-fonte | PSD/TIFF em camadas **é entregável**, vai para `source/` fora do build |
| Nomes | ASCII minúsculo, `-` e `_`, sem espaço/acento (§5) |
| Áudio-fonte | WAV 48 kHz / 24-bit. **MP3 proibido em qualquer etapa** |
| Loudness | -16 LUFS integrado, -1 dBTP de pico |
| Orçamento de VRAM (alvo) | ≤ 1,5 GB de textura residente em 1080p; alvo 8 GB, piso 6 GB |

**Orçamento estimado da camada de mapa** (para conferência): albedo 8192² BC7 ≈ 64 MB + mips ≈ 85 MB; máscaras 4096² ≈ 16 MB cada em RAM (não vão para VRAM — são consultadas em CPU); placa de cidade hero 8192×4608 BC7 ≈ 38 MB + mips ≈ 50 MB, **uma residente por vez**. Folgado dentro do alvo.

---

## 8. Contrato do exportador — a parte que destrava o desenvolvimento

Esta lista **não deve virar uma planilha paralela que apodrece**. Ela é um *esquema de slots* que a ferramenta valida. É isso que permite começar a programar antes de qualquer arte existir.

### 8.1 O que a ferramenta lê

`gazetteer/br.json` · `archetypes/*.md` · `dossiers/*.md` · `lenses/*.json`

### 8.2 O que a ferramenta emite

| Saída | Conteúdo |
|---|---|
| `build/map/definition.csv` | `r,g,b,place_id,name,level,parent_id` — o de-para cor↔ID (padrão EU4) |
| `build/map/adjacency.csv` | vizinhança + conexões especiais (ex.: ponte gêmea `petrolina`↔`juazeiro`, ferry Salvador↔Recôncavo) |
| `build/map/positions.json` | por localidade: âncora de rótulo, âncora de ícone, âncora de pin de estádio, âncora de porto |
| `build/db/places.json` | árvore achatada **com herança de arquétipo já resolvida** (cidade generic carrega o `archetypeId` da sub-região) |
| `build/db/landmarks.json` | landmarks extraídos dos dossiês, com slug gerado, tipo, função de gameplay e image prompt |
| `build/db/lens.<id>.json` | overlay da lente, separável (invariante 3) |
| **`build/assets.manifest.json`** | **o coração:** todo slot esperado, seu caminho, seu status, sua origem de herança |
| `build/report.md` | relatório de validação (§8.5) |

### 8.3 Formato do slot

Chave: `<scope>.<slot>[.<qualifier>]` — `scope` ∈ `country` `archetype` `city` `landmark` `club` `stadium` `ui`.

```json
{
  "slotId": "city.plate.lod0",
  "owner": "br.nordeste.ba.metropolitana-de-salvador.salvador",
  "path": "assets/city/br/nordeste/ba/salvador/plate/lod0/",
  "spec": { "kind": "image-tiles", "width": 8192, "height": 4608,
            "tile": 512, "format": "ktx2/bc7", "colorspace": "srgb" },
  "status": "missing",
  "resolvedFrom": null,
  "brief": "dossiers/br.nordeste.ba.salvador.md#visual-design-notes",
  "phase": "P0"
}
```

- `status` ∈ `final` · `wip` · `placeholder` · `missing` · `inherited`
- `resolvedFrom` grava **de onde o asset foi herdado** quando `status: inherited` (§4). Ex.: Mirassol resolve `city.card` de `archetype/cerrado-agroindustrial`.
- `brief` aponta para a âncora exata no dossiê ou arquétipo. **O artista nunca recebe briefing solto — recebe o link para a fonte canônica.** É isso que impede a arte de divergir da pesquisa.

### 8.4 Placeholders gerados (o item mais importante da P0)

Para **todo** slot com `status: missing`, a ferramenta gera um placeholder programático **com as dimensões finais corretas**:

- imagem → cor sólida tirada do campo *Palette* do arquétipo + o `slotId` e o `place_id` escritos por cima, em contraste alto
- áudio → silêncio com a duração especificada + um beep de 400 ms marcando o início do loop
- máscara → cores geradas deterministicamente a partir do hash do `place_id`

Assim o mapa **abre na engine, navega, clica, entra na cidade e volta** antes de existir um único pixel de arte final. A arte substitui placeholder por placeholder, sem nenhuma mudança de código. Esse é o mecanismo que responde ao seu "para que possamos progredir no desenvolvimento".

### 8.5 Validações que o exportador roda (falham o build)

1. Toda cor em `provinces.png` existe em `definition.csv` e vice-versa
2. Nenhuma província clicável abaixo de 24×24 px (vira pin, com aviso no relatório)
3. Todo `archetypeId` referenciado no gazetteer tem arquivo em `archetypes/`
4. Todo `dossier` não-nulo aponta para arquivo existente
5. Todo `cityId` da lente existe no gazetteer *(hoje passa: 11/11)*
6. Toda cidade `hero` tem dossiê **ou** está listada como pendente no `researchQueue` da lente
7. Toda cidade `generic+signature` tem campo `signature` preenchido
8. Máscaras: sem ICC, sem antialiasing, dimensão potência de dois
9. **Separabilidade da lente:** remover `lenses/` e reconstruir precisa gerar um build válido (invariante 3 do README)
10. Todo asset `final` bate com o `spec` do slot (dimensão, formato, espaço de cor)

---

## 9. Escopo por fase

### P0 — Fatia vertical (esta etapa)

Objetivo: **abrir o Brasil, clicar uma província, entrar em Salvador ou no Rio, ver os landmarks, sair.** Tudo o mais é placeholder gerado.

| Bloco | Itens | Qtd |
|---|---|---|
| Mapa nacional (§6.1) | 5 máscaras + 1 albedo em tiles | **6** |
| Arquétipos (§6.2) | 13 cards + 30 texturas de terreno + 13 LUTs + 13 silhuetas + 20 ambiências | **89** |
| Cidades hero (§6.3.1) — **Rio + Salvador** | 2 pirâmides de placa + 2 máscaras + 2 brasões + 2 loadings + 2 ambiências | **10** |
| Landmarks (§6.4) — 12 já escritos nos dossiês | 12 cards + 12 pins | **24** |
| Lente Brasileirão (§6.5) | 20 escudos + 5 estádios das cidades hero (card+pin) + 4 beds + 6 cantos | **40** |
| UI (§6.6) | molduras, painel de localidade, ícones, estados de pin, cursores, 2 fontes | **~85** |
| SFX de UI (§6.7) | click, hover, abrir/fechar painel, zoom, selecionar, entrar/sair da cidade, erro, notificação | **~25** |
| Vídeo | nenhum | **0** |
| **Total P0** | | **≈ 280 arquivos** |

Ordem de ataque recomendada: **(1)** exportador + placeholders → **(2)** máscaras do mapa nacional → **(3)** UI → **(4)** kits de arquétipo → **(5)** Salvador (o dossiê mais completo do repo) → **(6)** Rio → **(7)** lente.

### P1 — Completar a lente e o Nordeste

- 9 cidades hero restantes da lente (São Paulo é a prioridade: 3 clubes) — placa + máscara + brasão + loading + ambiência + 5-6 landmarks cada
- 14 cards e pins de estádio restantes
- 6 cidades `generic+signature` (12 arquivos)
- Cards sazonais de arquétipo (caatinga verde, safra da cana, ciclo da feira)
- Camadas de evento das cidades hero (Carnaval, Lavagem, Iemanjá)
- 5 temas musicais por macrorregião
- 6 overlays de clássico

### P2 — Expansão

- Arquétipos de novas macrorregiões (Amazônia p/ Belém, Sul p/ Porto Alegre, Sudeste interior) — a curva de saturação do `docs/saturation-log.md` prevê custo cheio aqui, porque são famílias culturais novas
- Loops "cartão-postal" em vídeo
- Abertura
- Trilha B (3D), se e quando o jogador for descer abaixo da vista de cidade

---

## 10. Checklist de entrega

### 10.1 Todo asset

- [ ] Caminho e nome exatamente conforme §5 (derivados do ID do gazetteer)
- [ ] Dimensão exata do `spec` do slot — nem maior "por segurança", nem menor
- [ ] Regras técnicas da §7 respeitadas (espaço de cor, potência de dois, sem perda onde exigido)
- [ ] Arquivo-fonte em camadas incluído em `source/`
- [ ] `status` atualizado no manifest

### 10.2 Portões de qualidade (playbook, Parte 4 — valem para arte, não só para pesquisa)

- [ ] **Modernidade:** o lugar está representado no presente. Pelo menos um elemento que não caberia num mapa de época (parque eólico, cidade agro em grade, arena moderna, orla requalificada)
- [ ] **Dignidade:** comunidades são protagonistas do próprio espaço, nunca cenário; religião viva, não pageantry patrimonial; áreas economicamente marginalizadas com complexidade, nunca como set de "zona de perigo"
- [ ] **Silhueta:** passa no teste de um segundo? A escarpa Alta/Baixa de Salvador lê à primeira vista em vista aérea? (playbook, Parte 3, regra 4)
- [ ] **Fidelidade ao dossiê:** a paleta bate com a seção *Visual Design Notes*? Salvador é mais saturada que o Rio, como o dossiê exige?

### 10.3 Jurídico (bloqueia entrega)

- [ ] **Escudos e nomes de clube são marcas registradas.** Os 20 escudos da lente exigem licença da CBF/clubes **ou** substituição por marcas fictícias. Definir antes de encomendar arte — refazer 20 escudos depois é retrabalho puro.
- [ ] Nomes de estádio com naming rights (Allianz Parque, Neo Química Arena, Arena MRV, Ligga Arena) têm titular adicional
- [ ] Fontes licenciadas para jogo comercial (não só para desktop)
- [ ] Áudio de campo gravado/licenciado com consentimento e crédito, especialmente ambiência de terreiro, romaria e feira

---

## Anexo — Pendências que dependem de você

Estas não bloqueiam o exportador nem a arte de arquétipo; bloqueiam decisões pontuais mais adiante.

1. **Trilha A ou B** (§3). Recomendação: A. Muda §6.3 e §6.9.
2. **Engine.** Muda só a coluna de container (KTX2 vs. formato nativo) e o codec de vídeo da P2.
3. **Lista de "prédios"** da grade do painel de localidade (§6.6). Espec. técnica já fechada em 64×64; falta a lista.
4. **Licenciamento dos clubes** (§10.3). Quanto antes, melhor.
5. **Pegada geográfica de cada cidade hero.** Fixei ~12 × 6,75 km como padrão (§6.3.1), o que serve bem Salvador e o Rio. Cidades muito lineares (Santos, Jericoacoara) podem precisar de outro enquadramento — decidir cidade a cidade na P1, sem mudar a resolução da placa.
