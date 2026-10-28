# BL-0002 — Adicionar unidades de medida

## Identificação e entrada

| Campo | Valor |
| --- | --- |
| ID | `BL-0002` |
| Título | Adicionar unidades de medida |
| Tipo | `melhoria` |
| Estado | `pronto_para_refinamento` |
| Severidade | `N/A` |
| Prioridade | `P1` |
| Data de entrada | `2026-07-24` |
| Origem | Item 3 da ordem de prioridade do roadmap em `AGENTS.md` |
| Ambiente/versão | Estado de `develop` em `2026-07-24` |
| Responsável | Engenharia Jaci |
| Atualizado em | `2026-08-05` |

### Comportamento observado

Itens de template e de execução armazenam quantidades numéricas, mas não
registram a unidade de medida correspondente. O significado de valores como
`1`, `2` ou `0,5` depende do entendimento dos membros do grupo.

### Comportamento esperado

O usuário deve poder planejar e registrar quantidades com um catálogo
padronizado de unidades de medida, sem conversões automáticas nem unidades
personalizadas na primeira entrega. Itens históricos permanecem com unidade não
informada; `un` será apenas o padrão editável para novos itens. A solução deve
preservar simplicidade, funcionamento offline, histórico e separação entre
template e execução.

### Impacto e abrangência

- Impacto: quantidades podem ser ambíguas para itens comprados por peso, volume
  ou embalagem.
- Abrangência: itens de template, itens de execução, apresentação, histórico e
  sincronização offline.
- Frequência: sempre que a quantidade não representar uma unidade implícita.

### Passos de reprodução

Não há falha pontual a reproduzir. Crie um item cuja quantidade seja `0,5` e
observe que o sistema não registra se o valor representa quilograma, litro ou
outra unidade.

### Evidências sanitizadas

- [Roadmap do Jaci](../../../../AGENTS.md#ordem-de-prioridade-do-roadmap).
- [Entidades do domínio](../../entities.md).
- [Modelo de itens de template](../../../../app/models/template.py).
- [Modelo de itens de execução](../../../../app/models/execution.py).
- [Snapshot offline](../../../../app/services/offline_cache_service.py).
- [Aprendizado de quantidades](../../template-learning.md#bl-031-e-bl-032--quantidades-recorrentes).

### Workaround

Informar a unidade no nome ou nas observações do item, com risco de
inconsistência e retrabalho.

## Triagem

| Campo | Valor |
| --- | --- |
| Confirmação | `confirmado` |
| Classificação | Melhoria de domínio e experiência para tornar explícita a semântica das quantidades; exige evolução incremental e compatível dos itens de template e execução |
| Domínio afetado | Planejamento por templates, execução da compra, aprendizado de quantidades, histórico financeiro e operação offline |
| Regras de negócio afetadas | Copiar a unidade do template ao criar a execução, preservar execuções existentes, não alterar templates automaticamente e interpretar preço unitário sem conversões implícitas |
| Risco de segurança | Baixo — o catálogo controlado não cria novo recurso protegido; entradas devem continuar validadas no servidor pelas rotas autorizadas existentes |
| Risco de LGPD | Não — unidade de medida não adiciona dado pessoal; evidências e payloads continuam sujeitos à proteção vigente |
| Risco de isolamento por grupo | Baixo — a unidade acompanha itens já isolados por grupo e não pode ampliar consultas ou aceitar IDs sem autorização |
| Risco offline/sincronização | Alto — unidade deve integrar snapshot, estado local e operações pendentes, mantendo compatibilidade com caches e payloads antigos sem o campo |
| Risco ao histórico financeiro | Alto — unidade altera a interpretação de quantidade e preço unitário; registros antigos ficam sem unidade e nenhum valor ou total será convertido retroativamente |
| Risco à recorrência | Médio — novas execuções devem copiar a unidade vigente no template sem alterar o cálculo do ciclo nem execuções anteriores |
| Risco à separação template/execução | Alto — a unidade deve ser copiada como snapshot; mudanças posteriores no template afetam apenas execuções futuras |
| Dependências | Modelos `TemplateItem` e `ExecutionItem`, criação de execuções, formulários e formatadores, aprendizado de quantidades, snapshot/fila offline; BL-0001 e BL-0003 são relacionados, mas não bloqueiam o refinamento |
| Duplicidades | Nenhuma identificada no backlog ativo ou legado; o aprendizado legado trata divergência numérica, não a unidade correspondente |
| Responsável pela próxima etapa | Engenharia Jaci |
| Próximo passo | Elaborar o refinamento para definir catálogo, persistência opcional, cópia template/execução, contratos online/offline, apresentação mobile-first e migração incremental |

## Acompanhamento até produção

- Documento refinado: ainda não criado.
- Implementação (commits/PRs): ainda não iniciada.
- Validações: triagem baseada nos modelos, serviços, apresentação e contratos
  offline existentes; validações de implementação ainda não iniciadas.
- Publicação: ainda não publicada.
- Itens relacionados: [BL-0001](BL-0001-operacao-offline-cobertura-rastreabilidade.md),
  [BL-0003](BL-0003-historico-precos.md) e aprendizado de quantidades do
  [backlog legado](../../decisions/backlog.md#aprendizado-de-templates).

### Impedimentos

- Nenhum registrado.

## Histórico

| Data/hora | Autor | Mudança | Motivo/evidência |
| --- | --- | --- | --- |
| `2026-07-24 00:48 -03` | Codex | Item criado em `recebido` | Migração do item aberto no roadmap legado |
| `2026-08-05 15:11 -03` | Usuário/Codex | `recebido` -> `em_triagem` | Catálogo sem conversões, compatibilidade histórica e prioridade definidos com o usuário |
| `2026-08-05 15:11 -03` | Codex | `em_triagem` -> `pronto_para_refinamento` | Confirmação, riscos, dependências, duplicidades e próximo passo documentados |
