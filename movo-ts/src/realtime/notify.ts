import { io } from "socket.io-client";

// يمكن تعطيل الويب سوكيت مؤقتًا بإرجاع noop لوقف الأخطاء أثناء العزل
const DISABLED = false;

export const socket = DISABLED
  ? (null as any)
  : io("/", { path: "/socket.io", transports:["websocket"], withCredentials: false });

export function subscribeTabNotify(tab: string, cb: (msg: string) => void): () => void {
  if (DISABLED || !socket) return () => {};
  const ev = `notify_tab:${tab}`;
  socket.on(ev, cb);
  return () => { socket.off(ev, cb); };
}


