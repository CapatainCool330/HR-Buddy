import { useState, useEffect, useRef } from 'react'
import { Send, User, Bot, Loader2, Wifi, WifiOff } from 'lucide-react'
import MessageBubble from './MessageBubble'

export default function ChatWindow() {
    const [messages, setMessages] = useState([
        { id: 1, sender: 'bot', text: 'Hi! I am HR Buddy. ask me about leave policies, holidays, or apply for leave.' }
    ])
    const [input, setInput] = useState('')
    const [isConnected, setIsConnected] = useState(false)
    const [sessionId] = useState(() => {
        const stored = localStorage.getItem('hr_buddy_session_id');
        if (stored) return stored;
        const newId = 'user-' + Math.random().toString(36).substr(2, 9);
        localStorage.setItem('hr_buddy_session_id', newId);
        return newId;
    })
    const ws = useRef(null)
    const messagesEndRef = useRef(null)

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
    }

    useEffect(() => {
        scrollToBottom()
    }, [messages])

    // WebSocket Connection Logic
    useEffect(() => {
        const apiUrl = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';
        // Convert http/https to ws/wss
        const wsUrl = apiUrl.replace('http', 'ws') + `/ws/${sessionId}`;

        const connect = () => {
            ws.current = new WebSocket(wsUrl);

            ws.current.onopen = () => {
                console.log("Connected to WebSocket");
                setIsConnected(true);
            };

            ws.current.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    const botMessage = {
                        id: Date.now(),
                        sender: 'bot',
                        text: data.content || data.response, // Handle potential variations
                        type: data.type
                    };
                    setMessages(prev => [...prev, botMessage]);
                } catch (e) {
                    console.error("Error parsing message:", e);
                }
            };

            ws.current.onclose = () => {
                console.log("Disconnected. Reconnecting...");
                setIsConnected(false);
                // Simple reconnect logic
                setTimeout(connect, 3000);
            };

            ws.current.onerror = (err) => {
                console.error("WebSocket error:", err);
                ws.current.close();
            };
        };

        connect();

        return () => {
            if (ws.current) {
                ws.current.close();
            }
        };
    }, [sessionId]);

    const handleSend = () => {
        if (!input.trim() || !isConnected) return

        const userMessage = { id: Date.now(), sender: 'user', text: input }
        setMessages(prev => [...prev, userMessage])

        // Send via WebSocket
        ws.current.send(JSON.stringify({ message: input }));

        setInput('')
    }

    const handleKeyPress = (e) => {
        if (e.key === 'Enter') handleSend()
    }

    return (
        <div className="flex flex-col h-full">
            {/* Connection Status Header */}
            <div className={`text-xs px-4 py-1 text-center text-white ${isConnected ? 'bg-green-500' : 'bg-red-500'} transition-colors duration-300`}>
                {isConnected ?
                    <span className="flex items-center justify-center gap-1"><Wifi size={12} /> Connected to Real-time Server</span> :
                    <span className="flex items-center justify-center gap-1"><WifiOff size={12} /> Disconnected - Trying to reconnect...</span>
                }
            </div>

            {/* Messages Area */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-slate-50">
                {messages.map((msg) => (
                    <MessageBubble key={msg.id} message={msg} />
                ))}
                <div ref={messagesEndRef} />
            </div>

            {/* Input Area */}
            <div className="p-4 bg-white border-t border-slate-100">
                <div className="flex gap-2">
                    <input
                        type="text"
                        className="flex-1 px-4 py-3 bg-slate-100 border-transparent focus:bg-white focus:border-primary focus:ring-2 focus:ring-primary/20 rounded-xl outline-none transition-all placeholder-slate-400"
                        placeholder="Type your question..."
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        onKeyPress={handleKeyPress}
                        disabled={!isConnected}
                    />
                    <button
                        onClick={handleSend}
                        disabled={!isConnected || !input.trim()}
                        className="bg-primary hover:bg-blue-700 text-white p-3 rounded-xl transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                        <Send className="w-5 h-5" />
                    </button>
                </div>
            </div>
        </div>
    )
}
