const CACHE_PREFIX = 'jaci-';
const CACHE_VERSION = 'v20';
const SHELL_CACHE = `${CACHE_PREFIX}shell-${CACHE_VERSION}`;
const STATIC_CACHE = `${CACHE_PREFIX}static-${CACHE_VERSION}`;
const PAGE_CACHE = `${CACHE_PREFIX}pages-${CACHE_VERSION}`;
const API_CACHE = `${CACHE_PREFIX}api-${CACHE_VERSION}`;
const ACTIVE_CACHES = [SHELL_CACHE, STATIC_CACHE, PAGE_CACHE, API_CACHE];
const OFFLINE_PAGE = '/static/offline.html';
const SHELL_ASSETS = [
    '/manifest.webmanifest',
    OFFLINE_PAGE,
    '/static/css/jaci-theme.css',
    '/static/js/jaci-confirm.js',
    '/static/js/execution-sync.js',
    '/static/js/loading-indicator.js',
    '/static/js/offline-cache.js',
    '/static/js/pwa-install.js',
    '/static/js/sync-status.js',
    '/static/img/jaci-2.png',
    '/static/img/icon-192.png',
    '/static/img/icon-512.png',
    '/static/img/apple-touch-icon.png',
];

self.addEventListener('install', function (event) {
    event.waitUntil(
        caches.open(SHELL_CACHE)
            .then(function (cache) {
                return cache.addAll(SHELL_ASSETS);
            })
            .then(function () {
                return self.skipWaiting();
            })
    );
});

self.addEventListener('activate', function (event) {
    event.waitUntil(
        caches.keys()
            .then(function (keys) {
                return Promise.all(
                    keys
                        .filter(function (key) {
                            return key.startsWith(CACHE_PREFIX)
                                && !ACTIVE_CACHES.includes(key);
                        })
                        .map(function (key) {
                            return caches.delete(key);
                        })
                );
            })
            .then(function () {
                return self.clients.claim();
            })
    );
});

self.addEventListener('fetch', function (event) {
    if (event.request.method !== 'GET') return;

    if (isApiRequest(event.request)) {
        event.respondWith(networkFirstApi(event.request));
        return;
    }

    if (event.request.mode === 'navigate') {
        event.respondWith(networkFirstPage(event.request));
        return;
    }

    if (isShellAsset(event.request)) {
        event.respondWith(cacheFirstShell(event.request));
        return;
    }

    if (isStaticAsset(event.request)) {
        event.respondWith(staleWhileRevalidate(event.request));
        return;
    }

    event.respondWith(networkFirstPage(event.request));
});

function isApiRequest(request) {
    const url = new URL(request.url);
    return url.origin === self.location.origin
        && (
            url.pathname.startsWith('/api/')
            || request.headers.get('accept')?.includes('application/json')
        );
}

function isShellAsset(request) {
    const url = new URL(request.url);
    return url.origin === self.location.origin
        && SHELL_ASSETS.includes(url.pathname);
}

function isStaticAsset(request) {
    const url = new URL(request.url);
    return url.origin === self.location.origin
        && (
            url.pathname.startsWith('/static/')
            || url.pathname === '/manifest.webmanifest'
            || url.pathname === '/service-worker.js'
        );
}

async function networkFirstPage(request) {
    try {
        const response = await fetch(request);
        if (response.ok) {
            const cache = await caches.open(PAGE_CACHE);
            await cache.put(request, response.clone());
        }
        return response;
    } catch (error) {
        return (await caches.match(request)) || caches.match(OFFLINE_PAGE);
    }
}

async function networkFirstApi(request) {
    try {
        const response = await fetch(request);
        if (response.ok) {
            const cache = await caches.open(API_CACHE);
            await cache.put(request, response.clone());
        }
        return response;
    } catch (error) {
        return (await caches.match(request)) || new Response(
            JSON.stringify({ error: 'offline', detail: 'Dados indisponíveis offline.' }),
            {
                status: 503,
                headers: { 'Content-Type': 'application/json' },
            }
        );
    }
}

async function cacheFirstShell(request) {
    const cached = await caches.match(request);
    if (cached) return cached;

    const response = await fetch(request);
    if (response.ok || response.type === 'opaque') {
        const cache = await caches.open(SHELL_CACHE);
        await cache.put(request, response.clone());
    }
    return response;
}

async function staleWhileRevalidate(request) {
    const cache = await caches.open(STATIC_CACHE);
    const cached = await cache.match(request);
    const updated = fetch(request)
        .then(function (response) {
            if (response.ok || response.type === 'opaque') {
                cache.put(request, response.clone());
            }
            return response;
        })
        .catch(function () {
            return cached;
        });

    return cached || updated;
}
