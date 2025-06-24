// Jest polyfills for ACGS Next.js application

// TextEncoder/TextDecoder polyfill for Node.js environment
const { TextEncoder, TextDecoder } = require('util');

global.TextEncoder = TextEncoder;
global.TextDecoder = TextDecoder;

// Crypto polyfill for Node.js environment
const { webcrypto } = require('crypto');

if (!global.crypto) {
  global.crypto = webcrypto;
}

// URL polyfill
const { URL, URLSearchParams } = require('url');

if (!global.URL) {
  global.URL = URL;
}

if (!global.URLSearchParams) {
  global.URLSearchParams = URLSearchParams;
}

// AbortController polyfill
if (!global.AbortController) {
  global.AbortController = require('abort-controller').AbortController;
}

// Performance polyfill
if (!global.performance) {
  global.performance = require('perf_hooks').performance;
}

// Blob polyfill
if (!global.Blob) {
  const { Blob } = require('buffer');
  global.Blob = Blob;
}

// File polyfill
if (!global.File) {
  global.File = class File extends global.Blob {
    constructor(chunks, filename, options = {}) {
      super(chunks, options);
      this.name = filename;
      this.lastModified = options.lastModified || Date.now();
    }
  };
}

// FormData polyfill
if (!global.FormData) {
  global.FormData = require('form-data');
}

// Headers polyfill
if (!global.Headers) {
  global.Headers = class Headers {
    constructor(init) {
      this._headers = new Map();
      if (init) {
        if (init instanceof Headers) {
          init.forEach((value, key) => this.set(key, value));
        } else if (Array.isArray(init)) {
          init.forEach(([key, value]) => this.set(key, value));
        } else if (typeof init === 'object') {
          Object.entries(init).forEach(([key, value]) => this.set(key, value));
        }
      }
    }

    append(name, value) {
      const existing = this._headers.get(name.toLowerCase());
      this._headers.set(name.toLowerCase(), existing ? `${existing}, ${value}` : value);
    }

    delete(name) {
      this._headers.delete(name.toLowerCase());
    }

    get(name) {
      return this._headers.get(name.toLowerCase()) || null;
    }

    has(name) {
      return this._headers.has(name.toLowerCase());
    }

    set(name, value) {
      this._headers.set(name.toLowerCase(), value);
    }

    forEach(callback) {
      this._headers.forEach((value, key) => callback(value, key, this));
    }

    *[Symbol.iterator]() {
      for (const [key, value] of this._headers) {
        yield [key, value];
      }
    }
  };
}

// Request polyfill
if (!global.Request) {
  global.Request = class Request {
    constructor(input, init = {}) {
      this.url = typeof input === 'string' ? input : input.url;
      this.method = init.method || 'GET';
      this.headers = new global.Headers(init.headers);
      this.body = init.body || null;
      this.mode = init.mode || 'cors';
      this.credentials = init.credentials || 'same-origin';
      this.cache = init.cache || 'default';
      this.redirect = init.redirect || 'follow';
      this.referrer = init.referrer || '';
      this.integrity = init.integrity || '';
    }

    clone() {
      return new Request(this.url, {
        method: this.method,
        headers: this.headers,
        body: this.body,
        mode: this.mode,
        credentials: this.credentials,
        cache: this.cache,
        redirect: this.redirect,
        referrer: this.referrer,
        integrity: this.integrity,
      });
    }
  };
}

// Response polyfill
if (!global.Response) {
  global.Response = class Response {
    constructor(body, init = {}) {
      this.body = body;
      this.status = init.status || 200;
      this.statusText = init.statusText || 'OK';
      this.headers = new global.Headers(init.headers);
      this.ok = this.status >= 200 && this.status < 300;
      this.redirected = false;
      this.type = 'default';
      this.url = '';
    }

    clone() {
      return new Response(this.body, {
        status: this.status,
        statusText: this.statusText,
        headers: this.headers,
      });
    }

    async text() {
      return typeof this.body === 'string' ? this.body : JSON.stringify(this.body);
    }

    async json() {
      const text = await this.text();
      return JSON.parse(text);
    }

    async arrayBuffer() {
      const text = await this.text();
      return new TextEncoder().encode(text).buffer;
    }

    async blob() {
      const text = await this.text();
      return new global.Blob([text]);
    }

    static json(data, init) {
      return new Response(JSON.stringify(data), {
        ...init,
        headers: {
          'Content-Type': 'application/json',
          ...init?.headers,
        },
      });
    }

    static error() {
      const response = new Response(null, { status: 0, statusText: '' });
      response.ok = false;
      response.type = 'error';
      return response;
    }

    static redirect(url, status = 302) {
      return new Response(null, {
        status,
        headers: { Location: url },
      });
    }
  };
}

// MessageChannel polyfill
if (!global.MessageChannel) {
  global.MessageChannel = class MessageChannel {
    constructor() {
      this.port1 = new MessagePort();
      this.port2 = new MessagePort();
      this.port1._otherPort = this.port2;
      this.port2._otherPort = this.port1;
    }
  };

  global.MessagePort = class MessagePort {
    constructor() {
      this._listeners = new Map();
      this._otherPort = null;
    }

    postMessage(message) {
      if (this._otherPort) {
        setTimeout(() => {
          const listeners = this._otherPort._listeners.get('message') || [];
          listeners.forEach(listener => listener({ data: message }));
        }, 0);
      }
    }

    addEventListener(type, listener) {
      if (!this._listeners.has(type)) {
        this._listeners.set(type, []);
      }
      this._listeners.get(type).push(listener);
    }

    removeEventListener(type, listener) {
      const listeners = this._listeners.get(type) || [];
      const index = listeners.indexOf(listener);
      if (index > -1) {
        listeners.splice(index, 1);
      }
    }

    start() {
      // No-op in polyfill
    }

    close() {
      this._listeners.clear();
    }
  };
}
