const CACHE_NAME = 'jaci-shell-v1';
const SHELL_ASSETS = [
    '/static/css/jaci-theme.css',
    '/static/js/jaci-confirm.js',
    '/static/js/execution-sync.js',
    '/static/js/sync-status.js',
    '/static/img/jaci-1.png',
    '/static/img/jaci-2.png',
];

self.addEventListener('install', function (event) {
    event.waitUntil(caches.open(CACHE_NAME).then(function (cache) {
        return cache.addAll(SHELL_ASSETS);
    }));
});

self.addEventListener('fetch', function (event) {
    if (event.request.method !== 'GET') return;

    event.respondWith(
        fetch(event.request)
            .then(function (response) {
                const copy = response.clone();
                caches.open(CACHE_NAME).then(function (cache) {
                    cache.put(event.request, copy);
                });
                return response;
            })
            .catch(function () {
                return caches.match(event.request);
            })
    );
});
