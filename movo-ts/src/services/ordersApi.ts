import axios from 'axios';

const API_URL = 'http://localhost:8000/api/v1'; // يجب أن يطابق مسار الباكند

export const getOrdersByStatus = async (status: string) => {
  try {
    return await axios.get(`${API_URL}/orders/`, { params: { status } });
  } catch (error) {
    throw error;
  }
};

export const getOrder = async (orderId: number) => {
  try {
    return await axios.get(`${API_URL}/orders/${orderId}`);
  } catch (error) {
    throw error;
  }
};

export const updateOrderStatus = async (orderId: number, newStatus: string, captainId?: number) => {
  try {
    return await axios.put(`${API_URL}/orders/${orderId}`, { status: newStatus, captain_id: captainId });
  } catch (error) {
    throw error;
  }
};

export const assignCaptain = async (orderId: number, captainId: number) => {
  try {
    return await axios.put(`${API_URL}/orders/${orderId}`, { captain_id: captainId });
  } catch (error) {
    throw error;
  }
};

export const getOrderNotes = async (orderId: number) => {
  try {
    return await axios.get(`${API_URL}/orders/${orderId}/notes`);
  } catch (error) {
    throw error;
  }
};

export const addNote = async (orderId: number, noteText: string) => {
  try {
    return await axios.post(`${API_URL}/orders/${orderId}/notes`, { note_text: noteText });
  } catch (error) {
    throw error;
  }
};

export const updateOrderAddress = async (orderId: number, newAddress: string) => {
  try {
    return await axios.patch(`${API_URL}/orders/${orderId}/address`, { new_address: newAddress });
  } catch (error) {
    throw error;
  }
};

// تجهيز لجلب عدة حالات دفعة واحدة مستقبلاً
export const getOrdersByStatuses = async (statuses: string[]) => {
  try {
    return await axios.get(`${API_URL}/orders/`, { params: { status: statuses.join(',') } });
  } catch (error) {
    throw error;
  }
}; 