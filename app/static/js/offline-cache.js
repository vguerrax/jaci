(function () {
    'use strict';

    const DB_NAME = 'jaci-offline-cache';
    const DB_VERSION = 10;
    const SNAPSHOT_URL = '/api/offline/snapshot';
    const START_EXECUTION_SYNC_URL = '/api/offline/operations/start-execution';
    const UPDATE_EXECUTION_SYNC_URL = '/api/offline/operations/update-execution';
    const EXECUTION_ITEM_SYNC_URL = '/api/offline/operations/execution-item';
    const ADD_EXECUTION_ITEM_SYNC_URL = '/api/offline/operations/add-execution-item';
    const REMOVE_EXECUTION_ITEM_SYNC_URL = '/api/offline/operations/remove-execution-item';
    const FINALIZE_EXECUTION_SYNC_URL = '/api/offline/operations/finalize-execution';
    const SYNC_CONFLICTS_URL = '/api/offline/conflicts';
    const PENDING_CHANGES_KEY = 'jaci_pending_changes';
    const PENDING_ERRORS_KEY = 'jaci_pending_errors';
    const PENDING_CONFLICTS_KEY = 'jaci_pending_conflicts';
    const SYNC_RETRY_BASE_DELAY_MS = 5000;
    const SYNC_RETRY_MAX_DELAY_MS = 120000;
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
    const syncCenter = document.querySelector('[data-sync-center]');
    const syncOperationList = document.querySelector('[data-sync-operation-list]');
    const syncEmpty = document.querySelector('[data-sync-empty]');
    const syncNowButton = document.querySelector('[data-sync-center-sync-now]');
    const syncCountPending = document.querySelector('[data-sync-count-pending]');
    const syncCountFailed = document.querySelector('[data-sync-count-failed]');
    const syncCountConflict = document.querySelector('[data-sync-count-conflict]');
    const syncAuditList = document.querySelector('[data-sync-audit-list]');
    const syncAuditEmpty = document.querySelector('[data-sync-audit-empty]');
    const syncAuditRefresh = document.querySelector('[data-sync-audit-refresh]');
    let syncFilter = 'all';
    let retryTimer = null;
    let syncInFlight = false;
    let offlineCompleteClickBound = false;

    function SyncFailure(message, requiresManualIntervention) {
        this.name = 'SyncFailure';
        this.message = message;
        this.requiresManualIntervention = requiresManualIntervention;
    }

    if (!('indexedDB' in window)) return;

    document.addEventListener('pointerdown', disableMissingCompleteModalTriggers, true);
    document.addEventListener('touchstart', disableMissingCompleteModalTriggers, true);
    document.addEventListener('click', handleOfflineCompleteItemClick, true);
    document.addEventListener('click', handleOfflineEditItemClick, true);
    offlineCompleteClickBound = true;

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
        const conflictCount = operations.filter(isConflictOperation).length;
        localStorage.setItem(PENDING_CHANGES_KEY, String(count));
        localStorage.setItem(PENDING_ERRORS_KEY, String(errorCount));
        localStorage.setItem(PENDING_CONFLICTS_KEY, String(conflictCount));
        if (window.JaciSyncStatus) {
            window.JaciSyncStatus.render();
        }
        renderSyncCenter(operations).catch(function () {});
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

    function operationIdForExecution(executionId) {
        return `update-execution-${executionId}`;
    }

    async function markExecutionUpdatedLocally(operation) {
        const db = await openDatabase();
        const execution = await getRecord(db, 'executions', operation.execution_id);
        if (execution) {
            execution.name = operation.name;
            execution.scheduled_date = operation.scheduled_date;
            execution.budget = operation.budget;
            execution.offline_updated_at = new Date().toISOString();
            await putRecord(db, 'executions', execution);
        }
        db.close();
    }

    async function enqueueUpdateExecutionOperation(operation) {
        const db = await openDatabase();
        const operationId = operationIdForExecution(operation.execution_id);
        const existing = await getRecord(db, 'pending_operations', operationId);

        await putRecord(db, 'pending_operations', Object.assign(
            buildQueuedOperation({
                id: operationId,
                tipo: 'UPDATE_EXECUTION',
                entidade: 'execution',
                entidadeId: operation.execution_id,
                action: 'update_execution',
                payload: operation,
                createdAt: existing?.created_at,
            }),
            { tentativas: Number(existing?.tentativas || 0) }
        ));
        db.close();
        await markExecutionUpdatedLocally(operation);
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

    function getRetryDelay(operation) {
        const attempts = Math.max(1, Number(operation.tentativas || 0) + 1);
        return Math.min(SYNC_RETRY_MAX_DELAY_MS, SYNC_RETRY_BASE_DELAY_MS * (2 ** (attempts - 1)));
    }

    function isTransientStatus(status) {
        return status === 429 || status >= 500;
    }

    function isConflictOperation(operation) {
        return operation?.status === 'conflict' || operation?.conflict?.type === 'sync_conflict';
    }

    function classifyOperation(operation) {
        if (isConflictOperation(operation)) return 'conflict';
        if (operation?.requires_manual_intervention || Number(operation?.tentativas || 0) > 0) return 'failed';
        return 'pending';
    }

    function detailMessage(detail) {
        if (!detail) return 'Falha de sincronização.';
        if (typeof detail === 'string') return detail;
        return detail.message || detail.detail || 'Falha de sincronização.';
    }

    function buildConflict(operation, statusCode, detail) {
        if (detail?.type === 'sync_conflict') return detail;
        return {
            type: 'sync_conflict',
            message: detailMessage(detail),
            entity: operation.entity,
            entity_id: operation.entity_id,
            reason: statusCode === 409 ? 'server_conflict' : 'manual_intervention',
            local: operation.payload,
            remote: detail?.remote || null,
        };
    }

    async function recordSyncAttempt(operation, requiresManualIntervention, conflict) {
        const db = await openDatabase();
        const conflictPayload = conflict?.type === 'sync_conflict' ? conflict : null;
        await putRecord(db, 'pending_operations', Object.assign({}, operation, {
            tentativas: Number(operation.tentativas || 0) + 1,
            requires_manual_intervention: Boolean(requiresManualIntervention),
            status: conflictPayload ? 'conflict' : operation.status,
            conflict: conflictPayload || operation.conflict || null,
            error_message: conflictPayload ? conflictPayload.message : operation.error_message,
            conflict_detected_at: conflictPayload ? new Date().toISOString() : operation.conflict_detected_at,
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
            } else if (operation.action === 'update_item') {
                item.name = operation.name;
                item.planned_quantity = operation.planned_quantity;
                item.category_id = operation.category_id;
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
        const operationTypeByAction = {
            complete_item: 'COMPLETE_ITEM',
            incomplete_item: 'INCOMPLETE_ITEM',
            update_item: 'UPDATE_ITEM',
        };

        await putRecord(db, 'pending_operations', Object.assign(
            buildQueuedOperation({
                id: operationId,
                tipo: operationTypeByAction[operation.action] || 'UPDATE_ITEM',
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
        await refreshLocalExecutionBudget(operation.execution_id);
    }

    async function markAddedExecutionItemLocally(operation) {
        const db = await openDatabase();
        await putRecord(db, 'execution_items', {
            id: operation.temp_id,
            execution_id: operation.execution_id,
            template_item_id: null,
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
            await refreshLocalExecutionBudget(operation.execution_id);
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
        await refreshLocalExecutionBudget(operation.execution_id);
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
        if (operation.action === 'update_execution') {
            url = UPDATE_EXECUTION_SYNC_URL;
        }
        if (
            operation.entity === 'execution_item'
            && ['complete_item', 'incomplete_item', 'update_item'].includes(operation.action)
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
            await recordSyncAttempt(operation, false);
            throw new SyncFailure('Falha temporária de rede.', false);
        }
        if (response.status === 401) return false;
        if (!response.ok) {
            let detail = null;
            try {
                const responseBody = await response.json();
                detail = responseBody?.detail || responseBody;
            } catch (error) {
                detail = null;
            }
            const requiresManualIntervention = !isTransientStatus(response.status);
            const conflict = response.status === 409 ? buildConflict(operation, response.status, detail) : null;
            await recordSyncAttempt(operation, requiresManualIntervention, conflict);
            throw new SyncFailure(
                conflict
                    ? conflict.message
                    : requiresManualIntervention
                    ? 'Sincronização requer intervenção manual.'
                    : 'Falha temporária ao sincronizar alteração offline.',
                requiresManualIntervention
            );
        }
        try {
            return await response.json();
        } catch (error) {
            return { status: 'applied' };
        }
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
        const appliedOperations = [];
        for (const operation of operations) {
            if (operation.requires_manual_intervention || isConflictOperation(operation)) {
                continue;
            }
            const applied = await syncPendingOperation(operation);
            if (applied) {
                const nextDb = await openDatabase();
                await deleteRecord(nextDb, 'pending_operations', operation.id);
                nextDb.close();
                appliedOperations.push({ operation: operation, result: applied });
            }
        }
        await updatePendingCount();
        window.dispatchEvent(new CustomEvent('jaci:sync-success'));
        const refreshed = await refreshCurrentExecutionFragments();
        if (!refreshed) {
            appliedOperations.forEach(reconcileAppliedOperationInDom);
        }
        await clearOfflineItemIndicatorsWhenSynced();
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
        await applyPersistedOfflineItemState();
        await clearOfflineItemIndicatorsWhenSynced();
    }

    function getNextRetryDelay() {
        return updatePendingCount().then(function () {
            return readSnapshot();
        }).then(function (snapshot) {
            const retryable = snapshot.pending_operations.filter(function (operation) {
                return Number(operation.tentativas || 0) > 0 && !operation.requires_manual_intervention;
            });
            if (!retryable.length) return SYNC_RETRY_BASE_DELAY_MS;
            return Math.max.apply(null, retryable.map(getRetryDelay));
        });
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
            if (error.requiresManualIntervention) {
                window.dispatchEvent(new CustomEvent('jaci:sync-error'));
            } else {
                window.dispatchEvent(new CustomEvent('jaci:sync-retry-scheduled'));
                getNextRetryDelay().then(scheduleAutomaticRetry);
            }
        } finally {
            syncInFlight = false;
            renderOfflineSummary();
        }
    }

    function clearLocalCache() {
        localStorage.removeItem(PENDING_CHANGES_KEY);
        localStorage.removeItem(PENDING_ERRORS_KEY);
        localStorage.removeItem(PENDING_CONFLICTS_KEY);
        return new Promise(function (resolve, reject) {
            const request = indexedDB.deleteDatabase(DB_NAME);
            request.onsuccess = resolve;
            request.onerror = function () { reject(request.error); };
            request.onblocked = resolve;
        });
    }

    function escapeHtml(value) {
        return String(value ?? '')
            .replaceAll('&', '&amp;')
            .replaceAll('<', '&lt;')
            .replaceAll('>', '&gt;')
            .replaceAll('"', '&quot;')
            .replaceAll("'", '&#039;');
    }

    function operationLabel(operation) {
        const labels = {
            start_execution: 'Iniciar compra',
            update_execution: 'Editar compra agendada',
            complete_item: 'Marcar item como comprado',
            incomplete_item: 'Desmarcar item',
            update_item: 'Editar item',
            add_execution_item: 'Adicionar item',
            remove_execution_item: 'Remover item',
            finalize_execution: 'Finalizar compra',
        };
        return labels[operation.action] || operation.tipo || 'Operação offline';
    }

    function operationTypeLabel(operationType) {
        const labels = {
            StartExecutionOperation: 'Iniciar compra',
            UpdateExecutionOperation: 'Editar compra agendada',
            ExecutionItemOperation: 'Alterar item da compra',
            AddExecutionItemOperation: 'Adicionar item',
            RemoveExecutionItemOperation: 'Remover item',
            FinalizeExecutionOperation: 'Finalizar compra',
        };
        return labels[operationType] || operationType || 'Operação de sincronização';
    }

    function entityLabel(entity) {
        const labels = {
            execution: 'Compra',
            execucao: 'Compra',
            execution_item: 'Item da compra',
            item_execucao: 'Item da compra',
            template: 'Lista',
            template_item: 'Item da lista',
            group: 'Grupo',
        };
        return labels[entity] || entity || 'Registro';
    }

    function fieldLabel(key) {
        const labels = {
            action: 'Ação',
            budget: 'Orçamento',
            category_id: 'Categoria',
            conflict_detected_at: 'Conflito detectado em',
            created_at: 'Criado em',
            entity: 'Entidade',
            entity_id: 'Identificador',
            execution_id: 'Compra',
            finished_at: 'Finalizada em',
            group_id: 'Grupo',
            id: 'Identificador',
            is_completed: 'Comprado',
            is_deleted: 'Removido',
            item_id: 'Item',
            location: 'Local de compra',
            name: 'Nome',
            new_date: 'Nova data',
            notes: 'Observações',
            planned_quantity: 'Quantidade planejada',
            purchased_quantity: 'Quantidade comprada',
            scheduled_date: 'Data agendada',
            status: 'Status',
            temp_id: 'Identificador temporário',
            template_id: 'Lista',
            unit_price: 'Valor unitário',
            updated_at: 'Atualizado em',
            user_id: 'Usuário',
            version: 'Versão',
        };
        return labels[key] || key;
    }

    function valueLabel(key, value) {
        if (value === true) return 'Sim';
        if (value === false) return 'Não';
        if (key === 'unit_price' || key === 'budget') {
            const number = Number(value);
            return Number.isFinite(number) ? `R$ ${number.toFixed(2)}` : value;
        }
        if (key === 'action') {
            return operationLabel({ action: value });
        }
        if (key === 'status') {
            const labels = {
                scheduled: 'Agendada',
                in_progress: 'Em andamento',
                completed: 'Finalizada',
                cancelled: 'Cancelada',
            };
            return labels[value] || value;
        }
        return value;
    }

    function operationStatusLabel(operation) {
        const statusName = classifyOperation(operation);
        if (statusName === 'conflict') return 'Conflito';
        if (statusName === 'failed') return 'Falha';
        return 'Pendente';
    }

    function resolutionLabel(resolution) {
        const labels = {
            discard_local: 'Servidor mantido',
            retry_local: 'Alteração local reenviada',
            local_applied: 'Alteração local aplicada',
            remote_applied: 'Servidor mantido',
        };
        return labels[resolution] || resolution || 'Pendente';
    }

    function fieldLabelForPayload(key, payload) {
        if (key === 'id' && payload?.execution_id) return 'Item';
        return fieldLabel(key);
    }

    function orderedPayloadEntries(payload) {
        const preferred = [
            'execution_id',
            'item_id',
            'id',
            'action',
            'name',
            'category_id',
            'planned_quantity',
            'purchased_quantity',
            'unit_price',
            'location',
            'notes',
            'scheduled_date',
            'budget',
            'status',
            'version',
        ];
        return Object.entries(payload).sort(function ([left], [right]) {
            const leftIndex = preferred.indexOf(left);
            const rightIndex = preferred.indexOf(right);
            if (leftIndex !== -1 || rightIndex !== -1) {
                if (leftIndex === -1) return 1;
                if (rightIndex === -1) return -1;
                return leftIndex - rightIndex;
            }
            return left.localeCompare(right);
        });
    }

    function formatPayload(payload) {
        if (!payload || typeof payload !== 'object') return '';
        return orderedPayloadEntries(payload)
            .filter(function ([, value]) { return value !== null && value !== undefined && value !== ''; })
            .map(function ([key, value]) { return `${fieldLabelForPayload(key, payload)}: ${valueLabel(key, value)}`; })
            .slice(0, 6)
            .join(' · ');
    }

    function filterOperations(operations) {
        if (syncFilter === 'all') return operations;
        return operations.filter(function (operation) {
            return classifyOperation(operation) === syncFilter;
        });
    }

    async function resolveOperation(operationId, resolution) {
        const db = await openDatabase();
        const operation = await getRecord(db, 'pending_operations', operationId);
        if (!operation) {
            db.close();
            return;
        }

        if (resolution === 'discard_local') {
            await deleteRecord(db, 'pending_operations', operationId);
        }
        if (resolution === 'retry_local') {
            await putRecord(db, 'pending_operations', Object.assign({}, operation, {
                status: 'pending',
                requires_manual_intervention: false,
                conflict: null,
                error_message: null,
                updated_at: new Date().toISOString(),
            }));
        }
        db.close();
        if (operation.conflict?.audit_id && navigator.onLine) {
            recordConflictResolution(operation.conflict.audit_id, resolution).catch(function () {});
        }
        await updatePendingCount();
        if (resolution === 'discard_local' && navigator.onLine) {
            refreshSnapshot().catch(function () {});
        }
        if (resolution === 'retry_local') {
            runAutomaticSync({ manual: true });
        }
    }

    async function recordConflictResolution(auditId, resolution) {
        const response = await fetch(`${SYNC_CONFLICTS_URL}/${auditId}/resolution`, {
            method: 'POST',
            headers: {
                Accept: 'application/json',
                'Content-Type': 'application/json',
            },
            credentials: 'same-origin',
            body: JSON.stringify({ resolution: resolution }),
        });
        if (response.ok) {
            renderConflictAuditHistory().catch(function () {});
        }
    }

    function operationCard(operation) {
        const statusName = classifyOperation(operation);
        const conflict = operation.conflict || {};
        const payload = formatPayload(operation.payload);
        const remote = formatPayload(conflict.remote);
        const failure = conflict.message || operation.error_message || (
            Number(operation.tentativas || 0) > 0 ? 'Aguardando nova tentativa automática.' : ''
        );

        return [
            `<article class="sync-operation sync-operation-${statusName}" data-operation-id="${escapeHtml(operation.id)}">`,
            '<div class="sync-operation-main">',
            `<span class="sync-operation-status">${operationStatusLabel(operation)}</span>`,
            `<h2>${escapeHtml(operationLabel(operation))}</h2>`,
            `<p>${escapeHtml(entityLabel(operation.entidade || operation.entity))} #${escapeHtml(operation.entidade_id || operation.entity_id)}</p>`,
            payload ? `<dl><dt>Local</dt><dd>${escapeHtml(payload)}</dd></dl>` : '',
            remote ? `<dl><dt>Servidor</dt><dd>${escapeHtml(remote)}</dd></dl>` : '',
            failure ? `<p class="sync-operation-message">${escapeHtml(failure)}</p>` : '',
            `<small>Criada em ${formatDate(operation.created_at)} · ${Number(operation.tentativas || 0)} tentativa(s)</small>`,
            '</div>',
            '<div class="sync-operation-actions">',
            statusName === 'conflict' || statusName === 'failed'
                ? `<button type="button" class="btn btn-sm btn-primary" data-sync-resolve="retry_local" data-operation-id="${escapeHtml(operation.id)}">Tentar local</button>`
                : '',
            statusName === 'conflict' || statusName === 'failed'
                ? `<button type="button" class="btn btn-sm btn-outline-secondary" data-sync-resolve="discard_local" data-operation-id="${escapeHtml(operation.id)}">Usar servidor</button>`
                : '',
            '</div>',
            '</article>',
        ].join('');
    }

    async function renderSyncCenter(operations) {
        if (!syncCenter || !syncOperationList) return;
        const snapshotOperations = operations || (await readSnapshot()).pending_operations;
        const sorted = sortOperationsByCreation(snapshotOperations);
        const visible = filterOperations(sorted);
        const pendingCount = sorted.filter(function (operation) {
            return classifyOperation(operation) === 'pending';
        }).length;
        const failedCount = sorted.filter(function (operation) {
            return classifyOperation(operation) === 'failed';
        }).length;
        const conflictCount = sorted.filter(function (operation) {
            return classifyOperation(operation) === 'conflict';
        }).length;

        if (syncCountPending) syncCountPending.textContent = String(pendingCount);
        if (syncCountFailed) syncCountFailed.textContent = String(failedCount);
        if (syncCountConflict) syncCountConflict.textContent = String(conflictCount);

        if (syncEmpty) {
            syncEmpty.hidden = visible.length > 0;
        }
        const cards = visible.map(operationCard).join('');
        syncOperationList.querySelectorAll('.sync-operation').forEach(function (card) {
            card.remove();
        });
        syncOperationList.insertAdjacentHTML('beforeend', cards);
    }

    function auditCard(conflict) {
        const local = formatPayload(conflict.local_state);
        const remote = formatPayload(conflict.remote_state);
        const resolution = resolutionLabel(conflict.resolution_applied);
        const userName = conflict.user_name || (conflict.user_id ? `usuário #${conflict.user_id}` : 'usuário não identificado');

        return [
            '<article class="sync-audit-card">',
            '<div>',
            `<span class="sync-operation-status">${escapeHtml(resolution)}</span>`,
            `<h3>${escapeHtml(operationTypeLabel(conflict.operation_type))}</h3>`,
            `<p>${escapeHtml(conflict.message)}</p>`,
            `<small>Compra ${escapeHtml(conflict.execution_id || 'n/a')} · ${escapeHtml(userName)} · ${formatDate(conflict.created_at)}</small>`,
            local ? `<dl><dt>Local</dt><dd>${escapeHtml(local)}</dd></dl>` : '',
            remote ? `<dl><dt>Servidor</dt><dd>${escapeHtml(remote)}</dd></dl>` : '',
            conflict.resolved_at ? `<small>Resolvido em ${formatDate(conflict.resolved_at)}</small>` : '',
            '</div>',
            '</article>',
        ].join('');
    }

    async function renderConflictAuditHistory() {
        if (!syncAuditList || !navigator.onLine) return;
        const response = await fetch(SYNC_CONFLICTS_URL, {
            headers: { Accept: 'application/json' },
            credentials: 'same-origin',
        });
        if (!response.ok) return;

        const data = await response.json();
        const conflicts = data.conflicts || [];
        if (syncAuditEmpty) {
            syncAuditEmpty.hidden = conflicts.length > 0;
        }
        syncAuditList.querySelectorAll('.sync-audit-card').forEach(function (card) {
            card.remove();
        });
        syncAuditList.insertAdjacentHTML('beforeend', conflicts.map(auditCard).join(''));
    }

    function setupSyncCenter() {
        if (!syncCenter) return;

        document.querySelectorAll('[data-sync-filter]').forEach(function (button) {
            button.addEventListener('click', function () {
                syncFilter = button.dataset.syncFilter || 'all';
                document.querySelectorAll('[data-sync-filter]').forEach(function (otherButton) {
                    otherButton.classList.toggle('btn-primary', otherButton === button);
                    otherButton.classList.toggle('btn-outline-primary', otherButton !== button);
                });
                renderSyncCenter().catch(function () {});
            });
        });

        syncOperationList.addEventListener('click', function (event) {
            const button = event.target.closest('[data-sync-resolve]');
            if (!button) return;
            resolveOperation(button.dataset.operationId, button.dataset.syncResolve).catch(function () {
                window.dispatchEvent(new CustomEvent('jaci:sync-error'));
            });
        });

        if (syncNowButton) {
            syncNowButton.addEventListener('click', function () {
                runAutomaticSync({ manual: true });
                renderSyncCenter().catch(function () {});
            });
        }
        if (syncAuditRefresh) {
            syncAuditRefresh.addEventListener('click', function () {
                renderConflictAuditHistory().catch(function () {});
            });
        }

        renderSyncCenter().catch(function () {});
        renderConflictAuditHistory().catch(function () {});
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

    function readExecutionOperationFromForm(form) {
        const formData = new FormData(form);
        const budget = normalizeNumber(formData.get('budget'));
        return {
            execution_id: Number(form.dataset.executionId),
            name: String(formData.get('name') || '').trim(),
            scheduled_date: String(formData.get('scheduled_date') || ''),
            budget: budget && budget > 0 ? budget : null,
        };
    }

    function markExecutionPageAsOfflineUpdated(operation) {
        document.querySelectorAll('[data-execution-name-label]').forEach(function (element) {
            element.textContent = operation.name;
        });
        document.querySelectorAll('[data-execution-date-label]').forEach(function (element) {
            element.textContent = operation.scheduled_date;
        });
        document.querySelectorAll('[data-execution-budget-label]').forEach(function (element) {
            element.textContent = operation.budget
                ? `R$ ${Number(operation.budget).toFixed(2)}`
                : 'Não definido';
        });

        const status = document.querySelector('[data-execution-sync-feedback]');
        if (status) {
            status.classList.remove('d-none');
        }
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

    function setupOfflineExecutionEditForms() {
        document.querySelectorAll('[data-offline-edit-execution]').forEach(function (form) {
            form.addEventListener('submit', function (event) {
                if (navigator.onLine) return;

                event.preventDefault();
                event.stopImmediatePropagation();

                if (form.dataset.executionStatus !== 'scheduled') {
                    window.dispatchEvent(new CustomEvent('jaci:sync-error'));
                    return;
                }

                const operation = readExecutionOperationFromForm(form);
                if (!operation.execution_id || !operation.name || !operation.scheduled_date) {
                    window.dispatchEvent(new CustomEvent('jaci:sync-error'));
                    return;
                }

                enqueueUpdateExecutionOperation(operation)
                    .then(function () {
                        markExecutionPageAsOfflineUpdated(operation);
                        hideContainingModal(form);
                        renderQueuedItemControl(form);
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

    function readEditItemOperationFromForm(form) {
        const formData = new FormData(form);
        const categoryId = normalizeNumber(formData.get('category_id'));
        return {
            execution_id: Number(form.dataset.executionId),
            item_id: Number(form.dataset.itemId),
            action: 'update_item',
            version: Number(formData.get('version')),
            name: String(formData.get('name') || '').trim(),
            planned_quantity: normalizeNumber(formData.get('planned_quantity')),
            category_id: categoryId && categoryId > 0 ? categoryId : null,
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

    function renderQueuedItemControl(element) {
        const button = element.matches('button') ? element : element.querySelector('button[type="submit"]');
        if (!button) return;

        button.classList.remove('btn-primary');
        button.classList.add('btn-outline-secondary');
        button.dataset.offlineQueued = 'true';
    }

    function offlineActionConfirmation(options) {
        return new Promise(function (resolve) {
            if (window.JaciConfirm) {
                window.JaciConfirm.show({
                    title: options.title || 'Confirmar',
                    message: options.message || 'Tem certeza?',
                    okLabel: options.okLabel || 'Confirmar',
                    okClass: options.okClass || 'btn-primary',
                    onConfirm: function () { resolve(true); },
                    onCancel: function () { resolve(false); },
                });
                return;
            }
            resolve(window.confirm(options.message || 'Tem certeza?'));
        });
    }

    function currentExecutionIdFromPage() {
        const container = document.querySelector('[data-current-execution-id]');
        if (container?.dataset.currentExecutionId) {
            return container.dataset.currentExecutionId;
        }
        const row = document.querySelector('[data-execution-item-row][data-execution-id]');
        return row?.dataset.executionId || null;
    }

    function roundMoney(value) {
        return Math.round((Number(value || 0) + Number.EPSILON) * 100) / 100;
    }

    function calculateExecutionTotal(items, executionId) {
        const currentId = Number(executionId);
        const total = items
            .filter(function (item) {
                return Number(item.execution_id) === currentId
                    && item.is_completed
                    && !item.is_deleted
                    && !item.offline_removed_at;
            })
            .reduce(function (sum, item) {
                return sum + roundMoney(
                    Number(item.purchased_quantity || 0) * Number(item.unit_price || 0)
                );
            }, 0);
        return roundMoney(total);
    }

    async function refreshLocalExecutionBudget(executionId, notify) {
        if (!executionId || !window.JaciExecutionBudget) return;
        const db = await openDatabase();
        const items = await readStore(db, 'execution_items');
        db.close();
        window.JaciExecutionBudget.updateTotal(
            calculateExecutionTotal(items, executionId),
            { notify: notify !== false }
        );
    }

    async function refreshCurrentExecutionFragments() {
        if (!navigator.onLine) return false;
        const executionId = currentExecutionIdFromPage();
        const itemsContainer = document.getElementById('items-container');
        if (!executionId || !itemsContainer) return false;

        const expandedIds = Array.from(itemsContainer.querySelectorAll('.collapse.show'))
            .filter(function (element) {
                return !element.hasAttribute('data-item-filter-forced-expanded');
            })
            .map(function (element) { return element.id; })
            .filter(Boolean);
        let response;
        try {
            response = await fetch(`/executions/${executionId}/items-fragment`, {
                headers: {
                    Accept: 'text/html',
                    'X-Collapse-State': expandedIds.join(','),
                },
                credentials: 'same-origin',
                cache: 'no-store',
            });
        } catch (error) {
            return false;
        }
        if (!response.ok) return false;

        const html = await response.text();
        const fragment = document.createElement('div');
        fragment.innerHTML = html;
        fragment.querySelectorAll('[hx-swap-oob]').forEach(function (outOfBand) {
            const target = outOfBand.id ? document.getElementById(outOfBand.id) : null;
            if (target && target !== outOfBand) {
                target.innerHTML = outOfBand.innerHTML;
            }
            outOfBand.remove();
        });
        itemsContainer.innerHTML = fragment.innerHTML;
        if (window.JaciExecutionBudget) {
            window.JaciExecutionBudget.refreshFromDocument({ notify: true });
        }

        const sidebar = document.getElementById('sidebar-container');
        if (sidebar) {
            fetch(`/executions/${executionId}/sidebar-fragment`, {
                headers: { Accept: 'text/html' },
                credentials: 'same-origin',
                cache: 'no-store',
            }).then(function (sidebarResponse) {
                if (!sidebarResponse.ok) return null;
                return sidebarResponse.text();
            }).then(function (sidebarHtml) {
                if (sidebarHtml !== null) sidebar.innerHTML = sidebarHtml;
            }).catch(function () {
                return null;
            });
        }
        return true;
    }

    function removeEmptyOfflineCategoryCard(row) {
        const card = row.closest('.card-jaci');
        row.remove();
        if (card && !card.querySelector('[data-execution-item-row]')) {
            card.remove();
        }
    }

    function reconcileAppliedOperationInDom(applied) {
        const operation = applied.operation || {};
        const result = applied.result || {};
        const itemId = operation.payload?.item_id || operation.entity_id || operation.entidade_id || result.item?.id;
        if (!itemId) return;

        const row = document.querySelector(`[data-execution-item-row][data-item-id="${itemId}"]`);
        if (!row) return;

        if (operation.action === 'remove_execution_item') {
            removeEmptyOfflineCategoryCard(row);
            return;
        }
        if (operation.action !== 'incomplete_item') return;

        row.classList.remove('opacity-75', 'is-offline-updated', 'is-offline-removed');
        row.dataset.itemFilterCompleted = 'false';
        row.dataset.itemFilterTotalPrice = '0';
        const check = row.querySelector('.check-jaci');
        if (check) check.classList.remove('checked');
        row.querySelectorAll('.text-strikethrough').forEach(function (element) {
            element.classList.remove('text-strikethrough');
        });
        const completedSummary = row.querySelector('[data-item-completed-summary]');
        if (completedSummary) completedSummary.remove();
        const incompleteForm = row.querySelector('[data-offline-incomplete-item]');
        if (incompleteForm) incompleteForm.remove();
        const badge = row.querySelector('[data-offline-item-badge]');
        if (badge) badge.classList.add('d-none');
    }

    function clearOfflineItemIndicators() {
        document.querySelectorAll('[data-execution-item-row].is-offline-updated, [data-execution-item-row].is-offline-removed')
            .forEach(function (row) {
                row.classList.remove('is-offline-updated', 'is-offline-removed');
                const badge = row.querySelector('[data-offline-item-badge]');
                if (badge) {
                    badge.classList.add('d-none');
                    badge.innerHTML = '<i class="bi bi-cloud-arrow-up-fill"></i> Comprado offline';
                }
                row.querySelectorAll('button, form button').forEach(function (button) {
                    button.disabled = false;
                });
            });
    }

    async function clearOfflineItemIndicatorsWhenSynced() {
        const pendingCount = await updatePendingCount();
        if (pendingCount === 0) {
            clearOfflineItemIndicators();
        }
    }

    function markItemRowAsOfflineUpdated(operation) {
        if (!operation?.item_id) return;
        const row = document.querySelector(`[data-execution-item-row][data-item-id="${operation.item_id}"]`);
        if (!row) return;

        row.classList.add('is-offline-updated');
        row.classList.toggle('opacity-75', operation.action === 'complete_item' || operation.action === 'remove_execution_item');
        row.classList.toggle('is-offline-removed', operation.action === 'remove_execution_item');

        const check = row.querySelector('.check-jaci');
        if (check) {
            check.classList.toggle('checked', operation.action === 'complete_item');
        }

        if (operation.action === 'update_item') {
            row.dataset.itemFilterName = operation.name;
            const nameLabel = row.querySelector('[data-item-name-label]');
            const plannedQuantityLabel = row.querySelector('[data-item-planned-quantity-label]');
            const notesLabel = row.querySelector('[data-item-notes-label]');
            const editButton = row.querySelector('[data-offline-edit-item]');
            if (nameLabel) nameLabel.textContent = operation.name;
            if (plannedQuantityLabel) plannedQuantityLabel.textContent = `${operation.planned_quantity}x`;
            if (notesLabel) notesLabel.textContent = operation.notes || '';
            if (editButton) {
                editButton.dataset.itemName = operation.name;
                editButton.dataset.plannedQuantity = operation.planned_quantity;
                editButton.dataset.categoryId = operation.category_id || '';
                editButton.dataset.notes = operation.notes || '';
            }
        }

        if (operation.action === 'incomplete_item') {
            row.dataset.itemFilterCompleted = 'false';
            row.dataset.itemFilterTotalPrice = '0';
            const completedSummary = row.querySelector('[data-item-completed-summary]');
            row.classList.remove('opacity-75');
            if (completedSummary) completedSummary.hidden = true;
        }

        if (operation.action === 'complete_item') {
            row.dataset.itemFilterCompleted = 'true';
            row.dataset.itemFilterTotalPrice = String(
                Number(operation.purchased_quantity || 0) * Number(operation.unit_price || 0)
            );
        }

        if (operation.action === 'remove_execution_item') {
            row.querySelectorAll('button, form button').forEach(function (button) {
                button.disabled = true;
            });
        }

        const badge = row.querySelector('[data-offline-item-badge]');
        if (badge) {
            badge.classList.remove('d-none');
            const labels = {
                complete_item: 'Comprado offline',
                incomplete_item: 'Não comprado offline',
                remove_execution_item: 'Removido offline',
                update_item: 'Alterado offline',
            };
            badge.innerHTML = `<i class="bi bi-cloud-arrow-up-fill"></i> ${labels[operation.action] || 'Alterado offline'}`;
        }
    }

    async function applyPersistedOfflineItemState() {
        const snapshot = await readSnapshot();
        snapshot.pending_operations.forEach(function (operation) {
            if (operation.entity !== 'execution_item' && operation.entidade !== 'execution_item') return;
            markItemRowAsOfflineUpdated(Object.assign({}, operation.payload, {
                action: operation.action,
                item_id: operation.payload?.item_id || operation.entity_id || operation.entidade_id,
            }));
        });
        snapshot.execution_items.forEach(function (item) {
            if (item.offline_removed_at || item.is_deleted) {
                markItemRowAsOfflineUpdated({ action: 'remove_execution_item', item_id: item.id });
            } else if (item.offline_updated_at && item.is_completed) {
                markItemRowAsOfflineUpdated({
                    action: 'complete_item',
                    item_id: item.id,
                    purchased_quantity: item.purchased_quantity,
                    unit_price: item.unit_price,
                });
            } else if (item.offline_updated_at) {
                markItemRowAsOfflineUpdated({
                    action: 'update_item',
                    item_id: item.id,
                    name: item.name,
                    planned_quantity: item.planned_quantity,
                    category_id: item.category_id,
                    notes: item.notes,
                });
            }
        });
        const currentExecutionId = Number(currentExecutionIdFromPage());
        const hasPendingItems = snapshot.pending_operations.some(function (operation) {
            const operationExecutionId = operation.payload?.execution_id;
            return Number(operationExecutionId) === currentExecutionId
                && (operation.entity === 'execution_item' || operation.entidade === 'execution_item');
        });
        if (!navigator.onLine || hasPendingItems) {
            refreshLocalExecutionBudget(currentExecutionIdFromPage(), false).catch(function () {});
        }
    }

    function itemLocationTimestamp(item) {
        return item.offline_updated_at
            || item.offline_created_at
            || item.updated_at
            || item.created_at
            || '1970-01-01T00:00:00.000Z';
    }

    async function getLastLocationForExecution(executionId, currentItemId) {
        const db = await openDatabase();
        const items = await readStore(db, 'execution_items');
        db.close();

        const itemId = String(currentItemId);
        const candidates = items.filter(function (item) {
            return Number(item.execution_id) === Number(executionId)
                && String(item.id) !== itemId
                && !item.is_deleted
                && item.location;
        }).sort(function (a, b) {
            return String(itemLocationTimestamp(b)).localeCompare(String(itemLocationTimestamp(a)));
        });
        return candidates[0]?.location || getLastLocationFromPage(executionId, currentItemId);
    }

    function getLastLocationFromPage(executionId, currentItemId) {
        const rows = Array.from(document.querySelectorAll('[data-execution-item-row][data-item-location]'));
        const currentId = String(currentItemId);
        const row = rows.reverse().find(function (candidate) {
            return String(candidate.dataset.executionId) === String(executionId)
                && String(candidate.dataset.itemId) !== currentId
                && candidate.dataset.itemLocation;
        });
        return row?.dataset.itemLocation || '';
    }

    async function openOfflineCompleteModal(button) {
        disableOfflineCompleteBootstrapTriggers();
        const modalEl = document.getElementById('offlineCompleteItemModal');
        if (!modalEl) return false;

        const form = modalEl.querySelector('[data-offline-complete-item-modal-form]');
        if (!form) return false;
        const lastLocation = button.dataset.location
            || await getLastLocationForExecution(button.dataset.executionId, button.dataset.itemId);

        form.dataset.executionId = button.dataset.executionId;
        form.dataset.itemId = button.dataset.itemId;
        form.dataset.forceOfflineSubmit = 'true';
        form.dataset.sourceButtonSelector = `[data-offline-complete-item][data-item-id="${button.dataset.itemId}"]`;
        form.querySelector('[name="version"]').value = button.dataset.version || '';
        form.querySelector('[name="purchased_quantity"]').value =
            button.dataset.purchasedQuantity || button.dataset.plannedQuantity || '1';
        form.querySelector('[name="unit_price"]').value = button.dataset.unitPrice || '';
        form.querySelector('[name="location"]').value = lastLocation || '';
        form.querySelector('[name="notes"]').value = button.dataset.notes || '';

        const title = modalEl.querySelector('#offlineCompleteItemModalLabel');
        if (title) {
            title.textContent = `${button.dataset.purchasedQuantity ? 'Editar compra' : 'Comprar'}: ${button.dataset.itemName || 'item'}`;
        }
        const planned = modalEl.querySelector('[data-offline-planned-quantity]');
        if (planned) {
            planned.textContent = button.dataset.plannedQuantity
                ? `Planejado: ${button.dataset.plannedQuantity}`
                : '';
        }

        showManualModal(modalEl);
        try {
            return await response.json();
        } catch (error) {
            return { status: 'applied' };
        }
    }

    function openOfflineEditModal(button) {
        const modalEl = document.getElementById('offlineEditItemModal');
        if (!modalEl) return false;

        const form = modalEl.querySelector('[data-offline-edit-item-modal-form]');
        if (!form) return false;

        form.dataset.executionId = button.dataset.executionId;
        form.dataset.itemId = button.dataset.itemId;
        form.dataset.forceOfflineSubmit = 'true';
        form.dataset.sourceButtonSelector = `[data-offline-edit-item][data-item-id="${button.dataset.itemId}"]`;
        form.querySelector('[name="version"]').value = button.dataset.version || '';
        form.querySelector('[name="name"]').value = button.dataset.itemName || '';
        form.querySelector('[name="planned_quantity"]').value = button.dataset.plannedQuantity || '1';
        form.querySelector('[name="category_id"]').value = button.dataset.categoryId || '';
        form.querySelector('[name="notes"]').value = button.dataset.notes || '';

        const title = modalEl.querySelector('#offlineEditItemModalLabel');
        if (title) {
            title.textContent = `Editar: ${button.dataset.itemName || 'item'}`;
        }

        showManualModal(modalEl);
        return true;
    }

    function showManualModal(modalEl) {
        closeManualModal();
        const backdrop = document.createElement('div');
        backdrop.className = 'modal-backdrop fade show';
        backdrop.dataset.jaciModalBackdrop = 'true';
        document.body.appendChild(backdrop);
        document.body.classList.add('modal-open');
        document.body.style.overflow = 'hidden';
        document.body.style.paddingRight = '0px';
        modalEl.hidden = false;
        modalEl.removeAttribute('aria-hidden');
        modalEl.setAttribute('aria-modal', 'true');
        modalEl.setAttribute('role', 'dialog');
        modalEl.style.display = 'block';
        modalEl.classList.add('show');
        modalEl.querySelector('input, textarea, button')?.focus();
    }

    function closeManualModal(modalEl) {
        const modal = modalEl || document.querySelector('.modal.show');
        if (modal) {
            modal.classList.remove('show');
            modal.style.display = 'none';
            modal.setAttribute('aria-hidden', 'true');
            modal.removeAttribute('aria-modal');
            modal.removeAttribute('role');
            modal.dispatchEvent(new Event('hidden.bs.modal'));
        }
        document.querySelectorAll('[data-jaci-modal-backdrop]').forEach(function (backdrop) {
            backdrop.remove();
        });
        document.body.classList.remove('modal-open');
        document.body.style.removeProperty('overflow');
        document.body.style.removeProperty('padding-right');
    }

    function hideContainingModal(element) {
        const modalEl = element.closest('.modal');
        if (!modalEl) return;
        closeManualModal(modalEl);
    }

    function setupOfflineCompleteModalControls() {
        document.addEventListener('click', function (event) {
            if (event.target.matches('[data-bs-dismiss="modal"]')) {
                event.preventDefault();
                const modalEl = event.target.closest('.modal');
                if (modalEl) closeManualModal(modalEl);
            }
        });
        document.addEventListener('keydown', function (event) {
            if (event.key === 'Escape') {
                closeManualModal();
            }
        });
    }

    window.JaciModal = {
        show: showManualModal,
        hide: closeManualModal,
    };

    function completeModalTargetMissing(button) {
        const targetSelector = button.getAttribute('data-bs-target') || button.dataset.onlineBsTarget;
        return Boolean(targetSelector && !document.querySelector(targetSelector));
    }

    function setOfflineCompleteBootstrapTriggersEnabled(enabled, missingOnly) {
        document.querySelectorAll('[data-offline-complete-item]').forEach(function (button) {
            if (missingOnly && !completeModalTargetMissing(button)) return;
            if (enabled) {
                if (button.dataset.onlineBsToggle) {
                    button.setAttribute('data-bs-toggle', button.dataset.onlineBsToggle);
                    delete button.dataset.onlineBsToggle;
                }
                if (button.dataset.onlineBsTarget) {
                    button.setAttribute('data-bs-target', button.dataset.onlineBsTarget);
                    delete button.dataset.onlineBsTarget;
                }
                return;
            }

            const toggle = button.getAttribute('data-bs-toggle');
            const target = button.getAttribute('data-bs-target');
            if (toggle) button.dataset.onlineBsToggle = toggle;
            if (target) button.dataset.onlineBsTarget = target;
            button.removeAttribute('data-bs-toggle');
            button.removeAttribute('data-bs-target');
        });
    }

    function disableOfflineCompleteBootstrapTriggers() {
        if (!navigator.onLine) {
            setOfflineCompleteBootstrapTriggersEnabled(false);
        }
    }

    function disableMissingCompleteModalTriggers() {
        setOfflineCompleteBootstrapTriggersEnabled(false, true);
    }

    function shouldUseOfflineCompleteModal(button) {
        if (!navigator.onLine) return true;
        return completeModalTargetMissing(button);
    }

    function handleOfflineCompleteItemClick(event) {
        const button = event.target.closest('[data-offline-complete-item]');
        if (!button || !shouldUseOfflineCompleteModal(button)) return;

        event.preventDefault();
        event.stopPropagation();
        event.stopImmediatePropagation();
        setOfflineCompleteBootstrapTriggersEnabled(false);
        openOfflineCompleteModal(button).catch(function () {
            window.dispatchEvent(new CustomEvent('jaci:sync-error'));
        });
    }

    function handleOfflineEditItemClick(event) {
        const button = event.target.closest('[data-offline-edit-item]');
        if (!button || navigator.onLine) return;

        event.preventDefault();
        event.stopPropagation();
        event.stopImmediatePropagation();

        if (!openOfflineEditModal(button)) {
            window.dispatchEvent(new CustomEvent('jaci:sync-error'));
        }
    }

    function setupOfflineItemOperations() {
        document.addEventListener('click', function (event) {
            const removeButton = event.target.closest('[data-offline-remove-item]');
            if (removeButton && !navigator.onLine) {
                event.preventDefault();
                event.stopImmediatePropagation();

                offlineActionConfirmation({
                    title: 'Remover item?',
                    message: removeButton.getAttribute('hx-confirm') || 'Remover item da compra?',
                    okLabel: removeButton.dataset.jaciConfirmOkLabel || 'Remover',
                    okClass: removeButton.dataset.jaciConfirmOkClass || 'btn-danger',
                }).then(function (confirmed) {
                    if (!confirmed) return;
                    const operation = readRemoveItemOperationFromButton(removeButton);
                    enqueueRemoveExecutionItemOperation(operation)
                        .then(function () {
                            renderQueuedItemControl(removeButton);
                            markItemRowAsOfflineUpdated(Object.assign({ action: 'remove_execution_item' }, operation));
                            renderOfflineSummary();
                        })
                        .catch(function () {
                            window.dispatchEvent(new CustomEvent('jaci:sync-error'));
                        });
                });
                return;
            }

            const editButton = event.target.closest('[data-offline-edit-item]');
            if (editButton && !navigator.onLine) {
                event.preventDefault();
                event.stopImmediatePropagation();

                if (!openOfflineEditModal(editButton)) {
                    window.dispatchEvent(new CustomEvent('jaci:sync-error'));
                }
                return;
            }

            const button = event.target.closest('[data-offline-complete-item]');
            if (!button || navigator.onLine) return;

            event.preventDefault();
            event.stopImmediatePropagation();

            handleOfflineCompleteItemClick(event);
        }, true);

        document.addEventListener('submit', function (event) {
            const completeForm = event.target.closest('[data-offline-complete-item-form]');
            const editForm = event.target.closest('[data-offline-edit-item-form]');
            const incompleteForm = event.target.closest('[data-offline-incomplete-item]');
            const forcedOfflineSubmit = completeForm?.dataset.forceOfflineSubmit === 'true';
            const forcedEditOfflineSubmit = editForm?.dataset.forceOfflineSubmit === 'true';
            if (
                (!completeForm && !editForm && !incompleteForm)
                || (navigator.onLine && !forcedOfflineSubmit && !forcedEditOfflineSubmit)
            ) return;

            event.preventDefault();
            event.stopImmediatePropagation();

            const form = completeForm || editForm || incompleteForm;
            const action = completeForm ? 'complete_item' : 'incomplete_item';
            if (incompleteForm && incompleteForm.dataset.offlineConfirmed !== 'true') {
                offlineActionConfirmation({
                    title: 'Marcar como não comprado?',
                    message: incompleteForm.getAttribute('hx-confirm') || 'Marcar item como não comprado?',
                    okLabel: incompleteForm.dataset.jaciConfirmOkLabel || 'Confirmar',
                    okClass: incompleteForm.dataset.jaciConfirmOkClass || 'btn-danger',
                }).then(function (confirmed) {
                    if (!confirmed) return;
                    incompleteForm.dataset.offlineConfirmed = 'true';
                    if (typeof incompleteForm.requestSubmit === 'function') {
                        incompleteForm.requestSubmit();
                    } else {
                        incompleteForm.dispatchEvent(new Event('submit', { bubbles: true, cancelable: true }));
                    }
                });
                return;
            }
            if (incompleteForm) delete incompleteForm.dataset.offlineConfirmed;
            const operation = editForm
                ? readEditItemOperationFromForm(form)
                : readItemOperationFromForm(form, action);
            if (editForm && (!operation.name || operation.planned_quantity <= 0)) {
                window.dispatchEvent(new CustomEvent('jaci:sync-error'));
                return;
            }
            const sourceSelector = completeForm?.dataset.sourceButtonSelector || editForm?.dataset.sourceButtonSelector;
            const sourceButton = sourceSelector
                ? document.querySelector(sourceSelector)
                : null;

            enqueueExecutionItemOperation(operation)
                .then(function () {
                    renderQueuedItemControl(sourceButton || form);
                    markItemRowAsOfflineUpdated(operation);
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
        if (window.JaciConfirm) {
            window.JaciConfirm.alert({
                title: 'Compra finalizada offline',
                message: 'A recorrência será processada quando a sincronização concluir.',
            });
        }
    }

    function setupOfflineFinalizeControls() {
        document.querySelectorAll('[data-offline-finalize-link]').forEach(function (link) {
            link.addEventListener('click', function (event) {
                if (navigator.onLine) return;

                event.preventDefault();
                const executionId = Number(link.dataset.executionId);
                countPendingItemsForExecution(executionId).then(function (pendingCount) {
                    if (pendingCount > 0) {
                        if (window.JaciConfirm) {
                            window.JaciConfirm.alert({
                                title: 'Itens pendentes',
                                message: 'Existem itens pendentes. Trate os pendentes antes de finalizar offline.',
                            });
                        }
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
        renderSyncCenter: renderSyncCenter,
        renderConflictAuditHistory: renderConflictAuditHistory,
        applyPersistedOfflineItemState: applyPersistedOfflineItemState,
        refreshCurrentExecutionFragments: refreshCurrentExecutionFragments,
        clearOfflineItemIndicators: clearOfflineItemIndicators,
        enqueueStartExecution: enqueueStartExecution,
        enqueueUpdateExecutionOperation: enqueueUpdateExecutionOperation,
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
    window.addEventListener('online', function () {
        setOfflineCompleteBootstrapTriggersEnabled(true);
        disableMissingCompleteModalTriggers();
    });
    window.addEventListener('offline', disableOfflineCompleteBootstrapTriggers);
    window.addEventListener('offline', renderOfflineSummary);
    window.addEventListener('jaci:sync-manual', function () {
        runAutomaticSync({ manual: true });
    });
    window.addEventListener('load', function () {
        setupOfflineStartForms();
        setupOfflineExecutionEditForms();
        setupOfflineAddItemForms();
        setupOfflineItemOperations();
        setupOfflineCompleteModalControls();
        disableMissingCompleteModalTriggers();
        disableOfflineCompleteBootstrapTriggers();
        setupOfflineFinalizeControls();
        setupSyncCenter();
        updatePendingCount().catch(function () {});
        applyPersistedOfflineItemState().catch(function () {});
        runAutomaticSync();
    });
    document.body.addEventListener('htmx:afterSwap', function () {
        applyPersistedOfflineItemState().catch(function () {});
    });
})();
