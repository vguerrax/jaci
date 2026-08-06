# Refinamento — BL-0020 — Bloquear renomeação de item vinculado ao template

## Rastreabilidade

- Item de backlog: [BL-0020](../backlog/items/BL-0020-bloquear-renomeacao-item-vinculado.md)
- Branch: `feature/BL-0020-bloquear-renomeacao-item-vinculado`
- Responsável pelo refinamento: Engenharia Jaci
- Estado do refinamento: `em_validacao`
- Itens relacionados: `BL-0003`, `BL-0005` e `BL-0011`
- Decisões de produto: nome vinculado visível em modo somente leitura; item
  incorporado recebe vínculo de proveniência; item da lista torna o nome
  imutável após a primeira compra; divergências históricas são preservadas.
- Aprovação da etapa 1: emitida explicitamente em `2026-08-05`, depois do
  commit documental `0fd7aaa`.
- Aprovação da etapa 2: emitida explicitamente em `2026-08-05`, depois do
  commit documental `4d34c08`.

## Objetivo e critérios de sucesso

### Objetivo

Preservar a identidade de itens originados de templates para que um produto
diferente não seja registrado sob o mesmo `template_item_id`, protegendo
análises de preço, frequência e quantidade sem reduzir a edição dos demais
atributos da execução ou do planejamento.

### Critérios de sucesso

1. Item com `template_item_id` conserva exatamente o nome de seu snapshot em
   edições agendadas e em andamento, online e offline.
2. Quantidade planejada, categoria e observações continuam editáveis sem
   renomear o item nem alterar o template.
3. Item sem `template_item_id` continua renomeável pelos contratos atuais.
4. A interface exibe o nome vinculado como somente leitura e orienta remover e
   adicionar quando o produto desejado for outro.
5. POST adulterado falha com `422`, sem mutação, incremento de versão ou evento
   Socket.IO.
6. Operação offline antiga que tente renomear gera conflito `409` auditável,
   preserva a fila e expõe o estado remoto para resolução explícita.
7. Nenhum nome histórico é reescrito e nenhuma mudança de modelo ou migração é
   introduzida.
8. Ao confirmar a incorporação de um item adicionado durante a execução, o
   `ExecutionItem` que originou a sugestão recebe o ID do novo `TemplateItem`
   na mesma unidade transacional, sem alterar seu snapshot financeiro.
9. IDs de sugestão adulterados, pertencentes a outra execução, template ou
   grupo, são rejeitados sem criar item nem vínculo parcial.
10. Um `TemplateItem` referenciado por ao menos um `ExecutionItem` com
    `is_completed = true` conserva exatamente seu nome; quantidade planejada,
    categoria e observações continuam editáveis.
11. Item de template sem compra vinculada continua renomeável.
12. A edição da lista apresenta o nome protegido como somente leitura e explica
    que um produto diferente deve ser cadastrado como novo item.

## Escopo

### Incluído

- Invariante de nome centralizada no serviço de edição de item de execução.
- Rejeição explícita de adulteração no adaptador HTML e na API offline.
- Estado remoto do conflito incluindo `template_item_id` e motivo estável
  `linked_template_item_name_immutable`.
- Nome somente leitura com ajuda contextual no modal server-rendered.
- Alternância segura entre somente leitura e editável no modal offline
  compartilhado, baseada em `data-template-item-id`.
- Compatibilidade de payload: atualizações válidas continuam enviando o nome
  atual para editar os demais campos.
- Atualização da versão do cache PWA e dos contratos de documentação/testes.
- Cenário Playwright futuro registrado para `BL-0011`, sem criar a
  infraestrutura nesta demanda.
- Vínculo do item incorporado na execução que originou a sugestão, com
  validação de pertencimento à mesma execução, template e grupo.
- Imutabilidade do nome do item da lista depois da primeira compra vinculada,
  centralizada no serviço e refletida no modal server-rendered.
- Edição normal dos demais atributos do item da lista e renomeação de itens
  ainda sem compra vinculada.

### Excluído

- Impedir remoção ou adição de itens durante a execução.
- Propagar alterações entre template e execuções já criadas.
- Comparar o snapshot com o nome atual do item do template.
- Corrigir, migrar, excluir ou sinalizar automaticamente divergências
  históricas já persistidas.
- Alterar preço, quantidade comprada, recorrência, status ou cálculos
  financeiros.
- Criar triggers, constraints de banco, migrações ou infraestrutura Playwright.
- Reescrever vínculos de itens incorporados antes desta correção.
- Alterar automaticamente nomes de snapshots ou propagar o nome atual do
  template para execuções existentes.
- Alterar nesta etapa a remoção de `TemplateItem` e o comportamento atual da FK
  `ON DELETE SET NULL`; essa política exige uma decisão separada de ciclo de
  vida para itens históricos.

## Riscos e regras preservadas

- Regras de negócio afetadas: quando `template_item_id IS NOT NULL`, o nome do
  snapshot torna-se imutável; itens avulsos permanecem editáveis. Se a FK ficar
  nula pelo comportamento `ON DELETE SET NULL`, o item passa a seguir a regra
  avulsa existente.
- Segurança e permissões: a regra reside no serviço e é aplicada depois do
  carregamento autorizado por execução; POST/API adulterados não contornam a
  interface.
- LGPD: nenhum dado novo é coletado. Auditoria offline conserva somente estados
  já usados pelo fluxo e permanece isolada por usuário/grupo.
- Isolamento por grupo: `get_execution_by_id` e a associação item/execução
  existentes permanecem obrigatórios; não haverá consulta nova sem filtro.
- Offline e sincronização: a UI nova não cria renomeações vinculadas. Operação
  antiga divergente vira conflito explícito, não repetição silenciosa nem perda
  da intenção local.
- Histórico financeiro: nenhuma linha passada é modificada. O bloqueio reduz
  contaminação futura de preço e quantidade associados ao item errado.
- Recorrência: `template_id`, datas, finalização e geração futura não mudam.
- Separação entre template e execução: o nome protegido é o snapshot atual da
  execução, não o nome vigente do template; edições continuam sem propagação.
- Segurança e permissões da incorporação: o `execution_item_id` recebido no
  formulário não será confiado isoladamente; a operação deve confirmar que o
  item pertence à execução em fechamento, vinculada ao mesmo template e grupo.
- Atomicidade da incorporação: criação do item do template e preenchimento do
  vínculo histórico serão confirmados juntos ou revertidos juntos.
- Identidade no planejamento: a existência de qualquer item de execução
  marcado como comprado bloqueia apenas a mudança de nome do `TemplateItem`;
  itens copiados, mas nunca comprados, não ativam o bloqueio.
- Exclusão: a FK atual usa `ON DELETE SET NULL`; como a demanda não altera a
  remoção de itens da lista, a perda de vínculo por exclusão permanece um risco
  conhecido e explicitamente fora desta etapa.

## Plano de implementação

### Etapa 1 — Proteger a identidade do item online e offline

#### Ticket 1.1 — Aplicar a invariante em todos os adaptadores

##### Fatia 1.1.1 — Contratos TDD e implementação completa

- Ordem: `1`
- Objetivo da fatia: escrever os contratos executáveis de todo o escopo e
  entregar a regra de domínio, respostas explícitas, UX somente leitura,
  conflito offline e distribuição PWA em uma unidade coerente.
- Dependências: aprovação explícita deste refinamento versionado.
- Arquivos esperados:
  - `tests/test_business_rules.py`
  - `tests/test_template_execution_flow.py`
  - `tests/test_offline_cache.py`
  - `tests/test_pwa.py`
  - `app/services/execution_service.py`
  - `app/routers/executions.py`
  - `app/routers/offline.py`
  - `app/templates/pages/executions/_edit_modal.html`
  - `app/templates/pages/executions/_items_fragment.html`
  - `app/templates/base.html`
  - `app/static/js/offline-cache.js`
  - `app/static/js/service-worker.js`
- Validações focadas:
  - `timeout 180 venv/bin/pytest tests/test_business_rules.py tests/test_template_execution_flow.py tests/test_offline_cache.py tests/test_pwa.py`
  - `node --check app/static/js/offline-cache.js`
  - `node --check app/static/js/service-worker.js`
  - `timeout 180 env PYTHONPATH=. venv/bin/pylint app/services/execution_service.py app/routers/executions.py app/routers/offline.py --errors-only`
  - validação manual online/offline em viewport móvel
- Documentação a atualizar:
  - `tests/README.md`
  - item e refinamento `BL-0020`

### Etapa 2 — Fechar o ciclo de identidade entre execução e planejamento

#### Ticket 2.1 — Preservar proveniência e nome após a primeira compra

##### Fatia 2.1.1 — Contratos TDD e implementação completa

- Ordem: `2`
- Objetivo da fatia: escrever os contratos executáveis da etapa 2 e entregar,
  numa unidade coerente, o vínculo atômico do item incorporado, a validação de
  pertencimento e o bloqueio server-side/UI da renomeação no template após a
  primeira compra.
- Dependências: aprovação explícita desta revisão versionada do refinamento.
- Arquivos esperados:
  - `tests/test_template_learning_tdd.py`
  - `tests/test_template_execution_flow.py`
  - `app/services/template_learning_service.py`
  - `app/services/template_service.py`
  - `app/routers/templates.py`
  - `app/templates/pages/templates/_items_fragment.html`
  - `docs/domain/template-learning.md`
  - `tests/README.md`
- Validações focadas:
  - `timeout 180 venv/bin/pytest tests/test_template_learning_tdd.py tests/test_template_execution_flow.py`
  - `timeout 180 env PYTHONPATH=. venv/bin/pylint app/services/template_learning_service.py app/services/template_service.py app/routers/templates.py --errors-only`
  - validação manual do fechamento e da edição da lista em viewport móvel
- Documentação a atualizar:
  - `docs/domain/template-learning.md`
  - `tests/README.md`
  - item e refinamento `BL-0020`

## Cenários TDD

Estes cenários devem ser escritos como testes antes da implementação, depois da
aprovação explícita deste refinamento.

1. Dado item com `template_item_id`, solicitar nome diferente no serviço falha
   sem modificar nome, demais campos ou versão.
2. Dado item vinculado e o mesmo nome exato, alterar quantidade planejada,
   categoria e observações funciona e incrementa a versão uma vez.
3. Dado item sem `template_item_id`, alterar o nome continua funcionando.
4. Dada execução finalizada ou cancelada, a imutabilidade geral continua tendo
   precedência e nenhuma edição é aceita.
5. Dado POST HTML adulterado para item vinculado, a rota responde `422`, não
   persiste parcialmente e não transmite `item_updated`.
6. Dado o modal online de item vinculado, o nome aparece como `readonly`, é
   enviado com o formulário e possui ajuda explicando remoção/adição; item
   avulso mantém o campo editável.
7. Dado o botão offline, `template_item_id` é exposto ao controlador; ao abrir
   itens vinculados e avulsos alternadamente, o modal ativa e remove
   `readonly` e a ajuda sem vazar estado entre aberturas.
8. Dada atualização offline válida de item vinculado com nome atual, os demais
   campos sincronizam normalmente.
9. Dada atualização offline divergente de item vinculado, a API retorna `409`
   com `reason=linked_template_item_name_immutable`, cria auditoria isolada,
   inclui `template_item_id` no estado remoto e não altera o item.
10. Dada uma operação divergente na fila, o cliente mantém a pendência e a
    apresenta para resolução explícita pelo fluxo de conflitos existente.
11. Dada a nova versão do shell PWA, clientes deixam de reutilizar o JavaScript
    antigo que permitia editar o nome vinculado.
12. Dado item adicionado durante uma execução vinculada, ao confirmar sua
    incorporação no fechamento, um novo item é criado no template e o item da
    execução recebe seu `template_item_id`; nome, quantidade comprada, preço,
    local, observações e versão do snapshot permanecem inalterados.
13. Dado item incorporado, a próxima execução copia o mesmo
    `template_item_id`, permitindo correlacionar a compra de origem e as compras
    futuras pela mesma identidade.
14. Dada sugestão ignorada, item inexistente, já vinculado, pertencente a outra
    execução, outro template ou outro grupo, nenhuma criação ou vinculação é
    persistida.
15. Dada falha entre criação e vínculo, a operação não deixa `TemplateItem`
    órfão nem `ExecutionItem` parcialmente atualizado.
16. Dado item de template com ao menos um item de execução comprado
    (`is_completed = true`), tentativa de alterar o nome no serviço falha sem
    modificar nome, quantidade planejada, categoria ou observações.
17. Dado o mesmo item comprado e o mesmo nome exato, editar quantidade
    planejada, categoria e observações continua funcionando.
18. Dado item de template sem item comprado vinculado, renomeá-lo continua
    funcionando e afeta somente execuções futuras.
19. Dado POST adulterado para renomear item da lista já comprado, a rota
    responde `422` sem persistência parcial.
20. Dado o modal de item da lista já comprado, o nome aparece como `readonly`,
    é enviado com o formulário e possui orientação para cadastrar outro
    produto; item nunca comprado mantém o nome editável.

### Contratos de etapas futuras

- Não haverá `xfail(strict=True)` no escopo executável das duas etapas.
- A `BL-0011` deve cobrir futuramente em Playwright, com dados do grupo
  autenticado: abrir compra vinculada online e offline, confirmar nome somente
  leitura e ajuda visível, editar quantidade/observações, reconectar e validar
  persistência; abrir item avulso e confirmar que o nome permanece editável;
  incorporar item no fechamento e validar o nome somente leitura na lista após
  a compra.

## Estratégia de validação

### Por fatia

- Escrever todos os contratos de serviço, rota, renderização, offline e PWA
  antes de alterar comportamento de produção.
- Implementar a invariante no serviço e manter rotas como adaptadores.
- Executar testes focados e verificações sintáticas dos dois arquivos
  JavaScript.
- Executar lint dos módulos Python tocados; registrar indisponibilidade do
  `pylint` como limitação ambiental, se ocorrer.
- Confirmar ausência de migração, reescrita histórica e arquivos `tests/ui`.
- Executar `venv/bin/graphify update .` após as mudanças de código.
- Atualizar item, índice, matriz de testes e progresso antes do commit técnico.

### Validação manual

1. Em viewport móvel, abrir uma execução agendada vinculada e confirmar nome
   visível somente para leitura, ajuda contextual e demais campos editáveis.
2. Repetir em execução em andamento, alterar quantidade e observações e
   confirmar que o nome e o template permanecem intactos.
3. Remover um item vinculado ainda pendente, adicionar outro produto e confirmar
   que o novo item avulso permite renomeação.
4. Desconectar a rede, editar os demais campos de item vinculado, confirmar
   estado local/fila e reconciliar após reconectar sem alteração de nome.
5. Abrir alternadamente itens vinculados e avulsos no modal offline e confirmar
   que `readonly` e a ajuda não vazam entre itens.
6. Simular payload online e offline com nome diferente e confirmar rejeição
   explícita sem mutação parcial nem broadcast.
7. Adicionar e comprar um item durante uma execução vinculada, selecioná-lo
   para incorporação no fechamento e confirmar que ele aparece nas execuções
   futuras associado à mesma identidade.
8. Abrir a lista após a incorporação, confirmar nome somente leitura e ajuda;
   alterar quantidade e categoria e confirmar que o nome permanece intacto.
9. Em item de lista nunca comprado, confirmar que o nome ainda é editável.
10. Adulterar o POST de edição do item já comprado e confirmar `422` sem
    alteração parcial.

### Regressão total

Como cada etapa possui uma fatia e a etapa 2 fecha o escopo revisado, executar
ao concluí-la e sem `xfail(strict=True)` desta demanda:

- `venv/bin/alembic upgrade head`
- `timeout 240 venv/bin/pytest`
- Playwright: infraestrutura ausente no Jaci; manter o cenário futuro na
  `BL-0011` e executar a validação manual definida acima.

## Progresso

| Etapa/ticket | Fatias concluídas | Fatias restantes | Estado |
| --- | ---: | ---: | --- |
| Etapa 1 / Ticket 1.1 — Identidade online/offline | `1/1` | `0` | Concluído |
| Etapa 2 / Ticket 2.1 — Proveniência e nome no planejamento | `1/1` | `0` | Concluído |

## Fechamento

- Commits/PRs: fatia 1.1.1 `f386127`; correção de validação `063bd7a`;
  fatia 2.1.1 `b82414a`; correção do fallback HTML `3b17680`;
  branch `feature/BL-0020-bloquear-renomeacao-item-vinculado`.
- Resultado das validações focadas: ciclo TDD inicial com 10 falhas esperadas e
  79 aprovações; após a implementação, 89 testes aprovados. `node --check`
  aprovou `offline-cache.js` e `service-worker.js`; compilação Python aprovada.
  A falha manual do modal de item comprado reproduziu 5 falhas esperadas e,
  depois da correção online/offline, 73 testes focados foram aprovados. O
  `pylint` não está instalado no venv. Na etapa 2, 10 contratos falharam antes
  da implementação; depois dela, 44 testes focados e 100 testes ampliados
  passaram, e os módulos Python alterados compilaram sem erro. A correção de
  validação do fallback HTML aprovou novamente os 44 testes focados.
- Resultado da validação manual: primeira rodada reprovada porque o modal de
  item comprado omitia o campo de nome e a orientação. Correção implementada;
  a segunda rodada foi aprovada pelo usuário em `2026-08-05`. A etapa 2 aguarda
  novo aceite: a primeira rodada dessa etapa encontrou uma resposta JSON após
  tentativa de renomeação; o fallback foi corrigido para renderizar a lista com
  alerta, nome `readonly` e ajuda contextual. A infraestrutura Playwright
  permanece futura na `BL-0011`.
- Resultado da regressão total: migrações no head; 247 testes aprovados e 5
  `xfail` legados fora do escopo após a etapa 2.
- `xfail(strict=True)` pendentes no escopo: nenhum.
- Documentação atualizada: item, índice, matriz de testes e este refinamento;
  grafo AST-only reconstruído.
