import { useEffect, useState, useCallback } from 'react';
import { wsService } from '../services/api';

export function useWebSocket() {
  const [isConnected, setIsConnected] = useState(false);

  useEffect(() => {
    wsService.connect();
    
    const handleConnect = () => setIsConnected(true);

    wsService.on('connected', handleConnect);
    
    return () => {
      wsService.off('connected', handleConnect);
      wsService.disconnect();
    };
  }, []);

  const subscribe = useCallback((event: string, callback: (data: any) => void) => {
    wsService.on(event, callback);
    return () => wsService.off(event, callback);
  }, []);

  return { isConnected, subscribe };
}