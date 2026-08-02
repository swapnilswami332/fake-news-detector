/** Empty in dev (Vite proxy). Set VITE_API_URL in production, e.g. https://your-api.onrender.com */
export const API_BASE = (import.meta.env.VITE_API_URL as string | undefined)?.replace(/\/$/, "") ?? "";
