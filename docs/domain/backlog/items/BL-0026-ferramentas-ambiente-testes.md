# BL-0026 — Ferramentas, ambiente de testes e rastreabilidade das releases

## Identificação e entrada

| Campo | Valor |
| --- | --- |
| ID | `BL-0026` |
| Título | Ferramentas, ambiente de testes e rastreabilidade das releases |
| Tipo | `melhoria` |
| Versão-alvo | `1.4.0` |
| Estado | `em_validacao` |
| Severidade | `N/A` |
| Prioridade | `P1` |
| Data de entrada | `2026-10-28` |
| Origem | Plano de próximas versões solicitado pelo usuário |
| Ambiente/versão | develop após release v1.3.0 |
| Responsável | Engenharia Jaci |
| Atualizado em | `2026-10-28` |

### Comportamento observado

Testes Python usam fixtures SQLite e chamadas de rotas; a execução manual e a
validação de tokens dependem do Tupã. Não há AUTH_MOCK, ambiente dedicado ou
scripts comuns de preparação/execução de testes. Releases ainda não têm visão
planejada e versão-alvo nos itens.

### Comportamento esperado

Disponibilizar ambiente local isolado, reproduzível e sem Tupã para automação e
uso manual, com identidades sintéticas e autorização real. Padronizar scripts e
rastrear versões, dependências, fatias e evidências sem mudar IDs ou diretórios.

### Impacto e abrangência

- Impacto: reduzir configuração manual e permitir testar fluxos reais com segurança.
- Abrangência: ambiente, fronteira de autenticação de teste, scripts e documentação.
- Frequência: desenvolvimento, validação local e CI.

### Passos de reprodução

1. Inspecionar conftest.py, run.py e tupa_auth_service.py.
2. Procurar AUTH_MOCK e scripts de ambiente/UI, ausentes nesta base.
3. Consultar itens e observar ausência de versão-alvo antes deste registro.

### Evidências sanitizadas

- Testes existentes e autenticação inspecionados; base final da 1.3.0 com 262 passes
  e 5 xfail registrados, não reexecutados nesta etapa documental.
- [Roadmap](../releases.md); [refinamento](../../tasks/BL-0026-ferramentas-ambiente-testes.md).

### Workaround

Usar fixtures Python e autenticação Tupã para testes manuais.

## Triagem

| Campo | Valor |
| --- | --- |
| Confirmação | confirmado por inventário de configuração, scripts e autenticação |
| Classificação | Estrutura de trabalho e ferramentas, sem migração de arquitetura |
| Domínio afetado | Ambiente, autenticação simulada, scripts e rastreabilidade |
| Regras de negócio afetadas | Autorização, isolamento por grupo e preservação de dados |
| Risco de segurança | Alto — mock deve ser impossível de ativar no ambiente de produção |
| Risco de LGPD | Médio — somente identidades e dados sintéticos; proibir cópia de produção |
| Risco de isolamento por grupo | Alto — mock autentica, mas não contorna autorização |
| Risco offline/sincronização | Médio — persistência de teste deve suportar reinício e duas sessões |
| Risco ao histórico financeiro | Médio — impedir setup/limpeza em bancos reais |
| Risco à recorrência | Baixo — cenário sintético, sem alterar cálculo existente |
| Risco à separação template/execução | Baixo — regras atuais preservadas |
| Dependências | Python 3.12+, Node para contratos JS existentes; Playwright/CI pertencem à BL-0011 |
| Duplicidades | BL-0011 possui testes UI/cobertura/CI; BL-0001 possui reconciliação offline |
| Responsável pela próxima etapa | Engenharia Jaci |
| Próximo passo | Acompanhar aceite e publicação da 1.4.0; fundação já integrada e validada pela BL-0011 |

## Acompanhamento até produção

- Documento refinado: [BL-0026](../../tasks/BL-0026-ferramentas-ambiente-testes.md).
- Implementação: 3/3 fatias entregues na integração feature/BL-0026-ferramentas-ambiente-testes;
  tarefa 1 em b6a3b47/245aa0e, merge e54974b; tarefa 2 em 02aef7e, merge 9005c51 na integração; develop inalterada.
- Validações: 278 passes/5 xfail legados, sem pendências próprias; bash -n e diff
  aprovados; migrações/seed em SQLite isolado, token/refresh/revogação, autorização
  HTTP/identidade WebSocket, scripts e smoke com servidor local aprovados.
  Sem inspeção visual ou Playwright; pylint ausente.
- Publicação: ainda não publicada.
- Itens relacionados: BL-0011 e BL-0001, alvos da 1.4.0.

### Impedimentos

- Publicação da 1.4.0 e aceite de release pendentes; integração realizada e UI automatizada aprovada.

## Histórico

| Data/hora | Autor | Mudança | Motivo/evidência |
| --- | --- | --- | --- |
| `2026-10-28 20:40 -03` | Codex | Registro em recebido, a_triar e a_definir | Execução da formalização do roadmap solicitada |
| `2026-10-28 20:40 -03` | Codex | recebido → em_triagem → pronto_para_refinamento; N/A e P1 | Escopo, limites, dependências e riscos inventariados |
| `2026-10-28 20:40 -03` | Codex | em_refinamento → pronto_para_implementacao | Refinamento pronto para revisão posterior ao versionamento |
| `2026-10-28` | Usuário/Codex | Refinamentos aprovados; BL-0026 em_implementacao | Aprovação explícita posterior a 54cc1c8, 76c6aea e c2f9ebb; tarefa 1 em feature/BL-0026-t1-ambiente |
| `2026-10-28 21:44 -03` | Codex | em_implementacao → em_validacao; 3/3 fatias entregues | Regressão com 278 passes/5 xfail; smoke HTTP local aprovado; sem merge na develop ou publicação |
| `2026-10-29` | Usuário/Codex | Integração autorizada e realizada em b289771 | Fundação disponível na develop e usada pela BL-0011; nove cenários UI e CI remoto aprovados, sem publicação da 1.4.0 |
