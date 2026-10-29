# Graph Report - jaci  (2026-10-28)

## Corpus Check
- 163 files · ~174,429 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 2174 nodes · 5115 edges · 129 communities (121 shown, 8 thin omitted)
- Extraction: 93% EXTRACTED · 7% INFERRED · 0% AMBIGUOUS · INFERRED: 353 edges (avg confidence: 0.74)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `e54974b6`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Refinamento — BL-0018 — Corrigir backdrop sobre o modal de completar item
- offline-cache.js
- Refinamento — BL-0021 — API externa para gestão de execuções
- test_offline_cache.py
- create_execution_from_template
- ValueError
- template_service.py
- categories.py
- Identificação e entrada
- main.py
- Refinamento — BL-0012 — Gestão documental compartilhada dos projetos VGX
- Refinamento — BL-0020 — Bloquear renomeação de item vinculado ao template
- Refinamento — BL-0025 — Preparar e publicar versão 1.3.0
- group_service.py
- AGENTS.md
- execution-budget.js
- item-filter.js
- Refinamento — BL-0015 — Adicionar item como comprado durante execução
- sync_center
- service-worker.js
- read
- loading-indicator.js
- sync-status.js
- get_group_by_id
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
- items/BL-0011-ampliar-cobertura-testes-ui.md
- Refinamento — BL-NNNN — Título
- Regras de negócio críticas
- test_pwa.py
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
- Backups do PostgreSQL
- Identificação e entrada
- Pricipais Entidades
- 0001 - Tratamento de datas e timezone
- Aprendizado contínuo dos templates
- Tela Inicial Operacional
- Identificação e entrada
- Identificação e entrada
- test_postgresql_backup.py
- Backlog legado do Jaci
- Edição de execuções agendadas
- FL-03 — Geração de Execução
- user-flows.md
- test_scheduled_execution_editing.py
- Identificação e entrada
- Refinamento — BL-0016 — Botão flutuante para adicionar itens
- FL-01 — Primeiro Acesso e Onboarding
- notification_service.py
- Identificação e entrada
- Identificação e entrada
- overview.md
- handle_setup_profile
- FL-08 — Consulta da Agenda e Histórico
- item-add-modal.js
- Refinamento — BL-0017 — Nome da execução avulsa
- auth.py
- create_template
- Identificação e entrada
- test_database_operations.py
- Identificação e entrada
- test_item_add_fab.py
- executions.py
- Refinamento — BL-0011 — Cobertura, navegador e CI
- Refinamento — BL-0026 — Ferramentas e ambiente de testes
- Identificação e entrada
- ConnectionManager
- User
- test_test_environment.py
- 0002 - Backup automático do PostgreSQL
- auth_service.py
- test_auth_service.py
- Refinamento — BL-0001 — Rastreabilidade da operação offline
- Identificação e entrada
- migrate_sqlite_to_postgres.py
- make_user
- list_notifications
- test_publish.py
- enums.py
- sync_conflict_audit_service.py
- Estratégia de Banco de Dados
- test_business_rules.py
- execution_service.py
- Planejamento de releases após a 1.3.0
- setup_test_env.sh
- ensure_schema_compatibility
- run_test_server.sh
- run_tests.sh
- execution_ws_handler
- FL-09 — Operação Offline
- FL-06 — Aprendizado do Template
- test_auth_pages.py
- get_user_groups

## God Nodes (most connected - your core abstractions)
1. `User` - 147 edges
2. `make_user()` - 126 edges
3. `make_group()` - 125 edges
4. `create_template()` - 98 edges
5. `create_execution_from_template()` - 89 edges
6. `Execution` - 77 edges
7. `add_item_to_template()` - 63 edges
8. `ExecutionItem` - 57 edges
9. `Group` - 47 edges
10. `ExecutionStatus` - 37 edges

## Surprising Connections (you probably didn't know these)
- `test_cloud_postgres_urls_are_normalized_to_psycopg_driver()` --calls--> `Settings`  [EXTRACTED]
  tests/test_database_operations.py → app/config.py
- `test_debug_environment_disables_secure_cookies_for_local_http()` --calls--> `Settings`  [EXTRACTED]
  tests/test_database_operations.py → app/config.py
- `test_production_environment_keeps_secure_cookies()` --calls--> `Settings`  [EXTRACTED]
  tests/test_database_operations.py → app/config.py
- `test_release_environment_name_disables_debug()` --calls--> `Settings`  [EXTRACTED]
  tests/test_database_operations.py → app/config.py
- `test_backup_settings_are_loaded_from_dotenv()` --calls--> `Settings`  [EXTRACTED]
  tests/test_postgresql_backup.py → app/config.py

## Import Cycles
- None detected.

## Communities (129 total, 8 thin omitted)

### Community 0 - "Refinamento — BL-0018 — Corrigir backdrop sobre o modal de completar item"
Cohesion: 0.09
Nodes (21): Cenários TDD, Contratos de etapas futuras, Critérios de sucesso, Escopo, Estratégia de validação, Etapa 1 — Restaurar o empilhamento dos modais de item, Excluído, Fatia 1.1.1 — Proteger a ordem de camadas e o cache PWA (+13 more)

### Community 1 - "offline-cache.js"
Cohesion: 0.05
Nodes (113): applyPersistedOfflineItemState(), auditCard(), buildConflict(), buildQueuedOperation(), calculateExecutionTotal(), classifyOperation(), clearOfflineItemIndicators(), clearOfflineItemIndicatorsWhenSynced() (+105 more)

### Community 2 - "Refinamento — BL-0021 — API externa para gestão de execuções"
Cohesion: 0.06
Nodes (32): Autenticação e escopo, Cenários TDD, Contrato HTTP v1, Contratos de etapas futuras, Critérios de sucesso, Escopo, Estratégia de validação, Etapa 1 — Persistir identidade, concorrência e rastreabilidade (+24 more)

### Community 3 - "test_offline_cache.py"
Cohesion: 0.09
Nodes (8): offline_snapshot(), Snapshot somente leitura dos dados essenciais para cache local., build_offline_snapshot(), _enum_value(), Any, Session, Monta dados essenciais somente leitura para consulta offline., test_offline_snapshot_requires_authentication()

### Community 4 - "create_execution_from_template"
Cohesion: 0.16
Nodes (33): add_item_to_execution(), create_execution_from_template(), finalize_execution(), Cria uma execução a partir de um template, copiando seus itens., Adiciona item à execução sem alterar o template associado., Finaliza a execução. Se discard_pending=True, remove itens não concluídos. Se…, test_fl06_finishing_purchase_suggests_runtime_items_without_applying_them(), test_fl06_only_selected_suggestions_are_applied_to_template() (+25 more)

### Community 5 - "ValueError"
Cohesion: 0.28
Nodes (14): get_settings(), allowed_runtime(), Path, Guardas sem efeitos colaterais para os ambientes sintéticos do Jaci., validate_database(), validate_runtime(), Seed idempotente permitido exclusivamente no banco sintético marcado., seed() (+6 more)

### Community 6 - "template_service.py"
Cohesion: 0.05
Nodes (94): Base, TemplateLearningDismissal, Template, TemplateItem, create_template_page(), edit_template_page(), _get_template_context(), _get_template_items_fragment() (+86 more)

### Community 7 - "categories.py"
Cohesion: 0.12
Nodes (38): Category, create_category_page(), delete_category_confirm_page(), edit_category_page(), handle_create_category(), handle_delete_category(), handle_edit_category(), handle_move_category() (+30 more)

### Community 8 - "Identificação e entrada"
Cohesion: 0.17
Nodes (12): Acompanhamento até produção, BL-0018 — Corrigir backdrop sobre o modal de completar item, Comportamento esperado, Comportamento observado, Evidências sanitizadas, Histórico, Identificação e entrada, Impacto e abrangência (+4 more)

### Community 9 - "main.py"
Cohesion: 0.19
Nodes (18): get_db(), set_sqlite_pragma(), get_active_group(), get_current_user(), get_current_user_ws(), get_unread_notification_count(), Request, Session (+10 more)

### Community 10 - "Refinamento — BL-0012 — Gestão documental compartilhada dos projetos VGX"
Cohesion: 0.05
Nodes (40): Acompanhamento até produção, BL-0012 — Gestão documental compartilhada dos projetos VGX, Comportamento esperado, Comportamento observado, Evidências sanitizadas, Histórico, Identificação e entrada, Impacto e abrangência (+32 more)

### Community 11 - "Refinamento — BL-0020 — Bloquear renomeação de item vinculado ao template"
Cohesion: 0.08
Nodes (24): Cenários TDD, Contratos de etapas futuras, Critérios de sucesso, Escopo, Estratégia de validação, Etapa 1 — Proteger a identidade do item online e offline, Etapa 2 — Fechar o ciclo de identidade entre execução e planejamento, Excluído (+16 more)

### Community 12 - "Refinamento — BL-0025 — Preparar e publicar versão 1.3.0"
Cohesion: 0.06
Nodes (33): Cenários TDD, Contratos de etapas futuras, Critérios de sucesso, Encerramento da release — 2026-10-28, Escopo, Estratégia de validação, Etapa 1 — Preparar o candidato, Etapa 2 — Validar e obter aceite (+25 more)

### Community 13 - "group_service.py"
Cohesion: 0.13
Nodes (21): invite_member(), Convida um novo membro para o grupo via magic link. Retorna dict com success,…, Troca o grupo ativo na sessão., switch_active_group(), _build_invite_email(), _build_login_email(), _build_magic_link(), Template HTML para e-mail de convite para grupo. (+13 more)

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

### Community 24 - "get_group_by_id"
Cohesion: 0.11
Nodes (32): create_group_page(), group_detail(), handle_create_group(), handle_edit_group(), handle_invite(), handle_remove_member(), list_groups(), get (+24 more)

### Community 25 - "🌙 Jaci"
Cohesion: 0.07
Nodes (29): 1. Clone o repositório, 3. Instale as dependências, 4. Execute, Ambiente sintético de testes (BL-0026), Backup automático do PostgreSQL, Banco de dados e migrações, Com Caddy (HTTPS automático), 📧 Configuração de e-mail (+21 more)

### Community 26 - "privacy_policy"
Cohesion: 0.47
Nodes (5): privacy_policy(), get, Request, Privacy Policy page - LGPD, terms_of_use()

### Community 28 - "Refinamento — BL-0013 — Busca e padronização das telas de itens"
Cohesion: 0.09
Nodes (23): Cenários TDD, Contratos de etapas futuras, Critérios de sucesso, Escopo, Estratégia de validação, Etapa 1 — Busca local e navegação padronizada, Excluído, Fatia 1.1.1 — Criar contratos TDD e integrar a Lista (+15 more)

### Community 29 - "tupa_auth_service.py"
Cohesion: 0.25
Nodes (16): create_user(), _credentials(), decode_access_token(), _jwks(), logout(), migrate_user(), Any, refresh() (+8 more)

### Community 30 - "run.py"
Cohesion: 0.50
Nodes (4): main(), parse_args(), Namespace, Executa o Jaci aplicando migrações antes de iniciar o servidor.

### Community 32 - "docker-entrypoint.sh"
Cohesion: 0.83
Nodes (3): is_server_process(), docker-entrypoint.sh script, write_cron_environment()

### Community 33 - "Refinamento — BL-0014 — Resumo de orçamento fixo durante a compra"
Cohesion: 0.09
Nodes (21): Cenários TDD, Contratos de etapas futuras, Critérios de sucesso, Escopo, Estratégia de validação, Etapa 1 — Acompanhamento contínuo do orçamento, Excluído, Fatia 1.1.1 — Implementar o contrato completo da BL-0014 (+13 more)

### Community 45 - "items/BL-0011-ampliar-cobertura-testes-ui.md"
Cohesion: 0.16
Nodes (4): Backlog legado — Sprint 4 — Aprendizado contínuo dos templates, Demandas do backlog com cobertura rastreada, Rastreabilidade das regras de negócio, Rastreabilidade dos fluxos do usuário

### Community 46 - "Refinamento — BL-NNNN — Título"
Cohesion: 0.10
Nodes (21): Cenários TDD, Contratos de etapas futuras, Critérios de sucesso, Escopo, Estratégia de validação, Etapa 1 — `<resultado da etapa>`, Excluído, Fatia 1.1.1 — `<resultado pequeno e verificável>` (+13 more)

### Community 47 - "Regras de negócio críticas"
Cohesion: 0.10
Nodes (19): Regras de negócio críticas, RN01, RN02, RN03, RN04, RN05, RN06, RN07 (+11 more)

### Community 48 - "test_pwa.py"
Cohesion: 0.11
Nodes (18): add_unread_count(), health_check(), home(), get, Request, Painel operacional do grupo ativo., Serve o service worker na raiz para permitir cache offline da aplicação., Serve o manifesto PWA com o tipo de conteúdo esperado pelos navegadores. (+10 more)

### Community 49 - "Fundação PWA e Offline"
Cohesion: 0.11
Nodes (18): BL-004 — Estratégia de Cache, BL-005 a BL-013 — Cache Local e Operações Offline, BL-014 — Fila Local de Operações, BL-015 — Sincronização Automática, BL-016 — Status Detalhado de Sincronização, BL-017 — Retentativa Automática, BL-019 — Resolução de Conflitos, BL-020 — Central de Sincronização (+10 more)

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

### Community 65 - "datetime.py"
Cohesion: 0.07
Nodes (59): agenda_calendar(), agenda_day(), agenda_list(), handle_reschedule(), get, post, Request, Session (+51 more)

### Community 66 - "Backups do PostgreSQL"
Cohesion: 0.29
Nodes (7): Agenda e logs, Backups do PostgreSQL, Configuração, Execução manual, Restauração manual em banco isolado, Retenção, Visão geral

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

### Community 74 - "test_postgresql_backup.py"
Cohesion: 0.24
Nodes (18): CompletedProcess, _backup_environment(), fake_postgres_tools(), fixture, parametrize, Path, _run_backup(), test_backup_disabled_exits_without_calling_postgres_tools() (+10 more)

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
Nodes (29): Atores, Atores, Atores, Atores, Cenários Alternativos, FL-02 — Criação de Template, FL-04 — Execução da Compra, FL-05 — Compra Colaborativa (+21 more)

### Community 79 - "test_scheduled_execution_editing.py"
Cohesion: 0.10
Nodes (33): handle_switch_group(), create_execution_standalone(), Cria uma execução avulsa sem template., Edita somente dados próprios de uma execução agendada., update_scheduled_execution(), make_request(), Request, test_home_alerts_are_limited_and_ordered_by_criticality() (+25 more)

### Community 80 - "Identificação e entrada"
Cohesion: 0.17
Nodes (12): Acompanhamento até produção, BL-0019 — Manter sessão autenticada por oito horas de inatividade, Comportamento esperado, Comportamento observado, Evidências sanitizadas, Histórico, Identificação e entrada, Impacto e abrangência (+4 more)

### Community 81 - "Refinamento — BL-0016 — Botão flutuante para adicionar itens"
Cohesion: 0.09
Nodes (21): Cenários TDD, Contratos de etapas futuras, Critérios de sucesso, Escopo, Estratégia de validação, Etapa 1 — Adição contextual por modal nas telas mutáveis, Excluído, Fatia 1.1.1 — Contratos TDD e fluxo modal completo online/offline (+13 more)

### Community 82 - "FL-01 — Primeiro Acesso e Onboarding"
Cohesion: 0.40
Nodes (5): Atores, FL-01 — Primeiro Acesso e Onboarding, Fluxo Principal, Objetivo, Resultado Esperado

### Community 83 - "notification_service.py"
Cohesion: 0.18
Nodes (16): Notification, create_notification(), get_notifications(), mark_all_as_read(), mark_as_read(), notify_execution_completed(), notify_execution_started(), notify_group_members() (+8 more)

### Community 84 - "Identificação e entrada"
Cohesion: 0.17
Nodes (12): Acompanhamento até produção, BL-0020 — Bloquear renomeação de item vinculado ao template, Comportamento esperado, Comportamento observado, Evidências sanitizadas, Histórico, Identificação e entrada, Impacto e abrangência (+4 more)

### Community 85 - "Identificação e entrada"
Cohesion: 0.17
Nodes (12): Acompanhamento até produção, BL-0024 — Autocompletar nomes de itens pelo histórico do grupo, Comportamento esperado, Comportamento observado, Evidências sanitizadas, Histórico, Identificação e entrada, Impacto e abrangência (+4 more)

### Community 87 - "handle_setup_profile"
Cohesion: 0.19
Nodes (15): handle_change_password(), handle_setup_profile(), handle_update_profile(), password_login(), post, Response, Session, Magic link de login foi substituído pelo Tupã. (+7 more)

### Community 88 - "FL-08 — Consulta da Agenda e Histórico"
Cohesion: 0.33
Nodes (6): Atores, Estado e rastreabilidade, FL-08 — Consulta da Agenda e Histórico, Fluxo Principal, Objetivo, Resultado Esperado

### Community 89 - "item-add-modal.js"
Cohesion: 0.27
Nodes (15): completeSuccess(), finishClose(), focusableElements(), formFor(), hideLocalModal(), hideModal(), initialize(), initializeModal() (+7 more)

### Community 90 - "Refinamento — BL-0017 — Nome da execução avulsa"
Cohesion: 0.09
Nodes (21): Cenários TDD, Contratos de etapas futuras, Critérios de sucesso, Escopo, Estratégia de validação, Etapa 1 — Nome exclusivo para compra sem lista, Excluído, Fatia 1.1.1 — Contratos TDD e implementação completa (+13 more)

### Community 91 - "auth.py"
Cohesion: 0.18
Nodes (18): login_error_page(), login_page(), login_sent_page(), logout(), profile_page(), get, Request, Tela de configuração de perfil (primeiro acesso). (+10 more)

### Community 92 - "create_template"
Cohesion: 0.13
Nodes (40): complete_item(), Inicia a execução (status -> in_progress)., Marca item como comprado com quantidade e valor., Remove item não concluído da execução., remove_item_from_execution(), start_execution(), add_item_to_template(), create_template() (+32 more)

### Community 93 - "Identificação e entrada"
Cohesion: 0.17
Nodes (12): Acompanhamento até produção, BL-0016 — Disponibilizar botão flutuante para adicionar itens, Comportamento esperado, Comportamento observado, Evidências sanitizadas, Histórico, Identificação e entrada, Impacto e abrangência (+4 more)

### Community 94 - "test_database_operations.py"
Cohesion: 0.08
Nodes (19): Aceita nomes usuais de ambiente além de booleanos., Usa psycopg 3 para URLs PostgreSQL fornecidas por provedores., Permite autenticação em desenvolvimento servido por HTTP., Settings, create_database_engine(), Cria engine com ajustes específicos para SQLite ou PostgreSQL., BaseSettings, Engine (+11 more)

### Community 95 - "Identificação e entrada"
Cohesion: 0.17
Nodes (12): Acompanhamento até produção, BL-0017 — Permitir informar um nome para execução avulsa, Comportamento esperado, Comportamento observado, Evidências sanitizadas, Histórico, Identificação e entrada, Impacto e abrangência (+4 more)

### Community 96 - "test_item_add_fab.py"
Cohesion: 0.28
Nodes (12): Path, read(), test_both_modal_pages_load_the_local_cached_controller(), test_fab_and_modal_styles_respect_safe_areas_and_local_fallback(), test_local_modal_controller_preserves_scroll_focus_and_keyboard_behavior(), test_managed_item_modals_stay_above_backdrop_and_page_actions(), test_modal_controller_closes_only_after_online_or_offline_success(), test_modal_pages_keep_the_single_form_available_without_javascript() (+4 more)

### Community 97 - "executions.py"
Cohesion: 0.10
Nodes (59): Group, close_execution_page(), complete_item_form(), _completed_page(), create_execution_page(), edit_item_form(), execution_detail(), execution_items_fragment() (+51 more)

### Community 98 - "Refinamento — BL-0011 — Cobertura, navegador e CI"
Cohesion: 0.11
Nodes (17): Cenários TDD e contratos futuros, Escopo, Estratégia de validação, Etapa 1 / Ticket 1 — Medição Python, Etapa 2 / Ticket 2 — Navegador real, Etapa 3 / Ticket 3 — CI e evidências, Fatia 1.1 — Baseline e relatórios, Fatia 2.1 — Runner e fixtures UI (+9 more)

### Community 99 - "Refinamento — BL-0026 — Ferramentas e ambiente de testes"
Cohesion: 0.10
Nodes (19): Cenários TDD, Contratos futuros, Entrega documental já autorizada, Escopo, Estratégia de validação, Etapa 1 / Ticket 1 — Ambiente e autenticação de teste, Etapa 2 / Ticket 2 — Scripts e operação local, Evidência da fatia 1.1 (+11 more)

### Community 100 - "Identificação e entrada"
Cohesion: 0.17
Nodes (12): Acompanhamento até produção, BL-0025 — Preparar e publicar versão 1.3.0, Comportamento esperado, Comportamento observado, Evidências sanitizadas, Histórico, Identificação e entrada, Impacto e abrangência (+4 more)

### Community 101 - "ConnectionManager"
Cohesion: 0.22
Nodes (8): ConnectionManager, Any, WebSocket, Gerenciador de conexões WebSocket. Agrupa conexões por execution_id para…, Aceita a conexão e registra na sala., Remove a conexão da sala., Envia mensagem para todos na sala, exceto o remetente (se informado). Formato:…, Envia mensagem para um único cliente.

### Community 102 - "User"
Cohesion: 0.17
Nodes (35): ExecutionStatus, User, AddExecutionItemOperation, ConflictResolutionOperation, _execution_state(), ExecutionItemOperation, FinalizeExecutionOperation, _item_state() (+27 more)

### Community 103 - "test_test_environment.py"
Cohesion: 0.26
Nodes (13): process(), parametrize, Contratos BL-0026: ambiente isolado, mock e comandos públicos., setup(), test_cleanup_refuses_wrong_environment_and_preserves_unrelated_files(), test_mock_cannot_start_outside_test(), test_mock_http_authorization_and_unsupported_operations(), test_mock_login_refresh_restart_revocation_and_tamper() (+5 more)

### Community 104 - "0002 - Backup automático do PostgreSQL"
Cohesion: 0.22
Nodes (8): 0002 - Backup automático do PostgreSQL, Consequências, Contexto, Decisão, Plano refinado, Progresso, Status, Validação

### Community 105 - "auth_service.py"
Cohesion: 0.22
Nodes (13): authenticate_with_password(), get_or_create_tupa_user(), Session, Associa uma identidade Tupã ao perfil local do Jaci., Autentica no Tupã e carrega o perfil local., Cria a identidade no Tupã e o perfil local no Jaci., Completa os dados locais do perfil., Atualiza os dados pessoais do usuário. (+5 more)

### Community 106 - "test_auth_service.py"
Cohesion: 0.37
Nodes (13): _decode(), decode_access_token(), _error(), _hash(), logout(), Autenticação sintética. Só é acessível após as guardas de APP_ENV/AUTH_MOCK., refresh(), _runtime() (+5 more)

### Community 107 - "Refinamento — BL-0001 — Rastreabilidade da operação offline"
Cohesion: 0.14
Nodes (13): Cenários TDD e contratos futuros, Escopo, Estratégia de validação, Etapa 1 / Ticket 1 — Reconciliação completa, Fatia 1.1 — Contratos da implementação efetiva, Fatia 1.2 — Documentação coerente e evidências, Fechamento, Objetivo e critérios de sucesso (+5 more)

### Community 108 - "Identificação e entrada"
Cohesion: 0.17
Nodes (12): Acompanhamento até produção, BL-0026 — Ferramentas, ambiente de testes e rastreabilidade das releases, Comportamento esperado, Comportamento observado, Evidências sanitizadas, Histórico, Identificação e entrada, Impacto e abrangência (+4 more)

### Community 109 - "migrate_sqlite_to_postgres.py"
Cohesion: 0.21
Nodes (12): load_target_database_url(), migrate_data(), normalize_postgres_target(), normalize_sqlite_source(), parse_args(), Namespace, Migra todos os dados do SQLite para PostgreSQL preservando IDs e relações., Normaliza URLs fornecidas por provedores para o driver Psycopg 3. (+4 more)

### Community 110 - "make_user"
Cohesion: 0.12
Nodes (43): Execution, ExecutionItem, Calcula o valor total do item (qtd * preço unitário)., db(), make_category(), make_group(), make_user(), fixture (+35 more)

### Community 111 - "list_notifications"
Cohesion: 0.22
Nodes (10): handle_mark_all_read(), handle_mark_read(), list_notifications(), get, post, Request, Session, List notifications for the current user. (+2 more)

### Community 112 - "test_publish.py"
Cohesion: 0.20
Nodes (5): publication(), fixture, parametrize, test_invalid_arguments_never_modify_environment_or_call_docker(), test_version_is_persisted_before_all_compose_steps()

### Community 113 - "enums.py"
Cohesion: 0.14
Nodes (12): RecurrenceType, future_flow, Contratos dos fluxos documentados e dos fluxos futuros ainda pendentes., test_fl08_price_history_is_scoped_by_group_and_item(), test_fl08_spending_analysis_uses_completed_executions_only(), test_fl09_offline_operation_is_queued_before_remote_sync(), test_fl09_reconnection_synchronizes_queued_operations_without_data_loss(), test_fl09_sync_conflict_requires_explicit_resolution_and_preserves_both_versions() (+4 more)

### Community 114 - "sync_conflict_audit_service.py"
Cohesion: 0.26
Nodes (12): SyncConflictAudit, offline_conflict_history(), get, Histórico auditável de conflitos de sincronização dos grupos do usuário., create_conflict_audit(), _jsonable(), list_conflict_audits(), Any (+4 more)

### Community 115 - "Estratégia de Banco de Dados"
Cohesion: 0.33
Nodes (5): Ambientes, Backups de produção, Estratégia de Banco de Dados, Migração de Dados, Migrações

### Community 116 - "test_business_rules.py"
Cohesion: 0.31
Nodes (9): update_execution_item(), make_completed_execution(), parametrize, test_linked_execution_item_rejects_rename_without_partial_update(), test_linked_execution_item_updates_other_fields_with_current_name(), test_rn02_completed_execution_is_immutable(), test_rn08_execution_edits_never_modify_template_items(), test_rn09_foreign_category_is_rejected_when_items_are_edited() (+1 more)

### Community 117 - "execution_service.py"
Cohesion: 0.13
Nodes (24): calculate_next_date(), generate_next_execution(), Calcula a próxima data baseada na recorrência. Usado para geração automática de…, Gera a próxima execução do ciclo, se aplicável. Condições: - Execução vinculada…, cancel_execution(), create_execution_from_pending(), ensure_execution_is_mutable(), generate_next_execution() (+16 more)

### Community 118 - "Planejamento de releases após a 1.3.0"
Cohesion: 0.50
Nodes (4): Contrato de acompanhamento, Dependências das próximas versões, Organização da 1.4.0, Planejamento de releases após a 1.3.0

### Community 120 - "ensure_schema_compatibility"
Cohesion: 0.50
Nodes (4): ensure_schema_compatibility(), Compatibilidade temporária para bancos SQLite anteriores ao Alembic., apply_migrations(), Aplica migrações Alembic e adota bancos SQLite legados.

### Community 123 - "execution_ws_handler"
Cohesion: 0.33
Nodes (6): websocket, WebSocket para sincronização em tempo real de uma execução. Autenticação via…, websocket_execution(), execution_ws_handler(), WebSocket, Gerencia a conexão WebSocket para uma execução específica. Autentica via token…

### Community 124 - "FL-09 — Operação Offline"
Cohesion: 0.33
Nodes (6): Atores, Estado e rastreabilidade, FL-09 — Operação Offline, Fluxo Principal, Objetivo, Resultado Esperado

### Community 125 - "FL-06 — Aprendizado do Template"
Cohesion: 0.33
Nodes (6): FL-06 — Aprendizado do Template, Fluxo Principal, Objetivo, Pré-condições, Resultado Esperado, Tipos de Sugestão

### Community 126 - "test_auth_pages.py"
Cohesion: 0.53
Nodes (5): make_request(), Request, test_invalid_registration_renders_register_page_and_preserves_identity_fields(), test_login_page_only_contains_login_form_and_registration_link(), test_register_page_contains_registration_form_and_login_link()

## Knowledge Gaps
- **656 isolated node(s):** `ACTIVE_CACHES`, `publish.sh script`, `backup_database.sh script`, `run_test_server.sh script`, `run_tests.sh script` (+651 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **8 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `User` connect `User` to `test_offline_cache.py`, `create_execution_from_template`, `ValueError`, `template_service.py`, `categories.py`, `main.py`, `group_service.py`, `sync_center`, `get_group_by_id`, `tupa_auth_service.py`, `test_pwa.py`, `datetime.py`, `test_scheduled_execution_editing.py`, `notification_service.py`, `handle_setup_profile`, `auth.py`, `executions.py`, `auth_service.py`, `make_user`, `list_notifications`, `sync_conflict_audit_service.py`, `execution_service.py`, `get_user_groups`?**
  _High betweenness centrality (0.064) - this node is a cross-community bridge._
- **Why does `Tela Inicial Operacional` connect `Tela Inicial Operacional` to `backlog/README.md`?**
  _High betweenness centrality (0.014) - this node is a cross-community bridge._
- **Why does `Refinamento — BL-0025 — Preparar e publicar versão 1.3.0` connect `Refinamento — BL-0025 — Preparar e publicar versão 1.3.0` to `items/BL-0011-ampliar-cobertura-testes-ui.md`?**
  _High betweenness centrality (0.013) - this node is a cross-community bridge._
- **Are the 9 inferred relationships involving `User` (e.g. with `Base` and `AddExecutionItemOperation`) actually correct?**
  _`User` has 9 INFERRED edges - model-reasoned connections that need verification._
- **Are the 123 inferred relationships involving `make_user()` (e.g. with `test_calendar_groups_executions_by_local_scheduled_date()` and `test_calendar_lists_group_executions_and_prioritizes_in_progress_status()`) actually correct?**
  _`make_user()` has 123 INFERRED edges - model-reasoned connections that need verification._
- **Are the 122 inferred relationships involving `make_group()` (e.g. with `test_calendar_groups_executions_by_local_scheduled_date()` and `test_calendar_lists_group_executions_and_prioritizes_in_progress_status()`) actually correct?**
  _`make_group()` has 122 INFERRED edges - model-reasoned connections that need verification._
- **What connects `ACTIVE_CACHES`, `publish.sh script`, `backup_database.sh script` to the rest of the system?**
  _656 weakly-connected nodes found - possible documentation gaps or missing edges._