# BL-0009 — Implementar criptografia de dados em repouso

## Identificação e entrada

| Campo | Valor |
| --- | --- |
| ID | `BL-0009` |
| Título | Implementar criptografia de dados em repouso |
| Tipo | `melhoria` |
| Estado | `recebido` |
| Severidade | `a_triar` |
| Prioridade | `a_definir` |
| Data de entrada | `2026-07-24` |
| Origem | Limitação de segurança registrada na Política de Privacidade |
| Ambiente/versão | Estado de `develop` em `2026-07-24` |
| Responsável | `a_definir` |
| Atualizado em | `2026-07-24` |

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
| Próximo passo | Realizar triagem do modelo de ameaça, infraestrutura e gestão de chaves |

## Acompanhamento até produção

- Documento refinado: ainda não criado.
- Implementação (commits/PRs): ainda não iniciada.
- Validações: ainda não iniciadas.
- Publicação: ainda não publicada.
- Itens relacionados: [BL-0007](BL-0007-replicacao-externa-backups.md).

### Impedimentos

- Nenhum registrado; controles existentes e requisitos devem ser confirmados na
  triagem.

## Histórico

| Data/hora | Autor | Mudança | Motivo/evidência |
| --- | --- | --- | --- |
| `2026-07-24 00:48 -03` | Codex | Item criado em `recebido` | Migração da limitação de segurança documentada |
