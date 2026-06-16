(function () {
    'use strict';

    const DB_NAME = 'jaci-offline-cache';
    const DB_VERSION = 10;
    const SNAPSHOT_URL = '/api/offline/snapshot';
    const START_EXECUTION_SYNC_URL = '/api/offline/operations/start-execution';
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

    function SyncFailure(message, requiresManualIntervention) {
        this.name = 'SyncFailure';
        this.message = message;
        this.requiresManualIntervention = requiresManualIntervention;
    }

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
            if (operation.requires_manual_intervention || isConflictOperation(operation)) {
                continue;
            }
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
            complete_item: 'Marcar item como comprado',
            incomplete_item: 'Desmarcar item',
            add_execution_item: 'Adicionar item',
            remove_execution_item: 'Remover item',
            finalize_execution: 'Finalizar compra',
        };
        return labels[operation.action] || operation.tipo || 'Operação offline';
    }

    function operationStatusLabel(operation) {
        const statusName = classifyOperation(operation);
        if (statusName === 'conflict') return 'Conflito';
        if (statusName === 'failed') return 'Falha';
        return 'Pendente';
    }

    function formatPayload(payload) {
        if (!payload || typeof payload !== 'object') return '';
        return Object.entries(payload)
            .filter(function ([, value]) { return value !== null && value !== undefined && value !== ''; })
            .map(function ([key, value]) { return `${key}: ${value}`; })
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
            `<p>${escapeHtml(operation.entidade || operation.entity)} #${escapeHtml(operation.entidade_id || operation.entity_id)}</p>`,
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
        const resolution = conflict.resolution_applied || 'Pendente';

        return [
            '<article class="sync-audit-card">',
            '<div>',
            `<span class="sync-operation-status">${escapeHtml(resolution)}</span>`,
            `<h3>${escapeHtml(conflict.operation_type)}</h3>`,
            `<p>${escapeHtml(conflict.message)}</p>`,
            `<small>Execução ${escapeHtml(conflict.execution_id || 'n/a')} · usuário #${escapeHtml(conflict.user_id)} · ${formatDate(conflict.created_at)}</small>`,
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
        renderSyncCenter: renderSyncCenter,
        renderConflictAuditHistory: renderConflictAuditHistory,
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
        setupSyncCenter();
        updatePendingCount().catch(function () {});
        runAutomaticSync();
    });
})();
