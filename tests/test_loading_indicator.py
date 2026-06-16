from pathlib import Path


def test_loading_indicator_handles_navigation_forms_and_htmx_requests():
    script = Path("app/static/js/loading-indicator.js").read_text()

    assert "SHOW_DELAY_MS = 120" in script
    assert "document.addEventListener('click'" in script
    assert "document.addEventListener('submit'" in script
    assert "!event.defaultPrevented" in script
    assert "htmx:beforeRequest" in script
    assert "htmx:afterRequest" in script
    assert "htmx:responseError" in script
    assert "document.body.classList.add('is-loading')" in script
    assert "document.body.classList.remove('is-loading')" in script


def test_loading_indicator_avoids_non_navigation_clicks():
    script = Path("app/static/js/loading-indicator.js").read_text()

    assert "link.target && link.target !== '_self'" in script
    assert "link.hasAttribute('download')" in script
    assert "startsWith('#')" in script
    assert "link.dataset.bsToggle" in script
    assert "url.origin === window.location.origin" in script


def test_loading_indicator_styles_block_repeat_taps():
    styles = Path("app/static/css/jaci-theme.css").read_text()

    assert ".page-loading" in styles
    assert "z-index: 2100" in styles
    assert "backdrop-filter" in styles
    assert ".page-loading-spinner" in styles
    assert "@keyframes jaci-spin" in styles
    assert ".is-loading" in styles
