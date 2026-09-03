'use client';

import React from 'react';
import { User } from 'lucide-react';
import { ChatMessageItem } from '@/lib/types';

interface ChatMessageUserProps {
  message: ChatMessageItem;
}

export const ChatMessageUser: React.FC<ChatMessageUserProps> = ({ message }) => {
  return (
    <div className="flex justify-end my-5 animate-fade-slide-up">
      <div className="max-w-[85%] sm:max-w-[78%] bg-[#2C2B5B] text-[#FAF8F4] rounded-2xl rounded-tr-sm p-4 sm:p-5 shadow-xs border border-[#2C2B5B]">
        <div className="flex items-center justify-between gap-3 mb-2 pb-1 border-b border-[#FAF8F4]/20 text-[11px] font-sans">
          <div className="flex items-center gap-1.5 font-medium">
            <User className="h-3.5 w-3.5 text-[#FAF8F4]" />
            <span className="font-semibold text-white">Authorized Query</span>
            {message.mode && (
              <span className="px-2 py-0.5 rounded bg-[#FAF8F4]/15 text-[#FAF8F4] text-[9px] font-mono uppercase tracking-wider">
                Mode: {message.mode.replace('generate_', '')}
              </span>
            )}
          </div>
          <span className="font-mono text-[10px] text-[#FAF8F4]/80">{message.timestamp}</span>
        </div>

        <p className="text-sm sm:text-base leading-relaxed whitespace-pre-wrap font-sans text-left">
          {message.content}
        </p>
      </div>
    </div>
  );
};
