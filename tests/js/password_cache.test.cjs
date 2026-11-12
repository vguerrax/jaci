const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const test = require('node:test');

test('password routes bypass service worker cache for all methods', () => {
    const handlers = {};
    const context = vm.createContext({
        self: {location: {origin: 'https://jaci.example'}, addEventListener: (name, fn) => handlers[name] = fn},
        URL,
    });
    vm.runInContext(fs.readFileSync('app/static/js/service-worker.js', 'utf8'), context);
    for (const path of ['/reset-password?token=synthetic-secret', '/auth/reset-password',
        '/auth/forgot-password', '/auth/profile/password']) {
        for (const method of ['GET', 'POST']) {
            let intercepted = false;
            handlers.fetch({
                request: {method, url: 'https://jaci.example' + path, mode: 'navigate'},
                respondWith() { intercepted = true; },
            });
            assert.equal(intercepted, false, method + ' ' + path.split('?')[0]);
        }
    }
});


test('activation removes only sensitive requests from retained caches', async () => {
    const handlers = {};
    const safe = {url: 'https://jaci.example/executions/12'};
    const sensitive = {url: 'https://jaci.example/reset-password?token=synthetic-secret'};
    const entries = new Map([[safe.url, safe], [sensitive.url, sensitive]]);
    const retained = {
        async keys() { return [...entries.values()]; },
        async delete(request) { return entries.delete(request.url); },
    };
    const names = ['jaci-pages-v34-owner-synthetic', 'jaci-session-state'];
    let claimed = false;
    const context = vm.createContext({
        self: {
            location: {origin: 'https://jaci.example'},
            addEventListener(name, fn) { handlers[name] = fn; },
            clients: {async claim() { claimed = true; }},
        },
        caches: {
            async keys() { return names; },
            async open() { return retained; },
            async delete() { throw Error('retained cache must not be deleted'); },
        },
        URL,
    });
    vm.runInContext(fs.readFileSync('app/static/js/service-worker.js', 'utf8'), context);
    let completion;
    handlers.activate({waitUntil(value) { completion = value; }});
    await completion;
    assert.equal(claimed, true);
    assert.deepEqual([...entries.keys()], [safe.url]);
});
