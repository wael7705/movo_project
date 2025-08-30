import { io, Socket } from "socket.io-client";

const socket: Socket = io("/", {
  path: "/socket.io",
  transports: ["websocket"],
  withCredentials: false,
});

export default socket;
