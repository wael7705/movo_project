import { io, Socket } from "socket.io-client";

const socket: Socket = io("/", {
  path: "/socket.io",
  transports: ["websocket", "polling"],
  withCredentials: false,
  reconnection: true,
  reconnectionAttempts: 10,
  reconnectionDelay: 1000,
});

export default socket;
