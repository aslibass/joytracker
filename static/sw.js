const CACHE_NAME = 'joybucket-v1';
const ASSETS = [
    '/',
    '/static/manifest.json',
    'https://cdn.tailwindcss.com',
    'https://unpkg.com/htmx.org@1.9.10'
];

self.addEventListener('install', (event) => {
    event.waitUntil(
        caches.open(CACHE_NAME).then((cache) => {
            return cache.addAll(ASSETS);
        })
    );
});

self.addEventListener('fetch', (event) => {
    event.respondWith(
        caches.match(event.request).then((response) => {
            return response || fetch(event.request);
        })
    );
});
