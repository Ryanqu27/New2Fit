import { useState, useEffect, useRef } from 'react';
import { getMessages, markMessagesAsRead, type MessageOut } from './messageService';

interface ChatWindowProps {
    conversationId: number;
    otherUserName: string;
    currentUserId: number;
    incomingMessage: MessageOut | null;
    onSend: (conversationId: number, content: string) => void;
}

export default function ChatWindow({
    conversationId,
    otherUserName,
    currentUserId,
    incomingMessage,
    onSend,
}: ChatWindowProps) {
    const [messages, setMessages] = useState<MessageOut[]>([]);
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(true);
    const bottomRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        let ignore = false;

        setLoading(true);
        setMessages([]);
        getMessages(conversationId)
            .then(data => {
                if (!ignore) {
                    setMessages([...data].reverse());
                }
            })
            .catch(console.error)
            .finally(() => {
                if (!ignore) {
                    setLoading(false);
                }
            });

        markMessagesAsRead(conversationId).catch(console.error);

        return () => { ignore = true; };
    }, [conversationId]);

    useEffect(() => {
        if (!incomingMessage) return;
        if (incomingMessage.conversation_id !== conversationId) return;

        setMessages(prev => {
            if (prev.some(m => m.id === incomingMessage.id)) return prev;
            return [...prev, incomingMessage];
        });

        if (incomingMessage.sender_id !== currentUserId) {
            markMessagesAsRead(conversationId).catch(console.error);
        }
    }, [incomingMessage, conversationId, currentUserId]);

    useEffect(() => {
        bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages]);

    const handleSend = () => {
        const trimmed = input.trim();
        if (!trimmed) return;
        onSend(conversationId, trimmed);
        setInput('');
    };

    const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSend();
        }
    };

    const formatTime = (iso: string) => {
        const d = new Date(iso);
        return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    };

    return (
        <>
            <div className="chat-header">
                <div className="chat-header-avatar">
                    {otherUserName.charAt(0).toUpperCase()}
                </div>
                <span className="chat-header-name">{otherUserName}</span>
            </div>

            {loading ? (
                <div className="chat-loading">Loading messages...</div>
            ) : (
                <div className="chat-messages">
                    {messages.map(msg => {
                        const isSent = msg.sender_id === currentUserId;
                        return (
                            <div key={msg.id} className={`message-row ${isSent ? 'sent' : 'received'}`}>
                                <div>
                                    <div className="message-bubble">{msg.content}</div>
                                    <div className="message-time">
                                        {formatTime(msg.created_at)}
                                        {isSent && msg.is_read && <span className="message-read"> • Read</span>}
                                    </div>
                                </div>
                            </div>
                        );
                    })}
                    <div ref={bottomRef} />
                </div>
            )}

            <div className="chat-input-bar">
                <textarea
                    className="chat-input"
                    rows={1}
                    placeholder="Type a message… (Enter to send)"
                    value={input}
                    onChange={e => setInput(e.target.value)}
                    onKeyDown={handleKeyDown}
                />
                <button
                    className="chat-send-btn"
                    onClick={handleSend}
                    disabled={!input.trim()}
                    aria-label="Send message"
                >
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                        <line x1="22" y1="2" x2="11" y2="13" />
                        <polygon points="22 2 15 22 11 13 2 9 22 2" />
                    </svg>
                </button>
            </div>
        </>
    );
}
