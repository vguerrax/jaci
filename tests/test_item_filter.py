from pathlib import Path


SCRIPT_PATH = Path("app/static/js/item-filter.js")
TEMPLATE_DETAIL_PATH = Path("app/templates/pages/templates/detail.html")
MUTABLE_EXECUTION_PATH = Path("app/templates/pages/executions/in_progress.html")
ITEMS_FRAGMENT_PATH = Path("app/templates/pages/executions/_items_fragment.html")
COMPLETED_EXECUTION_PATH = Path("app/templates/pages/executions/completed.html")
OFFLINE_CACHE_PATH = Path("app/static/js/offline-cache.js")


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_shared_item_filter_normalizes_and_matches_names_locally():
    script = read(SCRIPT_PATH)

    assert ".normalize('NFD')" in script
    assert "[\\u0300-\\u036f]" in script
    assert ".toLocaleLowerCase('pt-BR')" in script
    assert ".trim()" in script
    assert ".includes(query)" in script
    assert "fetch(" not in script
    assert "localStorage" not in script
    assert "indexedDB" not in script


def test_shared_item_filter_controls_rows_groups_counts_and_empty_state():
    script = read(SCRIPT_PATH)

    assert "[data-item-filter-root]" in script
    assert "[data-item-filter-input]" in script
    assert "[data-item-filter-row]" in script
    assert "[data-item-filter-group]" in script
    assert "[data-item-filter-count]" in script
    assert "[data-item-filter-empty]" in script
    assert "row.hidden" in script
    assert "group.hidden" in script
    assert "empty.hidden" in script
    assert "data-item-filter-original-count" in script


def test_shared_item_filter_preserves_query_across_dynamic_fragment_updates():
    script = read(SCRIPT_PATH)
    page = read(MUTABLE_EXECUTION_PATH)
    offline_cache = read(OFFLINE_CACHE_PATH)

    assert "MutationObserver" in script
    assert "childList: true" in script
    assert "subtree: true" in script
    assert "htmx:configRequest" in script
    assert "X-Collapse-State" in script
    assert "data-item-filter-forced-expanded" in script
    assert 'id="items-container"' in page
    assert "data-item-filter-root" in page
    assert '/static/js/item-filter.js' in page
    assert "function collapseAll()" not in page
    assert "data-item-filter-forced-expanded" in offline_cache
    assert "row.dataset.itemFilterName = operation.name" in offline_cache
    assert "row.dataset.itemFilterCompleted" in offline_cache
    assert "row.dataset.itemFilterTotalPrice" in offline_cache


def test_template_detail_exposes_accessible_filter_contract():
    page = read(TEMPLATE_DETAIL_PATH)

    assert "data-item-filter-root" in page
    assert 'type="search"' in page
    assert 'aria-label="Buscar itens por nome"' in page
    assert "data-item-filter-input" in page
    assert "data-item-filter-clear" in page
    assert "data-item-filter-empty" in page
    assert "data-item-filter-group" in page
    assert "data-item-filter-row" in page
    assert "data-item-filter-name" in page
    assert "data-item-filter-count" in page
    assert '/static/js/item-filter.js' in page


def test_mutable_execution_exposes_filter_and_visible_financial_metadata():
    fragment = read(ITEMS_FRAGMENT_PATH)

    assert 'type="search"' in fragment
    assert "data-item-filter-collapse-all" in fragment
    assert "data-item-filter-group" in fragment
    assert "data-item-filter-collapse" in fragment
    assert "data-item-filter-row" in fragment
    assert "data-item-filter-name" in fragment
    assert "data-item-filter-completed" in fragment
    assert "data-item-filter-total-price" in fragment
    assert 'data-item-filter-count-mode="execution"' in fragment
    assert "data-item-filter-global-summary" in fragment


def test_completed_execution_is_searchable_collapsible_and_read_only():
    page = read(COMPLETED_EXECUTION_PATH)

    assert 'type="search"' in page
    assert "data-item-filter-root" in page
    assert "data-item-filter-collapse-all" in page
    assert "data-item-filter-group" in page
    assert "data-item-filter-collapse" in page
    assert "data-item-filter-row" in page
    assert "data-item-filter-name" in page
    assert "data-item-filter-count" in page
    assert 'data-item-filter-count-mode="completed"' in page
    assert 'data-item-filter-count-mode="pending"' in page
    assert "Não comprados" in page
    assert "Resumo da Compra" in page
    assert "data-item-filter-global-summary" in page
    assert '/static/js/item-filter.js' in page
    assert "hx-post=" not in page
