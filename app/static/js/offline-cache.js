(function () {
    'use strict';

    const DB_NAME = 'jaci-offline-cache';
    const DB_VERSION = 2;
    const SNAPSHOT_URL = '/api/offline/snapshot';
    const START_EXECUTION_SYNC_URL = '/api/offline/operations/start-execution';
    const PENDING_CHANGES_KEY = 'jaci_pending_changes';
    const STORE_NAMES = [
        'groups',
        'categories',
        'templates',
        'template_items',
        'executions',
        'execution_items',
        'pending_operations',
        'metadata',
    ];

    const panel = document.getElementById('offline-cache-panel');
    const summary = document.getElementById('offline-cache-summary');

    if (!('indexedDB' in window)) return;

    function openDatabase() {
        return new Promise(function (resolve, reject) {
            const request = indexedDB.open(DB_NAME, DB_VERSION);

            request.onupgradeneeded = function () {
                const db = request.result;
                STORE_NAMES.forEach(function (name) {
                    if (!db.objectStoreNames.contains(name)) {
                        db.createObjectStore(name, { keyPath: 'id' });
                    }
                });
            };
            request.onsuccess = function () { resolve(request.result); };
            request.onerror = function () { reject(request.error); };
        });
    }

    function writeStore(db, name, records) {
        return new Promise(function (resolve, reject) {
            const transaction = db.transaction(name, 'readwrite');
            const store = transaction.objectStore(name);
            store.clear();
            records.forEach(function (record) { store.put(record); });
            transaction.oncomplete = resolve;
            transaction.onerror = function () { reject(transaction.error); };
        });
    }

    function getRecord(db, name, id) {
        return new Promise(function (resolve, reject) {
            const transaction = db.transaction(name, 'readonly');
            const request = transaction.objectStore(name).get(id);
            request.onsuccess = function () { resolve(request.result); };
            request.onerror = function () { reject(request.error); };
        });
    }

    function putRecord(db, name, record) {
        return new Promise(function (resolve, reject) {
            const transaction = db.transaction(name, 'readwrite');
            transaction.objectStore(name).put(record);
            transaction.oncomplete = resolve;
            transaction.onerror = function () { reject(transaction.error); };
        });
    }

    function deleteRecord(db, name, id) {
        return new Promise(function (resolve, reject) {
            const transaction = db.transaction(name, 'readwrite');
            transaction.objectStore(name).delete(id);
            transaction.oncomplete = resolve;
            transaction.onerror = function () { reject(transaction.error); };
        });
    }

    async function saveSnapshot(snapshot) {
        const db = await openDatabase();
        await Promise.all([
            writeStore(db, 'groups', snapshot.groups || []),
            writeStore(db, 'categories', snapshot.categories || []),
            writeStore(db, 'templates', snapshot.templates || []),
            writeStore(db, 'template_items', snapshot.template_items || []),
            writeStore(db, 'executions', snapshot.executions || []),
            writeStore(db, 'execution_items', snapshot.execution_items || []),
            writeStore(db, 'metadata', [{
                id: 'snapshot',
                schema_version: snapshot.schema_version,
                generated_at: snapshot.generated_at,
                cached_at: new Date().toISOString(),
            }]),
        ]);
        db.close();
    }

    function readStore(db, name) {
        return new Promise(function (resolve, reject) {
            const transaction = db.transaction(name, 'readonly');
            const request = transaction.objectStore(name).getAll();
            request.onsuccess = function () { resolve(request.result); };
            request.onerror = function () { reject(request.error); };
        });
    }

    async function readSnapshot() {
        const db = await openDatabase();
        const data = {
            groups: await readStore(db, 'groups'),
            categories: await readStore(db, 'categories'),
            templates: await readStore(db, 'templates'),
            executions: await readStore(db, 'executions'),
            pending_operations: await readStore(db, 'pending_operations'),
            metadata: await readStore(db, 'metadata'),
        };
        db.close();
        return data;
    }

    function renderPendingCount(count) {
        localStorage.setItem(PENDING_CHANGES_KEY, String(count));
        if (window.JaciSyncStatus) {
            window.JaciSyncStatus.render();
        }
    }

    async function updatePendingCount() {
        const db = await openDatabase();
        const pendingOperations = await readStore(db, 'pending_operations');
        db.close();
        renderPendingCount(pendingOperations.length);
        return pendingOperations.length;
    }

    async function markExecutionStartedLocally(executionId) {
        const db = await openDatabase();
        const execution = await getRecord(db, 'executions', executionId);
        if (execution) {
            execution.status = 'in_progress';
            execution.offline_updated_at = new Date().toISOString();
            await putRecord(db, 'executions', execution);
        }
        db.close();
    }

    async function enqueueStartExecution(executionId) {
        const db = await openDatabase();
        await putRecord(db, 'pending_operations', {
            id: `start-execution-${executionId}`,
            entity: 'execution',
            entity_id: executionId,
            action: 'start_execution',
            payload: { execution_id: executionId },
            status: 'pending',
            created_at: new Date().toISOString(),
        });
        db.close();
        await markExecutionStartedLocally(executionId);
        await updatePendingCount();
    }

    async function syncPendingOperation(operation) {
        if (operation.action !== 'start_execution') return false;

        const response = await fetch(START_EXECUTION_SYNC_URL, {
            method: 'POST',
            headers: {
                Accept: 'application/json',
                'Content-Type': 'application/json',
            },
            credentials: 'same-origin',
            body: JSON.stringify(operation.payload),
        });
        if (response.status === 401) return false;
        if (!response.ok) throw new Error('Falha ao sincronizar alteração offline.');
        return true;
    }

    async function syncPendingOperations() {
        if (!navigator.onLine) return;

        const db = await openDatabase();
        const operations = await readStore(db, 'pending_operations');
        db.close();

        if (!operations.length) {
            renderPendingCount(0);
            return;
        }

        window.dispatchEvent(new CustomEvent('jaci:sync-start'));
        for (const operation of operations) {
            const applied = await syncPendingOperation(operation);
            if (applied) {
                const nextDb = await openDatabase();
                await deleteRecord(nextDb, 'pending_operations', operation.id);
                nextDb.close();
            }
        }
        await updatePendingCount();
        window.dispatchEvent(new CustomEvent('jaci:sync-success'));
    }

    async function refreshSnapshot() {
        if (!navigator.onLine) return;
        window.dispatchEvent(new CustomEvent('jaci:sync-start'));
        const response = await fetch(SNAPSHOT_URL, {
            headers: { Accept: 'application/json' },
            credentials: 'same-origin',
        });
        if (response.status === 401) {
            window.dispatchEvent(new CustomEvent('jaci:sync-success'));
            return;
        }
        if (!response.ok) throw new Error('Falha ao atualizar cache offline.');
        await saveSnapshot(await response.json());
        window.dispatchEvent(new CustomEvent('jaci:sync-success'));
    }

    function clearLocalCache() {
        return new Promise(function (resolve, reject) {
            const request = indexedDB.deleteDatabase(DB_NAME);
            request.onsuccess = resolve;
            request.onerror = function () { reject(request.error); };
            request.onblocked = resolve;
        });
    }

    function formatDate(value) {
        if (!value) return 'nunca';
        return new Intl.DateTimeFormat('pt-BR', {
            dateStyle: 'short',
            timeStyle: 'short',
        }).format(new Date(value));
    }

    async function renderOfflineSummary() {
        if (!panel || !summary || navigator.onLine) {
            if (panel) panel.hidden = true;
            return;
        }

        const snapshot = await readSnapshot();
        const metadata = snapshot.metadata.find(function (item) {
            return item.id === 'snapshot';
        });

        panel.hidden = false;
        summary.innerHTML = [
            `<li>${snapshot.groups.length} grupo(s)</li>`,
            `<li>${snapshot.categories.length} categoria(s)</li>`,
            `<li>${snapshot.templates.length} lista(s)</li>`,
            `<li>${snapshot.executions.length} execução(ões) recente(s)</li>`,
            `<li>${snapshot.pending_operations.length} alteração(ões) aguardando sync</li>`,
            `<li>Atualizado em ${formatDate(metadata?.cached_at)}</li>`,
        ].join('');
    }

    function renderQueuedStart(form) {
        const button = form.querySelector('button[type="submit"]');
        if (!button) return;

        button.disabled = true;
        button.classList.remove('btn-primary');
        button.classList.add('btn-outline-secondary');
        button.innerHTML = 'Compra iniciada offline <i class="bi bi-cloud-arrow-up-fill"></i>';
    }

    function setupOfflineStartForms() {
        document.querySelectorAll('[data-offline-start-execution]').forEach(function (form) {
            form.addEventListener('submit', function (event) {
                if (navigator.onLine) return;

                event.preventDefault();
                const executionId = Number(form.dataset.executionId);
                if (!executionId) return;

                enqueueStartExecution(executionId)
                    .then(function () {
                        renderQueuedStart(form);
                        renderOfflineSummary();
                    })
                    .catch(function () {
                        window.dispatchEvent(new CustomEvent('jaci:sync-error'));
                    });
            });
        });
    }

    window.JaciOfflineCache = {
        refresh: refreshSnapshot,
        read: readSnapshot,
        syncPending: syncPendingOperations,
        enqueueStartExecution: enqueueStartExecution,
        clear: clearLocalCache,
    };

    if (window.location.pathname === '/auth/logout') {
        clearLocalCache();
        return;
    }

    window.addEventListener('online', function () {
        syncPendingOperations().then(refreshSnapshot).catch(function () {
            window.dispatchEvent(new CustomEvent('jaci:sync-error'));
        }).finally(renderOfflineSummary);
    });
    window.addEventListener('offline', renderOfflineSummary);
    window.addEventListener('load', function () {
        setupOfflineStartForms();
        updatePendingCount().catch(function () {});
        syncPendingOperations().then(refreshSnapshot).catch(function () {
            window.dispatchEvent(new CustomEvent('jaci:sync-error'));
        }).finally(renderOfflineSummary);
    });
})();
