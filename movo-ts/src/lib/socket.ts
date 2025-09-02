import { io, Socket } from 'socket.io-client';

export function createCaptainSocket(captainId: number): Socket {
  const base = `${location.protocol}//${location.host}`;
  return io(base, {
    path: '/socket.io',
    transports: ['websocket', 'polling'],
    reconnection: true,
    reconnectionAttempts: 3,
    reconnectionDelay: 500,
    timeout: 5000,
    auth: { captain_id: captainId },
  });
}

export function createCaptainSocketWS(captainId: number): WebSocket {
  const proto = location.protocol === 'https:' ? 'wss' : 'ws';
  const ws = new WebSocket(`${proto}://${location.host}/ws/captain/${captainId}`);
  
  // Add error handling to prevent console spam
  ws.onerror = (error) => {
    if (import.meta.env.DEV) {
      console.warn(`WebSocket connection failed for captain ${captainId}`);
    }
  };
  
  return ws;
}
