# BL-0020 — Bloquear renomeação de item vinculado ao template

## Identificação e entrada

| Campo | Valor |
| --- | --- |
| ID | `BL-0020` |
| Título | Bloquear renomeação de item vinculado ao template |
| Tipo | `ajuste` |
| Estado | `em_validacao` |
| Severidade | `N/A` |
| Prioridade | `P1` |
| Data de entrada | `2026-08-05` |
| Origem | Solicitação do usuário para proteger as análises de inteligência de compras |
| Ambiente/versão | Estado de `develop` (`f4c0399`) em `2026-08-05` |
| Responsável | Engenharia Jaci |
| Atualizado em | `2026-08-05` |

### Comportamento observado

Durante uma execução, o formulário de edição permite alterar o nome de um item
mesmo quando ele conserva `template_item_id`. Assim, o usuário pode transformar,
por exemplo, "Maçã" em "Manga" sem remover e adicionar um item avulso. O novo
produto permanece associado à identidade do item original do template.

Durante a validação também foram identificadas duas formas complementares de
perder essa identidade:

- ao incorporar no template um item adicionado durante a execução, o novo
  `TemplateItem` é criado, mas o `ExecutionItem` original permanece com
  `template_item_id = NULL`;
- o nome de um `TemplateItem` continua editável mesmo depois de esse item ter
  sido marcado como comprado em uma execução vinculada.

### Comportamento esperado

Um item de execução que possui `template_item_id` deve conservar seu nome. O
usuário continua podendo alterar quantidade planejada, categoria e observações,
mas deve remover o item e adicionar outro quando desejar comprar um produto
diferente. Itens avulsos sem `template_item_id` permanecem renomeáveis.

Quando um item avulso for incorporado ao template no fechamento, o item da
execução encerrada deve receber o ID do `TemplateItem` criado. Depois que um
item de template possuir ao menos um item de execução marcado como comprado,
seu nome deve ficar somente para leitura; quantidade planejada, categoria e
observações continuam editáveis. Itens de template nunca comprados permanecem
renomeáveis.

### Impacto e abrangência

- Impacto: trocas de produto sob a mesma identidade tornam análises futuras de
  preço, frequência e quantidade imprecisas.
- Abrangência: execuções agendadas, em andamento ou finalizadas, online e
  offline, aprendizado no fechamento e edição de itens das listas.
- Frequência: sempre que um item vinculado é editado; a troca de nome é
  atualmente aceita pelo serviço e pelas interfaces online/offline.

### Passos de reprodução

1. Criar uma execução a partir de um template que contenha "Maçã".
2. Abrir a edição do item durante a compra.
3. Alterar o nome para "Manga" e confirmar.
4. Observar que o item mantém o `template_item_id` de "Maçã" com o novo nome.

### Evidências sanitizadas

- [`update_execution_item`](../../../../app/services/execution_service.py)
  aceita e persiste o nome recebido sem considerar `template_item_id`.
- [Rota de edição da execução](../../../../app/routers/executions.py) e
  [sincronização offline](../../../../app/routers/offline.py) encaminham a
  alteração de nome ao mesmo serviço.
- [Aprendizado de templates](../../../../app/services/template_learning_service.py)
  usa `template_item_id` para correlacionar itens históricos.
- A incorporação atual cria o item da lista, mas não atualiza o
  `template_item_id` do item de execução que originou a sugestão.
- [`update_template_item`](../../../../app/services/template_service.py)
  persiste qualquer nome recebido sem verificar compras vinculadas.

### Workaround

Na execução, remover o item ainda não concluído e adicionar o produto correto
como item avulso. Para item da lista já comprado, não há workaround que preserve
simultaneamente a identidade histórica e permita trocar o produto.

## Triagem

| Campo | Valor |
| --- | --- |
| Confirmação | `confirmado` por inspeção do serviço, rota HTML, formulário e fila offline |
| Classificação | Ajuste de integridade bidirecional da identidade entre itens de execução e itens de template |
| Domínio afetado | Execuções, itens de execução, templates, edição online/offline, histórico de compras e aprendizado |
| Regras de negócio afetadas | Item vinculado conserva a identidade e o nome copiado; incorporação confirmada estabelece o vínculo histórico; item de template já comprado conserva o nome; alterações não propagam snapshots |
| Risco de segurança | Baixo — a validação deve ficar no serviço para impedir adulteração por POST ou API offline |
| Risco de LGPD | Baixo — nenhum dado novo é coletado; payloads e auditorias existentes não devem expor outro grupo |
| Risco de isolamento por grupo | Médio, mitigado — o ID da sugestão vem do cliente e deve ser validado contra a execução, o template e o grupo antes de criar ou vincular registros |
| Risco offline/sincronização | Médio — clientes ou operações antigas podem tentar renomear e precisam receber conflito explícito sem perder a fila |
| Risco ao histórico financeiro | Médio, mitigado — o vínculo será acrescentado ao item que originou a incorporação sem alterar nome, quantidade comprada, preço ou total; a imutabilidade evita novas associações incorretas |
| Risco à recorrência | Baixo — datas, status, geração do próximo ciclo e template permanecem inalterados |
| Risco à separação template/execução | Médio, mitigado — o vínculo de proveniência será preenchido somente após confirmação explícita; snapshots e dados financeiros não serão propagados ou reescritos |
| Dependências | Contrato de bloqueio otimista, fila/conflitos offline e distribuição PWA; `BL-0003`, `BL-0005` e futura cobertura UI em `BL-0011` |
| Duplicidades | Nenhuma identificada; `BL-0003` e `BL-0005` consomem a identidade protegida, mas não implementam este guardrail |
| Responsável pela próxima etapa | Engenharia Jaci |
| Próximo passo | Realizar aceite manual da etapa 2 e registrar a publicação antes de concluir a demanda |

## Acompanhamento até produção

- Documento refinado: [Refinamento da BL-0020](../../tasks/BL-0020-bloquear-renomeacao-item-vinculado.md).
- Implementação (commits/PRs): etapa 1 concluída no commit `f386127`;
  correção da validação manual no commit `063bd7a`; etapa 2 concluída no commit
  `b82414a`.
- Validações: ciclo TDD inicial aprovou 89 testes focados; a falha manual de
  visibilidade reproduziu 5 contratos vermelhos e a correção aprovou 73 testes
  focados; sintaxe JavaScript e compilação Python aprovadas; migrações no head;
  etapa 2 com 10 falhas TDD esperadas, 44 testes focados e 100 testes ampliados
  aprovados; compilação Python e migrações no head; regressão atual com 247
  testes aprovados e 5 `xfail` legados fora do escopo. A correção do fallback
  HTML aprovou novamente os 44 testes focados. `pylint` indisponível.
- Publicação: ainda não publicada.
- Itens relacionados: [BL-0003](BL-0003-historico-precos.md),
  [BL-0005](BL-0005-inteligencia-compras.md) e
  [BL-0011](BL-0011-ampliar-cobertura-testes-ui.md).

### Impedimentos

- Nenhum.

## Histórico

| Data/hora | Autor | Mudança | Motivo/evidência |
| --- | --- | --- | --- |
| `2026-08-05 20:09 -03` | Usuário/Codex | Item criado em `recebido` | Solicitação de proteção da identidade usada pela inteligência de compras |
| `2026-08-05 20:09 -03` | Codex | `recebido` → `em_triagem` → `pronto_para_refinamento` | Fluxos online/offline, impacto analítico, riscos, dependências e ausência de duplicidade confirmados |
| `2026-08-05 20:09 -03` | Codex | `pronto_para_refinamento` → `em_refinamento` → `pronto_para_implementacao` | Regra, UX, conflito offline, fatia TDD e validações definidos; implementação aguarda aprovação explícita |
| `2026-08-05 20:16 -03` | Usuário/Codex | Refinamento aprovado; `pronto_para_implementacao` → `em_implementacao` | Aprovação explícita recebida após o commit documental `0fd7aaa` |
| `2026-08-05 20:21 -03` | Codex | Fatia 1.1.1 concluída (`1/1`); `em_implementacao` → `em_validacao` | Regra online/offline, UX somente leitura e cache `v31` implementados; validações automatizadas aprovadas |
| `2026-08-05 20:21 -03` | Codex | Commit técnico registrado | Implementação, testes, documentação e grafo consolidados em `f386127` |
| `2026-08-05 20:31 -03` | Usuário/Codex | Falha encontrada na validação manual | Item comprado abria o modal de conclusão, que mostrava o nome somente no título e omitia o campo `readonly` e a orientação previstos |
| `2026-08-05 20:31 -03` | Codex | Correção de validação aplicada | Campo e orientação adicionados aos modais de comprar/editar compra online e offline; cache elevado para `v32` e regressão aprovada |
| `2026-08-05 20:31 -03` | Codex | Commit corretivo registrado | Correção visual, contratos, documentação e grafo consolidados em `063bd7a` |
| `2026-08-05 21:19 -03` | Usuário/Codex | Aceite manual da etapa 1 registrado | Campo de nome vinculado e orientação validados com sucesso na execução local |
| `2026-08-05 21:19 -03` | Usuário/Codex | Lacunas complementares identificadas; `em_validacao` → `em_refinamento` | Item incorporado não recebe o novo vínculo histórico e item da lista já comprado ainda pode ser renomeado |
| `2026-08-05 21:19 -03` | Codex | Refinamento revisado; `em_refinamento` → `pronto_para_implementacao` | Etapa 2, contratos TDD, isolamento, atomicidade e validações definidos; código aguarda nova aprovação explícita |
| `2026-08-05 21:32 -03` | Usuário/Codex | Revisão aprovada; `pronto_para_implementacao` → `em_implementacao` | Aprovação explícita recebida após o commit documental `4d34c08`; fatia 2.1.1 liberada para TDD e implementação |
| `2026-08-05 21:38 -03` | Codex | Fatia 2.1.1 concluída (`1/1`); `em_implementacao` → `em_validacao` | Vínculo atômico, validação de pertencimento e nome da lista somente leitura após compra implementados; 247 testes aprovados e 5 `xfail` legados |
| `2026-08-05 21:40 -03` | Codex | Commit técnico da etapa 2 registrado | Implementação, contratos TDD, documentação e grafo consolidados em `b82414a` |
| `2026-08-05 21:51 -03` | Usuário/Codex | Falha encontrada na validação manual da etapa 2 | POST de renomeação rejeitado abria uma tela branca com JSON em vez de manter o usuário na lista com orientação |
| `2026-08-05 21:51 -03` | Codex | Correção de validação aplicada | Resposta `422` passou a renderizar a página da lista em HTML, com alerta, nome `readonly` e ajuda contextual; novo aceite manual pendente |
