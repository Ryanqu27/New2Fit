import { useEffect, useRef, useState, useCallback } from 'react';
import { useAuth } from '../../Auth/AuthContext';
import { getConversations, type ConversationOut, type MessageOut } from './messageService';
import UserSearch from './UserSearch';
import ConversationList from './ConversationList';
import ChatWindow from './ChatWindow';
import './MessagesPage.css';

const WS_BASE = import.meta.env.VITE_WS_BASE_URL || 'ws://localhost:8000/api/messages';

export default function MessagesPage() {
    const { user } = useAuth();
    const [conversations, setConversations] = useState<ConversationOut[]>([]);
    const [activeConv, setActiveConv] = useState<ConversationOut | null>(null);
    const [incomingMessage, setIncomingMessage] = useState<MessageOut | null>(null);
    const wsRef = useRef<WebSocket | null>(null);

    useEffect(() => {
        getConversations().then(setConversations).catch(console.error);
    }, []);

    // Open persistent WebSocket on mount
    useEffect(() => {
        const ws = new WebSocket(`${WS_BASE}/ws`);
        wsRef.current = ws;

        ws.onmessage = (event) => {
            try {
                const msg: MessageOut = JSON.parse(event.data);
                setIncomingMessage(msg);

                setConversations(prev => prev.map(conv => {
                    if (conv.id !== msg.conversation_id) return conv;
                    const isActive = activeConvRef.current?.id === conv.id;
                    return {
                        ...conv,
                        last_message: msg.content,
                        unread_count: isActive ? 0 : (conv.unread_count + (msg.sender_id !== user?.id ? 1 : 0)),
                    };
                }));
            } catch {
                // Non-JSON messages (e.g. ping) can be ignored
            }
        };

        ws.onerror = (e) => console.error('WebSocket error', e);

        return () => {
            ws.close();
        };
    }, []);

    const activeConvRef = useRef<ConversationOut | null>(null);
    activeConvRef.current = activeConv;

    const handleSelectConversation = useCallback((conv: ConversationOut) => {
        setActiveConv(conv);
        // Clear unread badge on the selected conversation
        setConversations(prev => prev.map(c =>
            c.id === conv.id ? { ...c, unread_count: 0 } : c
        ));
    }, []);

    const handleConversationStart = useCallback((conv: ConversationOut) => {
        setConversations(prev => {
            const exists = prev.some(c => c.id === conv.id);
            return exists ? prev : [conv, ...prev];
        });
        setActiveConv(conv);
    }, []);

    const handleSend = useCallback((conversationId: number, content: string) => {
        if (!wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) {
            console.warn('WebSocket not open');
            return;
        }
        wsRef.current.send(JSON.stringify({ conversation_id: conversationId, content }));
    }, []);

    return (
        <div className="messages-page">
            <div className="messages-sidebar">
                <div className="messages-sidebar-header">
                    <h2 className="messages-sidebar-title">Messages</h2>
                    <UserSearch onConversationStart={handleConversationStart} />
                </div>
                <ConversationList
                    conversations={conversations}
                    activeConversationId={activeConv?.id ?? null}
                    onSelect={handleSelectConversation}
                />
            </div>

            <div className="chat-window">
                {activeConv ? (
                    <ChatWindow
                        key={activeConv.id}
                        conversationId={activeConv.id}
                        otherUserName={activeConv.other_user_name}
                        currentUserId={user?.id ?? 0}
                        incomingMessage={incomingMessage}
                        onSend={handleSend}
                    />
                ) : (
                    <div className="chat-empty-state">
                        <div className="chat-empty-icon">💬</div>
                        <p>Select a conversation or search for a user to get started.</p>
                    </div>
                )}
            </div>
        </div>
    );
}
