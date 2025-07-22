import React from 'react';

export interface Tab {
  label: string;
  value: string;
}

interface TabsProps {
  tabs: Tab[];
  active: string;
  onChange: (value: string) => void;
  dir?: 'rtl' | 'ltr';
  className?: string;
}

const Tabs: React.FC<TabsProps> = ({ tabs, active, onChange, dir = 'rtl', className }) => {
  // اعكس الترتيب عند اللغة العربية
  const displayTabs = dir === 'rtl' ? [...tabs].reverse() : tabs;
  return (
    <nav
      className={`w-full border-b border-gray-200 flex ${dir === 'rtl' ? 'flex-row-reverse justify-end' : 'flex-row justify-start'} ${className || ''}`}
      style={{ overflowX: 'auto' }}
    >
      {displayTabs.map((tab) => (
        <button
          key={tab.value}
          className={`relative px-5 py-2 mx-1 rounded-full font-bold text-base select-none transition-all duration-200 whitespace-nowrap
            ${active === tab.value
              ? 'bg-yellow-400 text-white border border-yellow-300 shadow-md'
              : 'bg-white text-purple-700 border border-purple-200 hover:bg-yellow-100'}
          `}
          style={{ minWidth: 110, textAlign: 'center' }}
          onClick={() => onChange(tab.value)}
        >
          {tab.label}
          {active === tab.value && (
            <span className="absolute left-2 right-2 -bottom-1 h-1 bg-yellow-400 rounded-full" style={{ content: '""' }} />
          )}
        </button>
      ))}
    </nav>
  );
};

export default Tabs; 