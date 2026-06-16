(function () {
    'use strict';

    const DB_NAME = 'jaci-offline-cache';
    const DB_VERSION = 3;
    const SNAPSHOT_URL = '/api/offline/snapshot';
    const START_EXECUTION_SYNC_URL = '/api/offline/operations/start-execution';
    const EXECUTION_ITEM_SYNC_URL = '/api/offline/operations/execution-item';
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
            execution_items: await readStore(db, 'execution_items'),
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

    function operationIdForItem(itemId) {
        return `execution-item-${itemId}`;
    }

    function normalizeNumber(value) {
        if (value === null || value === undefined || value === '') return null;
        const normalized = Number(String(value).replace(',', '.'));
        return Number.isFinite(normalized) ? normalized : null;
    }

    async function markExecutionItemLocally(operation) {
        const db = await openDatabase();
        const item = await getRecord(db, 'execution_items', operation.item_id);
        if (item) {
            item.offline_base_version = item.offline_base_version ?? operation.version;
            if (operation.action === 'complete_item') {
                item.is_completed = true;
                item.purchased_quantity = operation.purchased_quantity;
                item.unit_price = operation.unit_price;
                item.location = operation.location;
                item.notes = operation.notes;
            } else {
                item.is_completed = false;
                item.purchased_quantity = null;
                item.unit_price = null;
                item.location = null;
            }
            item.version = Math.max(Number(item.version || 0), Number(operation.version || 0)) + 1;
            item.offline_updated_at = new Date().toISOString();
            await putRecord(db, 'execution_items', item);
        }
        db.close();
    }

    async function enqueueExecutionItemOperation(operation) {
        const db = await openDatabase();
        const operationId = operationIdForItem(operation.item_id);
        const existing = await getRecord(db, 'pending_operations', operationId);
        const baseVersion = existing?.payload?.version ?? operation.version;
        const payload = Object.assign({}, operation, { version: baseVersion });

        await putRecord(db, 'pending_operations', {
            id: operationId,
            entity: 'execution_item',
            entity_id: operation.item_id,
            action: operation.action,
            payload: payload,
            status: 'pending',
            created_at: existing?.created_at || new Date().toISOString(),
            updated_at: new Date().toISOString(),
        });
        db.close();
        await markExecutionItemLocally(payload);
        await updatePendingCount();
    }

    async function syncPendingOperation(operation) {
        let url = null;

        if (operation.action === 'start_execution') {
            url = START_EXECUTION_SYNC_URL;
        }
        if (
            operation.entity === 'execution_item'
            && ['complete_item', 'incomplete_item'].includes(operation.action)
        ) {
            url = EXECUTION_ITEM_SYNC_URL;
        }
        if (!url) return false;

        const response = await fetch(url, {
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
        localStorage.removeItem(PENDING_CHANGES_KEY);
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
            `<li>${snapshot.execution_items.length} item(ns) de execução</li>`,
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

    function readItemOperationFromForm(form, action) {
        const formData = new FormData(form);
        return {
            execution_id: Number(form.dataset.executionId),
            item_id: Number(form.dataset.itemId),
            action: action,
            version: Number(formData.get('version')),
            purchased_quantity: normalizeNumber(formData.get('purchased_quantity')),
            unit_price: normalizeNumber(formData.get('unit_price')),
            location: formData.get('location') || null,
            notes: formData.get('notes') || null,
        };
    }

    function readItemOperationFromButton(button) {
        const quantity = prompt(
            `Quantidade comprada para ${button.dataset.itemName}`,
            button.dataset.purchasedQuantity || button.dataset.plannedQuantity || '1'
        );
        if (quantity === null) return null;

        const unitPrice = prompt('Valor unitario (R$)', button.dataset.unitPrice || '');
        if (unitPrice === null) return null;

        const purchasedQuantity = normalizeNumber(quantity);
        const normalizedUnitPrice = normalizeNumber(unitPrice);
        if (!purchasedQuantity || purchasedQuantity <= 0 || normalizedUnitPrice === null || normalizedUnitPrice < 0) {
            alert('Quantidade ou valor invalido.');
            return null;
        }

        const location = prompt('Local de compra', button.dataset.location || '');
        if (location === null) return null;

        const notes = prompt('Observacoes', button.dataset.notes || '');
        if (notes === null) return null;

        return {
            execution_id: Number(button.dataset.executionId),
            item_id: Number(button.dataset.itemId),
            action: 'complete_item',
            version: Number(button.dataset.version),
            purchased_quantity: purchasedQuantity,
            unit_price: normalizedUnitPrice,
            location: location || null,
            notes: notes || null,
        };
    }

    function renderQueuedItemControl(element) {
        const button = element.matches('button') ? element : element.querySelector('button[type="submit"]');
        if (!button) return;

        button.classList.remove('btn-primary');
        button.classList.add('btn-outline-secondary');
        button.dataset.offlineQueued = 'true';
    }

    function hideContainingModal(element) {
        const modalEl = element.closest('.modal');
        if (!modalEl || !window.bootstrap) return;

        const modal = bootstrap.Modal.getInstance(modalEl);
        if (modal) modal.hide();
    }

    function setupOfflineItemOperations() {
        document.addEventListener('click', function (event) {
            const button = event.target.closest('[data-offline-complete-item]');
            if (!button || navigator.onLine) return;

            event.preventDefault();
            event.stopImmediatePropagation();

            const operation = readItemOperationFromButton(button);
            if (!operation) return;

            enqueueExecutionItemOperation(operation)
                .then(function () {
                    renderQueuedItemControl(button);
                    renderOfflineSummary();
                })
                .catch(function () {
                    window.dispatchEvent(new CustomEvent('jaci:sync-error'));
                });
        }, true);

        document.addEventListener('submit', function (event) {
            const completeForm = event.target.closest('[data-offline-complete-item-form]');
            const incompleteForm = event.target.closest('[data-offline-incomplete-item]');
            if ((!completeForm && !incompleteForm) || navigator.onLine) return;

            event.preventDefault();
            event.stopImmediatePropagation();

            const form = completeForm || incompleteForm;
            const action = completeForm ? 'complete_item' : 'incomplete_item';
            const operation = readItemOperationFromForm(form, action);

            enqueueExecutionItemOperation(operation)
                .then(function () {
                    renderQueuedItemControl(form);
                    hideContainingModal(form);
                    renderOfflineSummary();
                })
                .catch(function () {
                    window.dispatchEvent(new CustomEvent('jaci:sync-error'));
                });
        }, true);
    }

    window.JaciOfflineCache = {
        refresh: refreshSnapshot,
        read: readSnapshot,
        syncPending: syncPendingOperations,
        enqueueStartExecution: enqueueStartExecution,
        enqueueExecutionItemOperation: enqueueExecutionItemOperation,
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
        setupOfflineItemOperations();
        updatePendingCount().catch(function () {});
        syncPendingOperations().then(refreshSnapshot).catch(function () {
            window.dispatchEvent(new CustomEvent('jaci:sync-error'));
        }).finally(renderOfflineSummary);
    });
})();
