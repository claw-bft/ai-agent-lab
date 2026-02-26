import { useEffect, useState } from 'react';

export function usePolling<T>(
  fetchFn: () => Promise<T>,
  interval: number = 5000,
  deps: any[] = []
) {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    let mounted = true;

    const fetch = async () => {
      try {
        setLoading(true);
        const result = await fetchFn();
        if (mounted) {
          setData(result);
          setError(null);
        }
      } catch (err) {
        if (mounted) {
          setError(err as Error);
        }
      } finally {
        if (mounted) {
          setLoading(false);
        }
      }
    };

    fetch();
    const timer = setInterval(fetch, interval);

    return () => {
      mounted = false;
      clearInterval(timer);
    };
  }, deps);

  return { data, loading, error, refetch: () => fetchFn() };
}