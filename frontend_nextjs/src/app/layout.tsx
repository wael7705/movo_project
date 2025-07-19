import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "MOVO Login",
  description: "تسجيل الدخول إلى نظام MOVO",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="ar" dir="rtl">
      <body className="min-h-screen bg-gray-50">
        <header className="w-full flex items-center justify-between px-6 py-4 bg-primary text-secondary font-bold shadow-md">
          <div className="flex items-center gap-3">
            {/* شعار الشركة */}
            <div className="w-12 h-12 rounded-full bg-secondary flex items-center justify-center text-white text-2xl font-extrabold">M</div>
            <span className="text-xl md:text-2xl font-extrabold tracking-tight">MOVO</span>
          </div>
        </header>
        <main className="max-w-2xl mx-auto py-8 px-4">
          {children}
        </main>
      </body>
    </html>
  );
}
