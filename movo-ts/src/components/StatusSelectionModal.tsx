import React, { useState } from 'react';

interface StatusSelectionModalProps {
  isOpen: boolean;
  onClose: () => void;
  onStatusSelect: (orderId: number, newStatus: string) => void;
  orderId: number;
  currentStatus: string;
  previousStatus?: string;
  lang?: 'ar' | 'en';
}

const statusOptions = [
  { value: 'pending', ar: 'قيد الانتظار', en: 'Pending' },
  { value: 'choose_captain', ar: 'تعيين كابتن', en: 'Captain Selection' },
  { value: 'processing', ar: 'معالجة', en: 'Processing' },
  { value: 'out_for_delivery', ar: 'خرج للتوصيل', en: 'Out for Delivery' },
  { value: 'delivered', ar: 'تم التوصيل', en: 'Delivered' },
  { value: 'cancelled', ar: 'ملغي', en: 'Cancelled' },
  { value: 'deferred', ar: 'مؤجل', en: 'Deferred' },
];

const StatusSelectionModal: React.FC<StatusSelectionModalProps> = ({
  isOpen,
  onClose,
  onStatusSelect,
  orderId,
  currentStatus,
  previousStatus,
  lang = 'ar',
}) => {
  const [selectedStatus, setSelectedStatus] = useState<string>('');

  if (!isOpen) return null;

  const handleSubmit = () => {
    if (selectedStatus) {
      onStatusSelect(orderId, selectedStatus);
      onClose();
      setSelectedStatus('');
    }
  };

  const handleCancel = () => {
    onClose();
    setSelectedStatus('');
  };

  const getStatusLabel = (status: string) => {
    const option = statusOptions.find(opt => opt.value === status);
    return option ? option[lang] : status;
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-xl shadow-2xl p-6 max-w-md w-full mx-4">
        <div className="text-center mb-6">
          <h3 className="text-xl font-bold text-gray-900 mb-2">
            {lang === 'ar' ? 'اختر حالة الطلب الجديدة' : 'Select New Order Status'}
          </h3>
          <p className="text-sm text-gray-600">
            {lang === 'ar' ? `الطلب #${orderId}` : `Order #${orderId}`}
          </p>
          <p className="text-sm text-gray-500 mt-1">
            {lang === 'ar' ? 'الحالة الحالية: ' : 'Current Status: '}
            <span className="font-semibold text-red-600">
              {getStatusLabel(currentStatus)}
            </span>
          </p>
          {previousStatus && (
            <p className="text-sm text-gray-500 mt-1">
              {lang === 'ar' ? 'الحالة السابقة: ' : 'Previous Status: '}
              <span className="font-semibold text-blue-600">
                {getStatusLabel(previousStatus)}
              </span>
            </p>
          )}
        </div>

        <div className="space-y-3 mb-6">
          {statusOptions.map((option) => (
            <button
              key={option.value}
              onClick={() => setSelectedStatus(option.value)}
              className={`w-full p-3 rounded-lg border-2 transition-all ${
                selectedStatus === option.value
                  ? 'border-blue-500 bg-blue-50 text-blue-700'
                  : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'
              } ${option.value === currentStatus ? 'opacity-50 cursor-not-allowed' : ''}`}
              disabled={option.value === currentStatus}
            >
              <div className="flex items-center justify-between">
                <span className="font-medium">{option[lang]}</span>
                {selectedStatus === option.value && (
                  <span className="text-blue-500">✓</span>
                )}
              </div>
            </button>
          ))}
        </div>

        <div className="flex gap-3">
          <button
            onClick={handleCancel}
            className="flex-1 px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition"
          >
            {lang === 'ar' ? 'إلغاء' : 'Cancel'}
          </button>
          <button
            onClick={handleSubmit}
            disabled={!selectedStatus}
            className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition"
          >
            {lang === 'ar' ? 'تأكيد' : 'Confirm'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default StatusSelectionModal;
