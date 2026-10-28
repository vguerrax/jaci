# BL-0019 — Manter sessão autenticada por oito horas de inatividade

## Identificação e entrada

| Campo | Valor |
| --- | --- |
| ID | `BL-0019` |
| Título | Manter sessão autenticada por oito horas de inatividade |
| Tipo | `melhoria` |
| Estado | `recebido` |
| Severidade | `a_triar` |
| Prioridade | `a_definir` |
| Data de entrada | `2026-08-05` |
| Origem | Solicitação do usuário |
| Ambiente/versão | Estado de `develop` em `2026-08-05` |
| Responsável | `a_definir` |
| Atualizado em | `2026-08-05` |

### Comportamento observado

A duração efetiva da sessão autenticada ainda não foi medida. O Jaci armazena
o access token em cookie com o tempo informado pelo Tupã e tenta renová-lo com
um refresh token quando a validação falha, mas a experiência atual não possui
um contrato documentado que garanta uma jornada autenticada baseada em
inatividade.

### Comportamento esperado

O usuário deve permanecer autenticado enquanto houver atividade e ter a sessão
encerrada somente depois de oito horas contínuas de inatividade. Logout
explícito, revogação, troca de senha e tokens inválidos devem continuar
encerrando ou impedindo a sessão imediatamente.

### Impacto e abrangência

- Impacto: autenticações repetidas podem interromper o planejamento ou a
  execução de compras ao longo do dia.
- Abrangência: usuários autenticados no navegador e no PWA, cookies de sessão,
  renovação de tokens e integração com o Tupã.
- Frequência: desconhecida até a medição do comportamento atual.

### Passos de reprodução

Ainda não há duração atual confirmada. A triagem deve autenticar um usuário,
acompanhar access token, refresh token e cookies durante períodos de atividade
e inatividade e registrar quando a sessão deixa de ser renovada.

### Evidências sanitizadas

- [Middleware de renovação](../../../../app/main.py).
- [Cookies de autenticação](../../../../app/utils/security.py).
- [Cliente de autenticação do Tupã](../../../../app/services/tupa_auth_service.py).
- [Segurança e autenticação](../../../../README.md).

### Workaround

Autenticar-se novamente quando a sessão deixar de ser reconhecida.

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
| Dependências | Política e contratos de access token, refresh token e revogação do Tupã; detalhamento `a_triar` |
| Duplicidades | `a_triar` |
| Responsável pela próxima etapa | `a_definir` |
| Próximo passo | Medir a duração atual, definir o conceito de atividade, avaliar riscos de segurança e identificar se será necessária uma demanda correspondente no Tupã |

## Acompanhamento até produção

- Documento refinado: ainda não criado.
- Implementação (commits/PRs): ainda não iniciada.
- Validações: somente diagnóstico documental inicial; validações da sessão ainda
  não iniciadas.
- Publicação: ainda não publicada.
- Itens relacionados: nenhum definido antes da triagem.

### Impedimentos

- Nenhum registrado; a duração atual e os contratos efetivos do Tupã devem ser
  confirmados na triagem.

## Histórico

| Data/hora | Autor | Mudança | Motivo/evidência |
| --- | --- | --- | --- |
| `2026-08-05 15:27 -03` | Usuário/Codex | Item criado em `recebido` | Solicitação para manter a sessão por oito horas de inatividade |
