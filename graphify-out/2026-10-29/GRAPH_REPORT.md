# Graph Report - jaci-bl0028  (2026-10-29)

## Corpus Check
- 189 files · ~185,743 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 2366 nodes · 5469 edges · 126 communities (118 shown, 8 thin omitted)
- Extraction: 93% EXTRACTED · 7% INFERRED · 0% AMBIGUOUS · INFERRED: 379 edges (avg confidence: 0.74)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `25439312`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Refinamento — BL-0018 — Corrigir backdrop sobre o modal de completar item
- offline-cache.js
- Refinamento — BL-0021 — API externa para gestão de execuções
- Identificação e entrada
- make_user
- Group
- template_service.py
- categories.py
- Identificação e entrada
- main.py
- Refinamento — BL-0012 — Gestão documental compartilhada dos projetos VGX
- Refinamento — BL-0020 — Bloquear renomeação de item vinculado ao template
- Refinamento — BL-0025 — Preparar e publicar versão 1.3.0
- Refinamento — BL-0028 — AUTH_MOCK como bypass local do Tupã
- AGENTS.md
- execution-budget.js
- item-filter.js
- Refinamento — BL-0015 — Adicionar item como comprado durante execução
- sync_center
- service-worker.js
- read
- loading-indicator.js
- sync-status.js
- User
- 🌙 Jaci
- privacy_policy
- Refinamento — BL-0013 — Busca e padronização das telas de itens
- tupa_auth_service.py
- run.py
- docker-entrypoint.sh
- Refinamento — BL-0014 — Resumo de orçamento fixo durante a compra
- backup_database.sh
- app/__init__.py
- publish.sh
- tests/README.md
- Refinamento — BL-NNNN — Título
- Regras de negócio críticas
- template_learning_service.py
- Fundação PWA e Offline
- Backlog de produção
- Identificação e entrada
- Identificação e entrada
- Identificação e entrada
- Identificação e entrada
- Identificação e entrada
- Identificação e entrada
- Identificação e entrada
- Identificação e entrada
- Identificação e entrada
- Identificação e entrada
- Identificação e entrada
- Identificação e entrada
- Identificação e entrada
- Identificação e entrada
- Execution
- Refinamento — BL-0027 — Incorporação sem categoria
- Identificação e entrada
- Pricipais Entidades
- 0001 - Tratamento de datas e timezone
- Aprendizado contínuo dos templates
- Tela Inicial Operacional
- Identificação e entrada
- Identificação e entrada
- Identificação e entrada
- Backlog legado do Jaci
- Edição de execuções agendadas
- FL-03 — Geração de Execução
- user-flows.md
- test_pwa.py
- Identificação e entrada
- Refinamento — BL-0016 — Botão flutuante para adicionar itens
- FL-04 — Execução da Compra
- notification_service.py
- Identificação e entrada
- Identificação e entrada
- FL-08 — Consulta da Agenda e Histórico
- test_purchase_playwright.py
- item-add-modal.js
- Refinamento — BL-0017 — Nome da execução avulsa
- auth.py
- offline_queue.test.cjs
- Identificação e entrada
- test_database_operations.py
- Identificação e entrada
- test_item_add_fab.py
- executions.py
- Refinamento — BL-0011 — Cobertura, navegador e CI
- Refinamento — BL-0026 — Ferramentas e ambiente de testes
- Identificação e entrada
- ConnectionManager
- test_offline_cache.py
- test_test_environment.py
- 0002 - Backup automático do PostgreSQL
- offline_cache_service.py
- datetime.py
- Refinamento — BL-0001 — Rastreabilidade da operação offline
- Identificação e entrada
- package.json
- utils/__init__.py
- test_coverage_runner.py
- Planejamento de releases após a 1.3.0
- setup_test_env.sh
- run_test_server.sh
- run_tests.sh
- run_ui_tests.sh
- ValueError
- FL-09 — Operação Offline
- FL-06 — Aprendizado do Template
- FL-05 — Compra Colaborativa
- test_offline_queue_node.py

## God Nodes (most connected - your core abstractions)
1. `User` - 153 edges
2. `make_user()` - 132 edges
3. `make_group()` - 128 edges
4. `create_template()` - 101 edges
5. `create_execution_from_template()` - 92 edges
6. `Execution` - 78 edges
7. `add_item_to_template()` - 65 edges
8. `ExecutionItem` - 58 edges
9. `Group` - 50 edges
10. `complete_item()` - 38 edges

## Surprising Connections (you probably didn't know these)
- `test_real_login_still_requires_password()` --indirect_call--> `get_db()`  [INFERRED]
  tests/test_auth_mock_bypass.py → app/database.py
- `test_http_ws_and_middleware_use_local_identity_and_group_authorization()` --indirect_call--> `main()`  [INFERRED]
  tests/test_auth_mock_bypass.py → scripts/test_environment.py
- `test_custom_environment_path_with_spaces()` --calls--> `run()`  [INFERRED]
  tests/test_publish.py → scripts/ui_test_runner.py
- `test_docker_failure_stops_sequence_and_retains_requested_version()` --calls--> `run()`  [INFERRED]
  tests/test_publish.py → scripts/ui_test_runner.py
- `test_failed_temporary_write_preserves_original_and_cleans_up()` --calls--> `run()`  [INFERRED]
  tests/test_publish.py → scripts/ui_test_runner.py

## Import Cycles
- None detected.

## Communities (126 total, 8 thin omitted)

### Community 0 - "Refinamento — BL-0018 — Corrigir backdrop sobre o modal de completar item"
Cohesion: 0.09
Nodes (21): Cenários TDD, Contratos de etapas futuras, Critérios de sucesso, Escopo, Estratégia de validação, Etapa 1 — Restaurar o empilhamento dos modais de item, Excluído, Fatia 1.1.1 — Proteger a ordem de camadas e o cache PWA (+13 more)

### Community 1 - "offline-cache.js"
Cohesion: 0.05
Nodes (113): applyPersistedOfflineItemState(), auditCard(), buildConflict(), buildQueuedOperation(), calculateExecutionTotal(), classifyOperation(), clearOfflineItemIndicators(), clearOfflineItemIndicatorsWhenSynced() (+105 more)

### Community 2 - "Refinamento — BL-0021 — API externa para gestão de execuções"
Cohesion: 0.06
Nodes (32): Autenticação e escopo, Cenários TDD, Contrato HTTP v1, Contratos de etapas futuras, Critérios de sucesso, Escopo, Estratégia de validação, Etapa 1 — Persistir identidade, concorrência e rastreabilidade (+24 more)

### Community 3 - "Identificação e entrada"
Cohesion: 0.17
Nodes (12): Acompanhamento até produção, BL-0027 — Incorporar item sem categoria ao finalizar compra, Comportamento esperado, Comportamento observado, Evidências sanitizadas, Histórico, Identificação e entrada, Impacto e abrangência (+4 more)

### Community 4 - "make_user"
Cohesion: 0.05
Nodes (148): AddExecutionItemOperation, Cria no servidor um item de execução gerado offline com ID temporário., sync_add_execution_item_operation(), add_item_to_execution(), complete_item(), create_execution_from_template(), create_execution_standalone(), finalize_execution() (+140 more)

### Community 5 - "Group"
Cohesion: 0.12
Nodes (18): get_settings(), Group, authenticate_with_password(), get_or_create_tupa_user(), Session, Cria a identidade no Tupã e o perfil local no Jaci., Completa os dados locais do perfil., Atualiza os dados pessoais do usuário. (+10 more)

### Community 6 - "template_service.py"
Cohesion: 0.09
Nodes (59): create_template_page(), edit_template_page(), _get_template_context(), _get_template_items_fragment(), handle_add_item(), handle_create_template(), handle_delete_template(), handle_edit_item() (+51 more)

### Community 7 - "categories.py"
Cohesion: 0.12
Nodes (38): Category, create_category_page(), delete_category_confirm_page(), edit_category_page(), handle_create_category(), handle_delete_category(), handle_edit_category(), handle_move_category() (+30 more)

### Community 8 - "Identificação e entrada"
Cohesion: 0.17
Nodes (12): Acompanhamento até produção, BL-0018 — Corrigir backdrop sobre o modal de completar item, Comportamento esperado, Comportamento observado, Evidências sanitizadas, Histórico, Identificação e entrada, Impacto e abrangência (+4 more)

### Community 9 - "main.py"
Cohesion: 0.08
Nodes (39): get_db(), get_active_group(), get_current_user(), get_current_user_ws(), get_unread_notification_count(), Request, Session, Dependências reutilizáveis para injeção em rotas. (+31 more)

### Community 10 - "Refinamento — BL-0012 — Gestão documental compartilhada dos projetos VGX"
Cohesion: 0.05
Nodes (40): Acompanhamento até produção, BL-0012 — Gestão documental compartilhada dos projetos VGX, Comportamento esperado, Comportamento observado, Evidências sanitizadas, Histórico, Identificação e entrada, Impacto e abrangência (+32 more)

### Community 11 - "Refinamento — BL-0020 — Bloquear renomeação de item vinculado ao template"
Cohesion: 0.08
Nodes (24): Cenários TDD, Contratos de etapas futuras, Critérios de sucesso, Escopo, Estratégia de validação, Etapa 1 — Proteger a identidade do item online e offline, Etapa 2 — Fechar o ciclo de identidade entre execução e planejamento, Excluído (+16 more)

### Community 12 - "Refinamento — BL-0025 — Preparar e publicar versão 1.3.0"
Cohesion: 0.06
Nodes (33): Cenários TDD, Contratos de etapas futuras, Critérios de sucesso, Encerramento da release — 2026-10-28, Escopo, Estratégia de validação, Etapa 1 — Preparar o candidato, Etapa 2 — Validar e obter aceite (+25 more)

### Community 13 - "Refinamento — BL-0028 — AUTH_MOCK como bypass local do Tupã"
Cohesion: 0.13
Nodes (14): Aprovação e início, Cenários TDD, Escopo, Estratégia de validação, Etapa 1 / Ticket 1 — Ajustar contrato do AUTH_MOCK, Fatia 1.1 — Contratos, configuração e adaptador de identidade local, Fatia 1.2 — Formulário, regressão e documentação de uso, Fechamento documental (+6 more)

### Community 14 - "AGENTS.md"
Cohesion: 0.05
Nodes (39): Arquitetura, Backend, Backend, Banco de Dados, Cache e Mensageria, Categoria, Conceitos do Domínio, Concorrência é controlada por bloqueio otimista. (+31 more)

### Community 15 - "execution-budget.js"
Cohesion: 0.29
Nodes (15): alertMessage(), applyVisualState(), budgetBand(), ensureToastContainer(), formatMoney(), handleRemoteAlerts(), init(), refreshFromDocument() (+7 more)

### Community 17 - "item-filter.js"
Cohesion: 0.30
Nodes (13): apply(), expandMatchingGroup(), formatMoney(), initAll(), initRoot(), normalize(), restoreForcedCollapse(), scheduleApply() (+5 more)

### Community 18 - "Refinamento — BL-0015 — Adicionar item como comprado durante execução"
Cohesion: 0.06
Nodes (34): Acompanhamento até produção, BL-0015 — Adicionar item como comprado durante execução, Comportamento esperado, Comportamento observado, Evidências sanitizadas, Histórico, Identificação e entrada, Impacto e abrangência (+26 more)

### Community 19 - "sync_center"
Cohesion: 0.22
Nodes (8): get, Request, Session, Central local para visualização e resolução da fila de sincronização., sync_center(), make_request(), Request, test_sync_center_requires_authentication()

### Community 20 - "service-worker.js"
Cohesion: 0.22
Nodes (3): ACTIVE_CACHES, isShellAsset(), SHELL_ASSETS

### Community 21 - "read"
Cohesion: 0.30
Nodes (11): Path, read(), test_clear_and_collapse_controls_share_a_safe_click_handler(), test_completed_execution_is_searchable_collapsible_and_read_only(), test_hidden_filter_rows_override_bootstrap_display_utilities(), test_mutable_execution_exposes_filter_and_visible_financial_metadata(), test_shared_item_filter_controls_rows_groups_counts_and_empty_state(), test_shared_item_filter_normalizes_and_matches_names_locally() (+3 more)

### Community 22 - "loading-indicator.js"
Cohesion: 0.33
Nodes (7): beginRequest(), endRequest(), isPlainLeftClick(), requestCount(), scheduleHide(), shouldShowForLink(), show()

### Community 23 - "sync-status.js"
Cohesion: 0.42
Nodes (8): failSync(), finishSync(), formatDateTime(), render(), renderDetails(), setState(), startSync(), waitForRetry()

### Community 24 - "User"
Cohesion: 0.09
Nodes (50): User, create_group_page(), group_detail(), handle_create_group(), handle_edit_group(), handle_invite(), handle_remove_member(), handle_switch_group() (+42 more)

### Community 25 - "🌙 Jaci"
Cohesion: 0.06
Nodes (31): 1. Clone o repositório, 3. Instale as dependências, 4. Execute, Ambiente sintético de testes (BL-0026), Backup automático do PostgreSQL, Banco de dados e migrações, CI no GitHub, Cobertura e testes de navegador — BL-0011 (+23 more)

### Community 26 - "privacy_policy"
Cohesion: 0.47
Nodes (5): privacy_policy(), get, Request, Privacy Policy page - LGPD, terms_of_use()

### Community 28 - "Refinamento — BL-0013 — Busca e padronização das telas de itens"
Cohesion: 0.09
Nodes (23): Cenários TDD, Contratos de etapas futuras, Critérios de sucesso, Escopo, Estratégia de validação, Etapa 1 — Busca local e navegação padronizada, Excluído, Fatia 1.1.1 — Criar contratos TDD e integrar a Lista (+15 more)

### Community 29 - "tupa_auth_service.py"
Cohesion: 0.12
Nodes (35): websocket, WebSocket para sincronização em tempo real de uma execução. Autenticação via…, websocket_execution(), _decode(), decode_access_token(), _error(), _hash(), logout() (+27 more)

### Community 30 - "run.py"
Cohesion: 0.50
Nodes (4): main(), parse_args(), Namespace, Executa o Jaci aplicando migrações antes de iniciar o servidor.

### Community 32 - "docker-entrypoint.sh"
Cohesion: 0.83
Nodes (3): is_server_process(), docker-entrypoint.sh script, write_cron_environment()

### Community 33 - "Refinamento — BL-0014 — Resumo de orçamento fixo durante a compra"
Cohesion: 0.09
Nodes (21): Cenários TDD, Contratos de etapas futuras, Critérios de sucesso, Escopo, Estratégia de validação, Etapa 1 — Acompanhamento contínuo do orçamento, Excluído, Fatia 1.1.1 — Implementar o contrato completo da BL-0014 (+13 more)

### Community 45 - "tests/README.md"
Cohesion: 0.17
Nodes (7): Backlog legado — Sprint 4 — Aprendizado contínuo dos templates, Cobertura Python — BL-0011, Contratos offline FL-09 — BL-0001, Demandas do backlog com cobertura rastreada, Navegador — BL-0011, Rastreabilidade das regras de negócio, Rastreabilidade dos fluxos do usuário

### Community 46 - "Refinamento — BL-NNNN — Título"
Cohesion: 0.10
Nodes (21): Cenários TDD, Contratos de etapas futuras, Critérios de sucesso, Escopo, Estratégia de validação, Etapa 1 — `<resultado da etapa>`, Excluído, Fatia 1.1.1 — `<resultado pequeno e verificável>` (+13 more)

### Community 47 - "Regras de negócio críticas"
Cohesion: 0.10
Nodes (19): Regras de negócio críticas, RN01, RN02, RN03, RN04, RN05, RN06, RN07 (+11 more)

### Community 48 - "template_learning_service.py"
Cohesion: 0.12
Nodes (31): TemplateLearningDismissal, Template, TemplateItem, analyze_template_history(), apply_template_suggestions(), dismiss_template_suggestions(), _dismissal_key_for_suggestion(), _dismissal_value_for_suggestion() (+23 more)

### Community 49 - "Fundação PWA e Offline"
Cohesion: 0.10
Nodes (21): BL-004 — Estratégia de Cache, BL-005 a BL-013 — Cache Local e Operações Offline, BL-014 — Fila Local de Operações, BL-015 — Sincronização Automática, BL-016 — Status Detalhado de Sincronização, BL-017 — Retentativa Automática, BL-019 — Resolução de Conflitos, BL-020 — Central de Sincronização (+13 more)

### Community 50 - "Backlog de produção"
Cohesion: 0.13
Nodes (15): Backlog de produção, Checklist de passagem ponta a ponta, Ciclo de vida, Classificações, Entrada rápida, Evidências e dados sensíveis, Git Flow, Itens arquivados (+7 more)

### Community 51 - "Identificação e entrada"
Cohesion: 0.17
Nodes (12): Acompanhamento até produção, BL-0010 — Disponibilizar reset de senha via login e área logada, Comportamento esperado, Comportamento observado, Evidências sanitizadas, Histórico, Identificação e entrada, Impacto e abrangência (+4 more)

### Community 52 - "Identificação e entrada"
Cohesion: 0.17
Nodes (12): Acompanhamento até produção, BL-0001 — Completar cobertura e rastreabilidade da operação offline, Comportamento esperado, Comportamento observado, Evidências sanitizadas, Histórico, Identificação e entrada, Impacto e abrangência (+4 more)

### Community 53 - "Identificação e entrada"
Cohesion: 0.17
Nodes (12): Acompanhamento até produção, BL-0002 — Adicionar unidades de medida, Comportamento esperado, Comportamento observado, Evidências sanitizadas, Histórico, Identificação e entrada, Impacto e abrangência (+4 more)

### Community 54 - "Identificação e entrada"
Cohesion: 0.17
Nodes (12): Acompanhamento até produção, BL-0003 — Disponibilizar histórico de preços por grupo e item, Comportamento esperado, Comportamento observado, Evidências sanitizadas, Histórico, Identificação e entrada, Impacto e abrangência (+4 more)

### Community 55 - "Identificação e entrada"
Cohesion: 0.17
Nodes (12): Acompanhamento até produção, BL-0004 — Disponibilizar análise de gastos e dashboard financeiro, Comportamento esperado, Comportamento observado, Evidências sanitizadas, Histórico, Identificação e entrada, Impacto e abrangência (+4 more)

### Community 56 - "Identificação e entrada"
Cohesion: 0.17
Nodes (12): Acompanhamento até produção, BL-0005 — Evoluir inteligência de compras, Comportamento esperado, Comportamento observado, Evidências sanitizadas, Histórico, Identificação e entrada, Impacto e abrangência (+4 more)

### Community 57 - "Identificação e entrada"
Cohesion: 0.17
Nodes (12): Acompanhamento até produção, BL-0006 — Exportar compras para calendário e compartilhar listas, compras e convites, Comportamento esperado, Comportamento observado, Evidências sanitizadas, Histórico, Identificação e entrada, Impacto e abrangência (+4 more)

### Community 58 - "Identificação e entrada"
Cohesion: 0.17
Nodes (12): Acompanhamento até produção, BL-0007 — Replicar backups em armazenamento externo, Comportamento esperado, Comportamento observado, Evidências sanitizadas, Histórico, Identificação e entrada, Impacto e abrangência (+4 more)

### Community 59 - "Identificação e entrada"
Cohesion: 0.17
Nodes (12): Acompanhamento até produção, BL-0008 — Disponibilizar autoexclusão e anonimização de conta, Comportamento esperado, Comportamento observado, Evidências sanitizadas, Histórico, Identificação e entrada, Impacto e abrangência (+4 more)

### Community 60 - "Identificação e entrada"
Cohesion: 0.17
Nodes (12): Acompanhamento até produção, BL-0009 — Implementar criptografia de dados em repouso, Comportamento esperado, Comportamento observado, Evidências sanitizadas, Histórico, Identificação e entrada, Impacto e abrangência (+4 more)

### Community 61 - "Identificação e entrada"
Cohesion: 0.17
Nodes (12): Acompanhamento até produção, BL-0011 — Ampliar cobertura automatizada e testes de UI, Comportamento esperado, Comportamento observado, Evidências sanitizadas, Histórico, Identificação e entrada, Impacto e abrangência (+4 more)

### Community 62 - "Identificação e entrada"
Cohesion: 0.17
Nodes (12): Acompanhamento até produção, BL-0013 — Buscar itens e padronizar categorias nas telas de Lista e Compra, Comportamento esperado, Comportamento observado, Evidências sanitizadas, Histórico, Identificação e entrada, Impacto e abrangência (+4 more)

### Community 63 - "Identificação e entrada"
Cohesion: 0.17
Nodes (12): Acompanhamento até produção, BL-0014 — Fixar resumo de orçamento durante a compra, Comportamento esperado, Comportamento observado, Evidências sanitizadas, Histórico, Identificação e entrada, Impacto e abrangência (+4 more)

### Community 64 - "Identificação e entrada"
Cohesion: 0.17
Nodes (12): Acompanhamento até produção, BL-NNNN — Título curto, Comportamento esperado, Comportamento observado, Evidências sanitizadas, Histórico, Identificação e entrada, Impacto e abrangência (+4 more)

### Community 65 - "Execution"
Cohesion: 0.09
Nodes (47): ExecutionStatus, RecurrenceType, Execution, build_calendar_data(), calculate_next_date(), generate_next_execution(), get_executions_for_date(), get_executions_for_month() (+39 more)

### Community 66 - "Refinamento — BL-0027 — Incorporação sem categoria"
Cohesion: 0.18
Nodes (10): Cenários TDD, Escopo e riscos, Estratégia de validação, Etapa 1 / Ticket 1 / Fatia 1.1 — Normalizar o sentinela, Fechamento, Objetivo e critérios de sucesso, Plano de implementação, Progresso (+2 more)

### Community 67 - "Identificação e entrada"
Cohesion: 0.17
Nodes (12): Acompanhamento até produção, BL-0021 — Expor API externa para criar e editar execuções, Comportamento esperado, Comportamento observado, Evidências sanitizadas, Histórico, Identificação e entrada, Impacto e abrangência (+4 more)

### Community 68 - "Pricipais Entidades"
Cohesion: 0.22
Nodes (8): Categoria, Execução, Grupo, Item de Execução, Item de Template, Pricipais Entidades, Template, Usuário

### Community 69 - "0001 - Tratamento de datas e timezone"
Cohesion: 0.25
Nodes (7): 0001 - Tratamento de datas e timezone, Antipadrões, Consequências, Contexto, Decisão, Exemplos, Status

### Community 70 - "Aprendizado contínuo dos templates"
Cohesion: 0.22
Nodes (9): Aprendizado contínuo dos templates, BL-029 — Detecção de itens adicionados na execução, BL-030 — Incorporação de itens, BL-031 e BL-032 — Quantidades recorrentes, BL-033 e BL-034 — Observações recorrentes, BL-075 e BL-076 — Orçamentos recorrentes, Configuração por grupo, Identidade do item após a primeira compra (+1 more)

### Community 71 - "Tela Inicial Operacional"
Cohesion: 0.29
Nodes (7): Alertas, Histórico Recente, Indicadores, Objetivo, Offline e Sincronização, Prioridade da Compra Principal, Tela Inicial Operacional

### Community 72 - "Identificação e entrada"
Cohesion: 0.17
Nodes (12): Acompanhamento até produção, BL-0022 — Unificar a gestão de categorias em uma única lista, Comportamento esperado, Comportamento observado, Evidências sanitizadas, Histórico, Identificação e entrada, Impacto e abrangência (+4 more)

### Community 73 - "Identificação e entrada"
Cohesion: 0.17
Nodes (12): Acompanhamento até produção, BL-0023 — Priorizar compras abertas por status e data, Comportamento esperado, Comportamento observado, Evidências sanitizadas, Histórico, Identificação e entrada, Impacto e abrangência (+4 more)

### Community 74 - "Identificação e entrada"
Cohesion: 0.17
Nodes (12): Acompanhamento até produção, BL-0028 — Usar AUTH_MOCK como bypass do Tupã para usuários locais, Comportamento esperado, Comportamento observado, Evidências sanitizadas, Histórico, Identificação e entrada, Impacto e abrangência (+4 more)

### Community 75 - "Backlog legado do Jaci"
Cohesion: 0.33
Nodes (6): Aprendizado de templates, Backlog legado do Jaci, Edição de execuções agendadas, Entregas concluídas sem identificador BL legado, Mapeamento das fontes abertas migradas, PWA, operação offline e sincronização

### Community 76 - "Edição de execuções agendadas"
Cohesion: 0.33
Nodes (5): Campos editáveis, Edição de execuções agendadas, Notificações e sincronização, Regras, Sincronização offline

### Community 77 - "FL-03 — Geração de Execução"
Cohesion: 0.33
Nodes (6): Atores, FL-03 — Geração de Execução, Fluxo Automático, Fluxo Manual, Objetivo, Resultado Esperado

### Community 78 - "user-flows.md"
Cohesion: 0.07
Nodes (26): Jaci, Operação com conexão instável, Qual problema o produto resolve?, Atores, Atores, Atores, FL-01 — Primeiro Acesso e Onboarding, FL-02 — Criação de Template (+18 more)

### Community 79 - "test_pwa.py"
Cohesion: 0.19
Nodes (8): Serve o service worker na raiz para permitir cache offline da aplicação., service_worker(), png_dimensions(), Path, test_base_template_declares_global_loading_indicator(), test_base_template_declares_manifest_ios_support_and_install_action(), test_pwa_icons_have_required_android_and_ios_dimensions(), test_pwa_root_assets_are_served_with_expected_media_types()

### Community 80 - "Identificação e entrada"
Cohesion: 0.17
Nodes (12): Acompanhamento até produção, BL-0019 — Manter sessão autenticada por oito horas de inatividade, Comportamento esperado, Comportamento observado, Evidências sanitizadas, Histórico, Identificação e entrada, Impacto e abrangência (+4 more)

### Community 81 - "Refinamento — BL-0016 — Botão flutuante para adicionar itens"
Cohesion: 0.09
Nodes (21): Cenários TDD, Contratos de etapas futuras, Critérios de sucesso, Escopo, Estratégia de validação, Etapa 1 — Adição contextual por modal nas telas mutáveis, Excluído, Fatia 1.1.1 — Contratos TDD e fluxo modal completo online/offline (+13 more)

### Community 82 - "FL-04 — Execução da Compra"
Cohesion: 0.33
Nodes (6): Atores, Cenários Alternativos, FL-04 — Execução da Compra, Fluxo Principal, Objetivo, Resultado Esperado

### Community 83 - "notification_service.py"
Cohesion: 0.11
Nodes (28): Notification, handle_mark_all_read(), handle_mark_read(), list_notifications(), get, post, Request, Session (+20 more)

### Community 84 - "Identificação e entrada"
Cohesion: 0.17
Nodes (12): Acompanhamento até produção, BL-0020 — Bloquear renomeação de item vinculado ao template, Comportamento esperado, Comportamento observado, Evidências sanitizadas, Histórico, Identificação e entrada, Impacto e abrangência (+4 more)

### Community 85 - "Identificação e entrada"
Cohesion: 0.17
Nodes (12): Acompanhamento até produção, BL-0024 — Autocompletar nomes de itens pelo histórico do grupo, Comportamento esperado, Comportamento observado, Evidências sanitizadas, Histórico, Identificação e entrada, Impacto e abrangência (+4 more)

### Community 86 - "FL-08 — Consulta da Agenda e Histórico"
Cohesion: 0.33
Nodes (6): Atores, Estado e rastreabilidade, FL-08 — Consulta da Agenda e Histórico, Fluxo Principal, Objetivo, Resultado Esperado

### Community 88 - "test_purchase_playwright.py"
Cohesion: 0.05
Nodes (54): allowed_runtime(), Path, Guardas sem efeitos colaterais para os ambientes sintéticos do Jaci., validate_database(), validate_runtime(), main(), Prepara explicitamente um ambiente sintético, sem ler .env de produção., run_python_tests() (+46 more)

### Community 89 - "item-add-modal.js"
Cohesion: 0.27
Nodes (15): completeSuccess(), finishClose(), focusableElements(), formFor(), hideLocalModal(), hideModal(), initialize(), initializeModal() (+7 more)

### Community 90 - "Refinamento — BL-0017 — Nome da execução avulsa"
Cohesion: 0.09
Nodes (21): Cenários TDD, Contratos de etapas futuras, Critérios de sucesso, Escopo, Estratégia de validação, Etapa 1 — Nome exclusivo para compra sem lista, Excluído, Fatia 1.1.1 — Contratos TDD e implementação completa (+13 more)

### Community 91 - "auth.py"
Cohesion: 0.08
Nodes (45): handle_change_password(), handle_setup_profile(), handle_update_profile(), login_error_page(), login_page(), login_sent_page(), logout(), password_login() (+37 more)

### Community 92 - "offline_queue.test.cjs"
Cohesion: 0.19
Nodes (12): assert, browser(), fs, { IDBFactory }, path, plain(), prepared(), response() (+4 more)

### Community 93 - "Identificação e entrada"
Cohesion: 0.17
Nodes (12): Acompanhamento até produção, BL-0016 — Disponibilizar botão flutuante para adicionar itens, Comportamento esperado, Comportamento observado, Evidências sanitizadas, Histórico, Identificação e entrada, Impacto e abrangência (+4 more)

### Community 94 - "test_database_operations.py"
Cohesion: 0.06
Nodes (50): Aceita nomes usuais de ambiente além de booleanos., Usa psycopg 3 para URLs PostgreSQL fornecidas por provedores., Permite autenticação em desenvolvimento servido por HTTP., Settings, create_database_engine(), Cria engine com ajustes específicos para SQLite ou PostgreSQL., BaseSettings, CompletedProcess (+42 more)

### Community 95 - "Identificação e entrada"
Cohesion: 0.17
Nodes (12): Acompanhamento até produção, BL-0017 — Permitir informar um nome para execução avulsa, Comportamento esperado, Comportamento observado, Evidências sanitizadas, Histórico, Identificação e entrada, Impacto e abrangência (+4 more)

### Community 96 - "test_item_add_fab.py"
Cohesion: 0.28
Nodes (12): Path, read(), test_both_modal_pages_load_the_local_cached_controller(), test_fab_and_modal_styles_respect_safe_areas_and_local_fallback(), test_local_modal_controller_preserves_scroll_focus_and_keyboard_behavior(), test_managed_item_modals_stay_above_backdrop_and_page_actions(), test_modal_controller_closes_only_after_online_or_offline_success(), test_modal_pages_keep_the_single_form_available_without_javascript() (+4 more)

### Community 97 - "executions.py"
Cohesion: 0.05
Nodes (93): agenda_calendar(), agenda_day(), agenda_list(), handle_reschedule(), get, post, Request, Session (+85 more)

### Community 98 - "Refinamento — BL-0011 — Cobertura, navegador e CI"
Cohesion: 0.08
Nodes (24): Cenários TDD e contratos futuros, Escopo, Estratégia de validação, Etapa 1 / Ticket 1 — Medição Python, Etapa 2 / Ticket 2 — Navegador real, Etapa 3 / Ticket 3 — CI e evidências, Evidência da tarefa 1 — Cobertura, Evidência da tarefa 2 — Navegador (+16 more)

### Community 99 - "Refinamento — BL-0026 — Ferramentas e ambiente de testes"
Cohesion: 0.09
Nodes (22): Cenários TDD, Contratos futuros, Entrega documental já autorizada, Entrega para integração, Escopo, Estratégia de validação, Etapa 1 / Ticket 1 — Ambiente e autenticação de teste, Etapa 2 / Ticket 2 — Scripts e operação local (+14 more)

### Community 100 - "Identificação e entrada"
Cohesion: 0.17
Nodes (12): Acompanhamento até produção, BL-0025 — Preparar e publicar versão 1.3.0, Comportamento esperado, Comportamento observado, Evidências sanitizadas, Histórico, Identificação e entrada, Impacto e abrangência (+4 more)

### Community 101 - "ConnectionManager"
Cohesion: 0.22
Nodes (8): ConnectionManager, Any, WebSocket, Gerenciador de conexões WebSocket. Agrupa conexões por execution_id para…, Aceita a conexão e registra na sala., Remove a conexão da sala., Envia mensagem para todos na sala, exceto o remetente (se informado). Formato:…, Envia mensagem para um único cliente.

### Community 102 - "test_offline_cache.py"
Cohesion: 0.07
Nodes (53): ExecutionItem, Calcula o valor total do item (qtd * preço unitário)., ConflictResolutionOperation, _execution_state(), ExecutionItemOperation, FinalizeExecutionOperation, _item_state(), offline_conflict_history() (+45 more)

### Community 103 - "test_test_environment.py"
Cohesion: 0.24
Nodes (14): test_mock_application_needs_no_smtp_or_named_environment(), process(), parametrize, Contratos BL-0026: ambiente isolado, mock e comandos públicos., setup(), test_cleanup_refuses_wrong_environment_and_preserves_unrelated_files(), test_mock_cannot_start_outside_test(), test_mock_http_authorization_and_unsupported_operations() (+6 more)

### Community 104 - "0002 - Backup automático do PostgreSQL"
Cohesion: 0.08
Nodes (20): 0002 - Backup automático do PostgreSQL, Consequências, Contexto, Decisão, Plano refinado, Progresso, Status, Validação (+12 more)

### Community 105 - "offline_cache_service.py"
Cohesion: 0.39
Nodes (7): build_offline_snapshot(), _enum_value(), _iso(), Any, datetime, Session, Monta dados essenciais somente leitura para consulta offline.

### Community 106 - "datetime.py"
Cohesion: 0.15
Nodes (17): Base, ensure_schema_compatibility(), Compatibilidade temporária para bancos SQLite anteriores ao Alembic., set_sqlite_pragma(), SyncConflictAudit, create_conflict_audit(), _jsonable(), list_conflict_audits() (+9 more)

### Community 107 - "Refinamento — BL-0001 — Rastreabilidade da operação offline"
Cohesion: 0.11
Nodes (18): Cenários TDD e contratos futuros, CI remoto e entrega para integração, Escopo, Estratégia de validação, Etapa 1 / Ticket 1 — Reconciliação completa, Fatia 1.1 — Contratos da implementação efetiva, Fatia 1.1 — Contratos efetivos, Fatia 1.2 — Documentação coerente e evidências (+10 more)

### Community 108 - "Identificação e entrada"
Cohesion: 0.17
Nodes (12): Acompanhamento até produção, BL-0026 — Ferramentas, ambiente de testes e rastreabilidade das releases, Comportamento esperado, Comportamento observado, Evidências sanitizadas, Histórico, Identificação e entrada, Impacto e abrangência (+4 more)

### Community 110 - "package.json"
Cohesion: 0.20
Nodes (9): fake-indexeddb, devDependencies, fake-indexeddb, engines, node, name, private, scripts (+1 more)

### Community 111 - "utils/__init__.py"
Cohesion: 0.27
Nodes (7): localdate_filter(), localdatetime_filter(), format_local_date(), format_local_datetime(), date, Convert UTC datetime to local timezone for display, Convert UTC datetime to local date only

### Community 116 - "test_coverage_runner.py"
Cohesion: 0.53
Nodes (5): Contratos BL-0011: relatórios úteis e piso de cobertura realmente aplicado., run_coverage(), test_coverage_floor_fails_a_passing_selection(), test_coverage_reports_are_created_for_selected_tests(), test_test_failure_is_not_hidden_by_coverage()

### Community 118 - "Planejamento de releases após a 1.3.0"
Cohesion: 0.33
Nodes (6): Ajuste de contrato do AUTH_MOCK antes da 1.4.0, Contrato de acompanhamento, Correções descobertas na validação da 1.4.0, Dependências das próximas versões, Organização da 1.4.0, Planejamento de releases após a 1.3.0

### Community 130 - "ValueError"
Cohesion: 0.50
Nodes (3): Cache explícito de dependências visuais reais, fixadas por hash para testes UI., setup(), ValueError

### Community 131 - "FL-09 — Operação Offline"
Cohesion: 0.33
Nodes (6): Atores, Estado e rastreabilidade, FL-09 — Operação Offline, Fluxo Principal, Objetivo, Resultado Esperado

### Community 132 - "FL-06 — Aprendizado do Template"
Cohesion: 0.33
Nodes (6): FL-06 — Aprendizado do Template, Fluxo Principal, Objetivo, Pré-condições, Resultado Esperado, Tipos de Sugestão

### Community 133 - "FL-05 — Compra Colaborativa"
Cohesion: 0.40
Nodes (5): Atores, FL-05 — Compra Colaborativa, Fluxo Principal, Objetivo, Resultado Esperado

## Knowledge Gaps
- **731 isolated node(s):** `ACTIVE_CACHES`, `name`, `private`, `test`, `node` (+726 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **8 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `User` connect `User` to `Execution`, `executions.py`, `make_user`, `Group`, `test_offline_cache.py`, `categories.py`, `template_service.py`, `main.py`, `datetime.py`, `offline_cache_service.py`, `notification_service.py`, `sync_center`, `test_purchase_playwright.py`, `auth.py`, `tupa_auth_service.py`?**
  _High betweenness centrality (0.068) - this node is a cross-community bridge._
- **Why does `Refinamento — BL-0025 — Preparar e publicar versão 1.3.0` connect `Refinamento — BL-0025 — Preparar e publicar versão 1.3.0` to `backlog/README.md`?**
  _High betweenness centrality (0.017) - this node is a cross-community bridge._
- **Why does `BL-0008 — Disponibilizar autoexclusão e anonimização de conta` connect `Identificação e entrada` to `backlog/README.md`?**
  _High betweenness centrality (0.014) - this node is a cross-community bridge._
- **Are the 9 inferred relationships involving `User` (e.g. with `Base` and `AddExecutionItemOperation`) actually correct?**
  _`User` has 9 INFERRED edges - model-reasoned connections that need verification._
- **Are the 129 inferred relationships involving `make_user()` (e.g. with `test_calendar_groups_executions_by_local_scheduled_date()` and `test_calendar_lists_group_executions_and_prioritizes_in_progress_status()`) actually correct?**
  _`make_user()` has 129 INFERRED edges - model-reasoned connections that need verification._
- **Are the 125 inferred relationships involving `make_group()` (e.g. with `test_calendar_groups_executions_by_local_scheduled_date()` and `test_calendar_lists_group_executions_and_prioritizes_in_progress_status()`) actually correct?**
  _`make_group()` has 125 INFERRED edges - model-reasoned connections that need verification._
- **What connects `ACTIVE_CACHES`, `name`, `private` to the rest of the system?**
  _731 weakly-connected nodes found - possible documentation gaps or missing edges._