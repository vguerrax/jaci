# BL-0017 — Permitir informar um nome para execução avulsa

## Identificação e entrada

| Campo | Valor |
| --- | --- |
| ID | `BL-0017` |
| Título | Permitir informar um nome para execução avulsa |
| Tipo | `ajuste` |
| Estado | `em_validacao` |
| Severidade | `N/A` |
| Prioridade | `P2` |
| Data de entrada | `2026-08-03` |
| Origem | Solicitação do usuário |
| Ambiente/versão | Estado de `develop` (`da7e087`) em `2026-08-03` |
| Responsável | Engenharia Jaci |
| Atualizado em | `2026-08-05` |

### Comportamento observado

O formulário de criação de uma execução avulsa permite informar a data e o
orçamento, mas não oferece um campo para nome. Toda execução criada por esse
fluxo recebe automaticamente o nome "Compra Avulsa".

### Comportamento esperado

O usuário deve poder informar um nome opcional para a execução avulsa sem lista
durante sua criação e alterá-lo enquanto ela estiver agendada. Execuções
vinculadas a um template, inclusive compras extras que não geram recorrência,
devem preservar o próprio nome e não permitir renomeação.

### Impacto e abrangência

- Impacto: execuções avulsas diferentes podem aparecer com o mesmo nome e
  exigir contexto adicional para serem identificadas.
- Abrangência: usuários e grupos que criam compras sem vínculo com um template.
- Frequência: sempre que uma execução avulsa é criada pelo formulário.

### Passos de reprodução

1. Acessar o formulário de criação de uma compra.
2. Selecionar "Compra avulsa (sem lista)".
3. Observar que o formulário não permite informar um nome.
4. Criar a execução e observar que ela recebe o nome "Compra Avulsa".

### Evidências sanitizadas

- [Formulário de criação](../../../../app/templates/pages/executions/create.html).
- [Serviço de execuções](../../../../app/services/execution_service.py).

### Workaround

Criar a execução e alterar seu nome depois, enquanto ela ainda estiver
agendada, adicionando uma etapa ao fluxo.

## Triagem

| Campo | Valor |
| --- | --- |
| Confirmação | `confirmado` |
| Classificação | Ajuste de identificação e restrição de edição de execuções |
| Domínio afetado | Execuções — criação, edição agendada e sincronização offline |
| Regras de negócio afetadas | Nome opcional somente para execução sem template; template e execução permanecem separados |
| Risco de segurança | Não — autorização atual por usuário/grupo será preservada e a regra ficará no serviço |
| Risco de LGPD | Baixo — campo textual já existente, limitado a 150 caracteres e sem novo registro em log |
| Risco de isolamento por grupo | Não — criação usa o grupo ativo e edição mantém a consulta autorizada existente |
| Risco offline/sincronização | Sim, baixo — edição offline deve aplicar a mesma restrição e rejeitar adulteração no servidor |
| Risco ao histórico financeiro | Não — nenhum valor financeiro ou registro histórico será alterado |
| Risco à recorrência | Não — `is_standalone` continua controlando recorrência, sem conceder renomeação quando há template |
| Risco à separação template/execução | Sim, mitigado — nome do template não será alterado e execuções vinculadas não poderão ser renomeadas |
| Dependências | Contrato atual de edição agendada e fila offline; cobertura futura de navegador na `BL-0011` |
| Duplicidades | Nenhuma identificada |
| Responsável pela próxima etapa | Engenharia Jaci |
| Próximo passo | Validar manualmente em navegador real e registrar a publicação antes do encerramento |

## Acompanhamento até produção

- Documento refinado: [Refinamento da BL-0017](../../tasks/BL-0017-nome-execucao-avulsa.md).
- Implementação (commits/PRs): fatia 1.1.1 implementada no commit `4f91170`.
- Validações: 56 testes focados e 57 testes ampliados aprovados; regressão com 225 aprovados e 5 `xfail` legados; migrações no head; compilação Python aprovada; `pylint` indisponível.
- Publicação: ainda não publicada.
- Itens relacionados: [BL-0011](BL-0011-ampliar-cobertura-testes-ui.md).

### Impedimentos

- Validação em navegador real e publicação ainda não registradas.

## Histórico

| Data/hora | Autor | Mudança | Motivo/evidência |
| --- | --- | --- | --- |
| `2026-08-03 23:59 -03` | Codex | Item criado em `recebido` | Solicitação do usuário |
| `2026-08-04 18:08 -03` | Codex | Triagem concluída; `recebido` → `pronto_para_refinamento` | Comportamento confirmado no formulário, rota, serviço e contratos de edição/offline |
| `2026-08-04 18:08 -03` | Codex | Refinamento criado; `pronto_para_refinamento` → `em_refinamento` → `pronto_para_implementacao` | Escopo, restrições, fatia TDD e validações definidos com o usuário |
| `2026-08-05 07:49 -03` | Usuário/Codex | Refinamento aprovado; `pronto_para_implementacao` → `em_implementacao` | Aprovação explícita posterior ao commit documental `e76c9a1` |
| `2026-08-05 07:49 -03` | Codex | Fatia 1.1.1 implementada; `em_implementacao` → `em_validacao` | Contratos focados, validação ampliada e regressão aprovados; publicação pendente |
| `2026-08-05 07:49 -03` | Codex | Commit da fatia registrado | Implementação e validações versionadas em `4f91170` |
