import { describe, test, expect, beforeEach } from 'vitest'
import { handleWebSocketMessage } from '../store/notifications'

describe('Notifications', () => {
  const mockAddNotification = vi.fn()

  beforeEach(() => {
    mockAddNotification.mockClear()
  })

  test('handles order_created message', () => {
    const message = {
      type: 'order_created',
      order_id: 123
    }

    handleWebSocketMessage(message, mockAddNotification)

    expect(mockAddNotification).toHaveBeenCalledWith({
      type: 'order_created',
      title: 'طلب جديد',
      message: 'تم إنشاء طلب رقم 123',
      tab: 'pending',
      orderId: 123
    })
  })

  test('handles status_changed message', () => {
    const message = {
      type: 'status_changed',
      order_id: 456,
      new_status: 'delivered'
    }

    handleWebSocketMessage(message, mockAddNotification)

    expect(mockAddNotification).toHaveBeenCalledWith({
      type: 'status_changed',
      title: 'تغير الحالة: تم التوصيل',
      message: 'طلب رقم 456 تغيرت حالته إلى تم التوصيل',
      tab: 'delivered',
      orderId: 456
    })
  })

  test('handles captain_assigned message', () => {
    const message = {
      type: 'captain_assigned',
      order_id: 789,
      captain_name: 'محمد أحمد'
    }

    handleWebSocketMessage(message, mockAddNotification)

    expect(mockAddNotification).toHaveBeenCalledWith({
      type: 'captain_assigned',
      title: 'تم تعيين كابتن',
      message: 'تم تعيين محمد أحمد للطلب رقم 789',
      tab: 'processing',
      orderId: 789
    })
  })
})
