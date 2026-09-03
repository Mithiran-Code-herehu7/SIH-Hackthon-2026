'use client';

import React from 'react';
import { MessageSquare, Sparkles } from 'lucide-react';

interface EmptyConversationProps {
  onTriggerDemo: () => void;
}

export const EmptyConversation: React.FC<EmptyConversationProps> = ({ onTriggerDemo }) => {
  return (
    <div className="h-full flex flex-col items-center justify-center py-16 px-4 text-center">
      {/* Decorative SVG Shapes */}
      <div className="relative mb-4">
        <div className="w-16 h-16 rounded-2xl bg-[#EFECE5] border border-[#DDD8D0] flex items-center justify-center text-[#39318C] shadow-sm transform -rotate-3">
          <MessageSquare className="h-8 w-8 stroke-[1.5]" />
        </div>
        <div className="absolute -top-1 -right-1 w-6 h-6 rounded-full bg-[#E98A3A] text-white flex items-center justify-center shadow-2xs">
          <Sparkles className="h-3.5 w-3.5" />
        </div>
      </div>

      <h3 className="font-display-serif text-2xl font-bold text-[#15151A] tracking-tight">
        Nothing in the conversation yet.
      </h3>

      <p className="text-xs sm:text-sm text-[#68656A] mt-2 max-w-md leading-relaxed font-sans">
        Ask about your indexed files, or choose a guided workflow to see the workbench in action.
      </p>

      <button
        onClick={onTriggerDemo}
        className="mt-5 px-4 py-2 rounded-xl text-xs font-semibold text-[#39318C] bg-[#EFECE5] border border-[#DDD8D0] hover:bg-[#39318C] hover:text-white transition-all shadow-2xs"
      >
        Explore guided workflows →
      </button>
    </div>
  );
};
