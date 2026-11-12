# BL-0009 — Implementar criptografia de dados em repouso

> **Abortada pelo usuário em 2026-11-10.** O estado terminal do processo é
> `rejeitado`. As implementações e validações abaixo são histórico, sem entrega
> em produção. Mantido o dump PostgreSQL diário existente, sem criptografia,
> com retenção de 30 dias por padrão. Cópias externas são manuais, sob controle
> do usuário. O código das tasks não deve ser integrado à release.

## Identificação e entrada

| Campo | Valor |
| --- | --- |
| ID | `BL-0009` |
| Título | Implementar criptografia de dados em repouso |
| Versão-alvo | `1.5.0` |
| Tipo | `melhoria` |
| Estado | `rejeitado` |
| Severidade | `N/A` |
| Prioridade | `P1` |
| Data de entrada | `2026-07-24` |
| Origem | Limitação de segurança registrada na Política de Privacidade |
| Ambiente/versão | Estado de `develop` em `2026-07-24` |
| Responsável | Engenharia Jaci |
| Atualizado em | `2026-11-10` |

### Comportamento observado

A Política de Privacidade declara que a aplicação não implementa criptografia
em repouso no MVP e depende da proteção oferecida pelo sistema de arquivos ou
pela infraestrutura que armazena o PostgreSQL e seus backups.

### Comportamento esperado

Dados persistidos e cópias de segurança devem ter proteção em repouso adequada
ao ambiente de produção, com gestão de chaves, controles de acesso e
procedimentos operacionais compatíveis com LGPD e recuperação de desastres.

### Impacto e abrangência

- Impacto: a confidencialidade dos dados armazenados depende integralmente da
  configuração da infraestrutura.
- Abrangência: PostgreSQL, volumes, backups e ambientes que armazenem dados do
  Jaci.
- Frequência: contínua enquanto a proteção não for definida e verificada.

### Passos de reprodução

1. Consultar a Política de Privacidade.
2. Verificar a seção de segurança da informação.
3. Observar a limitação declarada para criptografia em repouso.

### Evidências sanitizadas

- [Política de Privacidade](../../../../app/templates/pages/legal/privacy.html).
- [Operação de backups](../../../operations/postgresql-backups.md).

### Workaround

Usar criptografia de disco, volume ou banco fornecida pela infraestrutura e
restringir o acesso aos dados e backups.

## Triagem

| Campo | Valor |
| --- | --- |
| Confirmação | `confirmado` |
| Classificação | Melhoria de segurança, conformidade e infraestrutura para garantir proteção verificável dos dados persistidos no servidor e de suas cópias de segurança |
| Domínio afetado | PostgreSQL gerenciado, volumes do host, dumps locais, futuros backups externos, gestão de chaves, restauração e documentação operacional |
| Regras de negócio afetadas | Preservar disponibilidade, integridade e restauração completa; não alterar registros, recalcular recorrências nem propagar mudanças entre templates e execuções; não tornar a operação dependente de uma chave sem recuperação verificável |
| Risco de segurança | Alto — banco, volumes e dumps concentram dados de todos os grupos; controles de acesso, criptografia, chaves, logs e restauração devem impedir leitura, alteração ou indisponibilidade não autorizada |
| Risco de LGPD | Alto — os artefatos persistidos contêm dados pessoais e hábitos de consumo; finalidade, acesso, retenção, descarte e evidências dos controles devem ser coerentes com a Política de Privacidade |
| Risco de isolamento por grupo | Alto — acesso direto ao banco, backup ou chave contorna os filtros da aplicação e pode expor simultaneamente informações de múltiplos grupos |
| Risco offline/sincronização | Baixo — a proteção do servidor é independente do uso offline; esta demanda não exige criptografia do IndexedDB e não pode interromper cache, fila ou sincronização existentes |
| Risco ao histórico financeiro | Alto — perda, corrupção ou rotação incorreta de chaves pode inviabilizar a leitura e a restauração de valores e registros históricos |
| Risco à recorrência | Baixo — criptografia e restauração não devem recalcular ciclos; datas, estados e vínculos precisam ser preservados integralmente |
| Risco à separação template/execução | Baixo — a proteção é transversal e não deve alterar snapshots, vínculos existentes nem propagar mudanças retroativas entre templates e execuções |
| Dependências | Inventário dos controles reais do ambiente de produção; definição agnóstica de provedor para armazenamento, acesso, rotação e recuperação de chaves; integração com backup e restauração; [BL-0007](BL-0007-replicacao-externa-backups.md) é relacionada, mas não bloqueia esta demanda |
| Duplicidades | Nenhuma identificada; permissões atuais dos dumps, proteção eventualmente fornecida pela infraestrutura e a BL-0007 são controles ou evoluções relacionados, não substituem a verificação ponta a ponta desta demanda |
| Responsável pela próxima etapa | Engenharia Jaci |
| Próximo passo | Nenhuma execução ou integração; demanda abortada pelo usuário |

## Acompanhamento até produção

- Documento refinado: [BL-0009](../../tasks/BL-0009-criptografia-repouso.md).
- Branch: feature/BL-0009-criptografia-repouso; três subtarefas aprovadas, 3/3 implementadas; mesma worktree.
- Implementação (commits/PRs): 83a00d0 (configuração/contratos), 00d11c7 (pipeline/retenção), 0f3f0f7 (fechamento operacional) e registro posterior da validação; sem PR ou merge da BL-0007.
- Validações: AST, bash -n, links locais, diff e grafo na implementação. Depois,
  usuário informou ./scripts/run_tests.sh --coverage: 329 passes/1 skip age real/
  2 xfail FL-08, 19 avisos python-jose, 63,35s e cobertura de app 60,04%. Piso
  elevado a 60% por solicitação explícita. Depois, usuário informou teste age real
  isolado: 1 passed em 1,08s (criptografia/descriptografia, rotação, chave errada
  e corrupção; PostgreSQL simulado). Sem execução pelo Codex. Integração, build,
  restauração PostgreSQL, RPO/RTO e volume permanecem pendentes.
- Publicação: ainda não publicada.
- Itens relacionados: [BL-0007](BL-0007-replicacao-externa-backups.md).

### Decisão de encerramento

- Aborto explícito em 2026-11-10: manter o backup automático em dump e retenção
  de pelo menos 30 dias; não criptografar nem automatizar cópia externa.
- A configuração versionada existente tem BACKUP_ENABLED=true e retenção de
  30 dias por padrão, cron 02h30 America/Sao_Paulo e volume persistente no host.
  Não houve inspeção da configuração real ou execução do container.
- Os commits da implementação permanecem nas branches como histórico; não foram
  publicados ou integrados à release/develop/main. A worktree corrente volta ao
  código de backup existente na base 1cedb61. O piso independente de 60% permanece.
- Validações operacionais anteriores deixam de ser pendências dessas demandas.
  Arquivamento em rejeitado não equivale a publicação ou aceite de produção.

## Histórico

| Data/hora | Autor | Mudança | Motivo/evidência |
| --- | --- | --- | --- |
| `2026-07-24 00:48 -03` | Codex | Item criado em `recebido` | Migração da limitação de segurança documentada |
| `2026-08-05 22:28 -03` | Usuário/Codex | `recebido` -> `em_triagem` | Prioridade P1 e escopo de servidor e backups confirmados; política, configuração do banco, volume, dumps e persistência offline confrontados |
| `2026-08-05 22:28 -03` | Codex | `em_triagem` -> `pronto_para_refinamento` | Classificação, riscos, dependências, duplicidades, responsável e próximo passo definidos |
| `2026-10-28 20:40 -03` | Codex | Versão-alvo 1.5.0 associada | Roadmap aprovado para formalização; estado e prioridade preservados, sem autorizar implementação |
| `2026-10-29` | Usuário/Codex | pronto_para_refinamento → em_refinamento → pronto_para_implementacao | Decisões da 1.5.0 documentadas: máquina local ligada, Caddy por SFTP, age com chave privada do usuário, RPO 24h/RTO 4h/30 dias; aprovação pós-versionamento pendente |
| `2026-10-30` | Usuário/Codex | pronto_para_implementacao → em_implementacao | Pedido explícito “Implemente a BL-009 também” após refinamento 3660568; três subtarefas na mesma worktree, sem executar testes ou alterar ambiente/infraestrutura |
| `2026-10-30` | Codex | em_implementacao → em_validacao | Três subtarefas implementadas; testes não executados; instruções de guarda/recuperação e ficha OCI entregues sem afirmar ativação; integração, volume, restauração e publicação pendentes |
| `2026-10-30` | Usuário/Codex | Validação reportada e piso elevado a 60%; em_validacao mantido | Log do usuário: 329 passes/1 skip age real/2 xfail FL-08, 60,04% de app; pedido explícito do novo mínimo. Codex não repetiu testes; recuperação, volume, integração e publicação pendentes |
| `2026-10-30` | Usuário/Codex | Teste age real aprovado; em_validacao mantido | Execução focal informada pelo usuário: 1 passed em 1,08s, com chaves efêmeras e PostgreSQL simulado; sem repetir suíte, alterar ambiente ou assumir aceite de produção |
| `2026-11-10` | Usuário/Codex | em_validacao → rejeitado; abortada e arquivada | Usuário optou por dump diário existente, retenção de pelo menos 30 dias e cópia manual; sem criptografia, envio automático ou integração do código não publicado |
