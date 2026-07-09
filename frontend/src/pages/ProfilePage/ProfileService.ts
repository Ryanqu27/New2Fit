import api from '../../api';

export const ProfileService = {
    updateUsername: async (username: string) => {
        const response = await api.patch('/users/me/username', { username });
        return response.data;
    },

    uploadProfilePicture: async (file: File) => {
        const formData = new FormData();
        formData.append('file', file);
        const response = await api.post('/users/me/profile-picture', formData, {
            headers: {
                'Content-Type': 'multipart/form-data',
            },
        });
        return response.data;
    }
};
