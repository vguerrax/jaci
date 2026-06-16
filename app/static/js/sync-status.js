(function () {
    'use strict';

    const status = document.getElementById('sync-status');
    if (!status) return;

    const icon = status.querySelector('i');
    const label = status.querySelector('.sync-status-label');
    const pending = status.querySelector('.sync-status-pending');
    const STATES = {
        synced: {
            label: 'Sincronizado',
            icon: 'bi bi-cloud-check-fill',
            className: 'is-synced',
        },
        syncing: {
            label: 'Sincronizando',
            icon: 'bi bi-arrow-repeat',
            className: 'is-syncing',
        },
        offline: {
            label: 'Offline',
            icon: 'bi bi-cloud-slash-fill',
            className: 'is-offline',
        },
        error: {
            label: 'Erro de sincronização',
            icon: 'bi bi-exclamation-triangle-fill',
            className: 'is-error',
        },
    };

    let activeRequests = 0;
    let currentState = null;

    function renderPending() {
        const pendingCount = Number(localStorage.getItem('jaci_pending_changes') || 0);
        pending.classList.toggle('d-none', pendingCount === 0);
        pending.textContent = pendingCount ? `${pendingCount} pendente(s)` : '';
    }

    function setState(nextState) {
        const state = navigator.onLine ? nextState : 'offline';
        const config = STATES[state] || STATES.synced;
        currentState = state;

        status.dataset.state = state;
        status.classList.remove('is-synced', 'is-syncing', 'is-offline', 'is-error');
        status.classList.add(config.className);
        icon.className = config.icon;
        label.textContent = config.label;
        renderPending();
    }

    function startSync() {
        if (!navigator.onLine) {
            setState('offline');
            return;
        }
        activeRequests += 1;
        setState('syncing');
    }

    function finishSync() {
        activeRequests = Math.max(0, activeRequests - 1);
        if (activeRequests === 0) {
            setState('synced');
        }
    }

    function failSync() {
        activeRequests = 0;
        setState('error');
    }

    function render() {
        setState(navigator.onLine ? (currentState || 'synced') : 'offline');
    }

    window.JaciSyncStatus = {
        setState: setState,
        start: startSync,
        finish: finishSync,
        error: failSync,
        render: render,
    };

    window.addEventListener('online', render);
    window.addEventListener('offline', render);
    window.addEventListener('storage', function (event) {
        if (event.key === 'jaci_pending_changes') {
            renderPending();
        }
    });

    document.body.addEventListener('htmx:beforeRequest', startSync);
    document.body.addEventListener('htmx:afterRequest', function (event) {
        if (event.detail.successful) {
            finishSync();
        } else {
            failSync();
        }
    });
    document.body.addEventListener('htmx:sendError', failSync);
    document.body.addEventListener('htmx:responseError', failSync);
    document.body.addEventListener('htmx:timeout', failSync);

    window.addEventListener('jaci:sync-start', startSync);
    window.addEventListener('jaci:sync-success', finishSync);
    window.addEventListener('jaci:sync-error', failSync);
    render();

})();
