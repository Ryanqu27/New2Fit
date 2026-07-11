import { useState, useRef, useEffect } from 'react';
import { searchUsers, getOrCreateConversation, type UserSearchResult, type ConversationOut } from './messageService';

interface UserSearchProps {
    onConversationStart: (conv: ConversationOut) => void;
}

export default function UserSearch({ onConversationStart }: UserSearchProps) {
    const [query, setQuery] = useState('');
    const [results, setResults] = useState<UserSearchResult[]>([]);
    const [isOpen, setIsOpen] = useState(false);
    const [loading, setLoading] = useState(false);
    const debounceRef = useRef<ReturnType<typeof setTimeout> | null>(null);
    const wrapperRef = useRef<HTMLDivElement>(null);

    // Debounced search
    useEffect(() => {
        if (query.trim().length < 2) {
            setResults([]);
            setIsOpen(false);
            return;
        }
        if (debounceRef.current) clearTimeout(debounceRef.current);
        debounceRef.current = setTimeout(async () => {
            try {
                setLoading(true);
                const data = await searchUsers(query.trim());
                setResults(data);
                setIsOpen(true);
            } catch {
                setResults([]);
            } finally {
                setLoading(false);
            }
        }, 300);

        return () => { if (debounceRef.current) clearTimeout(debounceRef.current); };
    }, [query]);

    useEffect(() => {
        const handler = (e: MouseEvent) => {
            if (wrapperRef.current && !wrapperRef.current.contains(e.target as Node)) {
                setIsOpen(false);
            }
        };
        document.addEventListener('mousedown', handler);
        return () => document.removeEventListener('mousedown', handler);
    }, []);

    const handleSelect = async (userId: number) => {
        setQuery('');
        setIsOpen(false);
        setResults([]);
        try {
            const conv = await getOrCreateConversation(userId);
            onConversationStart(conv);
        } catch (e) {
            console.error('Failed to start conversation', e);
        }
    };

    return (
        <div className="user-search-wrapper" ref={wrapperRef}>
            <input
                className="user-search-input"
                type="text"
                placeholder="Search users to message..."
                value={query}
                onChange={e => setQuery(e.target.value)}
                autoComplete="off"
            />
            {isOpen && (
                <div className="user-search-results">
                    {loading ? (
                        <div className="user-search-no-results">Searching...</div>
                    ) : results.length > 0 ? (
                        results.map(u => (
                            <button
                                key={u.id}
                                className="user-search-result-item"
                                onClick={() => handleSelect(u.id)}
                            >
                                <div className="search-result-avatar">
                                    {u.first_name.charAt(0).toUpperCase()}
                                </div>
                                <span className="search-result-name">{u.first_name}</span>
                            </button>
                        ))
                    ) : (
                        <div className="user-search-no-results">No users found</div>
                    )}
                </div>
            )}
        </div>
    );
}
