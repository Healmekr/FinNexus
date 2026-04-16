import axios from 'axios';

const API_URL = 'http://localhost:5000/api/financial';

const getAuthHeader = () => ({
  'x-auth-token': localStorage.getItem('token')
});

export const fetchFinancialData = async () => {
  const res = await axios.get(`${API_URL}/me`, { headers: getAuthHeader() });
  return res.data;
};

export const transferMoney = async (recipient, amount) => {
  const res = await axios.post(`${API_URL}/transfer`, { recipient, amount }, { headers: getAuthHeader() });
  return res.data;
};

export const addFunds = async (amount) => {
  const res = await axios.post(`${API_URL}/add-funds`, { amount }, { headers: getAuthHeader() });
  return res.data;
};

export const dynamicUpdate = async () => {
  const res = await axios.post(`${API_URL}/dynamic-update`, {}, { headers: getAuthHeader() });
  return res.data;
};