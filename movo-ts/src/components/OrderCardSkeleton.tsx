import React from 'react';

interface OrderCardSkeletonProps {
  className?: string;
}

const OrderCardSkeleton: React.FC<OrderCardSkeletonProps> = ({ className = '' }) => {
  return (
    <div className={`bg-white rounded-xl shadow-md border p-5 mb-4 animate-pulse ${className}`}>
      {/* Header */}
      <div className="flex justify-between items-center mb-4">
        <div className="h-6 bg-gray-200 rounded w-16"></div>
        <div className="h-5 bg-gray-200 rounded w-24"></div>
      </div>
      
      {/* Content Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 px-5 py-4">
        {/* Left Column */}
        <div className="space-y-3">
          <div className="h-4 bg-gray-200 rounded w-20"></div>
          <div className="h-4 bg-gray-200 rounded w-16"></div>
          <div className="h-4 bg-gray-200 rounded w-24"></div>
          <div className="h-4 bg-gray-200 rounded w-18"></div>
        </div>
        
        {/* Right Column */}
        <div className="space-y-3">
          <div className="h-4 bg-gray-200 rounded w-16"></div>
          <div className="h-4 bg-gray-200 rounded w-20"></div>
          <div className="h-4 bg-gray-200 rounded w-14"></div>
          <div className="h-4 bg-gray-200 rounded w-22"></div>
        </div>
      </div>
      
      {/* Button Bar */}
      <div className="flex items-center justify-between px-5 py-3 border-t bg-slate-50">
        <div className="flex gap-2">
          <div className="h-8 bg-gray-200 rounded w-16"></div>
          <div className="h-8 bg-gray-200 rounded w-16"></div>
        </div>
        <div className="flex gap-2">
          <div className="h-8 bg-gray-200 rounded w-20"></div>
          <div className="h-8 bg-gray-200 rounded w-16"></div>
        </div>
      </div>
    </div>
  );
};

export default OrderCardSkeleton;
