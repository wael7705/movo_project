import React, { useState, useRef, useEffect } from 'react';

interface LanguageSwitcherProps {
  currentLang: 'ar' | 'en';
  onSwitch: (lang: 'ar' | 'en') => void;
}

const LANGUAGES = [
  { code: 'ar', icon: '🇸🇦' },
  { code: 'en', icon: '🇬🇧' },
];

const LanguageSwitcher: React.FC<LanguageSwitcherProps> = ({ currentLang, onSwitch }) => {
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (ref.current && !ref.current.contains(event.target as Node)) {
        setOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const current = LANGUAGES.find(l => l.code === currentLang) || LANGUAGES[0];

  return (
    <div className="relative inline-block text-left mb-4" ref={ref}>
      <button
        className="flex items-center justify-center px-2 py-1 rounded-full border border-gray-300 bg-white text-gray-700 hover:bg-gray-100 transition shadow-sm min-w-[36px] min-h-[36px] text-xl"
        onClick={() => setOpen(o => !o)}
        aria-haspopup="listbox"
        aria-expanded={open}
      >
        <span>{current.icon}</span>
      </button>
      {open && (
        <div className="absolute z-10 mt-2 w-12 bg-white border border-gray-200 rounded shadow-lg">
          <ul className="py-1 flex flex-col items-center" role="listbox">
            {LANGUAGES.map(lang => (
              <li
                key={lang.code}
                className={`flex items-center justify-center w-full py-2 cursor-pointer hover:bg-gray-100 text-xl ${lang.code === currentLang ? 'bg-gray-200 font-bold' : ''}`}
                onClick={() => { setOpen(false); onSwitch(lang.code as 'ar' | 'en'); }}
                role="option"
                aria-selected={lang.code === currentLang}
              >
                <span>{lang.icon}</span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};

export default LanguageSwitcher;