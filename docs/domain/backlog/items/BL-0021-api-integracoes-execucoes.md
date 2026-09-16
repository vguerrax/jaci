# BL-0021 — Expor API externa para criar e editar execuções

## Identificação e entrada

| Campo | Valor |
| --- | --- |
| ID | `BL-0021` |
| Título | Expor API externa para criar e editar execuções |
| Tipo | `melhoria` |
| Estado | `pronto_para_implementacao` |
| Severidade | `N/A` |
| Prioridade | `P2` |
| Data de entrada | `2026-09-16` |
| Origem | Solicitação do usuário para integrar o Jaci a outros sistemas |
| Ambiente/versão | Estado de `develop` (`179ce51`) em `2026-09-16` |
| Responsável | Engenharia Jaci |
| Atualizado em | `2026-09-16` |

### Comportamento observado

O Jaci possui rotas HTML e uma API de sincronização offline autenticadas pela
sessão de uma pessoa. Não existe credencial máquina a máquina vinculada a um
grupo nem contrato público para um sistema externo consultar categorias e
execuções, criar uma execução ou reconciliar alterações concorrentes.

Uma integração precisa simular a navegação autenticada de uma pessoa ou operar
diretamente no banco, alternativas que não oferecem um contrato estável, menor
privilégio, isolamento verificável por grupo, revogação ou auditoria adequada.

### Comportamento esperado

O proprietário do grupo deve poder criar múltiplas chaves nomeadas, com
expiração opcional, visualizar o segredo somente no momento da criação e
revogar cada integração separadamente.

Uma chave válida deve permitir ao sistema externo, dentro do grupo ao qual ela
pertence:

- consultar categorias e execuções;
- criar execuções avulsas agendadas, opcionalmente com itens planejados;
- editar cabeçalho e itens planejados enquanto a execução estiver agendada;
- repetir criações com idempotência e detectar atualizações concorrentes por
  versão, sem sobrescrita silenciosa.

A primeira versão não inicia, finaliza ou cancela compras e não escreve
quantidade comprada, preço, local ou conclusão de item.

### Impacto e abrangência

- Impacto: sistemas externos não conseguem automatizar o planejamento de
  compras sem acoplamento indevido à interface ou ao banco do Jaci.
- Abrangência: proprietários de grupo, chaves de integração, categorias,
  execuções avulsas e vinculadas, itens planejados, API REST, auditoria e
  infraestrutura Redis.
- Frequência: sempre que uma automação externa precisar criar, consultar ou
  atualizar o planejamento de uma compra.

### Passos de reprodução

1. Autenticar no Jaci como proprietário de um grupo.
2. Procurar uma opção para emitir uma chave de API vinculada ao grupo.
3. Procurar um endpoint público versionado para criar ou editar uma execução.
4. Confirmar que os dois recursos não existem.

### Evidências sanitizadas

- [`get_current_user`](../../../../app/dependencies.py) autentica rotas pela
  sessão de uma pessoa.
- [`app/routers/offline.py`](../../../../app/routers/offline.py) oferece
  operações JSON apenas para a fila offline do cliente autenticado.
- [`Execution`](../../../../app/models/execution.py) exige `created_by`, mas
  ainda não registra a chave responsável por uma mutação externa.
- [BL-0006](BL-0006-integracoes-externas.md) cobre exportação e
  compartilhamento iniciados pelo usuário e declara que outras integrações
  externas devem receber demandas próprias.

### Workaround

Não há workaround suportado. Automação da interface ou acesso direto ao banco
quebraria os limites de segurança e compatibilidade do produto.

## Triagem

| Campo | Valor |
| --- | --- |
| Confirmação | `confirmado` por inspeção das dependências, rotas, modelos e serviços atuais |
| Classificação | Melhoria de integração máquina a máquina com credencial de grupo, API REST versionada e concorrência explícita |
| Domínio afetado | Grupos, segurança, execuções, itens, categorias, sincronização, auditoria e infraestrutura |
| Regras de negócio afetadas | RN01, RN02, RN05, RN07, RN08, RN09, RN10, RN12, RN13 e RN14; datas civis seguem ADR 0001 |
| Risco de segurança | Alto — a chave autoriza escrita; segredo, hash, revogação, expiração, rate limit, auditoria e respostas sem enumeração devem ser obrigatórios |
| Risco de LGPD | Alto — nomes, datas, orçamento e itens revelam hábitos de consumo; respostas, auditoria e idempotência devem minimizar e reter somente dados necessários |
| Risco de isolamento por grupo | Alto — a chave deve derivar o grupo no servidor e toda categoria, execução e item deve ser carregado nesse escopo, ignorando IDs de outro grupo |
| Risco offline/sincronização | Alto — uma escrita externa pode concorrer com estado local pendente; versões, conflitos `409`, persistência antes do WebSocket e reconciliação são obrigatórios |
| Risco ao histórico financeiro | Médio — a v1 não escreve dados de compra e bloqueia execução não agendada; leituras e edições não podem alterar valores históricos |
| Risco à recorrência | Baixo — a API cria somente execuções avulsas e não executa transições de ciclo; editar execução vinculada não muda template ou recorrência |
| Risco à separação template/execução | Médio — edições afetam somente o snapshot da execução e devem preservar a imutabilidade do nome de item vinculado |
| Dependências | PostgreSQL/Alembic, Redis ainda não configurado no repositório, serviços de execução e categoria, Socket.IO complementar e infraestrutura futura de UI da BL-0011 |
| Duplicidades | Nenhuma; relacionada à [BL-0006](BL-0006-integracoes-externas.md), que cobre compartilhamento manual e não uma API de escrita |
| Responsável pela próxima etapa | Engenharia Jaci |
| Próximo passo | Obter aprovação explícita do refinamento versionado e iniciar contratos TDD pela fundação de credenciais, auditoria, idempotência e versões |

## Acompanhamento até produção

- Documento refinado: [Refinamento BL-0021](../../tasks/BL-0021-api-integracoes-execucoes.md).
- Implementação (commits/PRs): ainda não iniciada; bloqueada pelo gate de aprovação.
- Validações: revisão documental e `git diff --check`; testes executáveis ainda
  não iniciados.
- Publicação: ainda não publicada.
- Itens relacionados: [BL-0006](BL-0006-integracoes-externas.md) e
  [BL-0011](BL-0011-ampliar-cobertura-testes-ui.md).

### Impedimentos

- Implementação bloqueada até a aprovação explícita do refinamento versionado.

## Histórico

| Data/hora | Autor | Mudança | Motivo/evidência |
| --- | --- | --- | --- |
| `2026-09-16 19:45 -03` | Usuário/Codex | Item criado em `recebido` | Solicitação de API externa com chave vinculada ao grupo |
| `2026-09-16 19:45 -03` | Codex | `recebido` → `em_triagem` | Escopo confrontado com autenticação, grupos, execuções e API offline existentes |
| `2026-09-16 19:45 -03` | Usuário/Codex | `em_triagem` → `pronto_para_refinamento` | Escopo, autoria, leitura, concorrência, validade da chave e Redis decididos com o usuário |
| `2026-09-16 19:45 -03` | Codex | `pronto_para_refinamento` → `em_refinamento` → `pronto_para_implementacao` | Contrato HTTP, riscos, fatias TDD e validações definidos; aguarda aprovação explícita |
