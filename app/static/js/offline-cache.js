(function () {
    'use strict';

    const DB_NAME = 'jaci-offline-cache';
    const DB_VERSION = 9;
    const SNAPSHOT_URL = '/api/offline/snapshot';
    const START_EXECUTION_SYNC_URL = '/api/offline/operations/start-execution';
    const EXECUTION_ITEM_SYNC_URL = '/api/offline/operations/execution-item';
    const ADD_EXECUTION_ITEM_SYNC_URL = '/api/offline/operations/add-execution-item';
    const REMOVE_EXECUTION_ITEM_SYNC_URL = '/api/offline/operations/remove-execution-item';
    const FINALIZE_EXECUTION_SYNC_URL = '/api/offline/operations/finalize-execution';
    const PENDING_CHANGES_KEY = 'jaci_pending_changes';
    const PENDING_ERRORS_KEY = 'jaci_pending_errors';
    const SYNC_RETRY_DELAY_MS = 15000;
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
    let retryTimer = null;
    let syncInFlight = false;

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

    function renderPendingState(operations) {
        const count = operations.length;
        const errorCount = operations.filter(function (operation) {
            return Number(operation.tentativas || 0) > 0;
        }).length;
        localStorage.setItem(PENDING_CHANGES_KEY, String(count));
        localStorage.setItem(PENDING_ERRORS_KEY, String(errorCount));
        if (window.JaciSyncStatus) {
            window.JaciSyncStatus.render();
        }
    }

    async function updatePendingCount() {
        const db = await openDatabase();
        const pendingOperations = await readStore(db, 'pending_operations');
        db.close();
        renderPendingState(pendingOperations);
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
        await putRecord(db, 'pending_operations', buildQueuedOperation({
            id: `start-execution-${executionId}`,
            tipo: 'START_EXECUTION',
            entidade: 'execution',
            entidadeId: executionId,
            action: 'start_execution',
            payload: { execution_id: executionId },
        }));
        db.close();
        await markExecutionStartedLocally(executionId);
        await updatePendingCount();
    }

    function operationIdForItem(itemId) {
        return `execution-item-${itemId}`;
    }

    function operationIdForTempItem(tempId) {
        return `add-execution-item-${tempId}`;
    }

    function createTempId() {
        const random = Math.random().toString(36).slice(2, 10);
        return `temp-${Date.now()}-${random}`;
    }

    function normalizeNumber(value) {
        if (value === null || value === undefined || value === '') return null;
        const normalized = Number(String(value).replace(',', '.'));
        return Number.isFinite(normalized) ? normalized : null;
    }

    function buildQueuedOperation({ id, tipo, entidade, entidadeId, action, payload, createdAt, updatedAt }) {
        const created = createdAt || new Date().toISOString();
        return {
            id: id,
            tipo: tipo,
            entidade: entidade,
            entidade_id: entidadeId,
            payload: payload,
            created_at: created,
            tentativas: 0,
            entity: entidade,
            entity_id: entidadeId,
            action: action,
            status: 'pending',
            updated_at: updatedAt || created,
        };
    }

    function sortOperationsByCreation(operations) {
        return operations.slice().sort(function (a, b) {
            const byCreatedAt = String(a.created_at || '').localeCompare(String(b.created_at || ''));
            if (byCreatedAt !== 0) return byCreatedAt;
            return String(a.id).localeCompare(String(b.id));
        });
    }

    async function recordSyncAttempt(operation) {
        const db = await openDatabase();
        await putRecord(db, 'pending_operations', Object.assign({}, operation, {
            tentativas: Number(operation.tentativas || 0) + 1,
            updated_at: new Date().toISOString(),
        }));
        db.close();
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

        await putRecord(db, 'pending_operations', Object.assign(
            buildQueuedOperation({
                id: operationId,
                tipo: operation.action === 'complete_item' ? 'COMPLETE_ITEM' : 'INCOMPLETE_ITEM',
                entidade: 'execution_item',
                entidadeId: operation.item_id,
                action: operation.action,
                payload: payload,
                createdAt: existing?.created_at,
            }),
            { tentativas: Number(existing?.tentativas || 0) }
        ));
        db.close();
        await markExecutionItemLocally(payload);
        await updatePendingCount();
    }

    async function markAddedExecutionItemLocally(operation) {
        const db = await openDatabase();
        await putRecord(db, 'execution_items', {
            id: operation.temp_id,
            execution_id: operation.execution_id,
            category_id: operation.category_id,
            name: operation.name,
            planned_quantity: operation.planned_quantity,
            purchased_quantity: null,
            unit_price: null,
            location: null,
            is_completed: false,
            notes: operation.notes,
            version: 1,
            sort_order: Date.now(),
            is_deleted: false,
            is_temporary: true,
            offline_created_at: new Date().toISOString(),
        });
        db.close();
    }

    async function enqueueAddExecutionItemOperation(operation) {
        const db = await openDatabase();
        await putRecord(db, 'pending_operations', buildQueuedOperation({
            id: operationIdForTempItem(operation.temp_id),
            tipo: 'ADD_ITEM',
            entidade: 'execution_item',
            entidadeId: operation.temp_id,
            action: 'add_execution_item',
            payload: operation,
        }));
        db.close();
        await markAddedExecutionItemLocally(operation);
        await updatePendingCount();
    }

    async function markRemovedExecutionItemLocally(operation) {
        const db = await openDatabase();
        const item = await getRecord(db, 'execution_items', operation.item_id);
        if (item?.is_temporary) {
            await deleteRecord(db, 'execution_items', item.id);
            await deleteRecord(db, 'pending_operations', operationIdForTempItem(item.id));
            db.close();
            return;
        }
        if (item) {
            item.is_deleted = true;
            item.offline_removed_at = new Date().toISOString();
            await putRecord(db, 'execution_items', item);
        }
        db.close();
    }

    async function enqueueRemoveExecutionItemOperation(operation) {
        const db = await openDatabase();
        const item = await getRecord(db, 'execution_items', operation.item_id);
        if (item?.is_temporary) {
            db.close();
            await markRemovedExecutionItemLocally(operation);
            await updatePendingCount();
            return;
        }

        await putRecord(db, 'pending_operations', buildQueuedOperation({
            id: `remove-execution-item-${operation.item_id}`,
            tipo: 'REMOVE_ITEM',
            entidade: 'execution_item',
            entidadeId: operation.item_id,
            action: 'remove_execution_item',
            payload: operation,
        }));
        await deleteRecord(db, 'pending_operations', operationIdForItem(operation.item_id));
        db.close();
        await markRemovedExecutionItemLocally(operation);
        await updatePendingCount();
    }

    async function markExecutionFinalizedLocally(operation) {
        const db = await openDatabase();
        const execution = await getRecord(db, 'executions', operation.execution_id);
        const items = await readStore(db, 'execution_items');

        if (execution) {
            execution.status = 'completed';
            execution.finished_at = new Date().toISOString();
            execution.offline_finalized_at = execution.finished_at;
            await putRecord(db, 'executions', execution);
        }

        const pendingItems = items.filter(function (item) {
            return item.execution_id === operation.execution_id
                && !item.is_completed
                && !item.is_deleted;
        });
        for (const item of pendingItems) {
            item.is_deleted = true;
            item.offline_removed_at = new Date().toISOString();
            await putRecord(db, 'execution_items', item);
        }
        db.close();
    }

    async function enqueueFinalizeExecutionOperation(operation) {
        const db = await openDatabase();
        await putRecord(db, 'pending_operations', buildQueuedOperation({
            id: `finalize-execution-${operation.execution_id}`,
            tipo: 'FINALIZE_EXECUTION',
            entidade: 'execution',
            entidadeId: operation.execution_id,
            action: 'finalize_execution',
            payload: operation,
        }));
        db.close();
        await markExecutionFinalizedLocally(operation);
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
        if (operation.action === 'add_execution_item') {
            url = ADD_EXECUTION_ITEM_SYNC_URL;
        }
        if (operation.action === 'remove_execution_item') {
            url = REMOVE_EXECUTION_ITEM_SYNC_URL;
        }
        if (operation.action === 'finalize_execution') {
            url = FINALIZE_EXECUTION_SYNC_URL;
        }
        if (!url) return false;

        let response;
        try {
            response = await fetch(url, {
                method: 'POST',
                headers: {
                    Accept: 'application/json',
                    'Content-Type': 'application/json',
                },
                credentials: 'same-origin',
                body: JSON.stringify(operation.payload),
            });
        } catch (error) {
            await recordSyncAttempt(operation);
            throw error;
        }
        if (response.status === 401) return false;
        if (!response.ok) {
            await recordSyncAttempt(operation);
            throw new Error('Falha ao sincronizar alteração offline.');
        }
        return true;
    }

    async function syncPendingOperations() {
        if (!navigator.onLine) return;

        const db = await openDatabase();
        const operations = sortOperationsByCreation(await readStore(db, 'pending_operations'));
        db.close();

        if (!operations.length) {
            renderPendingState([]);
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

    function scheduleAutomaticRetry(delay) {
        if (!navigator.onLine) return;
        if (retryTimer) window.clearTimeout(retryTimer);
        retryTimer = window.setTimeout(function () {
            retryTimer = null;
            runAutomaticSync({ retry: true });
        }, delay);
    }

    async function runAutomaticSync(options) {
        if (!navigator.onLine || syncInFlight) return;
        syncInFlight = true;
        if (retryTimer) {
            window.clearTimeout(retryTimer);
            retryTimer = null;
        }

        try {
            await syncPendingOperations();
            await refreshSnapshot();
        } catch (error) {
            window.dispatchEvent(new CustomEvent('jaci:sync-error'));
            scheduleAutomaticRetry(SYNC_RETRY_DELAY_MS);
        } finally {
            syncInFlight = false;
            renderOfflineSummary();
        }
    }

    function clearLocalCache() {
        localStorage.removeItem(PENDING_CHANGES_KEY);
        localStorage.removeItem(PENDING_ERRORS_KEY);
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

    function readRemoveItemOperationFromButton(button) {
        return {
            execution_id: Number(button.dataset.executionId),
            item_id: button.dataset.itemId && button.dataset.itemId.startsWith('temp-')
                ? button.dataset.itemId
                : Number(button.dataset.itemId),
        };
    }

    function readFinalizeOperationFromForm(form, submitter) {
        const formData = new FormData(form);
        return {
            execution_id: Number(form.dataset.executionId),
            action: submitter?.value || formData.get('action') || 'discard',
            new_date: formData.get('new_date') || null,
        };
    }

    async function countPendingItemsForExecution(executionId) {
        const db = await openDatabase();
        const items = await readStore(db, 'execution_items');
        db.close();
        return items.filter(function (item) {
            return item.execution_id === executionId
                && !item.is_completed
                && !item.is_deleted;
        }).length;
    }

    function readAddItemOperationFromForm(form) {
        const formData = new FormData(form);
        const name = String(formData.get('name') || '').trim();
        const plannedQuantity = normalizeNumber(formData.get('planned_quantity')) || 1;
        const categoryId = normalizeNumber(formData.get('category_id'));

        return {
            execution_id: Number(form.dataset.executionId),
            temp_id: createTempId(),
            name: name,
            planned_quantity: plannedQuantity,
            category_id: categoryId && categoryId > 0 ? categoryId : null,
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
            const removeButton = event.target.closest('[data-offline-remove-item]');
            if (removeButton && !navigator.onLine) {
                event.preventDefault();
                event.stopImmediatePropagation();

                const operation = readRemoveItemOperationFromButton(removeButton);
                enqueueRemoveExecutionItemOperation(operation)
                    .then(function () {
                        renderQueuedItemControl(removeButton);
                        renderOfflineSummary();
                    })
                    .catch(function () {
                        window.dispatchEvent(new CustomEvent('jaci:sync-error'));
                    });
                return;
            }

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

    function setupOfflineAddItemForms() {
        document.querySelectorAll('[data-offline-add-item]').forEach(function (form) {
            form.addEventListener('submit', function (event) {
                if (navigator.onLine) return;

                event.preventDefault();
                event.stopImmediatePropagation();

                const operation = readAddItemOperationFromForm(form);
                if (!operation.name || operation.planned_quantity <= 0) {
                    window.dispatchEvent(new CustomEvent('jaci:sync-error'));
                    return;
                }

                enqueueAddExecutionItemOperation(operation)
                    .then(function () {
                        form.reset();
                        renderQueuedItemControl(form);
                        renderOfflineSummary();
                    })
                    .catch(function () {
                        window.dispatchEvent(new CustomEvent('jaci:sync-error'));
                    });
            });
        });
    }

    function renderFinalizeConfirmation() {
        alert('Compra finalizada offline. A recorrencia sera processada quando a sincronizacao concluir.');
    }

    function setupOfflineFinalizeControls() {
        document.querySelectorAll('[data-offline-finalize-link]').forEach(function (link) {
            link.addEventListener('click', function (event) {
                if (navigator.onLine) return;

                event.preventDefault();
                const executionId = Number(link.dataset.executionId);
                countPendingItemsForExecution(executionId).then(function (pendingCount) {
                    if (pendingCount > 0) {
                        alert('Existem itens pendentes. Trate os pendentes antes de finalizar offline.');
                        return;
                    }
                    enqueueFinalizeExecutionOperation({
                        execution_id: executionId,
                        action: 'discard',
                        new_date: null,
                    }).then(function () {
                        link.classList.remove('btn-success');
                        link.classList.add('btn-outline-secondary');
                        renderFinalizeConfirmation();
                        renderOfflineSummary();
                    });
                }).catch(function () {
                    window.dispatchEvent(new CustomEvent('jaci:sync-error'));
                });
            });
        });

        document.querySelectorAll('[data-offline-finalize-execution]').forEach(function (form) {
            form.addEventListener('submit', function (event) {
                if (navigator.onLine) return;

                event.preventDefault();
                event.stopImmediatePropagation();

                const operation = readFinalizeOperationFromForm(form, event.submitter);
                enqueueFinalizeExecutionOperation(operation)
                    .then(function () {
                        renderQueuedItemControl(form);
                        renderFinalizeConfirmation();
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
        syncNow: runAutomaticSync,
        enqueueStartExecution: enqueueStartExecution,
        enqueueExecutionItemOperation: enqueueExecutionItemOperation,
        enqueueAddExecutionItemOperation: enqueueAddExecutionItemOperation,
        enqueueRemoveExecutionItemOperation: enqueueRemoveExecutionItemOperation,
        enqueueFinalizeExecutionOperation: enqueueFinalizeExecutionOperation,
        clear: clearLocalCache,
    };

    if (window.location.pathname === '/auth/logout') {
        clearLocalCache();
        return;
    }

    window.addEventListener('online', runAutomaticSync);
    window.addEventListener('offline', renderOfflineSummary);
    window.addEventListener('jaci:sync-manual', function () {
        runAutomaticSync({ manual: true });
    });
    window.addEventListener('load', function () {
        setupOfflineStartForms();
        setupOfflineAddItemForms();
        setupOfflineItemOperations();
        setupOfflineFinalizeControls();
        updatePendingCount().catch(function () {});
        runAutomaticSync();
    });
})();
