"use client";
import React, { useState } from 'react';
import Link from 'next/link';

export default function LoginPage() {
  const [phone, setPhone] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const handleLogin = (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    if (!phone || !password) {
      setError('يرجى إدخال رقم الجوال وكلمة المرور');
      return;
    }
    // منطق تسجيل الدخول (وهمي حالياً)
    setSuccess('تم تسجيل الدخول بنجاح!');
  };

  return (
    <div className="bg-white rounded-xl shadow-lg p-8 max-w-md mx-auto mt-8 border border-gray-100">
      <h2 className="text-2xl font-bold text-secondary mb-6 text-center">تسجيل الدخول</h2>
      <form onSubmit={handleLogin} className="space-y-4">
        <div>
          <label className="block mb-1 font-medium">رقم الجوال</label>
          <input
            type="text"
            className="w-full px-4 py-2 border rounded focus:outline-none focus:ring-2 focus:ring-primary"
            value={phone}
            onChange={e => setPhone(e.target.value)}
            dir="ltr"
            placeholder="05xxxxxxxx"
          />
        </div>
        <div>
          <label className="block mb-1 font-medium">كلمة المرور</label>
          <input
            type="password"
            className="w-full px-4 py-2 border rounded focus:outline-none focus:ring-2 focus:ring-primary"
            value={password}
            onChange={e => setPassword(e.target.value)}
            placeholder="••••••••"
          />
        </div>
        {error && <div className="text-red-600 text-sm text-center">{error}</div>}
        {success && <div className="text-green-600 text-sm text-center">{success}</div>}
        <button
          type="submit"
          className="w-full py-2 bg-primary text-secondary font-bold rounded hover:bg-primary-dark transition"
        >
          دخول
        </button>
      </form>
      <div className="mt-6 text-center">
        <span>ليس لديك حساب؟ </span>
        <Link href="/signup" className="text-secondary font-bold hover:underline">سجّل الآن</Link>
      </div>
    </div>
  );
} 