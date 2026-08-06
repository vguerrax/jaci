# BL-0007 — Replicar backups em armazenamento externo

## Identificação e entrada

| Campo | Valor |
| --- | --- |
| ID | `BL-0007` |
| Título | Replicar backups em armazenamento externo |
| Tipo | `melhoria` |
| Estado | `pronto_para_refinamento` |
| Severidade | `N/A` |
| Prioridade | `P1` |
| Data de entrada | `2026-07-24` |
| Origem | Limitação futura registrada no README e na decisão de backup PostgreSQL |
| Ambiente/versão | Estado de `develop` em `2026-07-24` |
| Responsável | Engenharia Jaci |
| Atualizado em | `2026-08-05` |

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
| Confirmação | `confirmado` |
| Classificação | Melhoria de continuidade e recuperação de desastre para remover o servidor e seu volume local como domínio único de falha dos backups automáticos |
| Domínio afetado | Infraestrutura de produção, PostgreSQL, backups, segurança da informação e operação de restauração |
| Regras de negócio afetadas | Replicar somente dumps locais publicados após validação; preservar confidencialidade, integridade, retenção e restauração completa dos dados; não substituir o backup local nem tornar a recuperação dependente da aplicação ou de WebSocket |
| Risco de segurança | Alto — cada dump contém o banco completo; destino, transporte, credenciais, criptografia, logs e restauração devem seguir menor privilégio e impedir leitura, alteração ou exclusão não autorizada |
| Risco de LGPD | Alto — a cópia externa processa dados pessoais e hábitos de consumo; localização, retenção, acesso e descarte devem ser controlados e auditáveis |
| Risco de isolamento por grupo | Alto — um dump agrega dados de todos os grupos, portanto sua exposição ou restauração incorreta pode atravessar os limites de isolamento da aplicação |
| Risco offline/sincronização | Baixo — a replicação é operacional e assíncrona ao uso do produto; falhas externas não podem interromper o backup local, a aplicação ou a fila de sincronização |
| Risco ao histórico financeiro | Alto — a cópia deve preservar valores e registros históricos integralmente, e a restauração precisa detectar ausência, corrupção ou versão incompatível |
| Risco à recorrência | Baixo — a replicação não recalcula ciclos; uma restauração deve conservar datas, estados e vínculos que determinam as próximas execuções |
| Risco à separação template/execução | Baixo — não há alteração funcional, mas a restauração deve manter os registros e vínculos sem propagação retroativa entre templates e execuções |
| Dependências | Rotina local e runbook existentes em `scripts/backup_database.sh` e `docs/operations/postgresql-backups.md`; definição no refinamento de destino externo agnóstico de provedor, credenciais, criptografia, retenção, monitoramento e teste de restauração; [BL-0009](BL-0009-criptografia-repouso.md) é relacionada, mas não bloqueia a proteção obrigatória da cópia externa |
| Duplicidades | Nenhuma identificada; o backup local legado e a BL-0009 cobrem controles relacionados, mas não criam uma cópia em domínio de falha separado |
| Responsável pela próxima etapa | Engenharia Jaci |
| Próximo passo | Refinar destino externo, transferência verificável, criptografia, menor privilégio, retenção, monitoramento de falhas e restaurações periódicas, incluindo RPO e RTO |

## Acompanhamento até produção

- Documento refinado: ainda não criado.
- Implementação (commits/PRs): ainda não iniciada.
- Validações: triagem baseada na decisão e no runbook do backup PostgreSQL, na
  configuração de produção e na cobertura automatizada existente; validações de
  implementação ainda não iniciadas.
- Publicação: ainda não publicada.
- Itens relacionados: [BL-0009](BL-0009-criptografia-repouso.md) e backup local
  concluído nas
  [entregas legadas sem BL](../../decisions/backlog.md#entregas-concluídas-sem-identificador-bl-legado).

### Impedimentos

- Nenhum registrado; provedor, RPO, RTO e retenção externa serão definidos no
  refinamento sem bloquear a promoção do item.

## Histórico

| Data/hora | Autor | Mudança | Motivo/evidência |
| --- | --- | --- | --- |
| `2026-07-24 00:48 -03` | Codex | Item criado em `recebido` | Migração da limitação operacional documentada |
| `2026-08-05 22:15 -03` | Usuário/Codex | `recebido` -> `em_triagem` | Prioridade P1 e direção agnóstica de provedor confirmadas; evidências da rotina local e do domínio único de falha confrontadas |
| `2026-08-05 22:15 -03` | Codex | `em_triagem` -> `pronto_para_refinamento` | Classificação, riscos, dependências, duplicidades, responsável e próximo passo definidos |
