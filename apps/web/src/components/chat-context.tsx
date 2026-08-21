"use client";

import React, { createContext, useContext, useState, ReactNode } from 'react';

type Message = { role: 'user' | 'assistant'; content: string; citations?: any[] };

interface ChatContextType {
  messages: Message[];
  setMessages: React.Dispatch<React.SetStateAction<Message[]>>;
  soundEnabled: boolean;
  setSoundEnabled: React.Dispatch<React.SetStateAction<boolean>>;
}

const ChatContext = createContext<ChatContextType | undefined>(undefined);

export function ChatProvider({ children }: { children: ReactNode }) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [soundEnabled, setSoundEnabled] = useState(true);

  return (
    <ChatContext.Provider value={{ messages, setMessages, soundEnabled, setSoundEnabled }}>
      {children}
    </ChatContext.Provider>
  );
}

export function useChat() {
  const context = useContext(ChatContext);
  if (context === undefined) {
    throw new Error('useChat must be used within a ChatProvider');
  }
  return context;
}
