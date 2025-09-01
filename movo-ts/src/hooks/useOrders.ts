import { useState, useEffect, useCallback, useMemo } from 'react';
import { getOrdersByStatus } from '../services/ordersApi';
import api from '../lib/api';

interface UseOrdersOptions {
  status?: string;
  autoRefresh?: boolean;
  refreshInterval?: number;
}

interface UseOrdersReturn {
  orders: any[];
  counts: Record<string, number>;
  loading: boolean;
  error: string | null;
  refresh: () => Promise<void>;
  refreshCounts: () => Promise<void>;
}

export function useOrders(options: UseOrdersOptions = {}): UseOrdersReturn {
  const { status, autoRefresh = false, refreshInterval = 30000 } = options;
  
  const [orders, setOrders] = useState<any[]>([]);
  const [counts, setCounts] = useState<Record<string, number>>({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [lastRefresh, setLastRefresh] = useState<number>(Date.now());

  // Cache للطلبات
  const ordersCache = useMemo(() => new Map<string, { data: any[]; timestamp: number }>(), []);
  const CACHE_DURATION = 30000; // 30 ثانية

  const isCacheValid = useCallback((cacheKey: string) => {
    const cached = ordersCache.get(cacheKey);
    if (!cached) return false;
    return Date.now() - cached.timestamp < CACHE_DURATION;
  }, [ordersCache]);

  const getCachedOrders = useCallback((cacheKey: string) => {
    const cached = ordersCache.get(cacheKey);
    return cached?.data || null;
  }, [ordersCache]);

  const setCachedOrders = useCallback((cacheKey: string, data: any[]) => {
    ordersCache.set(cacheKey, { data, timestamp: Date.now() });
  }, [ordersCache]);

  const fetchOrders = useCallback(async (currentStatus?: string) => {
    try {
      setLoading(true);
      setError(null);
      
      const targetStatus = currentStatus || status;
      if (!targetStatus) return;

      const cacheKey = `orders_${targetStatus}`;
      
      // تحقق من الـ cache
      const cached = getCachedOrders(cacheKey);
      if (cached && isCacheValid(cacheKey)) {
        setOrders(cached);
        setLoading(false);
        return;
      }

      const data = await getOrdersByStatus(targetStatus);
      setOrders(data);
      setCachedOrders(cacheKey, data);
      setLastRefresh(Date.now());
    } catch (err) {
      setError(err instanceof Error ? err.message : 'حدث خطأ في جلب الطلبات');
    } finally {
      setLoading(false);
    }
  }, [status, getCachedOrders, isCacheValid, setCachedOrders]);

  const fetchCounts = useCallback(async () => {
    try {
      const data = await api.orders.counts();
      setCounts(data);
    } catch (err) {
      console.error('Error fetching counts:', err);
    }
  }, []);

  const refresh = useCallback(async () => {
    await fetchOrders();
  }, [fetchOrders]);

  const refreshCounts = useCallback(async () => {
    await fetchCounts();
  }, [fetchCounts]);

  // Auto-refresh
  useEffect(() => {
    if (!autoRefresh) return;

    const interval = setInterval(() => {
      fetchOrders();
      fetchCounts();
    }, refreshInterval);

    return () => clearInterval(interval);
  }, [autoRefresh, refreshInterval, fetchOrders, fetchCounts]);

  // Initial fetch
  useEffect(() => {
    fetchOrders();
    fetchCounts();
  }, [fetchOrders, fetchCounts]);

  return {
    orders,
    counts,
    loading,
    error,
    refresh,
    refreshCounts,
  };
}
