// إعدادات الأداء للتطبيق
export const PERFORMANCE_CONFIG = {
  // Cache settings
  CACHE: {
    ORDERS_TTL: 30000, // 30 ثانية
    COUNTS_TTL: 60000, // دقيقة واحدة
    USER_PREFERENCES_TTL: 300000, // 5 دقائق
  },

  // Debounce settings
  DEBOUNCE: {
    SEARCH: 300, // 300ms
    SCROLL: 100, // 100ms
    RESIZE: 250, // 250ms
  },

  // Throttle settings
  THROTTLE: {
    API_CALLS: 1000, // ثانية واحدة
    SCROLL_EVENTS: 100, // 100ms
    RESIZE_EVENTS: 250, // 250ms
  },

  // Pagination
  PAGINATION: {
    DEFAULT_PAGE_SIZE: 20,
    MAX_PAGE_SIZE: 100,
    LOAD_MORE_THRESHOLD: 0.8, // 80% من الصفحة
  },

  // Auto-refresh intervals
  AUTO_REFRESH: {
    ORDERS: 30000, // 30 ثانية
    COUNTS: 60000, // دقيقة واحدة
    NOTIFICATIONS: 15000, // 15 ثانية
  },

  // Animation durations
  ANIMATIONS: {
    FAST: 150,
    NORMAL: 300,
    SLOW: 500,
  },

  // Network timeouts
  TIMEOUTS: {
    API_REQUEST: 10000, // 10 ثوان
    IMAGE_LOAD: 5000, // 5 ثوان
    WEBSOCKET_RECONNECT: 3000, // 3 ثوان
  },

  // Memory management
  MEMORY: {
    MAX_CACHED_ITEMS: 1000,
    CLEANUP_INTERVAL: 300000, // 5 دقائق
  },
} as const;

// Helper functions
export const isLowEndDevice = (): boolean => {
  if (typeof navigator === 'undefined') return false;
  
  // تحقق من ذاكرة الجهاز
  const memory = (navigator as any).deviceMemory;
  if (memory && memory < 4) return true;
  
  // تحقق من عدد النوى
  const cores = (navigator as any).hardwareConcurrency;
  if (cores && cores < 4) return true;
  
  return false;
};

export const shouldEnableAnimations = (): boolean => {
  if (typeof window === 'undefined') return true;
  
  // تحقق من تفضيلات المستخدم
  const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  if (prefersReducedMotion) return false;
  
  // تحقق من نوع الجهاز
  if (isLowEndDevice()) return false;
  
  return true;
};

export const getOptimalRefreshInterval = (): number => {
  if (isLowEndDevice()) {
    return PERFORMANCE_CONFIG.AUTO_REFRESH.ORDERS * 2; // ضعف الفترة للجهاز الضعيف
  }
  return PERFORMANCE_CONFIG.AUTO_REFRESH.ORDERS;
};
