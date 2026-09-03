'use client';

import React from 'react';
import { ArrowDownRight, Sparkles, FileText } from 'lucide-react';

interface IntroSectionProps {
  onStartWithDocument: () => void;
  onTryGuidedDemo: () => void;
}

export const IntroSection: React.FC<IntroSectionProps> = ({
  onStartWithDocument,
  onTryGuidedDemo,
}) => {
  return (
    <section className="pt-8 pb-6 px-4 sm:px-8 max-w-7xl w-full mx-auto border-b border-[#DCD7CE]/60 mb-6 text-left">
      <div className="max-w-4xl text-left flex flex-col items-start">
        {/* Left-Aligned Headline */}
        <h2 className="font-display-serif text-3xl sm:text-4xl lg:text-5xl font-bold tracking-tight text-[#1C1B24] leading-[1.15] text-left">
          Ask better questions of the work you already have.
        </h2>

        {/* Left-Aligned Supporting Text */}
        <p className="text-base sm:text-lg text-[#666370] mt-3.5 leading-relaxed font-sans max-w-3xl text-left">
          Read confidential files, turn findings into useful deliverables, and see how every answer was formed — entirely on your own servers.
        </p>

        {/* Left-Aligned Action Buttons */}
        <div className="flex flex-wrap items-center gap-3 mt-6 text-left">
          <button
            onClick={onStartWithDocument}
            className="btn-retro px-4 py-2.5 text-xs font-semibold flex items-center gap-2 shadow-xs active:scale-97"
          >
            <FileText className="h-4 w-4 text-[#FAF8F4]" />
            <span>Start with a document</span>
          </button>

          <button
            onClick={onTryGuidedDemo}
            className="px-4 py-2.5 rounded-xl text-xs font-semibold text-[#1C1B24] bg-[#FAF8F4] border border-[#DCD7CE] hover:bg-[#EAE5DC] hover:border-[#2C2B5B] transition-all flex items-center gap-2 shadow-2xs"
          >
            <Sparkles className="h-4 w-4 text-[#2C2B5B]" />
            <span>Try a guided demo</span>
            <ArrowDownRight className="h-3.5 w-3.5 text-[#666370]" />
          </button>
        </div>
      </div>
    </section>
  );
};
