# BL-0007 — Replicar backups em armazenamento externo

## Identificação e entrada

| Campo | Valor |
| --- | --- |
| ID | `BL-0007` |
| Título | Replicar backups em armazenamento externo |
| Tipo | `melhoria` |
| Estado | `recebido` |
| Severidade | `a_triar` |
| Prioridade | `a_definir` |
| Data de entrada | `2026-07-24` |
| Origem | Limitação futura registrada no README e na decisão de backup PostgreSQL |
| Ambiente/versão | Estado de `develop` em `2026-07-24` |
| Responsável | `a_definir` |
| Atualizado em | `2026-07-24` |

### Comportamento observado

O backup automático mantém dumps validados em um volume persistente do host,
mas essa é a única cópia automática. A perda do servidor ou do volume pode
eliminar o banco e seus backups locais simultaneamente.

### Comportamento esperado

Backups validados devem possuir uma cópia externa protegida contra a perda do
servidor principal, mantendo confidencialidade, integridade, retenção e
procedimento verificável de restauração.

### Impacto e abrangência

- Impacto: um incidente no host pode remover também a única cópia automática
  disponível para recuperação.
- Abrangência: operação de produção, dumps PostgreSQL e continuidade do serviço.
- Frequência: contínua enquanto não houver cópia em domínio de falha separado.

### Passos de reprodução

1. Consultar a configuração atual de backup.
2. Observar que os dumps são persistidos apenas no volume do host.
3. Confirmar que não há destino externo configurado.

### Evidências sanitizadas

- [Decisão de backup PostgreSQL](../../../decisions/0002-backup-postgresql.md).
- [Operação de backups](../../../operations/postgresql-backups.md).
- [README do projeto](../../../../README.md#backup-automático-do-postgresql).

### Workaround

Copiar manualmente dumps validados para armazenamento externo com controles de
acesso adequados.

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
| Próximo passo | Realizar triagem de destino, proteção, retenção e verificação de restauração |

## Acompanhamento até produção

- Documento refinado: ainda não criado.
- Implementação (commits/PRs): ainda não iniciada.
- Validações: ainda não iniciadas.
- Publicação: ainda não publicada.
- Itens relacionados: backup local concluído nas
  [entregas legadas sem BL](../../decisions/backlog.md#entregas-concluídas-sem-identificador-bl-legado).

### Impedimentos

- Nenhum registrado; provedor e requisitos permanecem a definir na triagem.

## Histórico

| Data/hora | Autor | Mudança | Motivo/evidência |
| --- | --- | --- | --- |
| `2026-07-24 00:48 -03` | Codex | Item criado em `recebido` | Migração da limitação operacional documentada |
