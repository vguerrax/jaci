# Rastreabilidade das regras de negócio

| Regra | Cobertura principal |
|---|---|
| RN01 | `test_execution_is_a_snapshot_and_template_changes_only_affect_future_runs` |
| RN02 | `test_rn02_completed_execution_is_immutable` |
| RN03 | `test_next_cycle_uses_completion_date_and_not_rescheduled_date`, `test_rn03_recurrence_is_only_generated_after_completion` |
| RN04 | `test_next_cycle_uses_completion_date_and_not_rescheduled_date` |
| RN05 | `test_in_progress_execution_cannot_be_rescheduled` |
| RN06 | `test_pending_items_can_be_carried_to_a_new_standalone_execution`, `test_discarded_pending_items_remain_as_soft_deleted_history` |
| RN07 | `test_standalone_execution_never_generates_recurrence` |
| RN08 | `test_rn08_execution_edits_never_modify_template_items`, `test_template_notes_are_copied_without_linking_future_execution_edits` |
| RN09 | `test_group_data_is_only_visible_to_members`, `test_category_ids_from_another_group_are_rejected`, `test_rn09_foreign_category_is_rejected_when_items_are_edited` |
| RN10 | `test_stale_item_version_fails_explicitly_without_overwriting` |
| RN11 | `test_execution_budget_can_override_template_budget`, `test_execution_is_a_snapshot_and_template_changes_only_affect_future_runs` |
| RN12 | `test_rn12_websocket_failure_does_not_undo_persisted_api_mutation` |
| RN13 | `test_sync_center_renders_local_queue_management_shell`, `test_sync_center_frontend_reads_queue_and_resolves_conflicts` |
| RN14 | `test_offline_conflict_history_lists_and_resolves_audits`, `test_sync_center_frontend_reads_queue_and_resolves_conflicts` |
| RN15 | `test_home_prioritizes_in_progress_purchase_over_scheduled_purchase`, `test_home_uses_next_scheduled_purchase_when_none_is_in_progress` |
| RN16 | `test_home_metrics_and_history_are_scoped_to_active_group` |
| RN17 | `test_home_alerts_are_limited_and_ordered_by_criticality` |
| RN18 | `test_home_recent_history_is_limited_to_three_completed_executions` |

Execute a suíte com:

```bash
venv/bin/pytest
```

# Rastreabilidade dos fluxos do usuário

| Fluxo | Estado | Cobertura principal |
|---|---|---|
| FL-01 Primeiro acesso e onboarding | Implementado | `test_first_access_creates_default_home_and_categories`, `test_repeated_login_does_not_duplicate_default_home` |
| FL-02 Criação de template | Implementado | `test_fl02_template_is_active_and_items_are_grouped_with_notes` |
| FL-03 Geração de execução | Implementado | `test_fl03_manual_and_automatic_executions_are_available_in_agenda` |
| FL-04 Execução da compra | Implementado | `test_fl04_critical_purchase_flow_preserves_history` |
| FL-05 Compra colaborativa | Implementado | `test_fl05_collaborative_purchase_notifies_members_and_has_single_history`, `test_stale_item_version_fails_explicitly_without_overwriting` |
| FL-06 Aprendizado do template | Implementado | `test_fl06_finishing_purchase_suggests_runtime_items_without_applying_them`, `test_fl06_only_selected_suggestions_are_applied_to_template` |
| FL-07 Gestão de grupos | Implementado | `test_member_can_be_invited_to_the_group`, `test_fl07_accepted_member_can_access_shared_templates_and_executions` |
| FL-08 Agenda e histórico | Parcial | `test_fl08_completed_execution_remains_available_in_agenda_history`; histórico de preços está no [BL-0003](../docs/domain/backlog/items/BL-0003-historico-precos.md) e análise de gastos no [BL-0004](../docs/domain/backlog/items/BL-0004-analise-gastos-dashboard-financeiro.md) |
| FL-09 Operação offline | Implementado com rastreabilidade pendente | fila IndexedDB, sincronização e resolução explícita cobertas por `tests/test_offline_cache.py` e `tests/test_sync_center.py`; contratos Python legados permanecem em `xfail` e são acompanhados pelo [BL-0001](../docs/domain/backlog/items/BL-0001-operacao-offline-cobertura-rastreabilidade.md) |
| FL-10 Home operacional | Implementado | `test_home_renders_one_touch_purchase_actions_and_global_sync_indicator` e `tests/test_home_dashboard.py` |

Os contratos futuros usam `xfail(strict=True)`. Enquanto não implementados,
aparecem como `XFAIL`; quando começarem a passar, o `XPASS` falhará a suíte até
que o fluxo seja revisado. Os contratos legados de FL-09 não definem o estado
atual da implementação e devem ser reconciliados no BL-0001.

# Demandas do backlog ativo

| Item | Estado | Cobertura principal |
|---|---|---|
| [BL-0014](../docs/domain/backlog/items/BL-0014-fixar-orcamento-compra.md) Resumo de orçamento fixo | Em validação | `tests/test_sticky_budget.py`, `tests/test_agenda_and_budget_flow.py`, `tests/test_execution_totals_regression.py`, `tests/test_offline_cache.py` e `tests/test_pwa.py` |

# Backlog legado — Sprint 4 — Aprendizado contínuo dos templates

| Item legado | Estado | Cobertura TDD |
|---|---|---|
| BL-029 Detectar itens adicionados durante a execução | Implementado | `test_bl029_detects_runtime_items_only_for_template_executions` |
| BL-030 Sugerir incorporação de itens ao template | Implementado | `test_bl030_applies_only_selected_new_item_suggestions_to_future_executions` |
| BL-031 Detectar divergências recorrentes de quantidade | Implementado | `test_bl031_quantity_suggestions_require_recurrent_divergence`, `test_bl031_quantity_suggestions_are_not_generated_from_single_occurrence` |
| BL-032 Sugerir atualização de quantidades padrão | Implementado | `test_bl032_applies_quantity_suggestion_only_to_template_future_runs` |
| BL-033 Detectar alterações recorrentes em observações | Implementado | `test_bl033_detects_recurrent_notes_only_for_template_items` |
| BL-034 Sugerir atualização de observações do template | Implementado | `test_bl034_accepts_or_rejects_note_suggestions_without_representing_ignored_ones` |
| BL-075 Detectar divergências recorrentes de orçamento | Implementado | `test_bl075_budget_suggestion_uses_median_from_completed_template_executions`, `test_bl075_budget_learning_ignores_standalone_and_unfinished_executions` |
| BL-076 Sugerir atualização do orçamento do template | Implementado | `test_bl076_accepts_budget_suggestion_only_for_future_executions`, `test_bl076_rejected_budget_suggestion_is_not_represented_for_same_execution`, `test_bl076_close_flow_accepts_or_rejects_budget_suggestion` |
| RNF-S4.04 Desativar sugestões por grupo | Implementado | `test_rnf_s4_group_can_disable_template_learning_suggestions` |
