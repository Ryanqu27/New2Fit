import type { ConversationOut } from './messageService';

interface ConversationListProps {
    conversations: ConversationOut[];
    activeConversationId: number | null;
    onSelect: (conv: ConversationOut) => void;
}

export default function ConversationList({ conversations, activeConversationId, onSelect }: ConversationListProps) {
    if (conversations.length === 0) {
        return (
            <div className="conversations-empty">
                <p>No messages yet.</p>
                <p>Search for a user above to start chatting!</p>
            </div>
        );
    }

    return (
        <div className="conversations-list">
            {conversations.map(conv => (
                <button
                    key={conv.id}
                    className={`conversation-item ${conv.id === activeConversationId ? 'active' : ''}`}
                    onClick={() => onSelect(conv)}
                >
                    <div className="conversation-avatar">
                        {conv.other_user_name.charAt(0).toUpperCase()}
                    </div>
                    <div className="conversation-info">
                        <div className="conversation-name">{conv.other_user_name}</div>
                        {conv.last_message && (
                            <div className="conversation-preview">{conv.last_message}</div>
                        )}
                    </div>
                    {conv.unread_count > 0 && (
                        <span className="unread-badge">{conv.unread_count}</span>
                    )}
                </button>
            ))}
        </div>
    );
}
