'use client';

import React, { useState, useRef, useEffect } from 'react';
import { VoiceInput } from '@/components/voice-input';
import { ttsEngine } from '@/lib/tts';
import { Send, Volume2, VolumeX, FileText } from 'lucide-react';
import { useChat } from '@/components/chat-context';

export default function ResearchPage() {
  const [query, setQuery] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  
  // Chat state
  const { messages, setMessages, soundEnabled, setSoundEnabled } = useChat();

  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSubmit = async (e?: React.FormEvent) => {
    e?.preventDefault();
    if (!query.trim() || isProcessing) return;

    const userText = query;
    setQuery('');
    setMessages(prev => [...prev, { role: 'user', content: userText }]);
    setIsProcessing(true);

    let assistantText = '';
    let citationsData: any[] = [];
    
    // Add empty assistant message to stream into
    setMessages(prev => [...prev, { role: 'assistant', content: '', citations: [] }]);

    try {
      // Send last 3 messages as history
      const historyToSend = messages.slice(-3).map(m => ({ role: m.role, content: m.content }));

      const res = await fetch('/api/queries/stream', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          query: userText,
          history: historyToSend
        })
      });

      if (!res.ok) {
        throw new Error(`API Error: ${res.status} ${res.statusText}`);
      }

      if (res.body) {
        const reader = res.body.getReader();
        const decoder = new TextDecoder();
        let done = false;
        let buffer = '';

        while (!done) {
          const { value, done: doneReading } = await reader.read();
          done = doneReading;
          if (value) {
            buffer += decoder.decode(value, { stream: !done });
            // Responses are NDJSON
            const lines = buffer.split('\n');
            // Keep the last incomplete line in the buffer
            buffer = lines.pop() || '';
            
            for (const line of lines) {
              if (!line.trim()) continue;
              try {
                const data = JSON.parse(line);
                if (data.type === 'citations') {
                  citationsData = data.data;
                  setMessages(prev => {
                    const newArr = [...prev];
                    newArr[newArr.length - 1] = { ...newArr[newArr.length - 1], citations: citationsData };
                    return newArr;
                  });
                } else if (data.type === 'token') {
                  assistantText += data.data;
                  setMessages(prev => {
                    const newArr = [...prev];
                    newArr[newArr.length - 1] = { ...newArr[newArr.length - 1], content: assistantText };
                    return newArr;
                  });
                }
              } catch(e) {
                console.error("Failed to parse JSON stream line:", line, e);
              }
            }
          }
        }
        
        // When streaming is fully done, play the TTS
        if (soundEnabled && ttsEngine) {
          ttsEngine.speak(assistantText);
        }
      }
    } catch (err: any) {
      console.error(err);
      setMessages(prev => {
        const newArr = [...prev];
        const currentContent = newArr[newArr.length - 1].content;
        newArr[newArr.length - 1] = { 
          ...newArr[newArr.length - 1], 
          content: currentContent + `\n\n*(Error: ${err.message || 'Connection failed'})*`
        };
        return newArr;
      });
    } finally {
      setIsProcessing(false);
    }
  };

  const toggleSound = () => {
    setSoundEnabled(prev => !prev);
    if (soundEnabled && ttsEngine) {
      ttsEngine.stop();
    }
  };

  return (
    <div className="flex h-full flex-col max-w-5xl mx-auto w-full pt-8 pb-4 px-4">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-slate-100">Research Assistant</h1>
          <p className="text-slate-400 mt-1">Ask questions across your knowledge base.</p>
        </div>
        <button 
          onClick={toggleSound}
          className={`p-3 rounded-full transition-colors ${soundEnabled ? 'bg-blue-600 text-white' : 'bg-slate-800 text-slate-400'}`}
          title={soundEnabled ? "Mute Voice output" : "Enable Voice output"}
        >
          {soundEnabled ? <Volume2 className="h-5 w-5" /> : <VolumeX className="h-5 w-5" />}
        </button>
      </div>

      <div className="flex-1 overflow-y-auto mb-6 bg-slate-900/50 rounded-xl border border-slate-800 p-6 space-y-6">
        {messages.length === 0 ? (
          <div className="h-full flex items-center justify-center text-slate-500">
            Send a message or use your voice to begin.
          </div>
        ) : (
          messages.map((msg, i) => (
            <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
              <div className={`max-w-[80%] rounded-2xl p-5 ${
                msg.role === 'user' 
                  ? 'bg-blue-600 text-white rounded-br-none' 
                  : 'bg-slate-800 text-slate-200 border border-slate-700 rounded-bl-none'
              }`}>
                <div className="whitespace-pre-wrap">{msg.content}</div>
                
                {/* Citations */}
                {msg.citations && msg.citations.length > 0 && (
                  <div className="mt-4 pt-4 border-t border-slate-700 space-y-2">
                    <p className="text-xs text-slate-400 font-semibold uppercase tracking-wider">Sources</p>
                    <div className="flex flex-wrap gap-2">
                      {msg.citations.map((cit, idx) => (
                        <div key={idx} className="flex items-center space-x-1 text-xs bg-slate-900 px-2 py-1 rounded text-slate-300 group cursor-pointer" title={cit.snippet}>
                          <FileText className="h-3 w-3 text-blue-400" />
                          <span>[{cit.number}] {cit.document_name}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          ))
        )}
        <div ref={messagesEndRef} />
      </div>

      <div className="flex items-end space-x-4">
        <VoiceInput 
          onTranscribe={(text) => {
            setQuery(text);
            // Optionally auto-submit: setTimeout(() => handleSubmit(), 100);
          }} 
          isProcessing={isProcessing}
        />
        
        <form onSubmit={handleSubmit} className="flex-1 relative">
          <input 
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Ask a question..."
            disabled={isProcessing}
            className="w-full bg-slate-800 border border-slate-700 rounded-full py-4 pl-6 pr-14 text-slate-200 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent placeholder:text-slate-500"
          />
          <button 
            type="submit"
            disabled={!query.trim() || isProcessing}
            className="absolute right-2 top-2 bottom-2 aspect-square flex items-center justify-center rounded-full bg-blue-600 text-white hover:bg-blue-700 disabled:opacity-50 disabled:hover:bg-blue-600 transition-colors"
          >
            <Send className="h-4 w-4" />
          </button>
        </form>
      </div>
    </div>
  );
}
