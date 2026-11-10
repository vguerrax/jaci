/* Observe as respostas da aplicação sem gerar tráfego de sessão. */
(function () {
    'use strict';
    const meta = name => document.querySelector(`meta[name="${name}"]`)?.content || '';
    if (meta('jaci-session-guard') !== '1') return;

    const owner = meta('jaci-offline-owner');
    let csrf = meta('jaci-csrf');
    const activeOwnerKey = 'jaci-offline-active-owner';
    const ownerCookie = () => document.cookie.split('; ')
        .find(cookie => cookie.startsWith('jaci_offline_owner='))?.split('=')[1];
    if (meta('jaci-offline-page') !== '1') {
        if (owner && ownerCookie() === owner) {
            localStorage.setItem(activeOwnerKey, owner);
        } else if (!owner && !ownerCookie()) {
            localStorage.removeItem(activeOwnerKey);
        }
    } else if (localStorage.getItem(activeOwnerKey) !== owner || (ownerCookie() && ownerCookie() !== owner)) {
        document.documentElement.hidden = true;
        location.replace('/static/offline.html');
        return;
    }

    let paused = false;
    function requireLogin(target) {
        if (paused || !owner) return;
        paused = true;
        const url = new URL(target || '/auth/login?expired=1', location.origin);
        const link = document.getElementById('session-login-required');
        if (link) {
            link.href = url.origin === location.origin && url.pathname === '/auth/login'
                ? url.href : '/auth/login';
            link.hidden = false;
        }
        window.dispatchEvent(new Event('jaci:session-required'));
    }

    window.JaciSession = {
        owner,
        ownsCache: () => Boolean(owner && localStorage.getItem(activeOwnerKey) === owner
            && (!ownerCookie() || ownerCookie() === owner)),
        canMutate: () => Boolean(csrf),
        canSync: () => !paused && window.JaciSession.ownsCache(),
        requireLogin,
    };

    window.addEventListener('storage', event => {
        if (event.key === activeOwnerKey && event.newValue !== owner) {
            requireLogin();
            window.JaciExecutionSync?.disconnect();
        }
    });

    const originalFetch = window.fetch.bind(window);
    window.fetch = async function (resource, options) {
        const url = new URL(resource instanceof Request ? resource.url : resource, location.href);
        if (url.origin !== location.origin) return originalFetch(resource, options);

        const method = (options?.method || (resource instanceof Request && resource.method) || 'GET').toUpperCase();
        const headers = new Headers(options?.headers ?? (resource instanceof Request ? resource.headers : undefined));
        if (owner) headers.set('X-Jaci-Offline-Owner', owner);
        if (csrf && !['GET', 'HEAD', 'OPTIONS'].includes(method)) headers.set('X-CSRF-Token', csrf);
        const response = await originalFetch(resource, { ...options, headers });
        if (response.ok && url.pathname === '/api/offline/snapshot') {
            csrf = response.headers.get('X-Jaci-CSRF') || csrf;
        }
        if (response.status === 401 && response.headers.has('X-Session-Login')) {
            requireLogin(response.headers.get('X-Session-Login'));
        }
        if (response.status === 403) {
            const result = await response.clone().json().catch(() => null);
            if (result?.detail?.code === 'offline_account_changed') requireLogin();
        }
        return response;
    };

    document.addEventListener('htmx:configRequest', event => {
        if (owner) event.detail.headers['X-Jaci-Offline-Owner'] = owner;
        if (csrf) event.detail.headers['X-CSRF-Token'] = csrf;
    });
    document.addEventListener('htmx:beforeSwap', event => {
        const target = event.detail.xhr.getResponseHeader('X-Session-Login');
        if (event.detail.xhr.status === 403 && event.detail.xhr.getResponseHeader('X-Jaci-Account-Changed')) {
            requireLogin();
        }
        if (event.detail.xhr.status === 401 && target) {
            event.detail.shouldSwap = false;
            requireLogin(target);
        }
    });
})();
