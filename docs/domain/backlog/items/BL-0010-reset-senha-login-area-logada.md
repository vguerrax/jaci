# BL-0010 — Disponibilizar reset de senha via login e área logada

## Identificação e entrada

| Campo | Valor |
| --- | --- |
| ID | `BL-0010` |
| Título | Disponibilizar reset de senha via login e área logada |
| Tipo | `melhoria` |
| Estado | `recebido` |
| Severidade | `a_triar` |
| Prioridade | `a_definir` |
| Data de entrada | `2026-07-24` |
| Origem | Solicitação do usuário |
| Ambiente/versão | Estado de `develop` em `2026-07-24` |
| Responsável | `a_definir` |
| Atualizado em | `2026-07-24` |

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
| Dependências | Integração com o serviço de identidade Tupã; detalhamento `a_triar` |
| Duplicidades | `a_triar` |
| Responsável pela próxima etapa | `a_definir` |
| Próximo passo | Realizar triagem de produto, segurança, sessões e integração com o Tupã |

## Acompanhamento até produção

- Documento refinado: ainda não criado.
- Implementação (commits/PRs): ainda não iniciada.
- Validações: ainda não iniciadas.
- Publicação: ainda não publicada.
- Itens relacionados: nenhum definido antes da triagem.

### Impedimentos

- Nenhum registrado; os contratos disponíveis no Tupã dependem da triagem.

## Histórico

| Data/hora | Autor | Mudança | Motivo/evidência |
| --- | --- | --- | --- |
| `2026-07-24 00:57 -03` | Codex | Item criado em `recebido` | Solicitação do usuário |
