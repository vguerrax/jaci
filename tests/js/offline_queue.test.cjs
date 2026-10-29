'use strict';

const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const { IDBFactory } = require('fake-indexeddb');

const source = fs.readFileSync(path.join(__dirname, '../../app/static/js/offline-cache.js'), 'utf8');
const plain = value => JSON.parse(JSON.stringify(value));
const response = (body, status = 200) => ({ ok: status < 400, status, json: async () => plain(body) });
const completion = (itemId = 42, quantity = 2) => ({
    action: 'complete_item', execution_id: 1, item_id: itemId,
    purchased_quantity: quantity, unit_price: 10.5, location: 'Mercado teste',
    notes: 'Sintético', version: 1,
});
const snapshot = () => ({
    schema_version: 1, generated_at: '2026-10-29T12:00:00Z',
    groups: [{ id: 1, name: 'Grupo sintético' }],
    executions: [{ id: 1, group_id: 1, status: 'em_andamento' }],
    execution_items: [80, 7, 42].map(id => ({
        id, execution_id: 1, name: 'Item teste', planned_quantity: 1,
        is_completed: false, version: 1,
    })),
});

// Somente DOM/rede são simulados; transações reais de fake-indexeddb e o IIFE
// de produção ficam intactos. A cobertura de browser real pertence à BL-0011.
function browser(indexedDB = new IDBFactory(), storage = new Map()) {
    const calls = [];
    const events = [];
    let tick = 0;
    let handler = async url => {
        assert.equal(url, '/api/offline/snapshot');
        return response(snapshot());
    };
    const navigator = { onLine: false };
    const document = {
        getElementById: () => null, querySelector: () => null,
        querySelectorAll: () => [], addEventListener() {},
        body: { addEventListener() {} },
    };
    const window = {
        indexedDB, location: { pathname: '/executions/1' },
        addEventListener() {}, dispatchEvent: event => events.push(event.type),
        setTimeout: () => 1, clearTimeout() {},
    };
    const context = {
        window, document, navigator, indexedDB,
        localStorage: {
            getItem: key => storage.get(key) ?? null,
            setItem: (key, value) => storage.set(key, String(value)),
            removeItem: key => storage.delete(key),
        },
        CustomEvent: class { constructor(type) { this.type = type; } },
        Date: class extends Date {
            constructor(...args) { super(...(args.length ? args : [1793275200000 + tick++])); }
        },
        fetch: async (url, options = {}) => {
            const call = { url, method: options.method || 'GET',
                payload: options.body ? JSON.parse(options.body) : null };
            calls.push(call);
            return handler(url, call);
        },
    };
    vm.runInNewContext(source, context, { filename: 'app/static/js/offline-cache.js' });
    return {
        cache: window.JaciOfflineCache, navigator, calls, events, indexedDB, storage,
        respond: callback => { handler = callback; },
        posts: () => calls.filter(call => call.method === 'POST'),
    };
}

async function prepared() {
    const b = browser();
    b.navigator.onLine = true;
    await b.cache.refresh();
    b.navigator.onLine = false;
    b.calls.length = 0;
    return b;
}

test('FL-09: enqueue persiste antes de rede e sobrevive à recarga', { timeout: 5000 }, async () => {
    const b = await prepared();
    const payload = completion();
    await b.cache.enqueueExecutionItemOperation(payload);
    await b.cache.syncPending();
    assert.equal(b.calls.length, 0);

    const reloaded = browser(b.indexedDB, b.storage);
    const state = await reloaded.cache.read();
    assert.equal(state.pending_operations.length, 1);
    const queued = state.pending_operations[0];
    assert.equal(queued.status, 'pending');
    assert.equal(queued.tentativas, 0);
    assert.deepEqual(plain(queued.payload), payload);
    const item = state.execution_items.find(item => item.id === 42);
    assert.equal(item.is_completed, true);
    assert.equal(item.purchased_quantity, 2);
    assert.equal(item.unit_price, 10.5);
    assert.equal(item.offline_base_version, 1);
    assert.equal(item.version, 2);
    assert.equal(reloaded.calls.length, 0);
});

test('FL-09: alterações do mesmo item preservam a versão base', { timeout: 5000 }, async () => {
    const b = await prepared();
    await b.cache.enqueueExecutionItemOperation(completion());
    await b.cache.enqueueExecutionItemOperation({ ...completion(42, 3), version: 2 });
    const state = await b.cache.read();
    assert.equal(state.pending_operations.length, 1);
    assert.equal(state.pending_operations[0].payload.version, 1);
    assert.equal(state.pending_operations[0].payload.purchased_quantity, 3);
    assert.equal(state.execution_items.find(item => item.id === 42).purchased_quantity, 3);
});

test('FL-09: reconexão envia por criação e remove somente após confirmação', { timeout: 5000 }, async () => {
    const b = await prepared();
    for (const id of [80, 7]) await b.cache.enqueueExecutionItemOperation(completion(id));
    b.navigator.onLine = true;
    b.respond(async (url, call) => {
        assert.equal(url, '/api/offline/operations/execution-item');
        const pending = (await b.cache.read()).pending_operations;
        assert(pending.some(op => op.payload.item_id === call.payload.item_id));
        assert.deepEqual(call.payload, completion(call.payload.item_id));
        return response({ status: 'applied' });
    });
    await b.cache.syncPending();
    assert.deepEqual(b.posts().map(call => call.payload.item_id), [80, 7]);
    assert.equal((await b.cache.read()).pending_operations.length, 0);
    assert(b.events.includes('jaci:sync-success'));
});

test('FL-09: falha de rede retém a operação e impede ultrapassagem na fila', { timeout: 5000 }, async () => {
    const b = await prepared();
    for (const id of [80, 7, 42]) await b.cache.enqueueExecutionItemOperation(completion(id));
    b.navigator.onLine = true;
    b.respond(async (_url, call) => {
        if (call.payload.item_id === 7) throw new TypeError('Rede sintética indisponível');
        return response({ status: 'applied' });
    });
    await assert.rejects(b.cache.syncPending(), error => error.requiresManualIntervention === false);
    let state = await b.cache.read();
    assert.deepEqual(state.pending_operations.map(op => op.payload.item_id).sort((a, b) => a - b), [7, 42]);
    const failed = state.pending_operations.find(op => op.payload.item_id === 7);
    assert.equal(failed.tentativas, 1);
    assert.deepEqual(plain(failed.payload), completion(7));
    assert.equal(state.pending_operations.find(op => op.payload.item_id === 42).tentativas, 0);
    assert.deepEqual(b.posts().map(call => call.payload.item_id), [80, 7]);
    b.respond(async () => response({ status: 'applied' }));
    await b.cache.syncPending();
    state = await b.cache.read();
    assert.equal(state.pending_operations.length, 0);
    assert.deepEqual(b.posts().map(call => call.payload.item_id), [80, 7, 7, 42]);
});

test('FL-09: sessão expirada não confirma nem descarta a alteração', { timeout: 5000 }, async () => {
    const b = await prepared();
    await b.cache.enqueueExecutionItemOperation(completion());
    b.navigator.onLine = true;
    b.respond(async () => response({ detail: 'Não autenticado' }, 401));
    await b.cache.syncPending();
    const pending = (await b.cache.read()).pending_operations;
    assert.equal(pending.length, 1);
    assert.deepEqual(plain(pending[0].payload), completion());
});

test('FL-09: syncNow simultâneo não duplica o envio no mesmo contexto', { timeout: 5000 }, async () => {
    const b = await prepared();
    await b.cache.enqueueExecutionItemOperation(completion());
    b.navigator.onLine = true;
    let release;
    const ack = new Promise(resolve => { release = resolve; });
    let reached;
    const posting = new Promise(resolve => { reached = resolve; });
    b.respond(async (url) => {
        if (url === '/api/offline/snapshot') return response(snapshot());
        reached();
        await ack;
        return response({ status: 'applied' });
    });
    const first = b.cache.syncNow();
    await posting;
    await b.cache.syncNow();
    assert.equal(b.posts().length, 1);
    assert.equal((await b.cache.read()).pending_operations.length, 1);
    release();
    await first;
    assert.equal(b.posts().length, 1);
    assert.equal((await b.cache.read()).pending_operations.length, 0);
});

test('FL-09: 409 preserva versões local/remota e exige resolução explícita', { timeout: 5000 }, async () => {
    const b = await prepared();
    const local = completion();
    const remote = { id: 42, name: 'Item remoto', version: 2, purchased_quantity: 5, unit_price: 12 };
    await b.cache.enqueueExecutionItemOperation(local);
    b.navigator.onLine = true;
    b.respond(async () => response({ detail: {
        type: 'sync_conflict', message: 'Versão divergente', reason: 'version_mismatch',
        local, remote,
    } }, 409));
    await assert.rejects(b.cache.syncPending(), error => error.requiresManualIntervention === true);
    const reloaded = browser(b.indexedDB, b.storage);
    reloaded.navigator.onLine = true;
    const state = await reloaded.cache.read();
    assert.equal(state.pending_operations.length, 1);
    const conflict = state.pending_operations[0];
    assert.equal(conflict.status, 'conflict');
    assert.equal(conflict.requires_manual_intervention, true);
    assert.equal(conflict.tentativas, 1);
    assert.deepEqual(plain(conflict.payload), local);
    assert.deepEqual(plain(conflict.conflict.local), local);
    assert.deepEqual(plain(conflict.conflict.remote), remote);
    assert.equal(state.execution_items.find(item => item.id === 42).purchased_quantity, 2);
    await reloaded.cache.syncPending();
    assert.equal(reloaded.posts().length, 0);
    assert.equal((await reloaded.cache.read()).pending_operations.length, 1);
});
