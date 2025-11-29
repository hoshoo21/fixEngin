import React, { useState } from 'react';
import { placeOrder } from '../utils/orderServices';

const OrderForm = () => {
   const [formData, setFormData]= useState({
        side: 'BUY',
        symbol: '',
        quantity: '',
        price: '',
        ordertype: 'LIMIT',
        tif: 'DAY',
        notes: '',
   });
   const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };
  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await placeOrder(formData);
      console.log('Order response:', response);
      alert('Order placed successfully!');
    } catch (err) {
      alert('Failed to place order.');
    }
  };
    return (
    <div className="flex justify-center mt-10">
      <form onSubmit={handleSubmit} className="bg-white shadow-md rounded-lg p-6 w-full max-w-md space-y-4">
        
        <select
          name="side"
          className="w-full p-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-400"
          value = {formData.side}
          onChange={handleChange}  
        >
          <option value="BUY">Buy</option>
          <option value="SELL">Sell</option>
        </select>

        <input
          type="text"
          name="symbol"
          placeholder="Symbol"
          className="w-full p-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-400"
         onChange={handleChange}
         value = {formData.symbol}
       />

        <input
          type="number"
          name="quantity"
          placeholder="Quantity"
          className="w-full p-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-400"
          value = {formData.quantity}
          onChange={handleChange}
        />

        <input
          type="number"
          name="price"
          placeholder="Price"
          className="w-full p-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-400"
          value = {formData.price}
          onChange={handleChange}
       />

        <select
          name="ordertype"
          className="w-full p-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-400"
          value = {formData.ordertype}
          onChange={onchange}
    >
          <option value="MARKET">Market</option>
          <option value="LIMIT">Limit</option>
          <option value="STOP">Stop</option>
        </select>

        <select
          name="tif"
          className="w-full p-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-400"
          onChange={onchange}
          value ={formData.tif}
        >
          <option value="DAY">Day</option>
          <option value="GTC">GTC</option>
          <option value="IOC">IOC</option>
        </select>

        <textarea
          name="notes"
          placeholder="Notes"
          className="w-full p-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-400"
          value ={formData.notes}
          onChange={handleChange}
       ></textarea>

        <button
          type="submit"
          className="w-full bg-blue-500 text-white font-semibold py-2 px-4 rounded hover:bg-blue-600 transition"
        >
          Place Order
        </button>
      </form>
    </div>
  );
};

export default OrderForm;
