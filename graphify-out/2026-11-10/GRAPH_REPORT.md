# Graph Report - jaci  (2026-11-10)

## Corpus Check
- 210 files · ~210,575 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 2612 nodes · 6003 edges · 153 communities (144 shown, 9 thin omitted)
- Extraction: 93% EXTRACTED · 7% INFERRED · 0% AMBIGUOUS · INFERRED: 415 edges (avg confidence: 0.73)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `b4ed3eee`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Refinamento — BL-0018 — Corrigir backdrop sobre o modal de completar item
- offline-cache.js
- Refinamento — BL-0021 — API externa para gestão de execuções
- Identificação e entrada
- make_user
- Category
- template_service.py
- category_service.py
- Identificação e entrada
- utils/__init__.py
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
- SessionExpired
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
- agenda.py
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
- items/BL-0001-operacao-offline-cobertura-rastreabilidade.md
- test_pwa.py
- Identificação e entrada
- Refinamento — BL-0016 — Botão flutuante para adicionar itens
- FL-04 — Execução da Compra
- notification_service.py
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
- test_database_operations.py
- Identificação e entrada
- test_item_add_fab.py
- executions.py
- Refinamento — BL-0011 — Cobertura, navegador e CI
- Refinamento — BL-0026 — Ferramentas e ambiente de testes
- Identificação e entrada
- ConnectionManager
- Execution
- test_test_environment.py
- Refinamento — BL-0009 — Criptografia em repouso — 1.5.0
- get_execution_display_name
- sync_conflict_audit_service.py
- Refinamento — BL-0001 — Rastreabilidade da operação offline
- Identificação e entrada
- test_postgresql_backup.py
- package.json
- access_session_service.py
- ValueError
- migrate_sqlite_to_postgres.py
- run
- 0002 - Backup automático do PostgreSQL
- test_coverage_runner.py
- FL-05 — Compra Colaborativa
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
- Group
- test_offline_queue_node.py
- Refinamento — BL-0010 — Recuperação e troca de senha — 1.5.0
- Refinamento da versão 1.5.0 — Acesso à conta e continuidade da sessão
- FL-02 — Criação de Template
- list_notifications
- Backups do PostgreSQL
- write_result
- FL-01 — Primeiro Acesso e Onboarding
- execution_service.py
- FL-07 — Gestão de Grupos
- FL-10 — Home Operacional
- Fluxos Principais do Usuário — Jaci
- get_settings
- repositories/__init__.py
- test_session_auth_flow.py
- test_auth_service.py
- add_unread_count

## God Nodes (most connected - your core abstractions)
1. `User` - 155 edges
2. `make_user()` - 134 edges
3. `make_group()` - 128 edges
4. `create_template()` - 101 edges
5. `create_execution_from_template()` - 92 edges
6. `Execution` - 78 edges
7. `add_item_to_template()` - 65 edges
8. `ExecutionItem` - 58 edges
9. `Group` - 50 edges
10. `get_settings()` - 40 edges

## Surprising Connections (you probably didn't know these)
- `test_real_login_still_requires_password()` --indirect_call--> `get_db()`  [INFERRED]
  tests/test_auth_mock_bypass.py → app/database.py
- `Provider` --uses--> `AccessSession`  [INFERRED]
  tests/test_session_auth_flow.py → app/models/access_session.py
- `_guarded_identity()` --indirect_call--> `db()`  [INFERRED]
  app/websocket/handlers.py → tests/conftest.py
- `main()` --indirect_call--> `db()`  [INFERRED]
  scripts/prune_access_sessions.py → tests/conftest.py
- `test_http_ws_and_middleware_use_local_identity_and_group_authorization()` --indirect_call--> `main()`  [INFERRED]
  tests/test_auth_mock_bypass.py → scripts/test_environment.py

## Import Cycles
- None detected.

## Communities (153 total, 9 thin omitted)

### Community 0 - "Refinamento — BL-0018 — Corrigir backdrop sobre o modal de completar item"
Cohesion: 0.10
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
Nodes (150): handle_create_execution(), Create a new execution., add_item_to_execution(), complete_item(), create_execution_from_template(), create_execution_standalone(), finalize_execution(), datetime (+142 more)

### Community 5 - "Category"
Cohesion: 0.15
Nodes (18): Category, authenticate_with_password(), get_or_create_tupa_user(), get_user_from_claims(), Session, Cria a identidade no Tupã e o perfil local no Jaci., Completa os dados locais do perfil., Atualiza os dados pessoais do usuário. (+10 more)

### Community 6 - "template_service.py"
Cohesion: 0.05
Nodes (92): RecurrenceType, TemplateLearningDismissal, Template, TemplateItem, create_template_page(), edit_template_page(), _get_template_context(), _get_template_items_fragment() (+84 more)

### Community 7 - "category_service.py"
Cohesion: 0.10
Nodes (37): create_category_page(), delete_category_confirm_page(), edit_category_page(), handle_create_category(), handle_delete_category(), handle_edit_category(), handle_move_category(), handle_uncategorized_position() (+29 more)

### Community 8 - "Identificação e entrada"
Cohesion: 0.17
Nodes (12): Acompanhamento até produção, BL-0018 — Corrigir backdrop sobre o modal de completar item, Comportamento esperado, Comportamento observado, Evidências sanitizadas, Histórico, Identificação e entrada, Impacto e abrangência (+4 more)

### Community 9 - "utils/__init__.py"
Cohesion: 0.15
Nodes (17): _build_invite_email(), _build_login_email(), _build_magic_link(), Template HTML para e-mail de convite para grupo., Monta a URL completa do magic link., Envia e-mail com magic link. Se SMTP não configurado, faz log do link (modo…, Template HTML para e-mail de login., send_magic_link() (+9 more)

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
Cohesion: 0.22
Nodes (8): get, Request, Session, Central local para visualização e resolução da fila de sincronização., sync_center(), make_request(), Request, test_sync_center_requires_authentication()

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

### Community 24 - "User"
Cohesion: 0.12
Nodes (42): User, create_group_page(), group_detail(), handle_create_group(), handle_edit_group(), handle_invite(), handle_remove_member(), handle_switch_group() (+34 more)

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
Cohesion: 0.25
Nodes (16): create_user(), _credentials(), decode_access_token(), _jwks(), logout(), migrate_user(), Any, Exception (+8 more)

### Community 30 - "run.py"
Cohesion: 0.50
Nodes (4): main(), parse_args(), Namespace, Executa o Jaci aplicando migrações antes de iniciar o servidor.

### Community 32 - "docker-entrypoint.sh"
Cohesion: 0.83
Nodes (3): is_server_process(), docker-entrypoint.sh script, write_cron_environment()

### Community 33 - "Refinamento — BL-0014 — Resumo de orçamento fixo durante a compra"
Cohesion: 0.10
Nodes (21): Cenários TDD, Contratos de etapas futuras, Critérios de sucesso, Escopo, Estratégia de validação, Etapa 1 — Acompanhamento contínuo do orçamento, Excluído, Fatia 1.1.1 — Implementar o contrato completo da BL-0014 (+13 more)

### Community 45 - "tests/README.md"
Cohesion: 0.11
Nodes (10): Backlog legado — Sprint 4 — Aprendizado contínuo dos templates, Bypass local AUTH_MOCK — BL-0028, Cobertura Python — BL-0011, Contratos offline FL-09 — BL-0001, Demandas de backups abortadas — 2026-11-10, Demandas do backlog com cobertura rastreada, Navegador — BL-0011, Rastreabilidade das regras de negócio (+2 more)

### Community 46 - "Refinamento — BL-NNNN — Título"
Cohesion: 0.09
Nodes (21): Cenários TDD, Contratos de etapas futuras, Critérios de sucesso, Escopo, Estratégia de validação, Etapa 1 — `<resultado da etapa>`, Excluído, Fatia 1.1.1 — `<resultado pequeno e verificável>` (+13 more)

### Community 47 - "Regras de negócio críticas"
Cohesion: 0.10
Nodes (19): Regras de negócio críticas, RN01, RN02, RN03, RN04, RN05, RN06, RN07 (+11 more)

### Community 48 - "SessionExpired"
Cohesion: 0.16
Nodes (11): Exception, Falha temporária: não equivale a revogação nem renova atividade., SessionExpired, SessionUnavailable, MockSessionProvider, ProviderUnavailable, TupaSessionProvider, SessionMiddleware (+3 more)

### Community 49 - "Fundação PWA e Offline"
Cohesion: 0.10
Nodes (21): BL-004 — Estratégia de Cache, BL-005 a BL-013 — Cache Local e Operações Offline, BL-014 — Fila Local de Operações, BL-015 — Sincronização Automática, BL-016 — Status Detalhado de Sincronização, BL-017 — Retentativa Automática, BL-019 — Resolução de Conflitos, BL-020 — Central de Sincronização (+13 more)

### Community 50 - "Backlog de produção"
Cohesion: 0.12
Nodes (17): Backlog de produção, Checklist de passagem ponta a ponta, Ciclo de vida, Classificações, Decisão operacional de backups — 2026-11-10, Entrada rápida, Evidências e dados sensíveis, Git Flow (+9 more)

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
Nodes (12): Acompanhamento até produção, BL-0007 — Replicar backups em armazenamento externo, Comportamento esperado, Comportamento observado, Decisão de encerramento, Evidências sanitizadas, Histórico, Identificação e entrada (+4 more)

### Community 59 - "Identificação e entrada"
Cohesion: 0.15
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
Cohesion: 0.15
Nodes (12): Acompanhamento até produção, BL-NNNN — Título curto, Comportamento esperado, Comportamento observado, Evidências sanitizadas, Histórico, Identificação e entrada, Impacto e abrangência (+4 more)

### Community 65 - "agenda.py"
Cohesion: 0.10
Nodes (34): agenda_calendar(), agenda_day(), agenda_list(), handle_reschedule(), get, post, Request, Session (+26 more)

### Community 66 - "Refinamento — BL-0027 — Incorporação sem categoria"
Cohesion: 0.17
Nodes (12): Cenários TDD, Encerramento da 1.4.0, Escopo e riscos, Estratégia de validação, Etapa 1 / Ticket 1 / Fatia 1.1 — Normalizar o sentinela, Fechamento, Objetivo e critérios de sucesso, Plano de implementação (+4 more)

### Community 67 - "Identificação e entrada"
Cohesion: 0.17
Nodes (12): Acompanhamento até produção, BL-0021 — Expor API externa para criar e editar execuções, Comportamento esperado, Comportamento observado, Evidências sanitizadas, Histórico, Identificação e entrada, Impacto e abrangência (+4 more)

### Community 68 - "Pricipais Entidades"
Cohesion: 0.22
Nodes (8): Categoria, Execução, Grupo, Item de Execução, Item de Template, Pricipais Entidades, Template, Usuário

### Community 69 - "0001 - Tratamento de datas e timezone"
Cohesion: 0.29
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

### Community 78 - "items/BL-0001-operacao-offline-cobertura-rastreabilidade.md"
Cohesion: 0.26
Nodes (4): Jaci, Operação com conexão instável, Qual problema o produto resolve?, Fluxo Crítico do Produto

### Community 79 - "test_pwa.py"
Cohesion: 0.17
Nodes (10): Serve o service worker na raiz para permitir cache offline da aplicação., Serve o manifesto PWA com o tipo de conteúdo esperado pelos navegadores., service_worker(), web_app_manifest(), png_dimensions(), Path, test_base_template_declares_global_loading_indicator(), test_base_template_declares_manifest_ios_support_and_install_action() (+2 more)

### Community 80 - "Identificação e entrada"
Cohesion: 0.15
Nodes (13): Acompanhamento até produção, Acompanhamento da implementação, BL-0019 — Manter sessão autenticada por oito horas de inatividade, Comportamento esperado, Comportamento observado, Evidências sanitizadas, Histórico, Identificação e entrada (+5 more)

### Community 81 - "Refinamento — BL-0016 — Botão flutuante para adicionar itens"
Cohesion: 0.10
Nodes (21): Cenários TDD, Contratos de etapas futuras, Critérios de sucesso, Escopo, Estratégia de validação, Etapa 1 — Adição contextual por modal nas telas mutáveis, Excluído, Fatia 1.1.1 — Contratos TDD e fluxo modal completo online/offline (+13 more)

### Community 82 - "FL-04 — Execução da Compra"
Cohesion: 0.33
Nodes (6): Atores, Cenários Alternativos, FL-04 — Execução da Compra, Fluxo Principal, Objetivo, Resultado Esperado

### Community 83 - "notification_service.py"
Cohesion: 0.17
Nodes (18): Notification, create_notification(), get_notifications(), mark_all_as_read(), mark_as_read(), notify_execution_completed(), notify_execution_started(), notify_execution_updated() (+10 more)

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
Cohesion: 0.15
Nodes (21): _revoke_reference(), internal_return_url(), localdatetime_filter(), format_local_datetime(), Convert UTC datetime to local timezone for display, csrf_value(), _current(), failure_response() (+13 more)

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
Cohesion: 0.10
Nodes (40): confirm_logout(), handle_change_password(), handle_setup_profile(), handle_update_profile(), login_error_page(), login_page(), login_sent_page(), logout() (+32 more)

### Community 92 - "offline_queue.test.cjs"
Cohesion: 0.19
Nodes (12): assert, browser(), fs, { IDBFactory }, path, plain(), prepared(), response() (+4 more)

### Community 93 - "Identificação e entrada"
Cohesion: 0.17
Nodes (12): Acompanhamento até produção, BL-0016 — Disponibilizar botão flutuante para adicionar itens, Comportamento esperado, Comportamento observado, Evidências sanitizadas, Histórico, Identificação e entrada, Impacto e abrangência (+4 more)

### Community 94 - "test_database_operations.py"
Cohesion: 0.09
Nodes (21): Aceita nomes usuais de ambiente além de booleanos., Usa psycopg 3 para URLs PostgreSQL fornecidas por provedores., Permite autenticação em desenvolvimento servido por HTTP., Settings, create_database_engine(), Cria engine com ajustes específicos para SQLite ou PostgreSQL., BaseSettings, Engine (+13 more)

### Community 95 - "Identificação e entrada"
Cohesion: 0.17
Nodes (12): Acompanhamento até produção, BL-0017 — Permitir informar um nome para execução avulsa, Comportamento esperado, Comportamento observado, Evidências sanitizadas, Histórico, Identificação e entrada, Impacto e abrangência (+4 more)

### Community 96 - "test_item_add_fab.py"
Cohesion: 0.28
Nodes (12): Path, read(), test_both_modal_pages_load_the_local_cached_controller(), test_fab_and_modal_styles_respect_safe_areas_and_local_fallback(), test_local_modal_controller_preserves_scroll_focus_and_keyboard_behavior(), test_managed_item_modals_stay_above_backdrop_and_page_actions(), test_modal_controller_closes_only_after_online_or_offline_success(), test_modal_pages_keep_the_single_form_available_without_javascript() (+4 more)

### Community 97 - "executions.py"
Cohesion: 0.10
Nodes (54): close_execution_page(), complete_item_form(), _completed_page(), create_execution_page(), edit_item_form(), execution_detail(), execution_items_fragment(), execution_sidebar_fragment() (+46 more)

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
Cohesion: 0.18
Nodes (10): ConnectionManager, Any, WebSocket, Gerenciador de conexões WebSocket. Agrupa conexões por execution_id para…, Aceita a conexão e registra na sala., Remove a conexão da sala., Envia mensagem para todos na sala, exceto o remetente (se informado). Formato:…, Envia mensagem para um único cliente. (+2 more)

### Community 102 - "Execution"
Cohesion: 0.07
Nodes (63): Execution, ExecutionItem, Calcula o valor total do item (qtd * preço unitário)., AddExecutionItemOperation, ConflictResolutionOperation, _execution_state(), ExecutionItemOperation, FinalizeExecutionOperation (+55 more)

### Community 103 - "test_test_environment.py"
Cohesion: 0.24
Nodes (14): test_mock_application_needs_no_smtp_or_named_environment(), process(), parametrize, Contratos BL-0026: ambiente isolado, mock e comandos públicos., setup(), test_cleanup_refuses_wrong_environment_and_preserves_unrelated_files(), test_mock_cannot_start_outside_test(), test_mock_http_authorization_and_unsupported_operations() (+6 more)

### Community 104 - "Refinamento — BL-0009 — Criptografia em repouso — 1.5.0"
Cohesion: 0.07
Nodes (27): Aborto solicitado pelo usuário — 2026-11-10, Base de release definida pelo usuário, Cenários TDD após aprovação, Contrato funcional e interfaces, Decisões da 1.5.0, Entrega das três subtarefas — 2026-10-30, Etapa 1 / Ticket 1 — Três subtarefas sequenciais, Execução autorizada — 2026-10-30 (+19 more)

### Community 105 - "get_execution_display_name"
Cohesion: 0.18
Nodes (22): get_execution_display_name(), Retorna o nome próprio da execução, preservando fallback legado., _as_utc(), build_home_dashboard(), get_home_alerts(), get_home_metrics(), get_priority_execution(), get_recent_history() (+14 more)

### Community 106 - "sync_conflict_audit_service.py"
Cohesion: 0.36
Nodes (9): SyncConflictAudit, create_conflict_audit(), _jsonable(), list_conflict_audits(), Any, BaseModel, Session, resolve_conflict_audit() (+1 more)

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
Cohesion: 0.17
Nodes (27): AccessSession, Sessão do navegador, sem senha nem token em claro., lock_session(), Lock de sessão compartilhado entre workers, antes de tocar ou rotacionar., reference_hash(), _cipher(), cookie_grant(), _grant() (+19 more)

### Community 112 - "ValueError"
Cohesion: 0.23
Nodes (15): allowed_runtime(), Path, Guardas sem efeitos colaterais para os ambientes sintéticos do Jaci., validate_database(), validate_runtime(), Cache explícito de dependências visuais reais, fixadas por hash para testes UI., setup(), main() (+7 more)

### Community 113 - "migrate_sqlite_to_postgres.py"
Cohesion: 0.21
Nodes (12): load_target_database_url(), migrate_data(), normalize_postgres_target(), normalize_sqlite_source(), parse_args(), Namespace, Migra todos os dados do SQLite para PostgreSQL preservando IDs e relações., Normaliza URLs fornecidas por provedores para o driver Psycopg 3. (+4 more)

### Community 114 - "run"
Cohesion: 0.29
Nodes (11): run(), publication(), fixture, parametrize, test_custom_environment_path_with_spaces(), test_docker_failure_stops_sequence_and_retains_requested_version(), test_failed_temporary_write_preserves_original_and_cleans_up(), test_invalid_arguments_never_modify_environment_or_call_docker() (+3 more)

### Community 115 - "0002 - Backup automático do PostgreSQL"
Cohesion: 0.11
Nodes (13): 0002 - Backup automático do PostgreSQL, Consequências, Contexto, Decisão, Plano refinado, Progresso, Status, Validação (+5 more)

### Community 116 - "test_coverage_runner.py"
Cohesion: 0.53
Nodes (5): Contratos BL-0011: relatórios úteis e piso de cobertura realmente aplicado., run_coverage(), test_coverage_floor_fails_a_passing_selection(), test_coverage_reports_are_created_for_selected_tests(), test_test_failure_is_not_hidden_by_coverage()

### Community 117 - "FL-05 — Compra Colaborativa"
Cohesion: 0.40
Nodes (5): Atores, FL-05 — Compra Colaborativa, Fluxo Principal, Objetivo, Resultado Esperado

### Community 118 - "Planejamento de releases após a 1.3.0"
Cohesion: 0.17
Nodes (12): Ajuste de contrato do AUTH_MOCK antes da 1.4.0, Cancelamento do escopo da 1.5.0 — 2026-11-10, Contrato de acompanhamento, Correções descobertas na validação da 1.4.0, Dependências das próximas versões, Histórico da branch de integração da 1.5.0, Organização da 1.4.0, Planejamento de releases após a 1.3.0 (+4 more)

### Community 120 - "Refinamento — BL-0007 — Cópia externa por SSH/SFTP — 1.5.0"
Cohesion: 0.12
Nodes (16): Aborto solicitado pelo usuário — 2026-11-10, Base de release definida pelo usuário, Cenários TDD após aprovação, Contrato funcional e interfaces, Decisões da 1.5.0, Entrega das três subtarefas — 2026-10-29, Etapa 1 / Ticket 1 — Três subtarefas sequenciais, Evidência e limites (+8 more)

### Community 129 - "ensure_schema_compatibility"
Cohesion: 0.50
Nodes (4): ensure_schema_compatibility(), Compatibilidade temporária para bancos SQLite anteriores ao Alembic., apply_migrations(), Aplica migrações Alembic e adota bancos SQLite legados.

### Community 130 - "Refinamento — BL-0019 — Sessão por oito horas de inatividade — 1.5.0"
Cohesion: 0.10
Nodes (20): Autorização e atividade em HTTP, Cenários TDD do escopo, Concorrência, refresh e revogação, Contrato técnico proposto, Decisões e escopo, Diagnóstico e classificação da triagem, Estado persistido e credenciais, Estratégia de validação e publicação (+12 more)

### Community 131 - "FL-09 — Operação Offline"
Cohesion: 0.33
Nodes (6): Atores, Estado e rastreabilidade, FL-09 — Operação Offline, Fluxo Principal, Objetivo, Resultado Esperado

### Community 132 - "FL-06 — Aprendizado do Template"
Cohesion: 0.33
Nodes (6): FL-06 — Aprendizado do Template, Fluxo Principal, Objetivo, Pré-condições, Resultado Esperado, Tipos de Sugestão

### Community 133 - "Group"
Cohesion: 0.10
Nodes (31): Base, get_db(), set_sqlite_pragma(), get_active_group(), get_current_user(), get_current_user_ws(), get_unread_notification_count(), Request (+23 more)

### Community 135 - "Refinamento — BL-0010 — Recuperação e troca de senha — 1.5.0"
Cohesion: 0.12
Nodes (16): Cenários TDD, Confirmação de reset e troca no perfil, Dependências e limites, Entrada do link e formulário limpo, Escopo e fluxos, Estratégia de validação, Etapa 1 / Ticket 1 — Contratos e recuperação pública, Etapa 2 / Ticket 2 — Senha nova, perfil e sessão (+8 more)

### Community 136 - "Refinamento da versão 1.5.0 — Acesso à conta e continuidade da sessão"
Cohesion: 0.18
Nodes (11): Decisões explícitas do usuário, Dependência externa D-01 — Revogação no Tupã, Diagnóstico e fontes locais, Fechamento desta etapa documental, Ordem da versão e integração, Política comum de senha e sessão, Progresso, Rastreabilidade e aprovação (+3 more)

### Community 137 - "FL-02 — Criação de Template"
Cohesion: 0.40
Nodes (5): Atores, FL-02 — Criação de Template, Fluxo Principal, Objetivo, Resultado Esperado

### Community 138 - "list_notifications"
Cohesion: 0.22
Nodes (10): handle_mark_all_read(), handle_mark_read(), list_notifications(), get, post, Request, Session, List notifications for the current user. (+2 more)

### Community 139 - "Backups do PostgreSQL"
Cohesion: 0.25
Nodes (8): Agenda e logs, Backups do PostgreSQL, Configuração, Execução manual, Política mantida pelo usuário — 2026-11-10, Restauração manual em banco isolado, Retenção, Visão geral

### Community 140 - "write_result"
Cohesion: 0.33
Nodes (4): Path, write_result(), Contratos futuros BL-0011 para guardas do runner de navegador., test_ui_summary_is_written_when_playwright_removes_empty_output()

### Community 141 - "FL-01 — Primeiro Acesso e Onboarding"
Cohesion: 0.40
Nodes (5): Atores, FL-01 — Primeiro Acesso e Onboarding, Fluxo Principal, Objetivo, Resultado Esperado

### Community 142 - "execution_service.py"
Cohesion: 0.13
Nodes (27): ExecutionStatus, calculate_next_date(), generate_next_execution(), Calcula a próxima data baseada na recorrência. Usado para geração automática de…, Gera a próxima execução do ciclo, se aplicável. Condições: - Execução vinculada…, cancel_execution(), create_execution_from_pending(), ensure_execution_is_mutable() (+19 more)

### Community 143 - "FL-07 — Gestão de Grupos"
Cohesion: 0.40
Nodes (5): Atores, FL-07 — Gestão de Grupos, Fluxo Principal, Objetivo, Resultado Esperado

### Community 144 - "FL-10 — Home Operacional"
Cohesion: 0.40
Nodes (5): FL-10 — Home Operacional, Fluxo Principal, Objetivo, Resultado Esperado, Sessão durante a compra (BL-0019)

### Community 145 - "Fluxos Principais do Usuário — Jaci"
Cohesion: 0.67
Nodes (3): Fluxos Principais do Usuário — Jaci, Objetivo, Princípios Gerais

### Community 146 - "get_settings"
Cohesion: 0.17
Nodes (13): get_settings(), websocket, WebSocket para sincronização em tempo real de uma execução. Autenticação por…, websocket_execution(), Adaptadores de sessão. A integração real D-01 continua fechada, sem API…, execution_ws_handler(), _guarded_connection(), _guarded_identity() (+5 more)

### Community 150 - "test_session_auth_flow.py"
Cohesion: 0.21
Nodes (14): guard(), issue(), fixture, BL-0019: persistência, rotação e HTTP. Não executar sem liberação., test_cookie_reference_is_random_and_tokens_are_not_persisted_open(), test_each_request_touches_even_automatic_and_under_one_minute(), test_expired_local_session_never_refreshes_or_resurrects(), test_http_background_counts_but_expired_post_never_reaches_handler() (+6 more)

### Community 151 - "test_auth_service.py"
Cohesion: 0.37
Nodes (13): _decode(), decode_access_token(), _error(), _hash(), logout(), Bypass Tupã para usuários locais, habilitado somente por APP_ENV=test/AUTH_MOCK., refresh(), _runtime() (+5 more)

### Community 152 - "add_unread_count"
Cohesion: 0.29
Nodes (8): add_unread_count(), health_check(), home(), get, Request, Painel operacional do grupo ativo., Injeta unread_count no request.state para todas as requisições. Lê o cookie de…, middleware

## Knowledge Gaps
- **839 isolated node(s):** `navigationUpdate`, `ACTIVE_CACHES`, `name`, `private`, `test` (+834 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **9 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `User` connect `User` to `make_user`, `Group`, `template_service.py`, `category_service.py`, `Category`, `list_notifications`, `execution_service.py`, `get_settings`, `sync_center`, `test_auth_service.py`, `add_unread_count`, `tupa_auth_service.py`, `agenda.py`, `notification_service.py`, `test_purchase_playwright.py`, `auth.py`, `executions.py`, `Execution`, `get_execution_display_name`, `sync_conflict_audit_service.py`, `access_session_service.py`?**
  _High betweenness centrality (0.068) - this node is a cross-community bridge._
- **Why does `get_settings()` connect `get_settings` to `Group`, `Category`, `test_purchase_playwright.py`, `utils/__init__.py`, `access_session_service.py`, `ValueError`, `session_http.py`, `test_auth_service.py`, `User`, `auth.py`, `tupa_auth_service.py`, `test_database_operations.py`?**
  _High betweenness centrality (0.013) - this node is a cross-community bridge._
- **Are the 10 inferred relationships involving `User` (e.g. with `Base` and `AddExecutionItemOperation`) actually correct?**
  _`User` has 10 INFERRED edges - model-reasoned connections that need verification._
- **Are the 131 inferred relationships involving `make_user()` (e.g. with `test_calendar_groups_executions_by_local_scheduled_date()` and `test_calendar_lists_group_executions_and_prioritizes_in_progress_status()`) actually correct?**
  _`make_user()` has 131 INFERRED edges - model-reasoned connections that need verification._
- **Are the 125 inferred relationships involving `make_group()` (e.g. with `test_calendar_groups_executions_by_local_scheduled_date()` and `test_calendar_lists_group_executions_and_prioritizes_in_progress_status()`) actually correct?**
  _`make_group()` has 125 INFERRED edges - model-reasoned connections that need verification._
- **What connects `navigationUpdate`, `ACTIVE_CACHES`, `name` to the rest of the system?**
  _839 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Refinamento — BL-0018 — Corrigir backdrop sobre o modal de completar item` be split into smaller, more focused modules?**
  _Cohesion score 0.09523809523809523 - nodes in this community are weakly interconnected._