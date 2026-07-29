# Arquitetura do mapa — como a "pasta dentro de pasta" funciona de verdade

> Responde à pergunta: *como jogos como The Sims 4 mantêm uma estrutura de mapa em que cada localidade fica contida nas suas próprias interações — Cidade X > bairros Q,W,E,R,T,Y > edifícios e terrenos interativos?*
>
> Resposta curta: **a contenção não é só organização de arquivo. Ela é a fronteira de simulação e a fronteira de carregamento ao mesmo tempo.** É isso que torna a coisa possível — não uma estrutura de dados esperta.

---

## 1. O que realmente acontece nesses jogos

### The Sims 4

A hierarquia é `Mundo → Vizinhança → Lote`. Quando você olha o mapa de Willow Creek, você **não** está vendo a cidade rodando. Você está vendo:

- uma **ilustração pré-renderizada** do mundo (não uma cena 3D viva),
- um punhado de **pins** com hitbox, rótulo e card de tooltip,
- e um **snapshot de baixa fidelidade** dos lotes (quem mora lá, se está ocupado).

Nenhum Sim está sendo simulado. Quando você entra num lote, aí sim o jogo carrega a cena 3D daquele lote e liga a simulação completa: pathfinding, necessidades, objetos interativos, autonomia. **Um lote ativo por vez.** O resto do mundo continua "acontecendo" por um sistema estatístico barato — envelhecimento, empregos, relacionamentos evoluindo por regra, sem simular ninguém de fato.

O nome disso é **LOD de simulação**. É o mesmo conceito de LOD gráfico (malha mais simples ao longe), aplicado ao comportamento em vez da geometria.

### Europa Universalis 4

Vai ao extremo oposto e é ainda mais instrutivo: **não existe cena nenhuma.** A província não é um objeto 3D — é uma cor RGB num bitmap (`provinces.bmp`) mais uma linha numa tabela. O que você clica é um pixel; o jogo lê a cor, procura o ID na `definition.csv`, e abre um painel de UI preenchido com dados. Todas as milhares de províncias existem simultaneamente porque **nenhuma delas é uma cena** — são linhas de um banco de dados desenhadas por cima de uma textura.

### O que os dois têm em comum

| | Sims 4 | EU4 |
|---|---|---|
| Vista geral | ilustração + pins | bitmap + shader |
| A localidade "existe" como | registro + thumbnail | cor + linha de tabela |
| Simulação completa | 1 lote ativo | nenhum lugar — só regras agregadas |
| Custo de ter 10.000 localidades | ~zero (são registros) | ~zero (são pixels) |

**A lição:** o custo de um mapa gigante não vem do número de localidades. Vem de quantas você mantém *vivas* ao mesmo tempo. Uma cidade "fechada" custa o tamanho do registro dela — alguns KB.

---

## 2. Como isso se traduz para o nosso projeto

A boa notícia: **a estrutura de pastas que você descreveu já existe no repositório.** O `gazetteer/br.json` é uma árvore de pai único, e o invariante 1 do README (*"one tree, single parent"*) é exatamente a regra que faz a contenção funcionar.

O que faltava era ligar os dois pedaços: o gazetteer para na **cidade**, e bairros/locais viviam soltos dentro dos dossiês em markdown. O `tools/worldbuild.py` junta tudo numa árvore só:

```
nível 0  região        br.nordeste
nível 1  estado        br.nordeste.ba
nível 2  sub-região    br.nordeste.ba.metropolitana-de-salvador
nível 3  cidade        …salvador
nível 4  bairro        …salvador#centro-historico
nível 5  local         …salvador#pelourinho
```

O ID de bairro e local usa `#` de propósito: tudo antes do `#` é o nó canônico do gazetteer; tudo depois vem do dossiê. Isso mantém as duas fontes de verdade separadas mesmo dentro de um ID só.

Rodando hoje, com os dois dossiês que existem:

```
[cidade]  Salvador
  [bairro]  Centro Histórico (Pelourinho + Comércio)
    [local]   Pelourinho & Terreiro de Jesus
  [bairro]  Liberdade / Curuzu
  [bairro]  Península de Itapagipe (Bonfim/Ribeira)
    [local]   Igreja do Bonfim
  [bairro]  Orla Atlântica (Barra → Rio Vermelho → Itapuã)
    [local]   Rio Vermelho & Casa de Iemanjá
  [local]   Elevador Lacerda, Praça Tomé de Souza & Mercado Modelo
  [local]   Feira de São Joaquim
  [local]   Dique do Tororó & Arena Fonte Nova     ← overlay de lente, removível
```

Note que três locais ficaram **direto na cidade**, não num bairro. Isso é correto e importante: o Elevador Lacerda é literalmente a dobradiça entre Cidade Alta e Cidade Baixa — ele pertence a dois bairros, então pertence à cidade. **Um nó tem um pai só; o que não cabe nessa regra sobe um nível.** É o invariante 1 se aplicando sozinho.

---

## 3. Os quatro estados de uma localidade

Aqui está o mecanismo que responde "como cada localidade fica contida nas suas interações". Toda localidade da árvore está, a qualquer momento, em **um** destes estados:

| Estado | O que está carregado | Custo | Quando |
|---|---|---|---|
| **Registro** | só o nó: nome, tier, arquétipo, contagem de filhos | bytes | todas as ~5.570 cidades, sempre |
| **Vitrine** | + thumbnail, pins dos filhos, dados de painel | KB | o contêiner que o jogador está olhando |
| **Ativo** | + placa em alta resolução, máscaras, áudio, estado dos filhos | MB | 1 por vez — a cidade em que o jogador entrou |
| **Simulado** | + agentes, interações, gameplay rodando | o orçamento inteiro | 1 por vez — o local onde o jogador está |

**Entrar numa cidade** é promover um nó de *vitrine* para *ativo*, e rebaixar o anterior. Nada mais. Sair é o inverso, serializando o estado de volta para o registro.

A regra que segura tudo: **um nó só pode estar *simulado* se o pai dele estiver *ativo*.** Isso garante que só existe um caminho vivo na árvore por vez — da raiz até onde o jogador está. Todo o resto é registro.

```
br.nordeste            registro
  br.nordeste.ba       registro
    …salvador          ATIVO        ← jogador entrou aqui
      #centro-historico  vitrine
        #pelourinho        SIMULADO   ← jogador está aqui
      #liberdade         registro
      #itapagipe         registro
```

O que acontece nos nós em *registro* enquanto isso? A mesma coisa que no Sims: **regras agregadas, não simulação.** O calendário de festas de Salvador avança, a torcida do Bahia muda de humor depois da rodada, a caatinga fica verde depois da chuva — tudo isso é um tick barato sobre o registro, sem ninguém sendo simulado.

---

## 4. Onde escrever a lógica: no arquétipo, não na cidade

O playbook já contém a regra certa, na Parte 3: *"Script to the GROUP"*. Paradox escopa eventos para área/região para que um script cubra muitas províncias. Aplicado aqui:

> **Comportamento mora no arquétipo. Dados moram no nó. Exceções moram no dossiê.**

O ciclo semanal da feira é escrito **uma vez** em `agreste-feirante` e anima automaticamente toda cidade cuja sub-região referencia esse arquétipo — inclusive as centenas que você ainda nem cadastrou. O `worldbuild.py` já resolve essa herança e a expõe em cada nó:

```json
"archetypeResolved": "metropolitana-nordestina-litoral",
"archetypeInheritedFrom": "br.nordeste.ba.metropolitana-de-salvador"
```

Bairros e locais herdam também, subindo a árvore até achar quem declara. Por isso o Pelourinho já sabe qual é a paleta dele, qual é a trilha sonora da região e qual é o prompt de imagem — **sem nenhum dado escrito no Pelourinho.**

É daqui que vem a resposta prática para "ainda vou preencher as demais localizações": você não precisa preencher quase nada. Uma cidade nova custa uma linha no gazetteer se a sub-região dela já tem arquétipo.

---

## 5. Tradução para engine

O padrão tem nomes estabelecidos, e as duas engines principais já o implementam:

| Conceito aqui | Unity | Unreal |
|---|---|---|
| Nó em *registro* | entrada num ScriptableObject/JSON | linha de DataTable |
| Promover para *ativo* | `SceneManager.LoadSceneAsync(..., Additive)` | Level Streaming / World Partition |
| Rebaixar para registro | `UnloadSceneAsync` + serializar estado | `UnloadStreamLevel` |
| Herança de arquétipo | ScriptableObject compartilhado | DataAsset / herança de Blueprint |
| Vitrine (mapa navegável) | Canvas + sprites, nenhuma cena de mundo | UMG Widget, nenhum nível carregado |

O ponto que costuma ser feito errado: **a vista de mapa não deve ser uma cena de mundo.** No Sims ela é uma imagem com pins; no EU4 é um bitmap. Se você fizer a vista de cidade como uma cena 3D com todos os bairros carregados, perde exatamente a propriedade que torna o sistema escalável. A vista de mapa é UI.

---

## 6. O que a ferramenta faz hoje

`tools/worldbuild.py` — lê `gazetteer/` + `archetypes/` + `dossiers/` + `lenses/` e emite:

| Saída | Para que serve |
|---|---|
| `build/world.json` | a árvore inteira, com herança resolvida e overlays de lente aplicados — é o que a engine consome |
| `build/viewer.html` | visualizador self-contained: abre com duplo clique, sem servidor |
| `build/world.data.js` | o mesmo bundle para `tools/viewer/index.html` durante o desenvolvimento |
| `build/report.md` | validações: erros, avisos e notas |

`tools/viewer/` — o visualizador. Navega a árvore exatamente com o modelo da §3: clique seleciona (vitrine), duplo-clique entra (ativo), `Esc` sobe um nível. Mostra, por nó: tier, arquétipo resolvido com origem da herança, bairros e locais contidos, overlays de lente, texto integral do dossiê, prompt de imagem, e os slots de asset com status.

Como ainda não existe arte, cada nó renderiza um **placeholder determinístico** derivado do ID — mesma regra da §8.4 da lista de assets. Os filhos de uma cidade compartilham família cromática de propósito, para o placeholder ler como ausência de arte e não competir com ela.

```bash
python3 tools/worldbuild.py          # gera tudo em build/
python3 tools/worldbuild.py --check  # só valida; exit 1 se houver erro
```

Sem dependências — stdlib do Python 3.11+.

---

## 7. Como adicionar uma localidade nova

Na ordem de custo crescente:

1. **Cidade genérica** — uma linha em `gazetteer/br.json` com `parentId` apontando para uma sub-região que já tem `archetypeId`. Herda visual, som, economia e prompt. Custo: ~30 segundos, zero arte.
2. **Cidade com assinatura** — a mesma linha + `"tier": "generic+signature"` + `"signature": "descrição de uma linha"`. Custo: um asset (§6.3.2 da lista de assets).
3. **Cidade hero** — a linha + um dossiê em `dossiers/`, seguindo `dossiers/_template.md`. Os bairros viram nível 4 e os landmarks nível 5 automaticamente, desde que o markdown siga o formato:
   - bairros: `- **Nome:** descrição… Gameplay zones: a, b, c.`
   - locais: `### Location N: Nome (Bairro)` seguido de `- **Type:** …`, `- **Cultural Significance:** …` etc.
   - o parser aceita campos extras livremente (o Rio tem um `Authenticity note` que só ele tem)
4. **Sub-região nova** — uma linha com `archetypeId`. Só escreva um arquétipo novo depois de checar a biblioteca: **reutilizar > variar > criar novo**.

Depois de qualquer edição, `python3 tools/worldbuild.py` e o visualizador reflete na hora.

---

## 8. Estado atual (build de hoje)

```
69 nós:  5 regiões · 10 estados · 16 sub-regiões · 19 cidades · 7 bairros · 12 locais
10 arquétipos · 1 lente · 2 dossiês
176 slots de asset — 89 herdados de arquétipo, 87 faltando
0 erros · 15 avisos
```

Os 89 slots herdados contra 87 faltando são a curva de saturação funcionando: **mais da metade do que o jogo precisa desenhar já está coberto por herança**, com só dois dossiês escritos.

Os avisos que valem ação:

- **IDs divergentes de Salvador** — a lente usa `br.nordeste.ba.salvador`, o gazetteer usa `br.nordeste.ba.metropolitana-de-salvador.salvador`. O exportador resolve por alias e avisa, mas isso precisa ser decidido (lista de assets, §8.6).
- **O dossiê do Rio não segue `dossiers/_template.md`** — é um "Design Brief" de formato antigo, sem o campo `**Position:**`. O parser casa pelo nome do arquivo, mas o Rio deveria ser migrado para o template.
- **9 cidades sem arquétipo** — todas em estados sem passe de sub-região (SP, MG, RS, PR, SC, PA, RJ). Elas renderizam sem kit visual até o passe do estado rodar.
- **Recife e Fortaleza são hero sem dossiê e fora da fila de pesquisa** — a lente 2026 não as alcança (clubes rebaixados), o que é o comportamento esperado do sistema de lentes, mas vale confirmar que é intencional.
