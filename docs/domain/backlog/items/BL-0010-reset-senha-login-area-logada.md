# BL-0010 — Disponibilizar reset de senha via login e área logada

## Identificação e entrada

| Campo | Valor |
| --- | --- |
| ID | `BL-0010` |
| Título | Disponibilizar reset de senha via login e área logada |
| Versão-alvo | `1.5.0` |
| Tipo | `melhoria` |
| Estado | `em_validacao` |
| Severidade | `N/A` |
| Prioridade | `P1` |
| Data de entrada | `2026-07-24` |
| Origem | Solicitação do usuário |
| Ambiente/versão | Estado de `develop` em `2026-07-24` |
| Responsável | Engenharia Jaci |
| Atualizado em | `2026-11-11` |

### Comportamento observado

A tela de login não oferece uma ação para recuperar ou redefinir uma senha
esquecida. Na área logada, o perfil apenas informa que a senha é gerenciada
pelo Tupã e orienta o usuário a utilizar um canal externo não disponibilizado
diretamente pela interface do Jaci.

### Comportamento esperado

O usuário deve conseguir iniciar um fluxo seguro de redefinição de senha tanto
pela tela de login, quando não consegue acessar a conta, quanto pela área
logada, quando deseja trocar a senha. A identidade e as credenciais devem
continuar sob responsabilidade do Tupã.

### Impacto e abrangência

- Impacto: usuários dependem de suporte ou de um canal externo não apresentado
  pela aplicação para recuperar ou trocar a senha.
- Abrangência: usuários que utilizam autenticação por e-mail e senha, nos
  fluxos de login e perfil.
- Frequência: sempre que um usuário esquece ou deseja trocar a senha.

### Passos de reprodução

1. Acessar a tela de login e procurar uma ação de recuperação de senha.
2. Observar que não há opção para iniciar a redefinição.
3. Autenticar-se, acessar o perfil e procurar uma ação de troca de senha.
4. Observar que a aplicação apenas orienta o uso de um canal externo.

### Evidências sanitizadas

- [Tela de login](../../../../app/templates/pages/login.html).
- [Área de autenticação do perfil](../../../../app/templates/pages/profile.html).
- [Rota atual de alteração de senha](../../../../app/routers/auth.py).

### Workaround

Buscar o canal externo disponibilizado pelo Tupã; o Jaci não apresenta
diretamente esse acesso.

## Triagem

| Campo | Valor |
| --- | --- |
| Confirmação | `confirmado` |
| Classificação | Melhoria de experiência e segurança de autenticação para expor no Jaci os contratos de recuperação e troca de senha já fornecidos pelo Tupã |
| Domínio afetado | Autenticação por e-mail e senha, login, perfil, sessões, cliente do Tupã e entrega de notificações por e-mail |
| Regras de negócio afetadas | Manter identidade, senha e tokens sob responsabilidade do Tupã; não persistir senha ou token de redefinição no Jaci; preservar resposta genérica na solicitação para não enumerar contas; tratar o token como opaco, temporário e de uso único; apresentar falhas e expiração explicitamente sem expor dados sensíveis |
| Risco de segurança | Alto — o fluxo público e o fluxo autenticado manipulam credenciais e token de redefinição; logs, URLs, mensagens, validação da senha atual e política de revogação de sessões devem impedir enumeração, vazamento, reutilização e tomada de conta |
| Risco de LGPD | Médio — o e-mail identifica a pessoa e participa da notificação; respostas, logs e métricas não podem revelar cadastro, token ou credenciais, e o tratamento deve permanecer limitado à recuperação de acesso |
| Risco de isolamento por grupo | Baixo — o fluxo atua na identidade do produto, não em dados de grupos; o `product_id` do Jaci e a identidade autenticada devem impedir ações entre produtos ou contas, sem confiar em grupo enviado pelo cliente |
| Risco offline/sincronização | Baixo — recuperação, troca de senha e entrega de e-mail exigem conexão com o Tupã; indisponibilidade deve falhar de forma clara, sem enfileirar credenciais nem tornar estado local ou WebSocket fonte de verdade |
| Risco ao histórico financeiro | Baixo — nenhuma compra ou valor é alterado; troca de credencial e eventual encerramento de sessões devem preservar integralmente o histórico associado à conta |
| Risco à recorrência | Baixo — o fluxo de autenticação não deve criar, cancelar, reagendar ou recalcular execuções recorrentes |
| Risco à separação template/execução | Baixo — não há mutação de templates ou execuções e nenhum dado deve ser propagado entre esses domínios |
| Dependências | Contratos Tupã forgot/reset/change-password; Product.base_url e e-mail; guard da [BL-0019](BL-0019-sessao-autenticada-oito-horas-inatividade.md); D-01 publicada no Tupã 1.1.0 para revogação global, consulta de validade e reset vinculado à credencial do produto |
| Duplicidades | Nenhuma identificada; a BL-0019 trata duração de sessão e revogação, mas não disponibiliza recuperação nem troca de senha |
| Responsável pela próxima etapa | Engenharia Jaci |
| Próximo passo | Aceite manual da recuperação/perfil, conferência de e-mail/base_url/logs pelo operador e liberação da integração/publicação da 1.5.0 |

## Acompanhamento até produção

- Documento refinado: [BL-0010](../../tasks/BL-0010-reset-senha-login-area-logada.md).
- Coordenação: [versão 1.5.0](../../tasks/release-1.5.0-acesso-conta-sessao.md).
- Branch documental docs/refinamento-1.5.0; futura implementação feature/BL-0010-reset-senha-login-area-logada, somente na worktree atual.
- Implementação: 2721091 (núcleo/contratos), a559476 (fluxos HTTP/perfil/PWA);
  fatia 2.3 e evidências no commit que acompanha este documento.
- Validações: seis fatias implementadas e contratos automatizados aprovados;
  resultados finais e cenários rastreados no refinamento. Nenhum e-mail, serviço
  ou banco real foi usado para a regressão da BL-0010.
- Publicação: ainda não publicada.
- Itens relacionados:
  [BL-0019](BL-0019-sessao-autenticada-oito-horas-inatividade.md).

### Impedimentos

- Sem bloqueio de código. Aceite manual da BL-0019 confirmado. Pendente aceite
  da BL-0010, entrega real de e-mail, base_url, origem confiável/logs no proxy e
  liberação de integração/publicação do Jaci. Tupã 1.1.0 já publicado.

## Histórico

| Data/hora | Autor | Mudança | Motivo/evidência |
| --- | --- | --- | --- |
| `2026-07-24 00:57 -03` | Codex | Item criado em `recebido` | Solicitação do usuário |
| `2026-08-05 22:38 -03` | Usuário/Codex | `recebido` -> `em_triagem` | Prioridade P1 e responsável Engenharia Jaci confirmados; interface atual e contratos públicos e autenticados do Tupã confrontados |
| `2026-08-05 22:38 -03` | Codex | `em_triagem` -> `pronto_para_refinamento` | Classificação, riscos, dependências, duplicidades, responsável e próximo passo definidos |
| `2026-10-28 20:40 -03` | Codex | Versão-alvo 1.6.0 associada | Roadmap aprovado para formalização; estado e prioridade preservados, sem autorizar implementação |
| `2026-11-10` | Usuário/Codex | Versão-alvo 1.6.0 → 1.5.0 | Roadmap refeito após aborto da BL-0007/BL-0009; escopo remanescente antecipado em uma versão, estados e gates preservados |
| `2026-11-10` | Codex | pronto_para_refinamento → em_refinamento → pronto_para_implementacao | Seis fatias de recuperação/perfil, token opaco, cache/logs, CSRF e dependências BL-0019/D-01 refinadas; nenhuma implementação/teste iniciado |
| `2026-11-10` | Usuário/Codex | Política pós-senha definida | Novo login em todos os dispositivos, preservando fila; exigência depende de revogação atômica no Tupã e guard Jaci |


### Publicação da dependência — 2026-11-11

Tupã 1.1.0 publicado, conforme confirmação do usuário. A D-01 passou a
oferecer consulta de validade e revogação global da conta no produto.
O reset é vinculado ao produto quando o consumidor envia `X-Service-Token`.
A implementação da BL-0010 continua dependente de seu aceite de refinamento
e do guard da BL-0019.


## Implementação autorizada — 2026-11-11

Após aprovar o aceite manual da BL-0019, o usuário solicitou implementar a
BL-0010. A branch existente foi avançada por fast-forward para bfd31dc, base
validada da sessão, na mesma worktree. A integração à release segue pendente.


### Implementação entregue para validação — 2026-11-11

Seis fatias implementadas na branch pai, sem integração automática à release,
develop ou main. Recuperação genérica, limitação compartilhada, contexto protegido,
reset, perfil, revogação global e continuidade offline cobertos. Estado passa de
em_implementacao para em_validacao; publicação Jaci ainda não ocorreu.
