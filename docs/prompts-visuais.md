# Prompts visuais — sistematização do produto

Conjunto de prompts para gerar "prints" do produto final em geradores de imagem, organizados para que você possa **comparar como diferentes IAs imaginam o mesmo problema** e extrair pontos fortes e fracos de cada leitura.

Os prompts estão **em inglês** de propósito: praticamente todos os geradores (Midjourney, Imagen, Flux, SDXL, DALL·E, Firefly) foram treinados majoritariamente em legendas em inglês e perdem fidelidade em português — principalmente em vocabulário de UI. O texto ao redor fica em português.

---

## 0. Antes de rodar — três coisas que economizam tempo

**1. Gerador de imagem não escreve UI.** Todo texto sai truncado ou inventado. Duas estratégias, ambas úteis:

- **`--no text`** (ou "no text, no lettering, no labels"): você avalia **composição, hierarquia, paleta e densidade**. É o modo mais honesto para julgar layout.
- **deixar o texto sair torto**: você avalia **onde a IA acha que a informação deve morar**. O conteúdo é lixo, a posição é informação real.

Rode os dois. A divergência entre eles é reveladora.

**2. Fixe o eixo de comparação.** Se cada prompt mudar estilo, enquadramento e conteúdo ao mesmo tempo, você não consegue atribuir a diferença ao gerador. Use o **espinha de estilo** da §1 sem alterar nenhuma palavra, e mude só o bloco de conteúdo.

**3. O que estamos testando não é beleza.** É se a estrutura de contenção (país → cidade → bairro → local) **lê visualmente sem legenda**. Um print lindo em que você não sabe em que nível está é um print reprovado.

---

## 1. Espinha de estilo (colar em TODOS os prompts, sem editar)

```
Style: video game UI screenshot, isometric bird's-eye map view, semi-realistic
painterly game art, warm earthy palette with ochre and dendê-gold accents,
readable graphic silhouettes, high information density but calm composition,
subtle depth of field, no photorealism, no cartoon exaggeration, 4k game
capture look.
```

E o negativo, também fixo:

```
Negative: photorealistic photograph, stock photo, blurry, watermark, signature,
distorted faces, generic fantasy medieval, purple-blue gradient, neon cyberpunk,
oversaturated HDR, favela as slum stereotype, poverty tourism framing, colonial
nostalgia, tourists as main subject, cluttered unreadable UI.
```

> **Sobre as duas últimas linhas do negativo:** não são estética, são o portão de dignidade do playbook (Parte 4). Geradores de imagem puxam com força para "favela = perigo/miséria" e "Brasil colonial pitoresco" porque é o que domina os datasets. Se você tirar essas cláusulas, vai ver na prática — vale rodar uma vez sem elas só para saber contra o que você está trabalhando.

---

## 2. Bloco A — as telas do produto

O produto tem seis telas. Gere as seis no mesmo gerador antes de trocar de gerador.

### A1 · Mapa nacional (visão estratégica)

**Proporção:** 16:9 · **Serve para:** validar a camada EU4

```
Video game UI screenshot: a stylized strategic map of Brazil seen from above,
the country divided into visible provinces with soft colored borders, each
region tinted by a different landscape identity — silver-grey thorny scrubland
in the northeast interior, deep green rainforest in the north, geometric
agricultural grids in the center-west, dense coastal urban clusters along the
eastern shore. Small circular city markers of varying sizes sit on the map,
a few marked with a glowing football badge. A thin ornate side rail of controls
frames the left edge. Rivers thread across the terrain. Late afternoon light
rakes across the relief.
[ESPINHA DE ESTILO]
[NEGATIVO]
```

**O que olhar:** as regiões se distinguem sem legenda? Dá para dizer onde termina o sertão e começa o litoral? **Bandeira vermelha:** mapa bonito em que todas as regiões parecem a mesma coisa — significa que a identidade de arquétipo não está passando.

---

### A2 · Painel de localidade aberto sobre o mapa

**Proporção:** 16:9 · **Serve para:** o painel de província do EU4 traduzido

```
Video game UI screenshot: a strategic map of northeastern Brazil partially
covered by an open information panel on the left third of the screen. The panel
has an ornate dark frame and contains, from top to bottom: a wide horizontal
landscape illustration strip showing a coastal city with reefs and pastel
colonial rooftops, a row of small numeric stat readouts with icons, a four-
column grid of small square building icons where some are dimmed and crossed
out, and a lower section with two football club crests side by side. A second
small floating tooltip panel overlaps the map on the right. The map behind
shows a coastal region with a highlighted province outlined in gold.
[ESPINHA DE ESTILO]
[NEGATIVO]
```

**O que olhar:** a faixa de paisagem no topo domina o painel? Ela deveria — é o slot `archetype.card` (2048×512, §6.2 da lista de assets) e é o que dá identidade de graça a centenas de cidades.

---

### A3 · Vista de cidade — Salvador

**Proporção:** 16:9 · **Serve para:** a camada Sims 4. **A tela mais importante do conjunto.**

```
Video game UI screenshot: an illustrated bird's-eye map of a Brazilian coastal
city built on a dramatic cliff that splits it into an upper city and a lower
city, connected by a tall white art-deco elevator tower. A vast blue bay on one
side with small boats, an ocean shoreline on the other. The city is divided
into four gently tinted district zones with soft glowing boundaries. Floating
map pins with small circular icons mark individual landmarks: a hilltop white
church, a dense market of corrugated roofs by the water, a colorful colonial
quarter of steep streets, a modern stadium bowl beside a round lake. One pin is
highlighted and opens a small card showing a painted view of that landmark.
Areas outside the selected district are gently desaturated.
[ESPINHA DE ESTILO]
[NEGATIVO]
```

**O que olhar:**
- A escarpa Alta/Baixa lê à primeira vista? É o "one-glance identity" que o dossiê de Salvador exige.
- Os quatro distritos são distinguíveis **sem** as bordas brilhantes? Se só a borda separa, a arte não está fazendo o trabalho.
- A dessaturação do que não está selecionado apareceu? É o truque do Sims 4 e é economia de leitura pura.

---

### A4 · Dentro de um bairro

**Proporção:** 16:9 · **Serve para:** provar que existe um nível abaixo da cidade

```
Video game UI screenshot: a closer isometric view of a single historic district
inside a larger city map — steep cobbled streets of intensely colorful pastel
baroque facades in blue, pink and yellow, small plazas, twin-towered churches.
Individual buildings are marked with small floating interaction pins, three of
them highlighted. A circle of drummers performs in one plaza with a crowd
around them. A breadcrumb strip of nested location names runs along the top of
the screen. The surrounding city is visible but faded at the edges of the frame.
[ESPINHA DE ESTILO]
[NEGATIVO]
```

**O que olhar:** a trilha de navegação no topo apareceu? É a única pista visual de que você está **dentro de** algo. Se a IA não a colocou espontaneamente, é sinal de que a hierarquia precisa ser mais explícita no design real.

---

### A5 · Card de local

**Proporção:** 16:9 · **Serve para:** o slot `venue.card` (1024×576)

```
Video game UI screenshot, close-up of a single interface card floating over a
blurred city map background. The card shows a painted illustration of a white
church with light blue trim on a hilltop above a bay peninsula, its iron fence
covered in thousands of tiny colorful ribbons fluttering in the wind, a
procession of people dressed in white filling the long avenue toward it. Below
the illustration, a compact block of small stat rows with icons, and two action
buttons at the bottom. Ornate dark frame around the card.
[ESPINHA DE ESTILO]
[NEGATIVO]
```

**Nota:** a descrição da igreja saiu literalmente do campo *Image Prompt* da Igreja do Bonfim no dossiê de Salvador. **Todos os 12 landmarks de Rio e Salvador já têm esse campo escrito** — dá para gerar os 12 trocando só o parágrafo do meio.

---

### A6 · Dia de jogo (overlay de lente)

**Proporção:** 16:9 · **Serve para:** provar que a lente é uma camada, não um jogo à parte

```
Video game UI screenshot: the same illustrated bird's-eye city map, now
transformed by a match-day state — two rival supporter colors flood different
parts of the city, red-and-black crowds streaming from the north, blue-red-white
crowds from the center, converging on a modern horseshoe stadium beside a round
urban lake that holds tall colorful sculptural figures standing on the water.
Streets show flags and banners. A slim top bar displays a countdown and two club
crests facing each other. Transport routes glow faintly across the map.
[ESPINHA DE ESTILO]
[NEGATIVO]
```

**O que olhar:** dá para reconhecer que é **a mesma cidade** de A3? Tem que dar. Se a IA gerou outra cidade, o overlay virou reskin — exatamente o que o invariante 3 do README proíbe.

---

### A7 · Transição mapa → cidade

**Proporção:** 21:9 · **Serve para:** o momento "entrar na cidade"

```
Video game UI screenshot mid-transition: a strategic country map zooming
downward into a single city, motion blur radiating from the center, the province
borders dissolving as the illustrated city plate resolves into focus underneath,
map pins scaling up from tiny dots into full landmark markers. Sense of
descending altitude.
[ESPINHA DE ESTILO]
[NEGATIVO]
```

**Lembrete:** isso vira **efeito de engine**, não vídeo (§6.8 da lista de assets). O print serve para dirigir o efeito, não para virar asset.

---

## 3. Bloco B — os três verbos, mesma cidade

Este é o bloco que responde à pergunta da sprint passada: **qual jogo isso deveria ser.** Mesma Salvador, três loops. Rode os três lado a lado e veja qual te dá vontade de jogar.

### B1 · Tycoon de dia de jogo

```
Video game UI screenshot: an illustrated bird's-eye city map used as a logistics
board. Transport lines pulse between districts with small capacity numbers,
fan-zone areas are outlined as placeable colored footprints, crowd density is
shown as a soft heat gradient thickening near a stadium. A bottom toolbar of
placement tools. A right-side checklist panel with pass/fail indicators. Warning
icons hover over two congested streets.
[ESPINHA DE ESTILO]
[NEGATIVO]
```

**Força:** usa direto o que os dossiês já têm (bairros, transporte vertical, mega-eventos). **Fraqueza:** a cidade vira planilha; a cultura que você pesquisou vira número.

### B2 · Life-sim / RPG

```
Video game UI screenshot: an illustrated bird's-eye city map with a small
character avatar standing in a colorful colonial quarter, a radial menu of
activity icons open around them. Portrait cards of three local NPCs line the
bottom edge with relationship meters. A day-cycle dial and a weekly calendar sit
in the top corner. Warm evening light, string lights over a plaza, a drum circle
with a crowd.
[ESPINHA DE ESTILO]
[NEGATIVO]
```

**Força:** é onde o campo *Cultural Significance* dos dossiês vira jogo de verdade. **Fraqueza:** custo de conteúdo por cidade explode — inviabiliza a amplitude nacional que seu sistema foi construído para ter.

### B3 · Campanha estratégica

```
Video game UI screenshot: a strategic country map dominant on screen, cities
reduced to sized nodes with small crests, arrows and influence gradients
spreading between regions, a season calendar bar across the bottom with match
fixtures, a compact stats sidebar with ranked lists. The city itself appears only
as a small inset thumbnail in the corner panel.
[ESPINHA DE ESTILO]
[NEGATIVO]
```

**Força:** escala para 5.570 cidades sem custo. **Fraqueza:** a cidade deixa de ser lugar e vira número — você não precisaria de nada do trabalho de dossiê.

> **Como ler os três:** repare que B1 e B3 sobrevivem sem a camada de bairro, e B2 depende dela. A tela A4 (dentro do bairro) é o teste decisivo: se ela não for essencial, o nível 4 da árvore é ornamento e você economiza uma fortuna cortando-o.

---

## 4. Bloco C — assets isolados

Para alimentar direto a lista de assets, não para "print de produto".

### C1 · Card de arquétipo — sertão (`archetype.card`, 4:1, 2048×512)

```
Wide horizontal banner illustration, aspect 4:1: bird's-eye view of a small town
in semi-arid scrubland, grid of low whitewashed houses with colorful painted
facades, hilltop white chapel, large blue reservoir nearby, silver-grey thorny
vegetation stretching to rocky hills, harsh bright sunlight.
[ESPINHA DE ESTILO]
[NEGATIVO]
```

### C2 · Card de arquétipo — metropolitana litorânea (4:1)

```
Wide horizontal banner illustration, aspect 4:1: bird's-eye view of a tropical
coastal city district, pastel colonial core beside modern beachfront towers,
rivers crossed by bridges, mangrove edges, a dark reef line offshore with white
surf, red-tile rooftops inland, bright humid light.
[ESPINHA DE ESTILO]
[NEGATIVO]
```

### C3 · Silhueta assinatura (1:1, fundo transparente)

```
Single isolated isometric game asset on plain flat background: a tall white
art-deco elevator tower connecting a clifftop plaza to a lower harbor district,
golden colonial market hall at its base. Clean readable silhouette, no
background scenery.
[ESPINHA DE ESTILO]
[NEGATIVO]
```

> **Os outros 11 arquétipos já estão prontos.** Cada arquivo em `archetypes/` termina com um campo *Image prompt template*. Copie, cole a espinha de estilo, e você tem a biblioteca inteira sem escrever mais nada.

---

## 5. Grade de comparação entre geradores

Rode **A1, A3, A4 e B1** em cada gerador — quatro imagens são suficientes para caracterizar um modelo. Anote:

| Critério | Por que importa |
|---|---|
| **Legibilidade de hierarquia** | dá para saber em que nível você está sem ler texto? |
| **Diferenciação regional** | sertão e litoral parecem lugares diferentes? |
| **Densidade de UI** | a IA acha que a tela deve ser cheia (EU4) ou limpa (Sims)? Isso é uma opinião de design, e é de graça |
| **Onde ela põe a informação** | painel lateral, inferior, flutuante? Convergência entre modelos é sinal de convenção forte |
| **Viés cultural** | quantas vezes você precisou do negativo? |
| **Coerência entre A3 e A6** | é a mesma cidade? testa se overlay-como-camada é comunicável |

**O achado mais útil não vai ser a imagem mais bonita.** Vai ser onde todos os modelos concordam — isso é convenção de gênero que os jogadores já sabem ler, e brigar contra ela custa caro. E onde todos divergem: é espaço de design realmente em aberto.

---

## 6. Depois de gerar

Nenhuma dessas imagens é asset. São **direção de arte** — o que vira asset tem as especificações de dimensão, formato e espaço de cor da `lista-de-assets.md`, e o portão de qualidade da §10.2 (modernidade, dignidade, silhueta, fidelidade ao dossiê).

O caminho de volta é: escolher a direção → aplicar em Salvador (a cidade com dossiê mais completo) → medir contra o portão → só então encomendar as outras.
