import { User, Bot } from 'lucide-react'

export default function MessageBubble({ message }) {
    const isBot = message.sender === 'bot'

    return (
        <div className={`flex gap-3 ${isBot ? 'flex-row' : 'flex-row-reverse'}`}>
            <div className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 ${isBot ? 'bg-primary/10 text-primary' : 'bg-slate-200 text-slate-600'
                }`}>
                {isBot ? <Bot size={18} /> : <User size={18} />}
            </div>

            <div className={`max-w-[80%] rounded-2xl px-5 py-3 text-sm leading-relaxed shadow-sm ${isBot
                    ? 'bg-white text-slate-700 rounded-tl-none border border-slate-100'
                    : 'bg-primary text-white rounded-tr-none'
                }`}>
                <p>{message.text}</p>
                <span className={`text-[10px] mt-1 block opacity-70 ${isBot ? 'text-slate-400' : 'text-blue-100'}`}>
                    {new Date(message.id).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                </span>
            </div>
        </div>
    )
}
