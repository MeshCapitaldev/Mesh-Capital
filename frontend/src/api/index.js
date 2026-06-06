import axios from "axios";
const api = axios.create({ baseURL: "/api", timeout: 60000, headers: { "Content-Type": "application/json" } });
export default api;

export const routeQuote = (data) => api.post("/route/quote", data);
export const getMesh = (market) => api.get(`/mesh/${market}`);
export const openPerp = (data) => api.post("/perp/open", data);
export const closePerp = (id) => api.post(`/perp/${id}/close`);
export const listPerps = (wallet) => api.get("/perp", { params: { wallet } });
export const listVaults = () => api.get("/vault");
export const depositVault = (data) => api.post("/vault/deposit", data);
