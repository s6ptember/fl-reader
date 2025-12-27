const CACHE_VERSION = 'v1.0.0';
const CACHE_NAME = `lumina-reader-${CACHE_VERSION}`;

// Файлы для предварительного кэширования (статика)
const PRECACHE_URLS = [
  '/',
  '/static/css/output.css',
  '/static/js/htmx.min.js',
  '/static/js/alpine.min.js',
  '/static/favicon.svg',
  '/static/manifest.json',
  '/offline/',
];

// Паттерны для динамического кэширования
const CACHE_PATTERNS = {
  // Статические файлы - Cache First
  static: /\.(css|js|svg|woff2?|ttf|eot)$/,
  // Изображения - Cache First
  images: /\.(png|jpg|jpeg|gif|webp|ico)$/,
  // API и динамический контент - Network First
  dynamic: /\/(book|search|last-read)/,
  // Обложки книг - Cache First
  covers: /\/media\/covers\//,
  // Файлы книг - Cache First (для offline чтения)
  books: /\/media\/books\//,
};

// Установка Service Worker
self.addEventListener('install', (event) => {
  console.log('[SW] Installing service worker...');

  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => {
        console.log('[SW] Precaching app shell');
        return cache.addAll(PRECACHE_URLS.map(url => new Request(url, {
          credentials: 'same-origin'
        })));
      })
      .then(() => {
        console.log('[SW] Installation complete');
        return self.skipWaiting();
      })
      .catch((error) => {
        console.error('[SW] Precaching failed:', error);
      })
  );
});

// Активация и очистка старых кэшей
self.addEventListener('activate', (event) => {
  console.log('[SW] Activating service worker...');

  event.waitUntil(
    caches.keys()
      .then((cacheNames) => {
        return Promise.all(
          cacheNames
            .filter((name) => name.startsWith('lumina-reader-') && name !== CACHE_NAME)
            .map((name) => {
              console.log('[SW] Deleting old cache:', name);
              return caches.delete(name);
            })
        );
      })
      .then(() => {
        console.log('[SW] Activation complete');
        return self.clients.claim();
      })
  );
});

// Fetch - стратегии кэширования
self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);

  // Игнорируем не-GET запросы
  if (request.method !== 'GET') {
    return;
  }

  // Игнорируем chrome extensions и другие схемы
  if (!url.protocol.startsWith('http')) {
    return;
  }

  event.respondWith(
    handleFetch(request, url)
  );
});

async function handleFetch(request, url) {
  try {
    // Статические файлы и изображения - Cache First
    if (
      CACHE_PATTERNS.static.test(url.pathname) ||
      CACHE_PATTERNS.images.test(url.pathname) ||
      CACHE_PATTERNS.covers.test(url.pathname) ||
      CACHE_PATTERNS.books.test(url.pathname)
    ) {
      return await cacheFirst(request);
    }

    // Динамический контент - Network First
    if (CACHE_PATTERNS.dynamic.test(url.pathname)) {
      return await networkFirst(request);
    }

    // HTML страницы - Network First с offline fallback
    if (request.headers.get('accept')?.includes('text/html')) {
      return await networkFirstWithOffline(request);
    }

    // Все остальное - Network First
    return await networkFirst(request);
  } catch (error) {
    console.error('[SW] Fetch error:', error);
    return await offlineResponse(request);
  }
}

// Cache First стратегия (для статики)
async function cacheFirst(request) {
  const cached = await caches.match(request);
  if (cached) {
    return cached;
  }

  try {
    const response = await fetch(request);
    if (response.ok) {
      const cache = await caches.open(CACHE_NAME);
      cache.put(request, response.clone());
    }
    return response;
  } catch (error) {
    console.log('[SW] Cache first failed:', request.url);
    throw error;
  }
}

// Network First стратегия (для динамики)
async function networkFirst(request) {
  try {
    const response = await fetch(request);
    if (response.ok) {
      const cache = await caches.open(CACHE_NAME);
      cache.put(request, response.clone());
    }
    return response;
  } catch (error) {
    const cached = await caches.match(request);
    if (cached) {
      return cached;
    }
    throw error;
  }
}

// Network First с offline страницей
async function networkFirstWithOffline(request) {
  try {
    const response = await fetch(request);
    if (response.ok) {
      const cache = await caches.open(CACHE_NAME);
      cache.put(request, response.clone());
    }
    return response;
  } catch (error) {
    const cached = await caches.match(request);
    if (cached) {
      return cached;
    }
    // Возвращаем offline страницу
    const offlinePage = await caches.match('/offline/');
    if (offlinePage) {
      return offlinePage;
    }
    throw error;
  }
}

// Offline ответ
async function offlineResponse(request) {
  // Если это HTML, возвращаем offline страницу
  if (request.headers.get('accept')?.includes('text/html')) {
    const offlinePage = await caches.match('/offline/');
    if (offlinePage) {
      return offlinePage;
    }
  }

  // Иначе возвращаем кэшированную версию
  const cached = await caches.match(request);
  if (cached) {
    return cached;
  }

  // Базовый offline ответ
  return new Response('Offline', {
    status: 503,
    statusText: 'Service Unavailable',
    headers: new Headers({
      'Content-Type': 'text/plain',
    }),
  });
}

// Обработка сообщений от клиента
self.addEventListener('message', (event) => {
  if (event.data && event.data.type === 'SKIP_WAITING') {
    self.skipWaiting();
  }

  if (event.data && event.data.type === 'CACHE_BOOK') {
    // Кэшируем конкретную книгу для offline чтения
    const bookUrl = event.data.url;
    caches.open(CACHE_NAME).then(cache => {
      cache.add(bookUrl).then(() => {
        console.log('[SW] Book cached for offline:', bookUrl);
      });
    });
  }

  if (event.data && event.data.type === 'CLEAR_CACHE') {
    // Очистка всего кэша
    caches.keys().then(names => {
      names.forEach(name => caches.delete(name));
    });
  }
});

// Background Sync для отправки прогресса чтения
self.addEventListener('sync', (event) => {
  if (event.tag === 'sync-reading-progress') {
    event.waitUntil(syncReadingProgress());
  }
});

async function syncReadingProgress() {
  // Здесь можно синхронизировать прогресс чтения с сервером
  console.log('[SW] Syncing reading progress...');
}

// Периодическая синхронизация (требует permission)
self.addEventListener('periodicsync', (event) => {
  if (event.tag === 'update-library') {
    event.waitUntil(updateLibrary());
  }
});

async function updateLibrary() {
  console.log('[SW] Updating library in background...');
  // Обновляем библиотеку в фоне
}

// Push уведомления (для будущих фич)
self.addEventListener('push', (event) => {
  const options = {
    body: event.data ? event.data.text() : 'Новое уведомление',
    icon: '/static/icons/icon-192.png',
    badge: '/static/icons/badge-72.png',
    vibrate: [200, 100, 200],
    tag: 'lumina-notification',
    actions: [
      { action: 'open', title: 'Открыть' },
      { action: 'close', title: 'Закрыть' }
    ]
  };

  event.waitUntil(
    self.registration.showNotification('Lumina Reader', options)
  );
});

// Клик по уведомлению
self.addEventListener('notificationclick', (event) => {
  event.notification.close();

  if (event.action === 'open') {
    event.waitUntil(
      clients.openWindow('/')
    );
  }
});

console.log('[SW] Service Worker loaded');
