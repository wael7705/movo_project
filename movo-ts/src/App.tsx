import React from 'react';
import Dashboard from './pages/Dashboard'; // واجهة لوحة التحكم الرئيسية
import './styles/tailwind.css'; // استدعاء تنسيقات Tailwind (إذا ما كنت ضايفه بعد)

function App() {
  return (
    <main className="min-h-screen bg-gray-100 text-gray-900 font-sans">
      <Dashboard />
    </main>
  );
}

export default App;
