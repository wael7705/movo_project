import { lazy, Suspense } from "react";
import { createBrowserRouter, RouterProvider } from "react-router-dom";

// Lazy load components for code splitting
const AdminDashboard = lazy(() => import("./pages/AdminDashboard"));
const Dashboard = lazy(() => import("./pages/Dashboard"));
const Debug = lazy(() => import("./pages/Debug"));

// Simple loading component
const Loader = () => (
  <div className="min-h-screen bg-gray-100 flex items-center justify-center">
    <div className="p-6 text-sm opacity-70 text-center">
      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
      Loading...
    </div>
  </div>
);

// Router configuration
const router = createBrowserRouter([
  {
    path: "/",
    element: (
      <Suspense fallback={<Loader />}>
        <AdminDashboard />
      </Suspense>
    ),
  },
  {
    path: "/dashboard",
    element: (
      <Suspense fallback={<Loader />}>
        <Dashboard />
      </Suspense>
    ),
  },
  {
    path: "/debug",
    element: (
      <Suspense fallback={<Loader />}>
        <Debug />
      </Suspense>
    ),
  },
]);

export default function AppRouter() {
  return <RouterProvider router={router} />;
}
