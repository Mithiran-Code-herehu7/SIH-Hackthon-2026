'use client';

import React from 'react';
import { HelpCircle } from 'lucide-react';

interface UncertaintiesSectionProps {
  uncertainties?: string[];
}

export const UncertaintiesSection: React.FC<UncertaintiesSectionProps> = ({
  uncertainties,
}) => {
  if (!uncertainties || uncertainties.length === 0) return null;

  return (
    <div className="mt-5 pt-4 border-t border-[#DCD7CE]/80 text-left">
      <div className="flex items-center gap-1.5 text-xs font-semibold text-[#8C6B28] mb-2.5 uppercase tracking-wider font-sans">
        <HelpCircle className="h-3.5 w-3.5 text-[#8C6B28]" />
        <span>Information not found in the uploaded files ({uncertainties.length})</span>
      </div>

      <div className="p-3.5 rounded-xl bg-[#FFFBF0] border border-[#F0E4C3] text-xs text-[#5C471A] space-y-1.5">
        <ul className="list-disc list-inside space-y-1 font-sans">
          {uncertainties.map((item, idx) => (
            <li key={idx} className="leading-relaxed">
              <span>{item.replace(/^(?:UNCERTAINTY:\s*|\[UNCERTAINTY\]\s*)/i, '')}</span>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
};
