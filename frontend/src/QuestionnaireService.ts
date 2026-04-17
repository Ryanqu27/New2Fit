import api from './api.ts';

export const getQuestions = async () => {
  const response = await api.get('questionnaire/questions');
  return response.data;
}