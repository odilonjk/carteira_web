import axios from 'axios';

const resolveBaseUrl = (): string => {
  if (import.meta.env.VITE_API_BASE_URL) {
    return import.meta.env.VITE_API_BASE_URL;
  }

  const apiPort = import.meta.env.VITE_API_PORT ?? '5000';
  if (typeof window !== 'undefined') {
    const { protocol, hostname } = window.location;
    return `${protocol}//${hostname}:${apiPort}`;
  }

  return `http://localhost:${apiPort}`;
};

export const apiClient = axios.create({
  baseURL: resolveBaseUrl(),
  timeout: 10_000,
});
