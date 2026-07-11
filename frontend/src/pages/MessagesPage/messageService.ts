import api from '../../api';

export interface ConversationOut {
    id: number;
    other_user_id: number;
    other_user_name: string;
    last_message: string | null;
    unread_count: number;
    created_at: string;
}

export interface MessageOut {
    id: number;
    conversation_id: number;
    sender_id: number;
    content: string;
    is_read: boolean;
    created_at: string;
}

export interface UserSearchResult {
    id: number;
    first_name: string;
}

export async function searchUsers(query: string): Promise<UserSearchResult[]> {
    const res = await api.get(`/messages/users/search?q=${encodeURIComponent(query)}`);
    return res.data;
}

export async function getOrCreateConversation(other_user_id: number): Promise<ConversationOut> {
    const res = await api.post('/messages/conversations', { other_user_id });
    return res.data;
}

export async function getConversations(): Promise<ConversationOut[]> {
    const res = await api.get('/messages/conversations');
    return res.data;
}

export async function getMessages(conversation_id: number): Promise<MessageOut[]> {
    const res = await api.get(`/messages/conversations/${conversation_id}/messages`);
    return res.data;
}

export async function markMessagesAsRead(conversation_id: number): Promise<void> {
    await api.post(`/messages/conversations/${conversation_id}/read`);
}
