import React from 'react';

interface TabProps {
    label: string;
    active: boolean;
    onClick: () => void;
}

const Tab: React.FC<TabProps> = ({ label, active, onClick }) => {
    return (
        <button
            className={`px-4 py-2 rounded-full font-medium transition-colors 
        ${active ? 'bg-yellow-400 text-white' : 'bg-gray-200 text-gray-700 hover:bg-yellow-300'}`}
            onClick={onClick}
        >
            {label}
        </button>
    );
};

export default Tab;