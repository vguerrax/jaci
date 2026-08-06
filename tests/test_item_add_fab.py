import re
from pathlib import Path


TEMPLATE_DETAIL = Path("app/templates/pages/templates/detail.html")
TEMPLATE_ITEMS_FRAGMENT = Path(
    "app/templates/pages/templates/_items_fragment.html"
)
EXECUTION_DETAIL = Path("app/templates/pages/executions/in_progress.html")
COMPLETED_EXECUTION = Path("app/templates/pages/executions/completed.html")
MODAL_SCRIPT = Path("app/static/js/item-add-modal.js")
THEME = Path("app/static/css/jaci-theme.css")


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def z_index_for(theme: str, selector: str) -> int:
    block = re.search(
        rf"{re.escape(selector)}\s*\{{(?P<body>.*?)\}}",
        theme,
        re.DOTALL,
    )
    assert block, f"Seletor CSS ausente: {selector}"
    value = re.search(r"z-index:\s*(?P<value>\d+)", block.group("body"))
    assert value, f"z-index ausente em: {selector}"
    return int(value.group("value"))


def test_template_exposes_one_accessible_fab_and_one_canonical_modal_form():
    page = read(TEMPLATE_DETAIL)

    assert page.count("data-item-add-trigger") == 1
    assert page.count("data-item-add-modal") == 1
    assert page.count("data-item-add-form") == 1
    assert page.count('action="/templates/{{ template.id }}/items/add"') == 1
    assert 'aria-label="Adicionar item"' in page
    assert 'aria-haspopup="dialog"' in page
    assert 'aria-labelledby="templateAddItemModalLabel"' in page
    assert 'id="templateAddItemName"' in page
    assert 'for="templateAddItemName"' in page
    assert 'data-item-add-initial-focus' in page
    assert 'data-item-add-feedback' in page


def test_template_addition_targets_a_reusable_items_fragment_with_fallback_post():
    page = read(TEMPLATE_DETAIL)

    assert TEMPLATE_ITEMS_FRAGMENT.exists()
    assert 'id="template-items-container"' in page
    assert 'pages/templates/_items_fragment.html' in page
    assert 'method="post"' in page
    assert 'hx-post="/templates/{{ template.id }}/items/add"' in page
    assert 'hx-target="#template-items-container"' in page
    assert 'hx-swap="innerHTML"' in page


def test_mutable_execution_exposes_one_modal_form_and_preserves_offline_contract():
    page = read(EXECUTION_DETAIL)

    assert "{% if execution.status in ['scheduled', 'in_progress'] %}" in page
    assert page.count("data-item-add-trigger") == 1
    assert page.count("data-item-add-modal") == 1
    assert page.count("data-item-add-form") == 1
    assert page.count('action="/executions/{{ execution.id }}/items/add"') == 1
    assert page.count("data-offline-add-item") == 1
    assert 'data-execution-id="{{ execution.id }}"' in page
    assert 'data-execution-status="{{ execution.status }}"' in page
    assert 'data-item-add-sidebar-url="/executions/{{ execution.id }}/sidebar-fragment"' in page
    assert 'name="unit_price"' in page
    assert 'min="0.01"' in page
    assert "hx-on::after-request" not in page
    assert "data-item-add-trigger" not in read(COMPLETED_EXECUTION)


def test_modal_pages_keep_the_single_form_available_without_javascript():
    for path in (TEMPLATE_DETAIL, EXECUTION_DETAIL):
        page = read(path)
        assert "<noscript>" in page
        assert "data-item-add-noscript" in page
        assert ".item-add-fab" in page
        assert ".item-add-modal" in page


def test_local_modal_controller_preserves_scroll_focus_and_keyboard_behavior():
    script = read(MODAL_SCRIPT)

    assert "const TRIGGER_SELECTOR = '[data-item-add-trigger]'" in script
    assert "const MODAL_SELECTOR = '[data-item-add-modal]'" in script
    assert "const FORM_SELECTOR = '[data-item-add-form]'" in script
    assert "window.scrollY" in script
    assert "window.scrollTo(0, state.scrollY)" in script
    assert "window.JaciModal.show(modal)" in script
    assert "window.JaciModal.hide(modal)" in script
    assert "event.key === 'Escape'" in script
    assert "event.key !== 'Tab'" in script
    assert "data-item-add-initial-focus" in script
    assert "state.trigger.focus()" in script


def test_modal_controller_closes_only_after_online_or_offline_success():
    script = read(MODAL_SCRIPT)

    assert "htmx:afterRequest" in script
    assert "event.detail.successful" in script
    assert "refreshSidebarAfterOnlineSuccess(form)" in script
    assert "form.dataset.itemAddSidebarUrl" in script
    assert "window.htmx.ajax('GET', sidebarUrl" in script
    assert "jaci:item-add-success" in script
    assert "form.reset()" in script
    assert "hideModal(modal" in script
    assert "htmx:sendError" in script
    assert "htmx:responseError" in script
    assert "showFeedback" in script
    assert ".trim()" in script


def test_fab_and_modal_styles_respect_safe_areas_and_local_fallback():
    theme = read(THEME)

    assert ".page-with-item-add-fab" in theme
    assert ".item-add-fab" in theme
    assert "safe-area-inset-bottom" in theme
    assert "safe-area-inset-right" in theme
    assert ".item-add-fab:focus-visible" in theme
    assert ".item-add-modal" in theme
    assert "[data-jaci-modal-backdrop]" in theme
    assert "@media (max-width: 767.98px)" in theme


def test_managed_item_modals_stay_above_backdrop_and_page_actions():
    theme = read(THEME)

    modal_z_index = z_index_for(theme, ".modal")
    item_add_modal_z_index = z_index_for(theme, ".item-add-modal")
    backdrop_z_index = z_index_for(theme, "[data-jaci-modal-backdrop]")
    item_add_fab_z_index = z_index_for(theme, ".item-add-fab")

    assert modal_z_index > backdrop_z_index > item_add_fab_z_index
    assert item_add_modal_z_index > backdrop_z_index


def test_both_modal_pages_load_the_local_cached_controller():
    for path in (TEMPLATE_DETAIL, EXECUTION_DETAIL):
        page = read(path)
        assert '/static/js/item-add-modal.js' in page
