from collections import Counter, defaultdict
from statistics import median
from types import SimpleNamespace
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.enums import ExecutionStatus
from app.models.execution import Execution, ExecutionItem
from app.models.template import Template, TemplateItem
from app.models.template_learning import TemplateLearningDismissal
from app.services.template_service import stage_item_for_template, update_template_item

MIN_RECURRENT_OCCURRENCES = 3
BUDGET_DIVERGENCE_THRESHOLD = 0.10


class SuggestionList(list):
    def by_execution_item(self, execution_item_id: int):
        for suggestion in self:
            if suggestion.get("execution_item_id") == execution_item_id:
                return SimpleNamespace(id=suggestion["suggestion_id"])
        return None


class TemplateHistorySuggestions:
    def __init__(
        self,
        quantity: list[dict] | None = None,
        notes: list[dict] | None = None,
        budget: list[dict] | None = None,
    ):
        self.quantity = quantity or []
        self.notes = notes or []
        self.budget = budget or []

    def is_empty(self) -> bool:
        return not self.quantity and not self.notes and not self.budget


def _normalize_name(value: str | None) -> str:
    return " ".join((value or "").strip().casefold().split())


def _normalize_notes(value: str | None) -> str:
    return " ".join((value or "").strip().split())


def _template_item_names(db: Session, template_id: int) -> set[str]:
    return {
        _normalize_name(name)
        for name in db.scalars(
            select(TemplateItem.name).where(TemplateItem.template_id == template_id)
        )
        if name
    }


def _suggestion_id(suggestion_type: str, entity_id: int, value: Any = None) -> str:
    if isinstance(value, float):
        value = f"{value:g}"
    value_part = "" if value is None else f":{value}"
    return f"{suggestion_type}:{entity_id}{value_part}"


def _money(value: float | int | None) -> float | None:
    if value is None:
        return None
    return round(float(value), 2)


def _dismissed_keys(db: Session, execution_id: int) -> set[tuple]:
    dismissals = db.scalars(
        select(TemplateLearningDismissal).where(
            TemplateLearningDismissal.execution_id == execution_id
        )
    ).all()
    return {
        (
            dismissal.suggestion_type,
            dismissal.execution_item_id,
            dismissal.template_item_id,
            dismissal.value,
        )
        for dismissal in dismissals
    }


def _dismissal_value_for_suggestion(suggestion: dict) -> str | None:
    if suggestion.get("suggested_budget") is not None:
        value = _money(suggestion.get("suggested_budget"))
        return None if value is None else f"{value:g}"
    value = (
        suggestion.get("suggested_notes")
        or suggestion.get("suggested_quantity")
    )
    return None if value is None else str(value)


def _dismissal_key_for_suggestion(suggestion: dict) -> tuple:
    suggestion_type = suggestion.get("type")
    execution_item_id = suggestion.get("execution_item_id")
    template_item_id = suggestion.get("template_item_id")
    if not suggestion_type and suggestion.get("suggestion_id"):
        suggestion_type, entity_id = _parse_suggestion_id(suggestion["suggestion_id"])
        if suggestion_type == "new_item":
            execution_item_id = entity_id
        elif suggestion_type != "budget":
            template_item_id = entity_id
    return (
        suggestion_type,
        execution_item_id,
        template_item_id,
        _dismissal_value_for_suggestion(suggestion),
    )


def _is_learning_enabled_for_execution(execution: Execution) -> bool:
    return bool(execution.group and execution.group.template_learning_enabled)


def _is_learning_enabled_for_template(template: Template) -> bool:
    return bool(template.group and template.group.template_learning_enabled)


def get_template_suggestions(db: Session, execution: Execution) -> SuggestionList:
    """Detecta sugestões imediatas geradas por uma execução finalizada."""
    if not execution.template_id or execution.is_standalone:
        return SuggestionList()
    if not _is_learning_enabled_for_execution(execution):
        return SuggestionList()

    existing_template_names = _template_item_names(db, execution.template_id)
    dismissed = _dismissed_keys(db, execution.id)
    items = db.scalars(
        select(ExecutionItem)
        .where(ExecutionItem.execution_id == execution.id)
        .order_by(ExecutionItem.sort_order, ExecutionItem.name)
    ).all()

    suggestions = SuggestionList()
    for item in items:
        item_name = _normalize_name(item.name)
        dismissal_key = ("new_item", item.id, None, None)
        if item.template_item_id or item_name in existing_template_names or dismissal_key in dismissed:
            continue
        suggestions.append(
            {
                "suggestion_id": _suggestion_id("new_item", item.id),
                "type": "new_item",
                "template_id": execution.template_id,
                "execution_id": execution.id,
                "execution_item_id": item.id,
                "name": item.name,
                "category_id": item.category_id,
                "planned_quantity": item.planned_quantity,
                "notes": item.notes,
                "explanation": "Item adicionado durante a compra e ausente no template.",
            }
        )
    return suggestions


def analyze_template_history(
    db: Session,
    template: Template,
    execution: Execution | None = None,
) -> TemplateHistorySuggestions:
    """Analisa histórico concluído de um template e monta sugestões recorrentes."""
    if not _is_learning_enabled_for_template(template):
        return TemplateHistorySuggestions()

    executions = db.scalars(
        select(Execution).where(
            Execution.template_id == template.id,
            Execution.status == ExecutionStatus.completed,
        )
    ).all()
    execution_ids = [execution.id for execution in executions]
    if not execution_ids:
        return TemplateHistorySuggestions()

    budget_suggestions: list[dict] = []
    budgets = [
        _money(item.budget)
        for item in executions
        if item.template_id == template.id and item.budget is not None and item.budget > 0
    ]
    if len(budgets) >= MIN_RECURRENT_OCCURRENCES:
        suggested_budget = _money(median(budgets))
        current_budget = _money(template.budget)
        if suggested_budget and suggested_budget > 0:
            should_suggest = current_budget is None
            if current_budget and current_budget > 0:
                difference = abs(suggested_budget - current_budget) / current_budget
                should_suggest = difference >= BUDGET_DIVERGENCE_THRESHOLD
            if should_suggest:
                budget_suggestions.append(
                    {
                        "type": "budget",
                        "suggestion_id": _suggestion_id("budget", template.id, suggested_budget),
                        "template_id": template.id,
                        "current_budget": current_budget,
                        "suggested_budget": suggested_budget,
                        "sample_size": len(budgets),
                        "explanation": (
                            f"Mediana de R$ {suggested_budget:.2f} "
                            f"em {len(budgets)} execuções finalizadas recentes."
                        ),
                    }
                )

    history_items = db.scalars(
        select(ExecutionItem).where(
            ExecutionItem.execution_id.in_(execution_ids),
            ExecutionItem.template_item_id.is_not(None),
        )
    ).all()
    by_template_item: dict[int, list[ExecutionItem]] = defaultdict(list)
    for item in history_items:
        by_template_item[item.template_item_id].append(item)

    quantity_suggestions: list[dict] = []
    notes_suggestions: list[dict] = []
    template_items = sorted(template.items, key=lambda item: (item.sort_order, item.name))

    for template_item in template_items:
        items = by_template_item.get(template_item.id, [])
        purchased_values = [
            item.purchased_quantity
            for item in items
            if item.is_completed and item.purchased_quantity is not None
        ]
        quantity_counts = Counter(purchased_values)
        if quantity_counts:
            suggested_quantity, sample_size = quantity_counts.most_common(1)[0]
            if (
                sample_size >= MIN_RECURRENT_OCCURRENCES
                and suggested_quantity != template_item.planned_quantity
            ):
                quantity_suggestions.append(
                    {
                        "type": "quantity",
                        "suggestion_id": _suggestion_id("quantity", template_item.id, suggested_quantity),
                        "template_item_id": template_item.id,
                        "name": template_item.name,
                        "current_quantity": template_item.planned_quantity,
                        "suggested_quantity": suggested_quantity,
                        "sample_size": sample_size,
                        "explanation": f"Comprado {suggested_quantity:g}x em {sample_size} execuções recentes.",
                    }
                )

        notes_values = [
            _normalize_notes(item.notes)
            for item in items
            if _normalize_notes(item.notes)
        ]
        notes_counts = Counter(notes_values)
        if notes_counts:
            suggested_notes, sample_size = notes_counts.most_common(1)[0]
            current_notes = _normalize_notes(template_item.notes) or None
            if sample_size >= MIN_RECURRENT_OCCURRENCES and suggested_notes != current_notes:
                notes_suggestions.append(
                    {
                        "type": "notes",
                        "suggestion_id": _suggestion_id("notes", template_item.id, suggested_notes),
                        "template_item_id": template_item.id,
                        "name": template_item.name,
                        "current_notes": current_notes,
                        "suggested_notes": suggested_notes,
                        "sample_size": sample_size,
                        "explanation": f"Observação repetida em {sample_size} execuções recentes.",
                    }
                )

    suggestions = TemplateHistorySuggestions(quantity_suggestions, notes_suggestions, budget_suggestions)
    if not execution:
        return suggestions

    dismissed = _dismissed_keys(db, execution.id)
    suggestions.quantity = [
        suggestion
        for suggestion in suggestions.quantity
        if _dismissal_key_for_suggestion(suggestion) not in dismissed
    ]
    suggestions.notes = [
        suggestion
        for suggestion in suggestions.notes
        if _dismissal_key_for_suggestion(suggestion) not in dismissed
    ]
    suggestions.budget = [
        suggestion
        for suggestion in suggestions.budget
        if _dismissal_key_for_suggestion(suggestion) not in dismissed
    ]
    return suggestions


def _parse_suggestion_id(suggestion_id: str) -> tuple[str, int]:
    suggestion_type, raw_entity_id, *_ = suggestion_id.split(":")
    return suggestion_type, int(raw_entity_id)


def _validated_new_item_suggestion(
    db: Session,
    template: Template,
    execution: Execution | None,
    execution_item_id: int | None,
) -> ExecutionItem:
    if execution is None:
        raise ValueError("A execução é obrigatória para incorporar um novo item.")
    if (
        execution.template_id != template.id
        or execution.group_id != template.group_id
        or execution.is_standalone
    ):
        raise ValueError("A execução não pertence ao template informado.")
    if execution_item_id is None:
        raise ValueError("O item sugerido não pertence à execução em fechamento.")

    execution_item = db.get(ExecutionItem, execution_item_id)
    if not execution_item or execution_item.execution_id != execution.id:
        raise ValueError("O item sugerido não pertence à execução em fechamento.")
    if execution_item.template_item_id is not None:
        raise ValueError("O item sugerido já está vinculado a um item do template.")
    return execution_item


def _incorporate_execution_item(
    db: Session,
    template: Template,
    execution_item: ExecutionItem,
    suggestion: dict,
) -> TemplateItem:
    try:
        template_item = stage_item_for_template(
            db,
            template,
            execution_item.name,
            suggestion.get("planned_quantity") or execution_item.planned_quantity,
            suggestion.get("category_id", execution_item.category_id),
            execution_item.notes,
        )
        execution_item.template_item_id = template_item.id
        db.commit()
    except Exception:
        db.rollback()
        raise

    db.refresh(template_item)
    db.refresh(execution_item)
    return template_item


def apply_template_suggestions(
    db: Session,
    template: Template,
    suggestions: list[dict],
    selected_types: set[str] | None = None,
    *,
    execution: Execution | None = None,
) -> list[TemplateItem]:
    """Aplica somente sugestões confirmadas pelo usuário ao template."""
    applied: list[TemplateItem] = []
    selected_types = selected_types or set()

    for suggestion in suggestions:
        suggestion_type = suggestion.get("type")
        if not suggestion_type and suggestion.get("suggestion_id"):
            suggestion_type, entity_id = _parse_suggestion_id(suggestion["suggestion_id"])
            suggestion = {**suggestion, "type": suggestion_type}
            if suggestion_type == "new_item":
                suggestion["execution_item_id"] = entity_id
        if selected_types and suggestion_type not in selected_types:
            continue

        if suggestion_type == "new_item":
            execution_item = _validated_new_item_suggestion(
                db,
                template,
                execution,
                suggestion.get("execution_item_id"),
            )
            item = _incorporate_execution_item(
                db,
                template,
                execution_item,
                suggestion,
            )
            applied.append(item)
        elif suggestion_type == "quantity":
            template_item = db.get(TemplateItem, suggestion.get("template_item_id"))
            if template_item and template_item.template_id == template.id:
                item = update_template_item(
                    db,
                    template_item,
                    template_item.name,
                    suggestion["suggested_quantity"],
                    template_item.category_id,
                    template_item.notes,
                )
                applied.append(item)
        elif suggestion_type == "notes":
            template_item = db.get(TemplateItem, suggestion.get("template_item_id"))
            if template_item and template_item.template_id == template.id:
                item = update_template_item(
                    db,
                    template_item,
                    template_item.name,
                    template_item.planned_quantity,
                    template_item.category_id,
                    suggestion.get("suggested_notes"),
                )
                applied.append(item)
        elif suggestion_type == "budget":
            suggested_budget = _money(suggestion.get("suggested_budget"))
            if suggestion.get("template_id") == template.id and suggested_budget is not None:
                template.budget = suggested_budget
                db.commit()

    return applied


def dismiss_template_suggestions(
    db: Session,
    execution: Execution,
    suggestions: list[dict],
) -> None:
    """Registra sugestões ignoradas para não reapresentá-las na mesma execução."""
    dismissed = _dismissed_keys(db, execution.id)
    for suggestion in suggestions:
        suggestion_type = suggestion.get("type")
        execution_item_id = suggestion.get("execution_item_id")
        template_item_id = suggestion.get("template_item_id")
        value = _dismissal_value_for_suggestion(suggestion)
        if not suggestion_type and suggestion.get("suggestion_id"):
            suggestion_type, entity_id = _parse_suggestion_id(suggestion["suggestion_id"])
            if suggestion_type == "new_item":
                execution_item_id = entity_id
            elif suggestion_type != "budget":
                template_item_id = entity_id
        key = (suggestion_type, execution_item_id, template_item_id, value)
        if key in dismissed:
            continue
        dismissal = TemplateLearningDismissal(
            execution_id=execution.id,
            suggestion_type=suggestion_type,
            execution_item_id=execution_item_id,
            template_item_id=template_item_id,
            value=value,
        )
        db.add(dismissal)
        dismissed.add(key)
    db.commit()
