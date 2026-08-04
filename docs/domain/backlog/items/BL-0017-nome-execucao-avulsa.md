# BL-0017 — Permitir informar um nome para execução avulsa

## Identificação e entrada

| Campo | Valor |
| --- | --- |
| ID | `BL-0017` |
| Título | Permitir informar um nome para execução avulsa |
| Tipo | `ajuste` |
| Estado | `recebido` |
| Severidade | `a_triar` |
| Prioridade | `a_definir` |
| Data de entrada | `2026-08-03` |
| Origem | Solicitação do usuário |
| Ambiente/versão | Estado de `develop` (`da7e087`) em `2026-08-03` |
| Responsável | `a_definir` |
| Atualizado em | `2026-08-03` |

### Comportamento observado

O formulário de criação de uma execução avulsa permite informar a data e o
orçamento, mas não oferece um campo para nome. Toda execução criada por esse
fluxo recebe automaticamente o nome "Compra Avulsa".

### Comportamento esperado

O usuário deve poder informar um nome para a execução avulsa durante sua
criação, facilitando a identificação da compra desde o primeiro acesso.

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
| Confirmação | `a_triar` |
| Classificação | `a_triar` |
| Domínio afetado | `a_triar` |
| Regras de negócio afetadas | `a_triar` |
| Risco de segurança | `a_avaliar` |
| Risco de LGPD | `a_avaliar` |
| Risco de isolamento por grupo | `a_avaliar` |
| Risco offline/sincronização | `a_avaliar` |
| Risco ao histórico financeiro | `a_avaliar` |
| Risco à recorrência | `a_avaliar` |
| Risco à separação template/execução | `a_avaliar` |
| Dependências | `a_triar` |
| Duplicidades | `a_triar` |
| Responsável pela próxima etapa | `a_definir` |
| Próximo passo | Confirmar o comportamento, avaliar riscos e delimitar o ajuste durante a triagem |

## Acompanhamento até produção

- Documento refinado: ainda não criado.
- Implementação (commits/PRs): ainda não iniciada.
- Validações: somente diagnóstico documental; testes executáveis não iniciados.
- Publicação: ainda não publicada.
- Itens relacionados: nenhum identificado.

### Impedimentos

- Nenhum registrado; classificação e riscos dependem da triagem.

## Histórico

| Data/hora | Autor | Mudança | Motivo/evidência |
| --- | --- | --- | --- |
| `2026-08-03 23:59 -03` | Codex | Item criado em `recebido` | Solicitação do usuário |
