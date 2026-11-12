const CACHE_PREFIX = 'jaci-';
const CACHE_VERSION = 'v34';
const SHELL_CACHE = `${CACHE_PREFIX}shell-${CACHE_VERSION}`;
const STATIC_CACHE = `${CACHE_PREFIX}static-${CACHE_VERSION}`;
const PAGE_CACHE = `${CACHE_PREFIX}pages-${CACHE_VERSION}`;
const API_CACHE = `${CACHE_PREFIX}api-${CACHE_VERSION}`;
const SESSION_STATE_CACHE = `${CACHE_PREFIX}session-state`;
const OWNER_PAGE_PREFIX = `${PAGE_CACHE}-owner-`;
const OWNER_MARKER = '/__jaci_offline_owner';
let lastNavigation = 0;
let navigationUpdate = Promise.resolve();
const GUARD_MARKER = '/__jaci_session_guard';
const ACTIVE_CACHES = [SHELL_CACHE, STATIC_CACHE, PAGE_CACHE, API_CACHE, SESSION_STATE_CACHE];
const OFFLINE_PAGE = '/static/offline.html';
const SHELL_ASSETS = [
    '/manifest.webmanifest',
    OFFLINE_PAGE,
    '/static/css/jaci-theme.css',
    '/static/js/jaci-confirm.js',
    '/static/js/execution-budget.js',
    '/static/js/execution-sync.js',
    '/static/js/item-add-modal.js',
    '/static/js/item-filter.js',
    '/static/js/loading-indicator.js',
    '/static/js/offline-cache.js',
    '/static/js/pwa-install.js',
    '/static/js/sync-status.js',
    '/static/js/session-client.js',
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
                                && !ACTIVE_CACHES.includes(key)
                                && !key.startsWith(OWNER_PAGE_PREFIX);
                        })
                        .map(function (key) {
                            return caches.delete(key);
                        })
                );
            })
            .then(purgeSensitiveAuthCaches)
            .then(function () {
                return self.clients.claim();
            })
    );
});

self.addEventListener('fetch', function (event) {
    if (isSensitiveAuthRequest(event.request)) return;
    if (event.request.method !== 'GET') {
        const url = new URL(event.request.url);
        if (event.request.mode === 'navigate' && url.origin === self.location.origin
            && ['/auth/password-login', '/auth/register', '/auth/logout'].includes(url.pathname)) {
            event.respondWith(networkFirstPage(event.request));
        }
        return;
    }

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

function isSensitiveAuthRequest(request) {
    const url = new URL(request.url);
    const path = url.pathname.replace(/\/+$/, '');
    return url.origin === self.location.origin && [
        '/reset-password', '/auth/reset-password',
        '/auth/forgot-password', '/auth/profile/password',
    ].includes(path);
}

async function purgeSensitiveAuthCaches() {
    for (const name of await caches.keys()) {
        const cache = await caches.open(name);
        for (const request of await cache.keys()) {
            if (isSensitiveAuthRequest(request)) await cache.delete(request);
        }
    }
}

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

async function guardObserved(response) {
    if (response.headers.get('X-Jaci-Session-Guard') !== '1') return false;
    const state = await caches.open(SESSION_STATE_CACHE);
    await state.put(GUARD_MARKER, new Response('1'));
    return true;
}

async function legacyCache(name) {
    const state = await caches.open(SESSION_STATE_CACHE);
    return await state.match(GUARD_MARKER) ? null : caches.open(name);
}

function updateNavigation(sequence, owner) {
    navigationUpdate = navigationUpdate.catch(() => {}).then(async () => {
        if (sequence !== lastNavigation) return;
        const state = await caches.open(SESSION_STATE_CACHE);
        if (owner) {
            await state.put(OWNER_MARKER, new Response(owner));
        } else {
            await state.delete(OWNER_MARKER);
        }
    });
    return navigationUpdate;
}

async function cacheOwnerPage(request, response, owner) {
    // O HTML offline pode mostrar a interface, mas só uma página nova recebe CSRF.
    const html = (await response.clone().text())
        .replace(/<meta name="jaci-csrf" content="[^"]*">/g, '<meta name="jaci-offline-page" content="1">')
        .replace(/<input type="hidden" name="_csrf" value="[^"]*">/g, '');
    const cache = await caches.open(OWNER_PAGE_PREFIX + owner);
    await cache.put(request, new Response(html, {
        headers: { 'Content-Type': 'text/html; charset=utf-8' },
    }));
}

async function networkFirstPage(request) {
    const url = new URL(request.url);
    const navigation = request.mode === 'navigate' && url.origin === self.location.origin;
    const sequence = navigation ? ++lastNavigation : null;
    const authPath = url.pathname.startsWith('/auth/');
    let response;
    try {
        response = await fetch(request);
    } catch (error) {
        const cache = await legacyCache(PAGE_CACHE);
        if (navigation && !cache && !authPath && request.method === 'GET') {
            await navigationUpdate.catch(() => {});
            const state = await caches.open(SESSION_STATE_CACHE);
            const owner = await (await state.match(OWNER_MARKER))?.text();
            if (owner) {
                const ownerCache = await caches.open(OWNER_PAGE_PREFIX + owner);
                const page = await ownerCache.match(request);
                if (page) return page;
            }
        }
        return (await cache?.match(request)) || caches.match(OFFLINE_PAGE);
    }

    try {
        const guarded = await guardObserved(response);
        if (guarded && navigation) {
            const owner = response.headers.get('X-Jaci-Offline-Owner') || '';
            await updateNavigation(sequence, owner);
            if (owner && response.ok && !response.redirected && !authPath && request.method === 'GET'
                && response.headers.get('Content-Type')?.includes('text/html')) {
                await cacheOwnerPage(request, response, owner);
            }
        } else if (!guarded && response.ok && !authPath && request.method === 'GET') {
            const cache = await legacyCache(PAGE_CACHE);
            if (cache) await cache.put(request, response.clone());
        }
    } catch (error) {
        // Falha de armazenamento local não impede a resposta de rede.
    }
    return response;
}

async function networkFirstApi(request) {
    try {
        const response = await fetch(request);
        const guarded = await guardObserved(response);
        if (response.ok && !guarded) {
            const cache = await legacyCache(API_CACHE);
            if (cache) await cache.put(request, response.clone());
        }
        return response;
    } catch (error) {
        const cache = await legacyCache(API_CACHE);
        return (await cache?.match(request)) || new Response(
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
