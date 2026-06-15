(function () {
    'use strict';

    const status = document.getElementById('sync-status');
    if (!status) return;

    const icon = status.querySelector('i');
    const label = status.querySelector('.sync-status-label');
    const pending = status.querySelector('.sync-status-pending');

    function render() {
        const online = navigator.onLine;
        status.classList.toggle('is-offline', !online);
        icon.className = online ? 'bi bi-cloud-check-fill' : 'bi bi-cloud-slash-fill';
        label.textContent = online ? 'Sincronizado' : 'Modo offline';

        const pendingCount = Number(localStorage.getItem('jaci_pending_changes') || 0);
        pending.classList.toggle('d-none', pendingCount === 0);
        pending.textContent = pendingCount ? `${pendingCount} pendente(s)` : '';
    }

    window.addEventListener('online', render);
    window.addEventListener('offline', render);
    render();

    if ('serviceWorker' in navigator) {
        navigator.serviceWorker.register('/service-worker.js', { scope: '/' }).catch(function () {
            // O indicador continua funcional mesmo quando o cache offline falha.
        });
    }
})();
