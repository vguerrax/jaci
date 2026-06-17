import asyncio
import json
import struct
from pathlib import Path

from app.main import service_worker, web_app_manifest


STATIC = Path("app/static")


def png_dimensions(path: Path) -> tuple[int, int]:
    with path.open("rb") as image:
        signature = image.read(24)
    assert signature[:8] == b"\x89PNG\r\n\x1a\n"
    return struct.unpack(">II", signature[16:24])


def test_manifest_makes_jaci_installable_in_standalone_mode():
    manifest = json.loads((STATIC / "manifest.webmanifest").read_text())

    assert manifest["name"] == "Jaci - Compras Colaborativas"
    assert manifest["short_name"] == "Jaci"
    assert manifest["start_url"] == "/"
    assert manifest["scope"] == "/"
    assert manifest["display"] == "standalone"
    assert manifest["theme_color"] == "#2A4B4A"
    assert {icon["sizes"] for icon in manifest["icons"]} == {"192x192", "512x512"}
    assert all("maskable" in icon["purpose"] for icon in manifest["icons"])


def test_pwa_icons_have_required_android_and_ios_dimensions():
    assert png_dimensions(STATIC / "img/icon-192.png") == (192, 192)
    assert png_dimensions(STATIC / "img/icon-512.png") == (512, 512)
    assert png_dimensions(STATIC / "img/apple-touch-icon.png") == (180, 180)


def test_base_template_declares_manifest_ios_support_and_install_action():
    base = Path("app/templates/base.html").read_text()

    assert 'rel="manifest" href="/manifest.webmanifest"' in base
    assert 'name="theme-color"' in base
    assert 'name="apple-mobile-web-app-capable" content="yes"' in base
    assert 'rel="apple-touch-icon"' in base
    assert "data-pwa-install" in base
    assert "/static/js/pwa-install.js" in base


def test_base_template_declares_global_loading_indicator():
    base = Path("app/templates/base.html").read_text()

    assert 'id="page-loading"' in base
    assert 'role="status"' in base
    assert 'aria-live="polite"' in base
    assert "Carregando..." in base
    assert "/static/js/loading-indicator.js" in base


def test_service_worker_caches_shell_and_falls_back_offline():
    worker = (STATIC / "js/service-worker.js").read_text()

    assert "const CACHE_VERSION = 'v22'" in worker
    assert "SHELL_CACHE" in worker
    assert "STATIC_CACHE" in worker
    assert "PAGE_CACHE" in worker
    assert "API_CACHE" in worker
    assert "ACTIVE_CACHES" in worker
    assert "self.skipWaiting()" in worker
    assert "self.clients.claim()" in worker
    assert "event.request.method !== 'GET'" in worker
    assert "networkFirstPage" in worker
    assert "networkFirstApi" in worker
    assert "cacheFirstShell" in worker
    assert "staleWhileRevalidate" in worker
    assert "'/static/offline.html'" in worker
    assert "'/manifest.webmanifest'" in worker
    assert "'/static/js/loading-indicator.js'" in worker
    assert "'/static/js/offline-cache.js'" in worker


def test_service_worker_implements_bl004_cache_routing():
    worker = (STATIC / "js/service-worker.js").read_text()

    assert "isApiRequest(event.request)" in worker
    assert "event.respondWith(networkFirstApi(event.request))" in worker
    assert "event.request.mode === 'navigate'" in worker
    assert "event.respondWith(networkFirstPage(event.request))" in worker
    assert "isShellAsset(event.request)" in worker
    assert "event.respondWith(cacheFirstShell(event.request))" in worker
    assert "isStaticAsset(event.request)" in worker
    assert "event.respondWith(staleWhileRevalidate(event.request))" in worker
    assert "url.pathname.startsWith('/api/')" in worker
    assert "accept')?.includes('application/json')" in worker


def test_service_worker_invalidates_old_versioned_caches():
    worker = (STATIC / "js/service-worker.js").read_text()

    assert "key.startsWith(CACHE_PREFIX)" in worker
    assert "!ACTIVE_CACHES.includes(key)" in worker
    assert "return caches.delete(key)" in worker


def test_pwa_root_assets_are_served_with_expected_media_types():
    manifest_response = asyncio.run(web_app_manifest())
    worker_response = asyncio.run(service_worker())

    assert manifest_response.media_type == "application/manifest+json"
    assert worker_response.media_type == "application/javascript"
    assert worker_response.headers["service-worker-allowed"] == "/"
