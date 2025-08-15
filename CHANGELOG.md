## MOVO – Unified status + health + CORS + frontend data flow

### What changed
- Backend: CORS updated to allow `http://localhost:5173` and `http://127.0.0.1:5173` (all methods/headers, credentials enabled).
- Backend: Added `/health` returning `{ "ok": true }`.
- Backend: Added lightweight request logging middleware (→ METHOD PATH / ← STATUS PATH).
- Backend: `GET /api/v1/orders/` now returns a single authoritative `current_status` per order and avoids conflicting status fields.
- Frontend: Introduced `src/config.ts` with `API_BASE` and used it across API calls.
- Frontend: Added `src/api/orders.ts` with `fetchOrders()` used by React Query.
- Frontend: Added `uniqueById()` helper and `UseSafeButton` component to prevent duplicate actions.
- Frontend: Wired React Query in `main.tsx`; Dashboard uses `useQuery` with local tab partitioning and accurate counters; loading spinner only on first load; "refreshing" banner on background fetches.

### Why
- Single source of truth for order state ensures consistent UI partitioning and counters.
- Stable health endpoint simplifies uptime checks.
- CORS enables local Vite frontend to talk to FastAPI in dev.
- Safer UX for action buttons and avoids infinite loading patterns.

### How to test
1. Backend: run from project root: `uvicorn backend.app:app --reload --port 8000` then call `/health` → expect `{ "ok": true }` with 200.
2. Frontend: load dashboard; tabs show counts matching visible lists; switching tabs does not trigger refetch (local buckets); background updates show a light "تحديث البيانات…" banner without blocking buttons.
3. Actions: buttons execute once per click and show "جارٍ التنفيذ…" while busy.

