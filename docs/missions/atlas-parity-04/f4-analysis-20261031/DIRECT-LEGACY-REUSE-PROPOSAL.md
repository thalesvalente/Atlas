# AP04 — Reaproveitamento direto do Atlas antigo: proposta de execução

**Estado:** `REAL_LEGACY_SOURCE_REUSE_PROPOSED_NOT_EXECUTED`.  
**Data:** 2026-10-31. **Plano:** AP04-POR-v1.0-draft (preservado).  
**Referências aprovadas:** ADR-0003 v0.2 / descriptor atlas-legacy-presentation 0.2.0 / pacote `c3ea1e82938fd61cc5a22fee973352715a5bb527`; decisão humana `APPROVED_SCOPED` no comentário `6539419419` da PR #15.  
**C2 original:** PR #18, SHA `258eda6153ffe602d3fa8e6b4fe7a2ad74edbbd7`, qualificada SOMENTE em ensaios sintéticos, fonte real BLOCKED.

## 1. Diagnóstico e correção

Houve um erro de priorização: `atlas-legacy-synthetic-source/0.1.0` foi criado como formato de entrada do adaptador C2, embora o Atlas antigo já tenha uma representação real e um exportador implementado. O formato sintético deve permanecer apenas como fixture de regressão; **NÃO pode ser um pré-requisito ou substituto do formato de origem**.

O objetivo é **ler diretamente os bytes de uma projeção antiga já existente**, não executar o R4, reconstruir mais um formato-fonte, regenerar experimentos nem converter o acervo. Usar o descriptor efêmero **já aprovado** 0.2.0 somente como contrato de apresentação entre O1 e O3, distinto do formato sintético de origem. Remover também esse descriptor e abrir o HTML diretamente como formato novo do viewer seria desvio da ADR já aprovada, sujeito a nova decisão ARC-09.

## 2. Fontes de código identificadas por SHA

**R4 legado:** repositório `thalesvalente/R4-RNF-RES-FIX`, PRIVADO, revisão de referência `5c145615c8a1bd601351badddccaf3acea474ed2`.  
**Atlas novo:** repositório `thalesvalente/Atlas`, PÚBLICO. Código R4 acessível via GitHub não implica acesso físico aos bytes do Windows. Esta revisão de código não prova qual commit gerou a projeção F1.

| Arquivo do R4 | Contrato real / reutilização |
|---|---|
| `src/r4/campaigns/atlas.py` | `build()` serializa `project()` em JSON inerte para `builds/<fingerprint>/index.html`, gera `BUILD-RECEIPT.json` e um ponteiro `ATLAS-ATUAL.html`. **Não chamar build/project no adaptador**. |
| `src/r4/presentation/atlas_assets/template.html` | Bloco `<script type="application/json" id="data">`; extrair o conteúdo COMO TEXTO, sem executar script. |
| `src/r4/presentation/atlas_assets/app.js` | `DATA=JSON.parse(document.getElementById('data').textContent)` prova o ponto de entrada e estado da UI antiga. Não executá-lo na extração. |
| `src/r4/campaigns/notebook_projection.py` | `SCHEMA='r4-experiment-viewer-v5'`, `validate()` e coleções originais. Contrato de parser e mapeamento; validar versão do snapshot LOCAL. |
| `graph-layout.js`, `graph-cards.js` | Algoritmos/semântica de árvore e relações, como referência ou port seletivo de comportamento, aproveitando a F3A escalável já pronta. |
| `tables-coverage.js` | RF original, ID, módulo/núcleo, nome, descrição, critérios, importação opcional de PRESENTATION.json e binding gaps. Mapear para F3B existente. |
| `records-products.js`, `historical-catalog.js` | Produtos, documentos, dossiês, cobertura e demais PAR; priorizar depois do mínimo navegável, sem perder rastreabilidade. |

**Privacidade e licença:** o R4 é PRIVADO e Atlas é PÚBLICO. **Copiar linhas/módulos literais do R4 para o Atlas publica código privado**. Exige autorização humana específica para esses paths, verificação de direitos de terceiros/licenças e revisão da difusão; não confundir propriedade do repositório com autorização automática de toda dependência. Sem essa decisão, implementar o adaptador público original a partir do contrato de dados e usar o código R4 apenas como referência de comportamento, sem transferir seus bytes.

Mesmo autorizado, não importar `r4.*` no wheel do Atlas, nem copiar para o runtime o leitor Windows suspenso, os comandos PowerShell, file://, estado global e HTML ativo. O renderer antigo usa `innerHTML` e ID de linha com fallback ordinal: portar esses trechos literalmente violaria as garantias novas de texto inerte e separação `native_id` versus ID de apresentação.

## 3. Fluxo alvo: perfil real, não sintético

```text
Projeção HTML legada preexistente, escolhida/autorizada por path exato
   ATLAS-ATUAL.html (ponteiro), se autorizado → builds/…/index.html (alvo autorizado)
      |
      v
Ferramenta EXTERNA O1 — extração inerte de script#data e validação do schema legado
      |
      v
Objeto da projeção R4 REAL, com records/edges/result_tables e demais camadas declaradas
      |
      v
Transformação literal 1:1 para descriptor efêmero já aprovado 0.2.0
      |
      v
JSON temporário privado → File API manual O3 → F3A gráfica + F3B RF/RNF/RES
      |
      v
Via Caderno/SDK/Catalog/APIs C4 continua separada e sem regressão
```

Não seguir o link do ponteiro ou qualquer URI sem autorização do arquivo ALVO. Não abrir fontes originais de experimentos, regenerar builds, executar HTML/JS, descobrir drives ou converter pastas. BUILD-RECEIPT pode ser inspecionado somente se incluído na autorização.

## 4. Mapeamento verificável, não inventado

- `records[]`: id/título/família/kind como identidade e apresentação quando declarados; não inventar Project/Experiment/Run a partir da posição.
- `edges[]`: from/to/type/proofs com semântica e direção declaradas, sem transformar menção em causalidade.
- `result_tables[]` e `rows[]`: toda ordem original de linhas/cabeçalhos, ID nativo quando comprovado, `cells` literais, módulo, nome, descrição, critérios, categorias ausentes; nenhum ordinal transformado em identidade nativa.
- `products`, `resources`, `product_items`, `resource_documents`, `sources`, `source_crosswalk`: preservar papel e vínculo declarado; `File` continua `File`, URI inerte.
- Grafo de linhagem nativo: identificar no código e no snapshot real o campo/estrutura correto (p.ex. `lineage_graph` quando presente), NÃO reduzir a árvore a `records[]`. A F1 observou **159 records e 2.911 nós de linhagem**, populações diferentes; verificar ambos separadamente.
- Campos desconhecidos permanecem em `unmapped_fields`/gaps sem perda silenciosa. No caso não representável, falhar fechado com evidência e contrato mínimo necessário.

**Oracles F1 escopados:** 159 records, 5 tabelas/152 linhas, 2.911 nós e 1.595 relações de linhagem, 858 parent keys, 28 RF sem ID/admissão, 4 tabelas sem record vinculado, Run externo isolado/binding_gap, 22 endpoints null, 75 unresolved, 50 colisões e ocorrências repetidas. São contagens de um único snapshot, não do acervo global. RF literal original deve ser conferida em privado, sem publicar IDs/descrição/caminho/sha privados.

## 5. Trabalho executável e precedência corrigida

**C2-A — CHAT, branch EXISTENTE PR #18:** adicionar `real_r4_v5` ao parser da ferramenta externa C2, lendo o HTML do Atlas antigo de modo INERTE, tipando dados reais e mapeando ao descriptor 0.2.0; NÃO criar outro `atlas-legacy-*-synthetic` em produção. Fixtures inventadas, mas com EXATA forma do v5, para testes. Provar compilação e transformação por SHA. Se a revisão LOCAL não for v5, informar `FORMAT_VARIANT_UNVERIFIED`, não falsificar perfil.

**C2-B — CHAT, paralela, arquivos de segurança exclusivos:** implementar supervisor/worker e isolamento de recursos com limites nativos (Windows Job Object e perfil de FS/rede devidamente comprovado) conforme F2, usando apenas inputs inventados. 256 MiB/30 s hard e negação de rede/FS precisam de provas reais; checagem cooperativa NÃO substitui. Guard pode continuar fechando operação real até a qualificação. Revisão independente C sem autoria para A/B.

**L1 — LOCAL depois de C2 com código para formato legado:** autorização explícita NOVA para arquivos já localizados. Conferir o HTML real/fingerprint/versão e sua estrutura, comparar valores com F1 no host, provar hashes/tamanho/mtime idênticos antes/depois e executar ferramenta externa sob orçamento/isolation qualificado. Produzir descriptor e recibo PRIVADOS, publicar só síntese saneada. Se o código Git não coincidir com o snapshot LOCAL, devolver shape mínimo saneado para ajuste, sem copiar corpus privado.

**C3 — CHAT integração:** usar C0 adendo versão `d498504cd2c4d230088f86e04e55624bbe32df79`, C1 graph escalado `4764eb0ebb38cd272b1a5e5fafbb103e72b8e105`, F3B `72118073cc72b4d3cdca21fcc64c18cf742ae384`, C2 qualificado, mantendo File API opcional O3 e Catalog isolado. CI global C4 só depois do SHA integrado. F5 depois da autorização LOCAL própria.

A proposta anterior de **L0 obrigatório** é desnecessária para começar engenharia: o formato é documentado pelo código R4. Só solicitar uma observação estrutural LOCAL mínima se a revisão real do HTML divergir da versão de código consultada. Isto elimina a circularidade introduzida entre C2 e L1 sem alterar a ordem original F0–F6 ou dispensar os gates.

## 6. Critérios objetivos da primeira entrega útil

- HTML exportado **pelo Atlas antigo**, já existente → descriptor validado 0.2.0 → árvore F3A navegável + tabela F3B com pelo menos uma RF literal realmente comparada.
- Sem execução do R4, sem dados publicados, sem modificação de fonte ou migração.
- Nenhuma perda não declarada de 2.911 nós, 1.595 relações, 152 linhas; lacunas e colisões explícitas, sem vínculo inventado.
- Regressão Caderno/SDK/Atlas C4, Windows/Ubuntu, CI por SHA e revisão independente.
- G4 requer controles do host e aquisição real; G5 requer CI integrada; G6 requer navegador LOCAL com fonte real — não transferir PASS sintético para esses gates.
- Sem merge, release, deploy, promoção, limpeza, novas worktrees/clones, mudança R4 ou aprovação científica.

**Estado desta proposta:** `DIRECT_SOURCE_REUSE_PLAN_READY_FOR_HUMAN_SCOPE_DECISION`. Não aprova publicação de bytes R4 privados. Caso seja escolhida a cópia literal de módulos/algoritmos do R4 privado para o Atlas público, registrar autorização de transferência específica ANTES de publicar.

**END-OF-AP04-DIRECT-REUSE-PLAN — COMPLETE**
