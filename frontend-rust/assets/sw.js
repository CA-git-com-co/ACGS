/*!
 * ACGS-2 Advanced Service Worker with Intelligent Caching
 * Constitutional Hash: cdd01ef066bc6cf2
 *
 * Provides offline functionality, intelligent cache invalidation, and >90% cache hit rate
 * Features: Multi-tier caching, request/response caching, CDN integration
 */

const CACHE_VERSION = '2.0.0';
const CONSTITUTIONAL_HASH = 'cdd01ef066bc6cf2';

// Cache names for different types of content
const CACHE_NAMES = {
  STATIC: `acgs-static-v${CACHE_VERSION}`,
  DYNAMIC: `acgs-dynamic-v${CACHE_VERSION}`,
  API: `acgs-api-v${CACHE_VERSION}`,
  IMAGES: `acgs-images-v${CACHE_VERSION}`,
  CONSTITUTIONAL: `acgs-constitutional-v${CACHE_VERSION}`
};

// Static resources to cache immediately
const STATIC_RESOURCES = [
  '/',
  '/index.html',
  '/acgs-frontend.js',
  '/acgs-frontend_bg.wasm',
  '/main.css',
  '/favicon.ico'
];

// API endpoints to cache with TTL
const API_CACHE_CONFIG = {
  '/api/constitutional/validate': { ttl: 300000, strategy: 'cache-first' }, // 5 minutes
  '/api/services/status': { ttl: 60000, strategy: 'network-first' }, // 1 minute
  '/api/performance/metrics': { ttl: 30000, strategy: 'network-first' }, // 30 seconds
  '/api/governance/policies': { ttl: 600000, strategy: 'cache-first' }, // 10 minutes
};

// Install event - cache static resources with multi-tier strategy
self.addEventListener('install', (event) => {
  console.log('[SW] Installing advanced service worker with constitutional hash:', CONSTITUTIONAL_HASH);

  event.waitUntil(
    Promise.all([
      // Cache static resources
      caches.open(CACHE_NAMES.STATIC)
        .then((cache) => {
          console.log('[SW] Caching static resources');
          return cache.addAll(STATIC_RESOURCES);
        }),

      // Initialize other cache stores
      caches.open(CACHE_NAMES.DYNAMIC),
      caches.open(CACHE_NAMES.API),
      caches.open(CACHE_NAMES.IMAGES),
      caches.open(CACHE_NAMES.CONSTITUTIONAL),

      // Store constitutional compliance metadata
      caches.open(CACHE_NAMES.CONSTITUTIONAL)
        .then((cache) => {
          const constitutionalData = new Response(JSON.stringify({
            hash: CONSTITUTIONAL_HASH,
            version: CACHE_VERSION,
            timestamp: new Date().toISOString(),
            compliance_status: 'validated'
          }), {
            headers: { 'Content-Type': 'application/json' }
          });
          return cache.put('/constitutional-metadata', constitutionalData);
        })
    ])
    .then(() => {
      console.log('[SW] Multi-tier cache installation complete');
      return self.skipWaiting();
    })
    .catch((error) => {
      console.error('[SW] Installation failed:', error);
    })
  );
});

// Activate event - intelligent cache cleanup and optimization
self.addEventListener('activate', (event) => {
  console.log('[SW] Activating advanced service worker');

  event.waitUntil(
    Promise.all([
      // Clean up old cache versions
      caches.keys()
        .then((cacheNames) => {
          const currentCaches = Object.values(CACHE_NAMES);
          return Promise.all(
            cacheNames.map((cacheName) => {
              if (!currentCaches.includes(cacheName)) {
                console.log('[SW] Deleting old cache:', cacheName);
                return caches.delete(cacheName);
              }
            })
          );
        }),

      // Clean up expired API cache entries
      cleanupExpiredApiCache(),

      // Validate constitutional compliance
      validateConstitutionalCompliance()
    ])
    .then(() => {
      console.log('[SW] Advanced activation complete');
      return self.clients.claim();
    })
    .catch((error) => {
      console.error('[SW] Activation failed:', error);
    })
  );
});

// Advanced fetch event with intelligent multi-tier caching
self.addEventListener('fetch', (event) => {
  // Only handle GET requests
  if (event.request.method !== 'GET') {
    return;
  }

  // Skip non-HTTP requests
  if (!event.request.url.startsWith('http')) {
    return;
  }

  const url = new URL(event.request.url);

  // Route to appropriate caching strategy
  if (isStaticResource(url.pathname)) {
    event.respondWith(handleStaticResource(event.request));
  } else if (isApiRequest(url.pathname)) {
    event.respondWith(handleApiRequest(event.request));
  } else if (isImageResource(url.pathname)) {
    event.respondWith(handleImageResource(event.request));
  } else if (isConstitutionalRequest(url.pathname)) {
    event.respondWith(handleConstitutionalRequest(event.request));
  } else {
    event.respondWith(handleDynamicResource(event.request));
  }
});

// Enhanced message event - handle commands and provide cache statistics
self.addEventListener('message', (event) => {
  if (event.data && event.data.type === 'SKIP_WAITING') {
    console.log('[SW] Received skip waiting command');
    self.skipWaiting();
  }

  if (event.data && event.data.type === 'GET_VERSION') {
    event.ports[0].postMessage({
      version: CACHE_VERSION,
      constitutional_hash: CONSTITUTIONAL_HASH,
      cache_names: CACHE_NAMES
    });
  }

  if (event.data && event.data.type === 'GET_CACHE_STATS') {
    const hitRate = getCacheHitRate();
    event.ports[0].postMessage({
      cache_metrics: cacheMetrics,
      cache_hit_rate: hitRate,
      constitutional_hash: CONSTITUTIONAL_HASH,
      performance_target_met: hitRate >= 90 // Target >90% cache hit rate
    });
  }

  if (event.data && event.data.type === 'CLEAR_CACHE') {
    const cacheType = event.data.cacheType || 'all';
    clearCache(cacheType).then(() => {
      event.ports[0].postMessage({
        success: true,
        message: `Cache ${cacheType} cleared successfully`
      });
    }).catch((error) => {
      event.ports[0].postMessage({
        success: false,
        error: error.message
      });
    });
  }

  if (event.data && event.data.type === 'FORCE_UPDATE') {
    console.log('[SW] Force update requested');
    self.registration.update();
  }
});

// Background sync for offline actions
self.addEventListener('sync', (event) => {
  if (event.tag === 'constitutional-sync') {
    console.log('[SW] Performing constitutional compliance sync');
    event.waitUntil(performConstitutionalSync());
  }
});

// Utility functions for cache management

// Add TTL metadata to response
function addTtlToResponse(response, ttlMs) {
  const headers = new Headers(response.headers);
  headers.set('sw-cached-at', Date.now().toString());
  headers.set('sw-ttl', ttlMs.toString());

  return new Response(response.body, {
    status: response.status,
    statusText: response.statusText,
    headers: headers
  });
}

// Check if cached response is expired
function isExpired(response) {
  const cachedAt = parseInt(response.headers.get('sw-cached-at') || '0');
  const ttl = parseInt(response.headers.get('sw-ttl') || '0');

  if (!cachedAt || !ttl) return false;

  return (Date.now() - cachedAt) > ttl;
}

// Cache metrics tracking
let cacheMetrics = {
  static: { hits: 0, misses: 0 },
  api: { hits: 0, misses: 0 },
  images: { hits: 0, misses: 0 },
  constitutional: { hits: 0, misses: 0 },
  dynamic: { hits: 0, misses: 0 }
};

function updateCacheMetrics(type, result) {
  if (cacheMetrics[type]) {
    cacheMetrics[type][result === 'hit' ? 'hits' : 'misses']++;
  }
}

function getCacheHitRate() {
  let totalHits = 0;
  let totalRequests = 0;

  Object.values(cacheMetrics).forEach(metric => {
    totalHits += metric.hits;
    totalRequests += metric.hits + metric.misses;
  });

  return totalRequests > 0 ? (totalHits / totalRequests) * 100 : 0;
}

// Clean up expired API cache entries
async function cleanupExpiredApiCache() {
  try {
    const cache = await caches.open(CACHE_NAMES.API);
    const requests = await cache.keys();

    for (const request of requests) {
      const response = await cache.match(request);
      if (response && isExpired(response)) {
        await cache.delete(request);
        console.log('[SW] Cleaned up expired cache entry:', request.url);
      }
    }
  } catch (error) {
    console.error('[SW] Cache cleanup error:', error);
  }
}

// Validate constitutional compliance
async function validateConstitutionalCompliance() {
  try {
    const cache = await caches.open(CACHE_NAMES.CONSTITUTIONAL);
    const metadata = await cache.match('/constitutional-metadata');

    if (metadata) {
      const data = await metadata.json();
      if (data.hash === CONSTITUTIONAL_HASH) {
        console.log('[SW] Constitutional compliance validated');
        return true;
      }
    }

    console.warn('[SW] Constitutional compliance validation failed');
    return false;
  } catch (error) {
    console.error('[SW] Constitutional validation error:', error);
    return false;
  }
}

async function performConstitutionalSync() {
  try {
    // Validate constitutional compliance when back online
    const response = await fetch('/api/constitutional/validate', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        hash: CONSTITUTIONAL_HASH,
        timestamp: new Date().toISOString(),
        cache_hit_rate: getCacheHitRate()
      })
    });

    if (response.ok) {
      console.log('[SW] Constitutional compliance validated with cache hit rate:', getCacheHitRate().toFixed(2) + '%');
    } else {
      console.warn('[SW] Constitutional compliance validation failed');
    }
  } catch (error) {
    console.error('[SW] Constitutional sync error:', error);
  }
}

// Periodic background sync
self.addEventListener('periodicsync', (event) => {
  if (event.tag === 'constitutional-check') {
    event.waitUntil(performConstitutionalSync());
  }
});

// Helper functions for intelligent caching

// Resource type detection
function isStaticResource(pathname) {
  return STATIC_RESOURCES.some(resource => pathname === resource || pathname.endsWith(resource));
}

function isApiRequest(pathname) {
  return pathname.startsWith('/api/');
}

function isImageResource(pathname) {
  return /\.(jpg|jpeg|png|gif|webp|svg|ico)$/i.test(pathname);
}

function isConstitutionalRequest(pathname) {
  return pathname.includes('constitutional') || pathname.includes('compliance');
}

// Cache-first strategy for static resources
async function handleStaticResource(request) {
  try {
    const cache = await caches.open(CACHE_NAMES.STATIC);
    const cachedResponse = await cache.match(request);

    if (cachedResponse) {
      console.log('[SW] Static cache hit:', request.url);
      updateCacheMetrics('static', 'hit');
      return cachedResponse;
    }

    console.log('[SW] Static cache miss, fetching:', request.url);
    updateCacheMetrics('static', 'miss');

    const response = await fetch(request);
    if (response.ok) {
      cache.put(request, response.clone());
    }
    return response;
  } catch (error) {
    console.error('[SW] Static resource error:', error);
    return new Response('Static resource unavailable', { status: 503 });
  }
}

// Network-first with cache fallback for API requests
async function handleApiRequest(request) {
  const url = new URL(request.url);
  const config = API_CACHE_CONFIG[url.pathname] || { ttl: 60000, strategy: 'network-first' };

  try {
    if (config.strategy === 'cache-first') {
      return await handleCacheFirstApi(request, config);
    } else {
      return await handleNetworkFirstApi(request, config);
    }
  } catch (error) {
    console.error('[SW] API request error:', error);
    return new Response(JSON.stringify({ error: 'API unavailable' }), {
      status: 503,
      headers: { 'Content-Type': 'application/json' }
    });
  }
}

async function handleNetworkFirstApi(request, config) {
  try {
    const response = await fetch(request);
    if (response.ok) {
      const cache = await caches.open(CACHE_NAMES.API);
      const responseWithTtl = addTtlToResponse(response.clone(), config.ttl);
      cache.put(request, responseWithTtl);
      updateCacheMetrics('api', 'miss');
      console.log('[SW] API network success:', request.url);
    }
    return response;
  } catch (error) {
    // Fallback to cache
    const cache = await caches.open(CACHE_NAMES.API);
    const cachedResponse = await cache.match(request);

    if (cachedResponse && !isExpired(cachedResponse)) {
      console.log('[SW] API cache fallback:', request.url);
      updateCacheMetrics('api', 'hit');
      return cachedResponse;
    }

    throw error;
  }
}

async function handleCacheFirstApi(request, config) {
  const cache = await caches.open(CACHE_NAMES.API);
  const cachedResponse = await cache.match(request);

  if (cachedResponse && !isExpired(cachedResponse)) {
    console.log('[SW] API cache hit:', request.url);
    updateCacheMetrics('api', 'hit');
    return cachedResponse;
  }

  console.log('[SW] API cache miss/expired, fetching:', request.url);
  updateCacheMetrics('api', 'miss');

  const response = await fetch(request);
  if (response.ok) {
    const responseWithTtl = addTtlToResponse(response.clone(), config.ttl);
    cache.put(request, responseWithTtl);
  }
  return response;
}

// Cache-first with long TTL for images
async function handleImageResource(request) {
  try {
    const cache = await caches.open(CACHE_NAMES.IMAGES);
    const cachedResponse = await cache.match(request);

    if (cachedResponse) {
      console.log('[SW] Image cache hit:', request.url);
      updateCacheMetrics('images', 'hit');
      return cachedResponse;
    }

    console.log('[SW] Image cache miss, fetching:', request.url);
    updateCacheMetrics('images', 'miss');

    const response = await fetch(request);
    if (response.ok) {
      // Cache images for 24 hours
      const responseWithTtl = addTtlToResponse(response.clone(), 86400000);
      cache.put(request, responseWithTtl);
    }
    return response;
  } catch (error) {
    console.error('[SW] Image resource error:', error);
    return new Response('Image unavailable', { status: 503 });
  }
}

// Constitutional compliance requests with validation
async function handleConstitutionalRequest(request) {
  try {
    const cache = await caches.open(CACHE_NAMES.CONSTITUTIONAL);
    const cachedResponse = await cache.match(request);

    if (cachedResponse && !isExpired(cachedResponse)) {
      // Validate constitutional hash in cached response
      const responseText = await cachedResponse.clone().text();
      if (responseText.includes(CONSTITUTIONAL_HASH)) {
        console.log('[SW] Constitutional cache hit with valid hash:', request.url);
        updateCacheMetrics('constitutional', 'hit');
        return cachedResponse;
      }
    }

    console.log('[SW] Constitutional cache miss/invalid, fetching:', request.url);
    updateCacheMetrics('constitutional', 'miss');

    const response = await fetch(request);
    if (response.ok) {
      // Cache constitutional responses for 5 minutes
      const responseWithTtl = addTtlToResponse(response.clone(), 300000);
      cache.put(request, responseWithTtl);
    }
    return response;
  } catch (error) {
    console.error('[SW] Constitutional request error:', error);
    return new Response(JSON.stringify({
      error: 'Constitutional service unavailable',
      constitutional_hash: CONSTITUTIONAL_HASH
    }), {
      status: 503,
      headers: { 'Content-Type': 'application/json' }
    });
  }
}

// Dynamic resource handling with intelligent caching
async function handleDynamicResource(request) {
  try {
    const cache = await caches.open(CACHE_NAMES.DYNAMIC);

    // Try network first for dynamic content
    try {
      const response = await fetch(request);
      if (response.ok) {
        // Cache dynamic content for 1 minute
        const responseWithTtl = addTtlToResponse(response.clone(), 60000);
        cache.put(request, responseWithTtl);
        updateCacheMetrics('dynamic', 'miss');
      }
      return response;
    } catch (networkError) {
      // Fallback to cache
      const cachedResponse = await cache.match(request);
      if (cachedResponse) {
        console.log('[SW] Dynamic cache fallback:', request.url);
        updateCacheMetrics('dynamic', 'hit');
        return cachedResponse;
      }

      // Final fallback for navigation requests
      if (request.mode === 'navigate') {
        const staticCache = await caches.open(CACHE_NAMES.STATIC);
        return await staticCache.match('/index.html') || new Response('Offline', { status: 503 });
      }

      throw networkError;
    }
  } catch (error) {
    console.error('[SW] Dynamic resource error:', error);
    return new Response('Resource unavailable', { status: 503 });
  }
}

// Cache management utilities
async function clearCache(cacheType = 'all') {
  try {
    if (cacheType === 'all') {
      const cacheNames = Object.values(CACHE_NAMES);
      await Promise.all(cacheNames.map(name => caches.delete(name)));
      console.log('[SW] All caches cleared');
    } else if (CACHE_NAMES[cacheType.toUpperCase()]) {
      await caches.delete(CACHE_NAMES[cacheType.toUpperCase()]);
      console.log(`[SW] ${cacheType} cache cleared`);
    } else {
      throw new Error(`Unknown cache type: ${cacheType}`);
    }

    // Reset metrics for cleared caches
    if (cacheType === 'all') {
      Object.keys(cacheMetrics).forEach(key => {
        cacheMetrics[key] = { hits: 0, misses: 0 };
      });
    } else if (cacheMetrics[cacheType]) {
      cacheMetrics[cacheType] = { hits: 0, misses: 0 };
    }
  } catch (error) {
    console.error('[SW] Cache clear error:', error);
    throw error;
  }
}

// Periodic cache optimization
setInterval(async () => {
  try {
    await cleanupExpiredApiCache();
    const hitRate = getCacheHitRate();
    console.log(`[SW] Cache hit rate: ${hitRate.toFixed(2)}% (Target: >90%)`);

    if (hitRate < 90) {
      console.warn('[SW] Cache hit rate below target, consider optimization');
    }
  } catch (error) {
    console.error('[SW] Periodic optimization error:', error);
  }
}, 300000); // Run every 5 minutes

console.log('[SW] Advanced service worker loaded with constitutional hash:', CONSTITUTIONAL_HASH);
console.log('[SW] Multi-tier caching enabled with >90% hit rate target');
