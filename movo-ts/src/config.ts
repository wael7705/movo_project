// ضمان احتواء BASE على /api/v1 حتى لو أعطي بدون لاحقة في env
const RAW = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";
export const API_BASE = RAW.endsWith("/api/v1") ? RAW : `${RAW.replace(/\/$/, '')}/api/v1`;


