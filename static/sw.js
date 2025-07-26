// Service Worker - PWA対応
const CACHE_NAME = 'social-insurance-news-v1';
const urlsToCache = [
  '/',
  '/static/style.css',
  '/static/app.js'
];

// Install
self.addEventListener('install', function(event) {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(function(cache) {
        return cache.addAll(urlsToCache);
      })
  );
});

// Fetch
self.addEventListener('fetch', function(event) {
  event.respondWith(
    caches.match(event.request)
      .then(function(response) {
        if (response) {
          return response;
        }
        return fetch(event.request);
      }
    )
  );
});