# Graph Report - jaci  (2026-11-11)

## Corpus Check
- 212 files · ~212,580 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 2646 nodes · 6091 edges · 151 communities (142 shown, 9 thin omitted)
- Extraction: 93% EXTRACTED · 7% INFERRED · 0% AMBIGUOUS · INFERRED: 427 edges (avg confidence: 0.73)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `cced2c48`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Refinamento — BL-0018 — Corrigir backdrop sobre o modal de completar item
- offline-cache.js
- Refinamento — BL-0021 — API externa para gestão de execuções
- Identificação e entrada
- create_template
- create_execution_from_template
- template_service.py
- categories.py
- Identificação e entrada
- template_learning_service.py
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
- groups.py
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
- make_user
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
- datetime.py
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
- SessionExpired
- user-flows.md
- home_service.py
- Identificação e entrada
- Refinamento — BL-0016 — Botão flutuante para adicionar itens
- FL-04 — Execução da Compra
- main.py
- Identificação e entrada
- Identificação e entrada
- FL-08 — Consulta da Agenda e Histórico
- session_http.py
- test_purchase_playwright.py
- item-add-modal.js
- Refinamento — BL-0017 — Nome da execução avulsa
- auth.py
- offline_queue.test.cjs
- Identificação e entrada
- Settings
- Identificação e entrada
- test_item_add_fab.py
- executions.py
- Refinamento — BL-0011 — Cobertura, navegador e CI
- Refinamento — BL-0026 — Ferramentas e ambiente de testes
- Identificação e entrada
- ConnectionManager
- make_group
- test_test_environment.py
- Refinamento — BL-0009 — Criptografia em repouso — 1.5.0
- database.py
- User
- Refinamento — BL-0001 — Rastreabilidade da operação offline
- Identificação e entrada
- test_postgresql_backup.py
- package.json
- access_session_service.py
- ValueError
- migrate_sqlite_to_postgres.py
- test_business_rules.py
- 0002 - Backup automático do PostgreSQL
- test_coverage_runner.py
- test_sticky_budget.py
- Planejamento de releases após a 1.3.0
- setup_test_env.sh
- Refinamento — BL-0007 — Cópia externa por SSH/SFTP — 1.5.0
- run_test_server.sh
- run_tests.sh
- run_ui_tests.sh
- ensure_schema_compatibility
- Refinamento — BL-0019 — Sessão por oito horas de inatividade — 1.5.0
- FL-09 — Operação Offline
- FL-06 — Aprendizado do Template
- test_auth_mock_bypass.py
- test_offline_queue_node.py
- Refinamento — BL-0010 — Recuperação e troca de senha — 1.5.0
- Refinamento da versão 1.5.0 — Acesso à conta e continuidade da sessão
- FL-02 — Criação de Template
- test_tupa_session_provider.py
- Backups do PostgreSQL
- session_policy.py
- FL-01 — Primeiro Acesso e Onboarding
- RecurrenceType
- FL-03 — Geração de Execução
- FL-10 — Home Operacional
- .normalize_database_url
- get_settings
- repositories/__init__.py
- test_session_auth_flow.py

## God Nodes (most connected - your core abstractions)
1. `User` - 155 edges
2. `make_user()` - 135 edges
3. `make_group()` - 129 edges
4. `create_template()` - 101 edges
5. `create_execution_from_template()` - 92 edges
6. `Execution` - 78 edges
7. `add_item_to_template()` - 65 edges
8. `ExecutionItem` - 58 edges
9. `Group` - 50 edges
10. `get_settings()` - 41 edges

## Surprising Connections (you probably didn't know these)
- `test_real_login_still_requires_password()` --indirect_call--> `get_db()`  [INFERRED]
  tests/test_auth_mock_bypass.py → app/database.py
- `test_mock_http_login_accepts_missing_password_and_user_without_groups()` --indirect_call--> `get_db()`  [INFERRED]
  tests/test_auth_mock_bypass.py → app/database.py
- `Provider` --uses--> `AccessSession`  [INFERRED]
  tests/test_session_auth_flow.py → app/models/access_session.py
- `Provider` --uses--> `SessionMiddleware`  [INFERRED]
  tests/test_session_auth_flow.py → app/utils/session_http.py
- `main()` --indirect_call--> `db()`  [INFERRED]
  scripts/prune_access_sessions.py → tests/conftest.py

## Import Cycles
- None detected.

## Communities (151 total, 9 thin omitted)

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

### Community 4 - "create_template"
Cohesion: 0.12
Nodes (44): complete_item(), Inicia a execução (status -> in_progress)., Marca item como comprado com quantidade e valor., start_execution(), add_item_to_template(), create_template(), Cria um novo template no grupo., Adiciona um item ao template. (+36 more)

### Community 5 - "create_execution_from_template"
Cohesion: 0.14
Nodes (35): add_item_to_execution(), create_execution_from_template(), finalize_execution(), Cria uma execução a partir de um template, copiando seus itens., Adiciona item à execução sem alterar o template associado., Finaliza a execução. Se discard_pending=True, remove itens não concluídos. Se…, make_completed_execution(), Contratos dos fluxos documentados e dos fluxos futuros ainda pendentes. (+27 more)

### Community 6 - "template_service.py"
Cohesion: 0.09
Nodes (57): create_template_page(), edit_template_page(), _get_template_context(), _get_template_items_fragment(), handle_add_item(), handle_create_template(), handle_delete_template(), handle_edit_item() (+49 more)

### Community 7 - "categories.py"
Cohesion: 0.12
Nodes (38): Category, create_category_page(), delete_category_confirm_page(), edit_category_page(), handle_create_category(), handle_delete_category(), handle_edit_category(), handle_move_category() (+30 more)

### Community 8 - "Identificação e entrada"
Cohesion: 0.17
Nodes (12): Acompanhamento até produção, BL-0018 — Corrigir backdrop sobre o modal de completar item, Comportamento esperado, Comportamento observado, Evidências sanitizadas, Histórico, Identificação e entrada, Impacto e abrangência (+4 more)

### Community 9 - "template_learning_service.py"
Cohesion: 0.13
Nodes (30): Template, TemplateItem, analyze_template_history(), apply_template_suggestions(), dismiss_template_suggestions(), _dismissal_key_for_suggestion(), _dismissal_value_for_suggestion(), _dismissed_keys() (+22 more)

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
Cohesion: 0.10
Nodes (20): Aprovação e início, Cenários TDD, CI remoto / entrega para integração, Encerramento da 1.4.0, Escopo, Estratégia de validação, Etapa 1 / Ticket 1 — Ajustar contrato do AUTH_MOCK, Fatia 1.1 — Adaptador e identidade local (+12 more)

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
Cohesion: 0.23
Nodes (9): get, Request, Session, Central local para visualização e resolução da fila de sincronização., sync_center(), make_request(), Request, test_sync_center_renders_local_queue_management_shell() (+1 more)

### Community 20 - "service-worker.js"
Cohesion: 0.20
Nodes (10): ACTIVE_CACHES, cacheOwnerPage(), guardObserved(), isShellAsset(), legacyCache(), navigationUpdate, networkFirstApi(), networkFirstPage() (+2 more)

### Community 21 - "read"
Cohesion: 0.30
Nodes (11): Path, read(), test_clear_and_collapse_controls_share_a_safe_click_handler(), test_completed_execution_is_searchable_collapsible_and_read_only(), test_hidden_filter_rows_override_bootstrap_display_utilities(), test_mutable_execution_exposes_filter_and_visible_financial_metadata(), test_shared_item_filter_controls_rows_groups_counts_and_empty_state(), test_shared_item_filter_normalizes_and_matches_names_locally() (+3 more)

### Community 22 - "loading-indicator.js"
Cohesion: 0.33
Nodes (7): beginRequest(), endRequest(), isPlainLeftClick(), requestCount(), scheduleHide(), shouldShowForLink(), show()

### Community 23 - "sync-status.js"
Cohesion: 0.42
Nodes (8): failSync(), finishSync(), formatDateTime(), render(), renderDetails(), setState(), startSync(), waitForRetry()

### Community 24 - "groups.py"
Cohesion: 0.08
Nodes (51): create_group_page(), group_detail(), handle_create_group(), handle_edit_group(), handle_invite(), handle_remove_member(), handle_switch_group(), list_groups() (+43 more)

### Community 25 - "🌙 Jaci"
Cohesion: 0.06
Nodes (33): 1. Clone o repositório, 3. Instale as dependências, 4. Execute, Ambiente sintético de testes (BL-0026), AUTH_MOCK — bypass do Tupã (BL-0028), Backup automático do PostgreSQL, Banco de dados e migrações, CI no GitHub (+25 more)

### Community 26 - "privacy_policy"
Cohesion: 0.47
Nodes (5): privacy_policy(), get, Request, Privacy Policy page - LGPD, terms_of_use()

### Community 28 - "Refinamento — BL-0013 — Busca e padronização das telas de itens"
Cohesion: 0.09
Nodes (23): Cenários TDD, Contratos de etapas futuras, Critérios de sucesso, Escopo, Estratégia de validação, Etapa 1 — Busca local e navegação padronizada, Excluído, Fatia 1.1.1 — Criar contratos TDD e integrar a Lista (+15 more)

### Community 29 - "tupa_auth_service.py"
Cohesion: 0.08
Nodes (45): add_unread_count(), health_check(), get, Request, Serve o service worker na raiz para permitir cache offline da aplicação., Serve o manifesto PWA com o tipo de conteúdo esperado pelos navegadores., Injeta unread_count no request.state para todas as requisições. Lê o cookie de…, service_worker() (+37 more)

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
Cohesion: 0.12
Nodes (10): Backlog legado — Sprint 4 — Aprendizado contínuo dos templates, Bypass local AUTH_MOCK — BL-0028, Cobertura Python — BL-0011, Contratos offline FL-09 — BL-0001, Demandas de backups abortadas — 2026-11-10, Demandas do backlog com cobertura rastreada, Navegador — BL-0011, Rastreabilidade das regras de negócio (+2 more)

### Community 46 - "Refinamento — BL-NNNN — Título"
Cohesion: 0.10
Nodes (21): Cenários TDD, Contratos de etapas futuras, Critérios de sucesso, Escopo, Estratégia de validação, Etapa 1 — `<resultado da etapa>`, Excluído, Fatia 1.1.1 — `<resultado pequeno e verificável>` (+13 more)

### Community 47 - "Regras de negócio críticas"
Cohesion: 0.10
Nodes (19): Regras de negócio críticas, RN01, RN02, RN03, RN04, RN05, RN06, RN07 (+11 more)

### Community 48 - "make_user"
Cohesion: 0.11
Nodes (37): create_execution_standalone(), Cria uma execução avulsa sem template., future_flow, make_user(), test_calendar_groups_executions_by_local_scheduled_date(), test_calendar_lists_group_executions_and_prioritizes_in_progress_status(), test_discarded_pending_items_remain_as_soft_deleted_history(), test_in_progress_execution_cannot_be_rescheduled() (+29 more)

### Community 49 - "Fundação PWA e Offline"
Cohesion: 0.10
Nodes (21): BL-004 — Estratégia de Cache, BL-005 a BL-013 — Cache Local e Operações Offline, BL-014 — Fila Local de Operações, BL-015 — Sincronização Automática, BL-016 — Status Detalhado de Sincronização, BL-017 — Retentativa Automática, BL-019 — Resolução de Conflitos, BL-020 — Central de Sincronização (+13 more)

### Community 50 - "Backlog de produção"
Cohesion: 0.11
Nodes (18): Backlog de produção, Checklist de passagem ponta a ponta, Ciclo de vida, Classificações, Decisão operacional de backups — 2026-11-10, Dependência externa publicada — 2026-11-11, Entrada rápida, Evidências e dados sensíveis (+10 more)

### Community 51 - "Identificação e entrada"
Cohesion: 0.15
Nodes (13): Acompanhamento até produção, BL-0010 — Disponibilizar reset de senha via login e área logada, Comportamento esperado, Comportamento observado, Evidências sanitizadas, Histórico, Identificação e entrada, Impacto e abrangência (+5 more)

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
Nodes (12): Acompanhamento até produção, BL-0007 — Replicar backups em armazenamento externo, Comportamento esperado, Comportamento observado, Decisão de encerramento, Evidências sanitizadas, Histórico, Identificação e entrada (+4 more)

### Community 59 - "Identificação e entrada"
Cohesion: 0.17
Nodes (12): Acompanhamento até produção, BL-0008 — Disponibilizar autoexclusão e anonimização de conta, Comportamento esperado, Comportamento observado, Evidências sanitizadas, Histórico, Identificação e entrada, Impacto e abrangência (+4 more)

### Community 60 - "Identificação e entrada"
Cohesion: 0.17
Nodes (12): Acompanhamento até produção, BL-0009 — Implementar criptografia de dados em repouso, Comportamento esperado, Comportamento observado, Decisão de encerramento, Evidências sanitizadas, Histórico, Identificação e entrada (+4 more)

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

### Community 65 - "datetime.py"
Cohesion: 0.08
Nodes (47): agenda_calendar(), agenda_day(), agenda_list(), handle_reschedule(), get, post, Request, Session (+39 more)

### Community 66 - "Refinamento — BL-0027 — Incorporação sem categoria"
Cohesion: 0.15
Nodes (12): Cenários TDD, Encerramento da 1.4.0, Escopo e riscos, Estratégia de validação, Etapa 1 / Ticket 1 / Fatia 1.1 — Normalizar o sentinela, Fechamento, Objetivo e critérios de sucesso, Plano de implementação (+4 more)

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

### Community 77 - "SessionExpired"
Cohesion: 0.18
Nodes (11): AccessTokenExpired, Exception, Falha temporária: não equivale a revogação nem renova atividade., SessionExpired, SessionUnavailable, MockSessionProvider, ProviderUnavailable, Adaptadores da sessão local para o Tupã e para o bypass de testes. (+3 more)

### Community 78 - "user-flows.md"
Cohesion: 0.10
Nodes (17): Jaci, Operação com conexão instável, Qual problema o produto resolve?, Atores, Atores, FL-05 — Compra Colaborativa, FL-07 — Gestão de Grupos, Fluxo Crítico do Produto (+9 more)

### Community 79 - "home_service.py"
Cohesion: 0.26
Nodes (16): home(), Painel operacional do grupo ativo., _as_utc(), build_home_dashboard(), get_home_alerts(), get_home_metrics(), get_priority_execution(), get_recent_history() (+8 more)

### Community 80 - "Identificação e entrada"
Cohesion: 0.13
Nodes (15): Acompanhamento até produção, Acompanhamento da implementação, BL-0019 — Manter sessão autenticada por oito horas de inatividade, Comportamento esperado, Comportamento observado, Evidência externa — 2026-11-11, Evidências sanitizadas, Histórico (+7 more)

### Community 81 - "Refinamento — BL-0016 — Botão flutuante para adicionar itens"
Cohesion: 0.09
Nodes (21): Cenários TDD, Contratos de etapas futuras, Critérios de sucesso, Escopo, Estratégia de validação, Etapa 1 — Adição contextual por modal nas telas mutáveis, Excluído, Fatia 1.1.1 — Contratos TDD e fluxo modal completo online/offline (+13 more)

### Community 82 - "FL-04 — Execução da Compra"
Cohesion: 0.33
Nodes (6): Atores, Cenários Alternativos, FL-04 — Execução da Compra, Fluxo Principal, Objetivo, Resultado Esperado

### Community 83 - "main.py"
Cohesion: 0.07
Nodes (47): get_db(), get_active_group(), get_current_user(), get_current_user_ws(), get_unread_notification_count(), Request, Session, Dependências reutilizáveis para injeção em rotas. (+39 more)

### Community 84 - "Identificação e entrada"
Cohesion: 0.17
Nodes (12): Acompanhamento até produção, BL-0020 — Bloquear renomeação de item vinculado ao template, Comportamento esperado, Comportamento observado, Evidências sanitizadas, Histórico, Identificação e entrada, Impacto e abrangência (+4 more)

### Community 85 - "Identificação e entrada"
Cohesion: 0.17
Nodes (12): Acompanhamento até produção, BL-0024 — Autocompletar nomes de itens pelo histórico do grupo, Comportamento esperado, Comportamento observado, Evidências sanitizadas, Histórico, Identificação e entrada, Impacto e abrangência (+4 more)

### Community 86 - "FL-08 — Consulta da Agenda e Histórico"
Cohesion: 0.33
Nodes (6): Atores, Estado e rastreabilidade, FL-08 — Consulta da Agenda e Histórico, Fluxo Principal, Objetivo, Resultado Esperado

### Community 87 - "session_http.py"
Cohesion: 0.14
Nodes (20): _revoke_reference(), localdate_filter(), localdatetime_filter(), csrf_value(), _current(), failure_response(), _load(), offline_owner() (+12 more)

### Community 88 - "test_purchase_playwright.py"
Cohesion: 0.11
Nodes (26): browser_context_args(), only_synthetic_environment(), pinned_browser_assets(), fixture, ui_purchase(), create_local_account(), create_purchase(), install_assets() (+18 more)

### Community 89 - "item-add-modal.js"
Cohesion: 0.27
Nodes (15): completeSuccess(), finishClose(), focusableElements(), formFor(), hideLocalModal(), hideModal(), initialize(), initializeModal() (+7 more)

### Community 90 - "Refinamento — BL-0017 — Nome da execução avulsa"
Cohesion: 0.09
Nodes (21): Cenários TDD, Contratos de etapas futuras, Critérios de sucesso, Escopo, Estratégia de validação, Etapa 1 — Nome exclusivo para compra sem lista, Excluído, Fatia 1.1.1 — Contratos TDD e implementação completa (+13 more)

### Community 91 - "auth.py"
Cohesion: 0.07
Nodes (58): confirm_logout(), handle_change_password(), handle_setup_profile(), handle_update_profile(), login_error_page(), login_page(), login_sent_page(), logout() (+50 more)

### Community 92 - "offline_queue.test.cjs"
Cohesion: 0.19
Nodes (12): assert, browser(), fs, { IDBFactory }, path, plain(), prepared(), response() (+4 more)

### Community 93 - "Identificação e entrada"
Cohesion: 0.17
Nodes (12): Acompanhamento até produção, BL-0016 — Disponibilizar botão flutuante para adicionar itens, Comportamento esperado, Comportamento observado, Evidências sanitizadas, Histórico, Identificação e entrada, Impacto e abrangência (+4 more)

### Community 94 - "Settings"
Cohesion: 0.13
Nodes (15): Permite autenticação em desenvolvimento servido por HTTP., Settings, create_database_engine(), Cria engine com ajustes específicos para SQLite ou PostgreSQL., BaseSettings, Engine, model_validator, create_database_if_missing() (+7 more)

### Community 95 - "Identificação e entrada"
Cohesion: 0.17
Nodes (12): Acompanhamento até produção, BL-0017 — Permitir informar um nome para execução avulsa, Comportamento esperado, Comportamento observado, Evidências sanitizadas, Histórico, Identificação e entrada, Impacto e abrangência (+4 more)

### Community 96 - "test_item_add_fab.py"
Cohesion: 0.28
Nodes (12): Path, read(), test_both_modal_pages_load_the_local_cached_controller(), test_fab_and_modal_styles_respect_safe_areas_and_local_fallback(), test_local_modal_controller_preserves_scroll_focus_and_keyboard_behavior(), test_managed_item_modals_stay_above_backdrop_and_page_actions(), test_modal_controller_closes_only_after_online_or_offline_success(), test_modal_pages_keep_the_single_form_available_without_javascript() (+4 more)

### Community 97 - "executions.py"
Cohesion: 0.08
Nodes (75): Group, close_execution_page(), complete_item_form(), _completed_page(), create_execution_page(), edit_item_form(), execution_detail(), execution_items_fragment() (+67 more)

### Community 98 - "Refinamento — BL-0011 — Cobertura, navegador e CI"
Cohesion: 0.07
Nodes (26): Cenários TDD e contratos futuros, Encerramento da 1.4.0, Escopo, Estratégia de validação, Etapa 1 / Ticket 1 — Medição Python, Etapa 2 / Ticket 2 — Navegador real, Etapa 3 / Ticket 3 — CI e evidências, Evidência da tarefa 1 — Cobertura (+18 more)

### Community 99 - "Refinamento — BL-0026 — Ferramentas e ambiente de testes"
Cohesion: 0.08
Nodes (24): Cenários TDD, Contratos futuros, Encerramento da 1.4.0, Entrega documental já autorizada, Entrega para integração, Escopo, Estratégia de validação, Etapa 1 / Ticket 1 — Ambiente e autenticação de teste (+16 more)

### Community 100 - "Identificação e entrada"
Cohesion: 0.17
Nodes (12): Acompanhamento até produção, BL-0025 — Preparar e publicar versão 1.3.0, Comportamento esperado, Comportamento observado, Evidências sanitizadas, Histórico, Identificação e entrada, Impacto e abrangência (+4 more)

### Community 101 - "ConnectionManager"
Cohesion: 0.14
Nodes (11): ConnectionManager, Any, WebSocket, Gerenciador de conexões WebSocket. Agrupa conexões por execution_id para…, Aceita a conexão e registra na sala., Remove a conexão da sala., Envia mensagem para todos na sala, exceto o remetente (se informado). Formato:…, Envia mensagem para um único cliente. (+3 more)

### Community 102 - "make_group"
Cohesion: 0.08
Nodes (33): Execution, ExecutionItemOperation, Aplica uma alteração offline em item de execução com bloqueio otimista., sync_execution_item_operation(), make_group(), test_local_user_logs_in_without_password_or_tupa_link(), test_execution_add_item_htmx_error_stays_in_modal_without_mutation(), test_member_can_be_invited_to_the_group() (+25 more)

### Community 103 - "test_test_environment.py"
Cohesion: 0.26
Nodes (13): process(), parametrize, Contratos BL-0026: ambiente isolado, mock e comandos públicos., setup(), test_cleanup_refuses_wrong_environment_and_preserves_unrelated_files(), test_mock_cannot_start_outside_test(), test_mock_http_authorization_and_unsupported_operations(), test_mock_login_refresh_restart_revocation_and_tamper() (+5 more)

### Community 104 - "Refinamento — BL-0009 — Criptografia em repouso — 1.5.0"
Cohesion: 0.07
Nodes (27): Aborto solicitado pelo usuário — 2026-11-10, Base de release definida pelo usuário, Cenários TDD após aprovação, Contrato funcional e interfaces, Decisões da 1.5.0, Entrega das três subtarefas — 2026-10-30, Etapa 1 / Ticket 1 — Três subtarefas sequenciais, Execução autorizada — 2026-10-30 (+19 more)

### Community 105 - "database.py"
Cohesion: 0.17
Nodes (12): Base, set_sqlite_pragma(), TemplateLearningDismissal, build_offline_snapshot(), _enum_value(), _iso(), Any, datetime (+4 more)

### Community 106 - "User"
Cohesion: 0.12
Nodes (45): ExecutionStatus, ExecutionItem, Calcula o valor total do item (qtd * preço unitário)., SyncConflictAudit, User, AddExecutionItemOperation, ConflictResolutionOperation, _execution_state() (+37 more)

### Community 107 - "Refinamento — BL-0001 — Rastreabilidade da operação offline"
Cohesion: 0.10
Nodes (20): Cenários TDD e contratos futuros, CI remoto e entrega para integração, Encerramento da 1.4.0, Escopo, Estratégia de validação, Etapa 1 / Ticket 1 — Reconciliação completa, Fatia 1.1 — Contratos da implementação efetiva, Fatia 1.1 — Contratos efetivos (+12 more)

### Community 108 - "Identificação e entrada"
Cohesion: 0.17
Nodes (12): Acompanhamento até produção, BL-0026 — Ferramentas, ambiente de testes e rastreabilidade das releases, Comportamento esperado, Comportamento observado, Evidências sanitizadas, Histórico, Identificação e entrada, Impacto e abrangência (+4 more)

### Community 109 - "test_postgresql_backup.py"
Cohesion: 0.24
Nodes (18): CompletedProcess, _backup_environment(), fake_postgres_tools(), fixture, parametrize, Path, _run_backup(), test_backup_disabled_exits_without_calling_postgres_tools() (+10 more)

### Community 110 - "package.json"
Cohesion: 0.20
Nodes (9): fake-indexeddb, devDependencies, fake-indexeddb, engines, node, name, private, scripts (+1 more)

### Community 111 - "access_session_service.py"
Cohesion: 0.21
Nodes (23): AccessSession, Sessão do navegador, sem senha nem token em claro., lock_session(), Lock de sessão compartilhado entre workers, antes de tocar ou rotacionar., reference_hash(), _access_deadline(), _cipher(), cookie_grant() (+15 more)

### Community 112 - "ValueError"
Cohesion: 0.10
Nodes (32): allowed_runtime(), Path, Guardas sem efeitos colaterais para os ambientes sintéticos do Jaci., validate_database(), validate_runtime(), Seed idempotente permitido exclusivamente no banco sintético marcado., seed(), Cache explícito de dependências visuais reais, fixadas por hash para testes UI. (+24 more)

### Community 113 - "migrate_sqlite_to_postgres.py"
Cohesion: 0.21
Nodes (12): load_target_database_url(), migrate_data(), normalize_postgres_target(), normalize_sqlite_source(), parse_args(), Namespace, Migra todos os dados do SQLite para PostgreSQL preservando IDs e relações., Normaliza URLs fornecidas por provedores para o driver Psycopg 3. (+4 more)

### Community 114 - "test_business_rules.py"
Cohesion: 0.18
Nodes (15): ensure_execution_is_mutable(), Impede qualquer alteração em uma execução já finalizada., update_execution_item(), make_category(), fixture, Session, parametrize, test_linked_execution_item_rejects_rename_without_partial_update() (+7 more)

### Community 115 - "0002 - Backup automático do PostgreSQL"
Cohesion: 0.12
Nodes (13): 0002 - Backup automático do PostgreSQL, Consequências, Contexto, Decisão, Plano refinado, Progresso, Status, Validação (+5 more)

### Community 116 - "test_coverage_runner.py"
Cohesion: 0.53
Nodes (5): Contratos BL-0011: relatórios úteis e piso de cobertura realmente aplicado., run_coverage(), test_coverage_floor_fails_a_passing_selection(), test_coverage_reports_are_created_for_selected_tests(), test_test_failure_is_not_hidden_by_coverage()

### Community 117 - "test_sticky_budget.py"
Cohesion: 0.24
Nodes (4): make_request(), Request, render_items_fragment(), test_scheduled_budget_is_not_sticky_and_missing_budget_has_no_summary()

### Community 118 - "Planejamento de releases após a 1.3.0"
Cohesion: 0.15
Nodes (13): Ajuste de contrato do AUTH_MOCK antes da 1.4.0, Cancelamento do escopo da 1.5.0 — 2026-11-10, Contrato de acompanhamento, Correções descobertas na validação da 1.4.0, Dependências das próximas versões, Histórico da branch de integração da 1.5.0, Organização da 1.4.0, Planejamento de releases após a 1.3.0 (+5 more)

### Community 120 - "Refinamento — BL-0007 — Cópia externa por SSH/SFTP — 1.5.0"
Cohesion: 0.12
Nodes (16): Aborto solicitado pelo usuário — 2026-11-10, Base de release definida pelo usuário, Cenários TDD após aprovação, Contrato funcional e interfaces, Decisões da 1.5.0, Entrega das três subtarefas — 2026-10-29, Etapa 1 / Ticket 1 — Três subtarefas sequenciais, Evidência e limites (+8 more)

### Community 129 - "ensure_schema_compatibility"
Cohesion: 0.50
Nodes (4): ensure_schema_compatibility(), Compatibilidade temporária para bancos SQLite anteriores ao Alembic., apply_migrations(), Aplica migrações Alembic e adota bancos SQLite legados.

### Community 130 - "Refinamento — BL-0019 — Sessão por oito horas de inatividade — 1.5.0"
Cohesion: 0.09
Nodes (22): Autorização e atividade em HTTP, Cenários TDD do escopo, Concorrência, refresh e revogação, Contrato técnico proposto, Decisões e escopo, Diagnóstico e classificação da triagem, Estado persistido e credenciais, Estratégia de validação e publicação (+14 more)

### Community 131 - "FL-09 — Operação Offline"
Cohesion: 0.33
Nodes (6): Atores, Estado e rastreabilidade, FL-09 — Operação Offline, Fluxo Principal, Objetivo, Resultado Esperado

### Community 132 - "FL-06 — Aprendizado do Template"
Cohesion: 0.33
Nodes (6): FL-06 — Aprendizado do Template, Fluxo Principal, Objetivo, Pré-condições, Resultado Esperado, Tipos de Sugestão

### Community 133 - "test_auth_mock_bypass.py"
Cohesion: 0.15
Nodes (11): mock_auth(), fixture, parametrize, BL-0028: bypass usa identidade local, preservando autorização e sessões., test_mock_application_needs_no_smtp_or_named_environment(), test_mock_http_login_accepts_missing_password_and_user_without_groups(), test_mock_id_lookup_binds_integer_for_postgresql(), test_mock_sessions_expire_rotate_revoke_and_recheck_activity() (+3 more)

### Community 135 - "Refinamento — BL-0010 — Recuperação e troca de senha — 1.5.0"
Cohesion: 0.12
Nodes (17): Cenários TDD, Confirmação de reset e troca no perfil, Dependência publicada — 2026-11-11, Dependências e limites, Entrada do link e formulário limpo, Escopo e fluxos, Estratégia de validação, Etapa 1 / Ticket 1 — Contratos e recuperação pública (+9 more)

### Community 136 - "Refinamento da versão 1.5.0 — Acesso à conta e continuidade da sessão"
Cohesion: 0.17
Nodes (12): Atualização da dependência externa — 2026-11-11, Decisões explícitas do usuário, Dependência externa D-01 — Revogação no Tupã, Diagnóstico e fontes locais, Fechamento desta etapa documental, Ordem da versão e integração, Política comum de senha e sessão, Progresso (+4 more)

### Community 137 - "FL-02 — Criação de Template"
Cohesion: 0.40
Nodes (5): Atores, FL-02 — Criação de Template, Fluxo Principal, Objetivo, Resultado Esperado

### Community 138 - "test_tupa_session_provider.py"
Cohesion: 0.16
Nodes (6): contract(), fixture, parametrize, signing_key(), test_malformed_active_response_never_authorizes(), test_service_credential_or_provider_failure_does_not_revoke_user()

### Community 139 - "Backups do PostgreSQL"
Cohesion: 0.25
Nodes (8): Agenda e logs, Backups do PostgreSQL, Configuração, Execução manual, Política mantida pelo usuário — 2026-11-10, Restauração manual em banco isolado, Retenção, Visão geral

### Community 140 - "session_policy.py"
Cohesion: 0.33
Nodes (9): deadline(), internal_return_url(), is_active(), Política local de inatividade. Identidade e revogação pertencem ao provedor., parametrize, BL-0019: contratos escritos antes do guard; não executados pelo agente., test_exact_idle_boundary_and_incoherent_clock(), test_return_preserves_safe_page_query_and_removes_fragment() (+1 more)

### Community 141 - "FL-01 — Primeiro Acesso e Onboarding"
Cohesion: 0.40
Nodes (5): Atores, FL-01 — Primeiro Acesso e Onboarding, Fluxo Principal, Objetivo, Resultado Esperado

### Community 142 - "RecurrenceType"
Cohesion: 0.19
Nodes (12): RecurrenceType, generate_next_execution(), Gera a próxima execução do ciclo, se aplicável. Condições: - Execução vinculada…, str, test_rn03_recurrence_is_only_generated_after_completion(), test_next_cycle_uses_completion_date_and_not_rescheduled_date(), test_standalone_execution_never_generates_recurrence(), make_request() (+4 more)

### Community 143 - "FL-03 — Geração de Execução"
Cohesion: 0.33
Nodes (6): Atores, FL-03 — Geração de Execução, Fluxo Automático, Fluxo Manual, Objetivo, Resultado Esperado

### Community 144 - "FL-10 — Home Operacional"
Cohesion: 0.40
Nodes (5): FL-10 — Home Operacional, Fluxo Principal, Objetivo, Resultado Esperado, Sessão durante a compra (BL-0019)

### Community 145 - ".normalize_database_url"
Cohesion: 0.40
Nodes (3): Aceita nomes usuais de ambiente além de booleanos., Usa psycopg 3 para URLs PostgreSQL fornecidas por provedores., field_validator

### Community 146 - "get_settings"
Cohesion: 0.14
Nodes (12): get_settings(), websocket, WebSocket para sincronização em tempo real de uma execução. Autenticação por…, websocket_execution(), execution_ws_handler(), _guarded_connection(), WebSocket, Gerencia a conexão WebSocket para uma execução específica. Usa cookie opaco… (+4 more)

### Community 150 - "test_session_auth_flow.py"
Cohesion: 0.19
Nodes (16): guard(), issue(), fixture, BL-0019: persistência, rotação e HTTP. Não executar sem liberação., test_access_expiring_during_validation_refreshes_once_without_ending_session(), test_cookie_reference_is_random_and_tokens_are_not_persisted_open(), test_each_request_touches_even_automatic_and_under_one_minute(), test_expired_local_session_never_refreshes_or_resurrects() (+8 more)

## Knowledge Gaps
- **846 isolated node(s):** `navigationUpdate`, `ACTIVE_CACHES`, `name`, `private`, `test` (+841 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **9 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `User` connect `User` to `create_execution_from_template`, `template_service.py`, `categories.py`, `test_auth_mock_bypass.py`, `RecurrenceType`, `get_settings`, `sync_center`, `groups.py`, `tupa_auth_service.py`, `make_user`, `datetime.py`, `home_service.py`, `main.py`, `test_purchase_playwright.py`, `auth.py`, `executions.py`, `make_group`, `database.py`, `access_session_service.py`, `ValueError`?**
  _High betweenness centrality (0.070) - this node is a cross-community bridge._
- **Why does `🌙 Jaci` connect `🌙 Jaci` to `user-flows.md`?**
  _High betweenness centrality (0.017) - this node is a cross-community bridge._
- **Are the 10 inferred relationships involving `User` (e.g. with `Base` and `AddExecutionItemOperation`) actually correct?**
  _`User` has 10 INFERRED edges - model-reasoned connections that need verification._
- **Are the 132 inferred relationships involving `make_user()` (e.g. with `test_calendar_groups_executions_by_local_scheduled_date()` and `test_calendar_lists_group_executions_and_prioritizes_in_progress_status()`) actually correct?**
  _`make_user()` has 132 INFERRED edges - model-reasoned connections that need verification._
- **Are the 126 inferred relationships involving `make_group()` (e.g. with `test_calendar_groups_executions_by_local_scheduled_date()` and `test_calendar_lists_group_executions_and_prioritizes_in_progress_status()`) actually correct?**
  _`make_group()` has 126 INFERRED edges - model-reasoned connections that need verification._
- **What connects `navigationUpdate`, `ACTIVE_CACHES`, `name` to the rest of the system?**
  _846 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Refinamento — BL-0018 — Corrigir backdrop sobre o modal de completar item` be split into smaller, more focused modules?**
  _Cohesion score 0.09090909090909091 - nodes in this community are weakly interconnected._