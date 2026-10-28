# BL-0010 — Disponibilizar reset de senha via login e área logada

## Identificação e entrada

| Campo | Valor |
| --- | --- |
| ID | `BL-0010` |
| Título | Disponibilizar reset de senha via login e área logada |
| Tipo | `melhoria` |
| Estado | `pronto_para_refinamento` |
| Severidade | `N/A` |
| Prioridade | `P1` |
| Data de entrada | `2026-07-24` |
| Origem | Solicitação do usuário |
| Ambiente/versão | Estado de `develop` em `2026-07-24` |
| Responsável | Engenharia Jaci |
| Atualizado em | `2026-08-05` |

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
| Dependências | Contratos existentes do Tupã `POST /auth/forgot-password`, `POST /auth/reset-password` e `POST /auth/change-password`; entrega de e-mail; `base_url` pública do produto Jaci configurada no Tupã; definição no refinamento da política de sessão após troca autenticada; [BL-0019](BL-0019-sessao-autenticada-oito-horas-inatividade.md) é relacionada, mas não bloqueia esta demanda |
| Duplicidades | Nenhuma identificada; a BL-0019 trata duração de sessão e revogação, mas não disponibiliza recuperação nem troca de senha |
| Responsável pela próxima etapa | Engenharia Jaci |
| Próximo passo | Refinar os fluxos público e autenticado, o tratamento seguro do token opaco, mensagens e limites, configuração da URL pública, comportamento das sessões e cobertura automatizada, identificando eventual demanda correspondente no Tupã se o contrato precisar mudar |

## Acompanhamento até produção

- Documento refinado: ainda não criado.
- Implementação (commits/PRs): ainda não iniciada.
- Validações: triagem baseada nas páginas e rotas atuais do Jaci e nos contratos,
  esquemas e testes existentes do Tupã; validações de implementação ainda não
  iniciadas.
- Publicação: ainda não publicada.
- Itens relacionados:
  [BL-0019](BL-0019-sessao-autenticada-oito-horas-inatividade.md).

### Impedimentos

- Nenhum registrado; a configuração efetiva da `base_url` pública e a política
  de revogação após troca autenticada serão confirmadas no refinamento sem
  bloquear a promoção do item.

## Histórico

| Data/hora | Autor | Mudança | Motivo/evidência |
| --- | --- | --- | --- |
| `2026-07-24 00:57 -03` | Codex | Item criado em `recebido` | Solicitação do usuário |
| `2026-08-05 22:38 -03` | Usuário/Codex | `recebido` -> `em_triagem` | Prioridade P1 e responsável Engenharia Jaci confirmados; interface atual e contratos públicos e autenticados do Tupã confrontados |
| `2026-08-05 22:38 -03` | Codex | `em_triagem` -> `pronto_para_refinamento` | Classificação, riscos, dependências, duplicidades, responsável e próximo passo definidos |
