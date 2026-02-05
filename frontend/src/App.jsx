import { useState } from 'react'
import ChatWindow from './components/ChatWindow'
import { MessageSquare } from 'lucide-react'

function App() {
  return (
    <div className="min-h-screen bg-slate-100 flex flex-col items-center justify-center p-4">
      <header className="mb-6 text-center">
        <div className="flex items-center justify-center gap-2 mb-2">
          <div className="bg-primary p-2 rounded-lg">
            <MessageSquare className="w-8 h-8 text-white" />
          </div>
          <h1 className="text-3xl font-bold text-slate-800">HR Buddy</h1>
        </div>
        <p className="text-slate-500">Your AI assistant for HR queries and leaves</p>
      </header>

      <main className="w-full max-w-2xl bg-white rounded-2xl shadow-xl overflow-hidden h-[600px] border border-slate-200">
        <ChatWindow />
      </main>
    </div>
  )
}

export default App
