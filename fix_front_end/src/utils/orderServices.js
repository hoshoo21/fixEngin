// src/utils/orderService.js
import { apiClient } from './apiClient';

/**
 * Place an order through the FIX web server
 * @param {Object} orderData - { side, symbol, quantity, price, ordertype, tif, notes }
 */
export const placeOrder = async (orderData) => {
  try {
    // Assuming your Python/FIX server has a route like /orders
    const result = await apiClient.post('/orders', orderData);
    return result;
  } catch (error) {
    console.error('Order placement failed:', error);
    throw error;
  }
};
