import api from '../../api.ts';

export const getQuestions = async () => {
  const response = await api.get('questionnaire/questions');
  return response.data;
}


export const submitQuestions = async (userResponses: string[]) => {
  const response = await api.post('questionnaire/submit', { answers: userResponses });
  return response.data;
}