import api from './api.ts';

export const getGymLocations = async () => {
    const response = await api.get("/gymLocations/gyms");
    return response.data;
}