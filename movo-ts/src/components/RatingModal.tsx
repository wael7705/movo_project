import React, { useState, useEffect } from 'react';
import api from '../lib/api';

interface RatingModalProps {
  isOpen: boolean;
  onClose: () => void;
  orderId: number;
  onSubmit: (rating: number, comment: string) => void;
  lang?: 'ar' | 'en';
}

const RatingModal: React.FC<RatingModalProps> = ({
  isOpen,
  onClose,
  orderId,
  onSubmit,
  lang = 'ar'
}) => {
  const [rating, setRating] = useState(0);
  const [comment, setComment] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [loading, setLoading] = useState(false);
  const [existingRating, setExistingRating] = useState<any>(null);

  // جلب التقييم الموجود عند فتح النافذة
  useEffect(() => {
    if (isOpen && orderId) {
      setLoading(true);
      api.orders.rating.get(orderId)
        .then((data) => {
          console.log('🔴 Rating data received:', data);
          if (data && data.order_emoji_score) {
            console.log('🔴 Setting existing rating:', data.order_emoji_score);
            setRating(data.order_emoji_score);
            setComment(data.order_comment || '');
            setExistingRating(data);
          } else {
            console.log('🔴 No existing rating found');
            setRating(0);
            setComment('');
            setExistingRating(null);
          }
        })
        .catch((error) => {
          console.error('Error fetching existing rating:', error);
          setRating(0);
          setComment('');
          setExistingRating(null);
        })
        .finally(() => {
          setLoading(false);
        });
    }
  }, [isOpen, orderId]);

  const handleSubmit = async () => {
    if (rating === 0) return;
    
    setIsSubmitting(true);
    try {
      await onSubmit(rating, comment);
      onClose();
      setRating(0);
      setComment('');
    } catch (error) {
      console.error('Error submitting rating:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleClose = () => {
    if (!isSubmitting) {
      onClose();
      setRating(0);
      setComment('');
    }
  };

  console.log('🔴 RatingModal render - isOpen:', isOpen, 'orderId:', orderId);
  console.log('🔴 RatingModal props:', { isOpen, orderId, lang });
  if (!isOpen) return null;

  const translations = {
    ar: {
      title: existingRating ? 'تعديل التقييم' : 'تقييم الطلب',
      subtitle: `طلب رقم #${orderId}`,
      ratingLabel: 'التقييم:',
      commentLabel: 'تعليق (اختياري):',
      commentPlaceholder: 'اكتب تعليقك هنا...',
      submit: 'إرسال التقييم',
      cancel: 'إلغاء',
      stars: ['ممتاز', 'جيد جداً', 'جيد', 'مقبول', 'ضعيف']
    },
    en: {
      title: existingRating ? 'Edit Rating' : 'Rate Order',
      subtitle: `Order #${orderId}`,
      ratingLabel: 'Rating:',
      commentLabel: 'Comment (optional):',
      commentPlaceholder: 'Write your comment here...',
      submit: 'Submit Rating',
      cancel: 'Cancel',
      stars: ['Excellent', 'Very Good', 'Good', 'Fair', 'Poor']
    }
  };

  const t = translations[lang];

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      {/* Backdrop */}
      <div 
        className="absolute inset-0 bg-black/20 backdrop-blur-sm"
        onClick={handleClose}
      />
      
      {/* Modal */}
      <div className="relative w-full max-w-md mx-4 bg-white/95 backdrop-blur-md rounded-2xl shadow-2xl border border-white/20 overflow-hidden">
        {/* Header */}
        <div className="bg-gradient-to-r from-amber-500 to-orange-500 px-6 py-4">
          <h2 className="text-xl font-bold text-white text-center">
            {t.title}
          </h2>
          <p className="text-amber-100 text-center text-sm mt-1">
            {t.subtitle}
          </p>
        </div>

        {/* Content */}
        <div className="p-6 space-y-6">
          {loading ? (
            <div className="text-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-amber-500 mx-auto mb-4"></div>
              <p className="text-gray-600">{lang === 'ar' ? 'جاري التحميل...' : 'Loading...'}</p>
            </div>
          ) : (
            <>
          
          {/* Rating Stars */}
          <div className="space-y-3">
            <label className="block text-sm font-medium text-gray-700">
              {t.ratingLabel}
            </label>
            <div className="flex justify-center space-x-2 rtl:space-x-reverse">
              {[1, 2, 3, 4, 5].map((star) => (
                <button
                  key={star}
                  type="button"
                  onClick={() => setRating(star)}
                  className={`text-3xl transition-all duration-200 hover:scale-110 ${
                    star <= rating 
                      ? 'text-yellow-400 hover:text-yellow-500' 
                      : 'text-gray-300 hover:text-gray-400'
                  }`}
                  title={t.stars[star - 1]}
                >
                  {star <= rating ? '⭐' : '☆'}
                </button>
              ))}
            </div>
            {rating > 0 && (
              <p className="text-center text-sm text-gray-600 font-medium">
                {t.stars[rating - 1]}
              </p>
            )}
          </div>

          {/* Comment */}
          <div className="space-y-2">
            <label className="block text-sm font-medium text-gray-700">
              {t.commentLabel}
            </label>
            <textarea
              value={comment}
              onChange={(e) => setComment(e.target.value)}
              placeholder={t.commentPlaceholder}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-amber-500 focus:border-transparent resize-none"
              rows={3}
              disabled={isSubmitting}
            />
          </div>

          {/* Footer */}
          <div className="bg-gray-50 px-6 py-4 flex gap-3 justify-end -mx-6 -mb-6">
            <button
              type="button"
              onClick={handleClose}
              disabled={isSubmitting}
              className="px-4 py-2 text-gray-600 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 transition-colors"
            >
              {t.cancel}
            </button>
            <button
              type="button"
              onClick={handleSubmit}
              disabled={rating === 0 || isSubmitting}
              className="px-6 py-2 bg-gradient-to-r from-amber-500 to-orange-500 text-white rounded-lg hover:from-amber-600 hover:to-orange-600 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 font-medium"
            >
              {isSubmitting ? (
                <span className="flex items-center gap-2">
                  <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                  {lang === 'ar' ? 'جاري الإرسال...' : 'Sending...'}
                </span>
              ) : (
                t.submit
              )}
            </button>
          </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
};

export default RatingModal;
