const BASE_URL = "http://127.0.0.1:8000";

export const healthCheck = async () => {
  const res = await fetch(`${BASE_URL}/health`);
  return res.json();
};
