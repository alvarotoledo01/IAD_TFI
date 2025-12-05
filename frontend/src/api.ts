import axios from 'axios';
import { SystemState, Emergencia } from './types';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

export const getSystemState = async (): Promise<SystemState> => {
  const response = await axios.get(`${API_URL}/estado`);
  return response.data;
};

export const createEmergencia = async (tipo: string, descripcion: string, zona_id: number): Promise<Emergencia> => {
  const response = await axios.post(`${API_URL}/emergencias`, {
    tipo,
    descripcion,
    zona_id
  });
  return response.data;
};

