# BL-0019 — Manter sessão autenticada por oito horas de inatividade

## Identificação e entrada

| Campo | Valor |
| --- | --- |
| ID | `BL-0019` |
| Título | Manter sessão autenticada por oito horas de inatividade |
| Versão-alvo | `1.5.0` |
| Tipo | `melhoria` |
| Estado | `concluido` |
| Severidade | `N/A` |
| Prioridade | `P1` |
| Data de entrada | `2026-08-05` |
| Origem | Solicitação do usuário |
| Ambiente/versão | Estado de `develop` em `2026-08-05` |
| Responsável | Engenharia Jaci |
| Atualizado em | `2026-11-11` |

### Comportamento observado

Inspeção estática em 2026-11-10: não existe last_activity/deadline persistido.
O cookie access usa expires_in; refresh cookie tem 30 dias. O middleware tenta
renovar quando access falta/falha, sem validar oito horas de inatividade ou
serializar refresh entre workers. A produção não foi medida nem seu ambiente lido.

O Tupã local (4cee88f) possui access de 15min/refresh de 7d por padrão e refresh
rotativo, mas valida access sem consulta de revogação. Reset revoga refresh;
troca autenticada não revoga refresh. Não há contrato de introspecção identificado.
A referência Potira (f17047c7) possui sessão persistida e refresh sob lock, com
política de limites/requests distinta da escolhida explicitamente para o Jaci.

### Comportamento esperado

Cada requisição HTTP autenticada ao servidor renova uma janela de oito horas,
inclusive requests automáticos, conforme decisão do usuário. Pings/pongs,
frames e permanência do WebSocket não atualizam atividade. Handshake HTTP
autenticado conta como requisição. Sem request,
validar passivamente na próxima tentativa, antes de refresh ou mutação.

Logout, revogação, usuário inativo e tokens inválidos impedem acesso. O usuário
aprovou novo login de todos os dispositivos após troca/reset, preservando a fila
offline. O contrato de revogação global efetiva do Tupã é dependência externa,
não garantia já existente. Não revalidar uma sessão vencida usando refresh válido.

### Impacto e abrangência

- Impacto: autenticações repetidas podem interromper o planejamento ou a
  execução de compras ao longo do dia.
- Abrangência: usuários autenticados no navegador e no PWA, cookies de sessão,
  renovação de tokens e integração com o Tupã.
- Frequência: desconhecida até a medição do comportamento atual.

### Passos de reprodução

Diagnóstico nesta triagem: ler middleware, cookies, cliente e dependências e
constatar ausência de estado de inatividade/guard compartilhado. Inspecionar
contrato Tupã para duração/rotação/revogação sem executar login. A medição prática
com relógio controlado e provedor sintético fica na validação futura, após aprovação;
não é evidência de uma duração observada em produção.

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
| Confirmação | `confirmado` |
| Classificação | Melhoria de continuidade/segurança com lacuna contratual confirmada por inspeção estática; não foi medido um defeito temporal em produção |
| Domínio afetado | Autenticação Jaci/Tupã, cookies, sessão persistida, HTTP/HTMX/API, WebSocket e retomada offline |
| Regras de negócio afetadas | Servidor valida prazo de 28.800s desde último request autenticado antes de renovar/autorização; cada HTTP válido conta, ping WS não; identidade/senha/revogação permanecem no Tupã; nunca ressuscitar sessão morta |
| Risco de segurança | Alto — replay/fixação, produto errado, refresh concorrente ou revogação ignorada; cookie opaco, CSRF/Origin, persistência compartilhada, lock e contrato D-01 da coordenação |
| Risco de LGPD | Médio — sessão e cache identificam pessoa; mínimo de metadados, tokens protegidos fora do browser/log e partição offline por identidade |
| Risco de isolamento por grupo | Alto — nova sessão não substitui vínculo por grupo; revalidar recursos e nunca retomar fila de outra conta |
| Risco offline/sincronização | Alto — preservar fila/versionamento/conflitos após expiração ou senha, suspender envio até autenticar mesma identidade; requests HTTP automáticos válidos contam conforme decisão explícita |
| Risco ao histórico financeiro | Baixo na regra de sessão, alto se retomada incorreta; não sobrescrever itens/totais/snapshots nem repetir comandos de compra como efeito do login |
| Risco à recorrência | Baixo — relogar/renovar não cria, reagenda ou recalcula execuções |
| Risco à separação template/execução | Baixo — nenhum efeito retroativo entre template e execução; preservar snapshots e observações |
| Dependências | BL-0010 para fluxos de senha; D-01 publicada no Tupã 1.1.0 e confirmada em 2026-11-11; concluir o adaptador e validar a integração do guard com o provedor |
| Duplicidades | Nenhuma; BL-0010 expõe recuperação/troca, enquanto esta task controla validade, concorrência e preservação da fila |
| Responsável pela próxima etapa | Engenharia Jaci |
| Próximo passo | Nenhum de implementação; 1.5.0 publicada e aceite aprovado. Divergência da tag registrada no roteiro |

## Acompanhamento até produção

- Documento refinado: [BL-0019](../../tasks/BL-0019-sessao-autenticada-oito-horas-inatividade.md).
- Coordenação: [versão 1.5.0](../../tasks/release-1.5.0-acesso-conta-sessao.md).
- Branch documental docs/refinamento-1.5.0; futura implementação feature/BL-0019-sessao-autenticada-oito-horas-inatividade, somente na worktree atual.
- Implementação: 37f0a09, b4ed3ee, cced2c4, fa438ae e bfd31dc; seis fatias
  implementadas, integração real e correção de primeiro acesso validadas.
- Validações: regressão/cobertura, UI, PostgreSQL concorrente e integração real
  com Tupã 1.1.0 aprovadas; resultados no refinamento. Aceite manual confirmado
  pelo usuário em 2026-11-11; publicação Jaci pendente.
- Publicação: Jaci 1.5.0, confirmada pelo usuário em 2026-11-11; commit implantado não informado. Tag local observada v1.5.0 em d959aff; divergência com a preparação registrada no roteiro.
- Itens relacionados: [BL-0010](BL-0010-reset-senha-login-area-logada.md); D-01
  externa publicada no Tupã 1.1.0.

### Impedimentos

- O adaptador e a validação automatizada estão concluídos. A ativação da
  sessão real usa chave/produto configurados. Aceite manual já aprovado;
  integração e publicação do Jaci dependem de liberação.

## Histórico

| Data/hora | Autor | Mudança | Motivo/evidência |
| --- | --- | --- | --- |
| `2026-08-05 15:27 -03` | Usuário/Codex | Item criado em `recebido` | Solicitação para manter a sessão por oito horas de inatividade |
| `2026-10-28 20:40 -03` | Codex | Versão-alvo 1.6.0 associada | Roadmap aprovado para formalização; estado e prioridade preservados, sem autorizar implementação |
| `2026-11-10` | Usuário/Codex | Versão-alvo 1.6.0 → 1.5.0 | Roadmap refeito após aborto da BL-0007/BL-0009; escopo remanescente antecipado em uma versão, estados e gates preservados |
| `2026-11-10` | Usuário/Codex | recebido → em_triagem → pronto_para_refinamento | Lacuna confirmada estaticamente em Jaci 9d6a18c e Tupã 4cee88f; N/A/P1 e riscos definidos; sem medição ou teste em produção |
| `2026-11-10` | Usuário/Codex | Critério de atividade e encerramento definido | Cada request autenticado conta, inclusive automático; ping WS não; trocar/recuperar senha exige novo login em todos os dispositivos preservando fila |
| `2026-11-10` | Codex | pronto_para_refinamento → em_refinamento → pronto_para_implementacao | Plano de seis fatias e dependência D-01 documentados; gate de aprovação pós-versionamento preservado; nenhuma implementação iniciada |

| `2026-11-10` | Usuário/Codex | pronto_para_implementacao → em_implementacao | Pedido explícito de criar/usar release e implementar após refinamento 75ac29e; release/v1.5.0 avançada ao refinamento e branch pai atualizada; sem testes, ambientes ou trabalho no Tupã |


## Acompanhamento da implementação

O código local foi preparado na branch `feature/BL-0019-sessao-autenticada-oito-horas-inatividade`,
a partir de `release/v1.5.0`. Sessão persistida, HTTP, WebSocket e fila por conta
têm implementação opt-in e contratos de teste. O contrato D-01 foi publicado no Tupã 1.1.0. O aceite executável e a
integração do adaptador são acompanhados na branch. A demanda segue em `em_validacao` após as verificações registradas em 2026-11-11.


### Evidência externa — 2026-11-11

O usuário confirmou a publicação do Tupã 1.1.0 e informou a instância de
testes na porta 8005. A consulta do contrato com token sintético inválido
retornou `active=false` e `no-store`. Referência externa Tupã:
`docs/release-1.1.0.md`, integração main `78244b6`.


### Integração e validação — 2026-11-11

Adaptador real da D-01 implementado. A última regressão completa executada
teve 351 testes aprovados, dois xfails previstos e cobertura de 63,27%.
O cenário Playwright da sessão/fila passou, assim como os três testes focais
de WebSocket. PostgreSQL descartável confirmou um único refresh para duas
conexões concorrentes. A integração com Tupã de testes passou com conta
temporária removida ao final. Transição `em_implementacao -> em_validacao`.
Aceite manual e publicação do Jaci permanecem pendentes.

### Correção durante validação — 2026-11-11

Ajustado o primeiro acesso pela raiz para abrir o login sem aviso de
expiração quando o navegador não apresenta sessão anterior. Correção
tratada na própria BL-0019 e na sua branch pai, com contratos HTTP e UI.


### Aceite manual — 2026-11-11

O usuário confirmou a validação manual da BL-0019 e aprovou o resultado.
A publicação do Jaci e a integração das branches seguem pendentes.


### Integração e preparação da 1.5.0 — 2026-11-11

Código integrado à release/v1.5.0 (b3ef2d5) e develop (5e9d777, PR #48),
confirmado pelo usuário e pelo histórico local. As notas e o roteiro de
publicação estão em docs/releases/1.5.0.md e docs/releases/1.5.0-publicacao.md.
Preparação com metadados 1.5.0 validada na release; sua integração, ativação do
guard/chave em produção e publicação ainda estão pendentes. Aceite manual
preservado e estado em_validacao até publicação; ambiente real intocado.


## Publicação confirmada — 2026-11-11

Usuário confirmou a publicação do Jaci 1.5.0. Aceite manual e validações da
implementação já aprovados; demanda passa de em_validacao para concluido.
Registro baseado no relato de publicação, sem executar novo deploy, migração,
consulta à produção ou teste. Nenhuma configuração real foi alterada.

Referências locais conferidas: main 903cb1b, develop 4315e76 e tag v1.5.0 em
d959aff. A preparação 98ece73 está na main/develop, mas não está na tag atual.
O commit efetivamente implantado não foi informado; não atribuir o relato do
deploy ao hash da tag por inferência. Preservar a tag, sem movê-la ou recriá-la.
A divergência de rastreabilidade fica registrada no roteiro da release.
