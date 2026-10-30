# BL-0011 — Ampliar cobertura automatizada e testes de UI

## Identificação e entrada

| Campo | Valor |
| --- | --- |
| ID | `BL-0011` |
| Título | Ampliar cobertura automatizada e testes de UI |
| Versão-alvo | `1.4.0` |
| Tipo | `melhoria` |
| Estado | `em_validacao` |
| Severidade | `N/A` |
| Prioridade | `P1` |
| Data de entrada | `2026-07-24` |
| Origem | Solicitação do usuário |
| Ambiente/versão | Estado de `develop` (`e062249`) em `2026-07-24` |
| Responsável | Engenharia Jaci |
| Atualizado em | `2026-10-29` |

### Comportamento observado

A última regressão da v1.3.0 registrou 262 passes e 5 xfail (267 casos). Esse
resultado é histórico e não foi reexecutado nesta etapa documental. A suíte
rastreia regras de negócio e fluxos do usuário, mas não há medição de cobertura configurada,
suíte de testes executada em navegador real nem automação de CI versionada para
aplicar continuamente testes de UI.

### Comportamento esperado

A qualidade automatizada deve ter cobertura mensurável e evolutiva, validar em
navegador os fluxos críticos da interface com prioridade mobile-first e aplicar
esses testes automaticamente de forma confiável e reproduzível.

### Impacto e abrangência

- Impacto: lacunas de cobertura e regressões de interface podem permanecer sem
  detecção objetiva antes da publicação.
- Abrangência: suíte de testes, fluxos críticos da interface, documentação de
  rastreabilidade e automação de validação.
- Frequência: em toda alteração que afete comportamento, integração ou
  experiência do usuário.

### Passos de reprodução

1. Coletar a suíte atual com `venv/bin/pytest --collect-only -q`.
2. Inspecionar a configuração do Pytest e observar que não há medição de
   cobertura.
3. Procurar uma suíte de navegador e sua execução automatizada no repositório.
4. Observar que esses recursos ainda não estão versionados.

### Evidências sanitizadas

- [Rastreabilidade dos testes](../../../../tests/README.md).
- [Configuração do Pytest](../../../../pytest.ini).
- [Dependências de desenvolvimento](../../../../requirements-dev.txt).

### Workaround

Executar manualmente `venv/bin/pytest` e validar os fluxos críticos diretamente
no navegador antes de cada publicação.

## Triagem

| Campo | Valor |
| --- | --- |
| Confirmação | confirmado por inventário de pytest.ini, requirements-dev.txt e tests/ |
| Classificação | Cobertura mensurável, testes reais de navegador e automação de CI |
| Domínio afetado | Qualidade, browser, autenticação de teste e publicação de evidências |
| Regras de negócio afetadas | Isolamento, bloqueio otimista, snapshot financeiro, offline e recorrência |
| Risco de segurança | Alto — usar AUTH_MOCK somente em ambiente test e validar seu bloqueio em produção |
| Risco de LGPD | Médio — artifacts somente de dados sintéticos, sem cookies/tokens ou banco real |
| Risco de isolamento por grupo | Alto — cenários explícitos com dois grupos e acesso negado |
| Risco offline/sincronização | Alto — navegador testa fila persistida, reconexão e conflito explícito |
| Risco ao histórico financeiro | Médio — testes preservam totais e snapshot, usando dados sintéticos |
| Risco à recorrência | Médio — verificar finalização e próximo ciclo sem duplicação |
| Risco à separação template/execução | Médio — alterações de execução não propagam ao template |
| Dependências | BL-0026 para ambiente/mock e scripts Python; Chromium e dependências de browser no CI |
| Duplicidades | BL-0001 reconcilia contratos legados e matriz offline; esta demanda possui infraestrutura UI/CI/cobertura |
| Responsável pela próxima etapa | Engenharia Jaci |
| Próximo passo | Autorizar integração final na develop e registrar publicação da 1.4.0 |

## Acompanhamento até produção

- Documento refinado: [BL-0011](../../tasks/BL-0011-ampliar-cobertura-testes-ui.md).
- Implementação: 4/4 fatias na branch de integração feature/BL-0011-refinamento-1-4-0;
  commits 048a000 (cobertura), c15e453 (UI) e 78cbfb1 (CI). PR de validação:
  https://github.com/vguerrax/jaci/pull/43, em rascunho e sem merge.
- Validações: regressão local 288 passes/5 xfail legados, cobertura 56,18%,
  nove cenários Playwright aprovados. YAML validado por actionlint.
  GitHub Actions 40814194309: Python coverage e Chromium mobile and desktop
  concluíram com success em 78cbfb1. Link:
  https://github.com/vguerrax/jaci/actions/runs/40814194309.
- Publicação: ainda não publicada.
- Itens relacionados: [BL-0001](BL-0001-operacao-offline-cobertura-rastreabilidade.md).

### Impedimentos

- Publicação da 1.4.0 pendente; implementação, validações e integração aprovadas.

## Histórico

| Data/hora | Autor | Mudança | Motivo/evidência |
| --- | --- | --- | --- |
| `2026-07-24 01:11 -03` | Codex | Item criado em `recebido` | Solicitação do usuário |
| `2026-10-28 20:40 -03` | Codex | Versão-alvo 1.4.0 associada | Roadmap aprovado para formalização; estado e prioridade preservados, sem autorizar implementação |
| `2026-10-28 20:40 -03` | Codex | recebido → em_triagem → pronto_para_refinamento; N/A e P1 | Inventário atualizado pela regressão histórica da 1.3.0; lacunas de browser/cobertura/CI confirmadas |
| `2026-10-28 20:40 -03` | Codex | em_refinamento → pronto_para_implementacao | Escopo, etapas, contratos futuros e validação da 1.4.0 refinados; aguardando aprovação |
| `2026-10-29 00:04 -03` | Usuário/Codex | Refinamento aprovado; em_implementacao | Integração BL-0026 autorizada e realizada em b289771; BL-0011 iniciada em branch de tarefa própria |
| `2026-10-29` | Usuário/Codex | em_implementacao → em_validacao; 4/4 fatias entregues | Execução UI autorizada; 288 passes/5 xfail, cobertura 56,18%, nove cenários Chromium e CI remoto aprovados; sem merge final ou deploy |
| `2026-10-29` | Usuário/Codex | Integração autorizada e realizada na develop | Merge 70d36ba da branch de integração; candidato 9fa6151 aprovado no run 40814716172; sem deploy |
