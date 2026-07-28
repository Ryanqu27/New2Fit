import { useState, useEffect, useRef } from 'react';
import { getMessages, markMessagesAsRead, type MessageOut } from './messageService';

interface ChatWindowProps {
    conversationId: number;
    otherUserName: string;
    currentUserId: number;
    incomingMessage: MessageOut | null;
    incomingTypingEvent: { conversation_id: number, sender_id: number, is_typing: boolean } | null;
    onSend: (conversationId: number, content: string) => void;
    onTyping: (conversationId: number, isTyping: boolean) => void;
}

export default function ChatWindow({
    conversationId,
    otherUserName,
    currentUserId,
    incomingMessage,
    incomingTypingEvent,
    onSend,
    onTyping,
}: ChatWindowProps) {
    const [messages, setMessages] = useState<MessageOut[]>([]);
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(true);
    const [isOtherUserTyping, setIsOtherUserTyping] = useState(false);
    const bottomRef = useRef<HTMLDivElement>(null);
    const typingTimeoutRef = useRef<number | null>(null);

    // Cleanup typing timeout on unmount
    useEffect(() => {
        return () => {
            if (typingTimeoutRef.current) {
                clearTimeout(typingTimeoutRef.current);
            }
        };
    }, []);

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
        if (!incomingTypingEvent) return;
        if (incomingTypingEvent.conversation_id !== conversationId) return;
        if (incomingTypingEvent.sender_id === currentUserId) return;
        
        setIsOtherUserTyping(incomingTypingEvent.is_typing);
    }, [incomingTypingEvent, conversationId, currentUserId]);

    useEffect(() => {
        bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages]);

    const handleSend = () => {
        const trimmed = input.trim();
        if (!trimmed) return;
        
        // Clear local typing timeout immediately
        if (typingTimeoutRef.current) {
            clearTimeout(typingTimeoutRef.current);
            typingTimeoutRef.current = null;
        }
        
        onSend(conversationId, trimmed);
        setInput('');
    };

    const handleInputChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
        setInput(e.target.value);
        
        if (typingTimeoutRef.current) {
            clearTimeout(typingTimeoutRef.current);
        } else {
            // First keystroke -> send typing start
            onTyping(conversationId, true);
        }
        
        // Stop typing after 1.5 seconds of inactivity
        typingTimeoutRef.current = window.setTimeout(() => {
            onTyping(conversationId, false);
            typingTimeoutRef.current = null;
        }, 1500);
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

            {isOtherUserTyping && (
                <div className="typing-indicator-container">
                    <span className="typing-username">{otherUserName} is typing</span>
                    <div className="typing-dots">
                        <span>.</span><span>.</span><span>.</span>
                    </div>
                </div>
            )}

            <div className="chat-input-bar">
                <textarea
                    className="chat-input"
                    rows={1}
                    placeholder="Type a message… (Enter to send)"
                    value={input}
                    onChange={handleInputChange}
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
