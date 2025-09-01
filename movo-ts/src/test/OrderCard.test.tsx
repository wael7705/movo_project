import { render, screen } from '@testing-library/react'
import OrderCard from '../components/OrderCard'

const mockOrder = {
  order_id: 1,
  name: 'أحمد محمد',
  address: 'دمشق، سوريا',
  phone: '+963912345678',
  totalAmountValue: 50,
  rName: 'مطعم الشام',
  lang: 'ar' as const,
  current_tab: 'pending',
  onStatusChange: vi.fn(),
  onInvoice: vi.fn(),
  onNotes: vi.fn(),
  onTrack: vi.fn(),
  onRate: vi.fn(),
}

describe('OrderCard', () => {
  test('renders order card with basic info', () => {
    render(<OrderCard {...mockOrder} />)
    
    expect(screen.getByText('أحمد محمد')).toBeInTheDocument()
    expect(screen.getByText('دمشق، سوريا')).toBeInTheDocument()
    expect(screen.getByText('+963912345678')).toBeInTheDocument()
    expect(screen.getByText('50')).toBeInTheDocument()
    expect(screen.getByText('مطعم الشام')).toBeInTheDocument()
  })

  test('shows order ID', () => {
    render(<OrderCard {...mockOrder} />)
    expect(screen.getByText(/1/)).toBeInTheDocument()
  })
})
