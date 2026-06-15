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
| RN13 | Pendente: requer uma interface de fila de sincronização offline. |
| RN14 | Pendente: requer uma interface de resolução de conflitos offline. |

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
| FL-06 Aprendizado do template | Contrato TDD (`xfail`) | `test_fl06_finishing_purchase_suggests_runtime_items_without_applying_them`, `test_fl06_only_selected_suggestions_are_applied_to_template` |
| FL-07 Gestão de grupos | Implementado | `test_member_can_be_invited_to_the_group`, `test_fl07_accepted_member_can_access_shared_templates_and_executions` |
| FL-08 Agenda e histórico | Parcial | `test_fl08_completed_execution_remains_available_in_agenda_history`; histórico de preços e análise de gastos estão em `xfail` |
| FL-09 Operação offline | Contrato TDD (`xfail`) | fila local, sincronização e resolução explícita de conflitos |

Os contratos futuros usam `xfail(strict=True)`. Enquanto não implementados, aparecem
como `XFAIL`; quando começarem a passar, o `XPASS` falhará a suíte até que o fluxo
seja revisado e marcado como implementado.
