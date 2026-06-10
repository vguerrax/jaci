import logging
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import select, func

from app.models.user import User
from app.models.group import Group, group_members
from app.models.category import Category
from app.models.template import TemplateItem
from app.models.execution import ExecutionItem

logger = logging.getLogger("jaci.categories")


def get_categories_by_group(db: Session, group_id: int) -> list[Category]:
    """Retorna todas as categorias de um grupo na ordem configurada."""
    return (
        db.execute(
            select(Category)
            .where(Category.group_id == group_id)
            .order_by(Category.sort_order, Category.name)
        )
        .scalars()
        .all()
    )


def get_category_by_id(
    db: Session, category_id: int, user: User
) -> Optional[Category]:
    """
    Retorna uma categoria se pertencer a um grupo do usuário.
    """
    return db.scalar(
        select(Category)
        .join(Group, Category.group_id == Group.id)
        .join(group_members, Group.id == group_members.c.group_id)
        .where(
            Category.id == category_id,
            group_members.c.user_id == user.id,
        )
    )


def create_category(
    db: Session, group: Group, name: str, color: Optional[str] = None
) -> Category:
    """Cria uma nova categoria no grupo."""
    max_order = db.scalar(
        select(func.max(Category.sort_order)).where(Category.group_id == group.id)
    )
    category = Category(
        name=name.strip(),
        color=color,
        group_id=group.id,
        sort_order=(max_order if max_order is not None else -1) + 1,
    )
    db.add(category)
    db.commit()
    db.refresh(category)
    logger.info(f"Categoria '{category.name}' criada no grupo '{group.name}'")
    return category


def move_category(db: Session, category: Category, direction: str) -> bool:
    """Move uma categoria uma posição para cima ou para baixo."""
    categories = get_categories_by_group(db, category.group_id)
    current_index = next(
        (index for index, item in enumerate(categories) if item.id == category.id),
        None,
    )
    if current_index is None:
        return False

    target_index = current_index + (-1 if direction == "up" else 1)
    if direction not in {"up", "down"} or target_index < 0 or target_index >= len(categories):
        return False

    categories[current_index], categories[target_index] = (
        categories[target_index],
        categories[current_index],
    )
    for sort_order, item in enumerate(categories):
        item.sort_order = sort_order

    db.commit()
    return True


def set_uncategorized_position(db: Session, group: Group, position: str) -> bool:
    """Define se o grupo sem categoria aparece primeiro ou por último."""
    if position not in {"first", "last"}:
        return False

    group.uncategorized_first = position == "first"
    db.commit()
    db.refresh(group)
    return True


def update_category(
    db: Session, category: Category, name: str, color: Optional[str] = None
) -> Category:
    """Atualiza nome e/ou cor da categoria."""
    category.name = name.strip()
    if color is not None:
        category.color = color
    db.commit()
    db.refresh(category)
    logger.info(f"Categoria '{category.name}' atualizada")
    return category


def count_items_using_category(db: Session, category_id: int) -> dict:
    """
    Conta quantos itens (template e execução) usam esta categoria.
    Retorna dict com 'template_items' e 'execution_items'.
    """
    template_count = db.scalar(
        select(func.count(TemplateItem.id)).where(
            TemplateItem.category_id == category_id
        )
    )
    execution_count = db.scalar(
        select(func.count(ExecutionItem.id)).where(
            ExecutionItem.category_id == category_id
        )
    )
    return {
        "template_items": template_count or 0,
        "execution_items": execution_count or 0,
        "total": (template_count or 0) + (execution_count or 0),
    }


def delete_category(db: Session, category: Category) -> dict:
    """
    Exclui a categoria e define category_id = null nos itens afetados.
    Retorna dict com contagem de itens afetados.
    """
    counts = count_items_using_category(db, category.id)

    # Desvincula itens do template
    db.execute(
        select(TemplateItem).where(TemplateItem.category_id == category.id)
    )
    
    db.query(TemplateItem).filter(TemplateItem.category_id == category.id).update({"category_id": None})

    # Desvincula itens de execução
    db.query(ExecutionItem).filter(ExecutionItem.category_id == category.id).update({"category_id": None})

    # Exclui a categoria
    name = category.name
    db.delete(category)
    db.commit()

    logger.info(
        f"Categoria '{name}' excluída. "
        f"{counts['total']} itens desvinculados."
    )
    return counts
