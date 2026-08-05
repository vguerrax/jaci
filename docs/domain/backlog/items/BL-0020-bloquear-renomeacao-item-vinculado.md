# BL-0020 — Bloquear renomeação de item vinculado ao template

## Identificação e entrada

| Campo | Valor |
| --- | --- |
| ID | `BL-0020` |
| Título | Bloquear renomeação de item vinculado ao template |
| Tipo | `ajuste` |
| Estado | `pronto_para_implementacao` |
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

### Comportamento esperado

Um item de execução que possui `template_item_id` deve conservar seu nome. O
usuário continua podendo alterar quantidade planejada, categoria e observações,
mas deve remover o item e adicionar outro quando desejar comprar um produto
diferente. Itens avulsos sem `template_item_id` permanecem renomeáveis.

### Impacto e abrangência

- Impacto: trocas de produto sob a mesma identidade tornam análises futuras de
  preço, frequência e quantidade imprecisas.
- Abrangência: execuções agendadas ou em andamento, online e offline, com itens
  originados de templates.
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

### Workaround

Remover o item ainda não concluído e adicionar o produto correto como item
avulso. A interface atual não orienta o usuário a usar esse fluxo.

## Triagem

| Campo | Valor |
| --- | --- |
| Confirmação | `confirmado` por inspeção do serviço, rota HTML, formulário e fila offline |
| Classificação | Ajuste de integridade da identidade de itens usados por histórico e inteligência de compras |
| Domínio afetado | Execuções, itens de execução, edição online/offline, histórico de compras e aprendizado |
| Regras de negócio afetadas | Item vinculado conserva a identidade e o nome copiado; outro produto exige remoção e adição; alterações não propagam para o template |
| Risco de segurança | Baixo — a validação deve ficar no serviço para impedir adulteração por POST ou API offline |
| Risco de LGPD | Baixo — nenhum dado novo é coletado; payloads e auditorias existentes não devem expor outro grupo |
| Risco de isolamento por grupo | Baixo — consultas autorizadas existentes serão preservadas e nenhum novo ID do cliente será confiado |
| Risco offline/sincronização | Médio — clientes ou operações antigas podem tentar renomear e precisam receber conflito explícito sem perder a fila |
| Risco ao histórico financeiro | Médio, mitigado — o bloqueio evita novas associações incorretas; registros históricos existentes não serão reescritos |
| Risco à recorrência | Baixo — datas, status, geração do próximo ciclo e template permanecem inalterados |
| Risco à separação template/execução | Médio, mitigado — o nome do snapshot é preservado sem consultar ou atualizar retroativamente o nome atual do template |
| Dependências | Contrato de bloqueio otimista, fila/conflitos offline e distribuição PWA; `BL-0003`, `BL-0005` e futura cobertura UI em `BL-0011` |
| Duplicidades | Nenhuma identificada; `BL-0003` e `BL-0005` consomem a identidade protegida, mas não implementam este guardrail |
| Responsável pela próxima etapa | Engenharia Jaci |
| Próximo passo | Obter aprovação explícita do refinamento versionado e executar a fatia TDD única |

## Acompanhamento até produção

- Documento refinado: [Refinamento da BL-0020](../../tasks/BL-0020-bloquear-renomeacao-item-vinculado.md).
- Implementação (commits/PRs): ainda não iniciada; aguarda aprovação explícita
  do refinamento versionado.
- Validações: inspeção estática dos contratos atuais concluída; testes
  executáveis ainda não iniciados.
- Publicação: ainda não publicada.
- Itens relacionados: [BL-0003](BL-0003-historico-precos.md),
  [BL-0005](BL-0005-inteligencia-compras.md) e
  [BL-0011](BL-0011-ampliar-cobertura-testes-ui.md).

### Impedimentos

- Gate de implementação: aprovação explícita do refinamento após seu commit
  documental.

## Histórico

| Data/hora | Autor | Mudança | Motivo/evidência |
| --- | --- | --- | --- |
| `2026-08-05 20:09 -03` | Usuário/Codex | Item criado em `recebido` | Solicitação de proteção da identidade usada pela inteligência de compras |
| `2026-08-05 20:09 -03` | Codex | `recebido` → `em_triagem` → `pronto_para_refinamento` | Fluxos online/offline, impacto analítico, riscos, dependências e ausência de duplicidade confirmados |
| `2026-08-05 20:09 -03` | Codex | `pronto_para_refinamento` → `em_refinamento` → `pronto_para_implementacao` | Regra, UX, conflito offline, fatia TDD e validações definidos; implementação aguarda aprovação explícita |
