(function () {
    'use strict';

    const DB_NAME = 'jaci-offline-cache';
    const DB_VERSION = 1;
    const SNAPSHOT_URL = '/api/offline/snapshot';
    const STORE_NAMES = [
        'groups',
        'categories',
        'templates',
        'template_items',
        'executions',
        'execution_items',
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
            metadata: await readStore(db, 'metadata'),
        };
        db.close();
        return data;
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
            `<li>Atualizado em ${formatDate(metadata?.cached_at)}</li>`,
        ].join('');
    }

    window.JaciOfflineCache = {
        refresh: refreshSnapshot,
        read: readSnapshot,
        clear: clearLocalCache,
    };

    if (window.location.pathname === '/auth/logout') {
        clearLocalCache();
        return;
    }

    window.addEventListener('online', function () {
        refreshSnapshot().catch(function () {
            window.dispatchEvent(new CustomEvent('jaci:sync-error'));
        }).finally(renderOfflineSummary);
    });
    window.addEventListener('offline', renderOfflineSummary);
    window.addEventListener('load', function () {
        refreshSnapshot().catch(function () {
            window.dispatchEvent(new CustomEvent('jaci:sync-error'));
        }).finally(renderOfflineSummary);
    });
})();
