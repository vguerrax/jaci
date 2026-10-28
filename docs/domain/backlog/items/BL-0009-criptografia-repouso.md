# BL-0009 — Implementar criptografia de dados em repouso

## Identificação e entrada

| Campo | Valor |
| --- | --- |
| ID | `BL-0009` |
| Título | Implementar criptografia de dados em repouso |
| Tipo | `melhoria` |
| Estado | `pronto_para_refinamento` |
| Severidade | `N/A` |
| Prioridade | `P1` |
| Data de entrada | `2026-07-24` |
| Origem | Limitação de segurança registrada na Política de Privacidade |
| Ambiente/versão | Estado de `develop` em `2026-07-24` |
| Responsável | Engenharia Jaci |
| Atualizado em | `2026-08-05` |

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
| Próximo passo | Refinar modelo de ameaça, inventário de dados e controles, camadas de proteção, gestão e recuperação de chaves, evidências operacionais, restauração e atualização dos documentos legais |

## Acompanhamento até produção

- Documento refinado: ainda não criado.
- Implementação (commits/PRs): ainda não iniciada.
- Validações: triagem baseada na Política de Privacidade, na configuração do
  PostgreSQL, no volume e na rotina local de backups e na arquitetura offline;
  validações de implementação ainda não iniciadas.
- Publicação: ainda não publicada.
- Itens relacionados: [BL-0007](BL-0007-replicacao-externa-backups.md).

### Impedimentos

- Nenhum registrado; o provedor e os controles reais de produção serão
  inventariados no refinamento sem bloquear a promoção do item.

## Histórico

| Data/hora | Autor | Mudança | Motivo/evidência |
| --- | --- | --- | --- |
| `2026-07-24 00:48 -03` | Codex | Item criado em `recebido` | Migração da limitação de segurança documentada |
| `2026-08-05 22:28 -03` | Usuário/Codex | `recebido` -> `em_triagem` | Prioridade P1 e escopo de servidor e backups confirmados; política, configuração do banco, volume, dumps e persistência offline confrontados |
| `2026-08-05 22:28 -03` | Codex | `em_triagem` -> `pronto_para_refinamento` | Classificação, riscos, dependências, duplicidades, responsável e próximo passo definidos |
