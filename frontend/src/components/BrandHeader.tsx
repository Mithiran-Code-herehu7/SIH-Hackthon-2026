'use client';

import React, { useState, useEffect } from 'react';
import { Server, ToggleLeft, ToggleRight } from 'lucide-react';
import { getApiBaseUrl } from '@/lib/api';

interface BrandHeaderProps {
  isMockMode: boolean;
  onToggleMockMode: (enabled: boolean) => void;
}

export const BrandHeader: React.FC<BrandHeaderProps> = ({
  isMockMode,
  onToggleMockMode,
}) => {
  const [isScrolled, setIsScrolled] = useState(false);
  const apiBase = getApiBaseUrl();

  useEffect(() => {
    let ticking = false;

    const handleScroll = () => {
      if (!ticking) {
        window.requestAnimationFrame(() => {
          const sy = window.scrollY;
          if (sy > 60) {
            setIsScrolled(true);
          } else if (sy < 15) {
            setIsScrolled(false);
          }
          ticking = false;
        });
        ticking = true;
      }
    };

    window.addEventListener('scroll', handleScroll, { passive: true });
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  return (
    <header
      className={`w-full border-b border-[#DCD7CE] bg-[#F5F2EB]/95 backdrop-blur-md sticky top-0 z-40 px-4 sm:px-8 transition-all duration-300 ease-in-out ${
        isScrolled ? 'py-2.5 shadow-xs' : 'py-4 sm:py-5'
      }`}
    >
      <div className="max-w-7xl mx-auto flex items-center justify-between gap-4 transition-all duration-300 ease-in-out">
        {/* Refined Brand Title: Balanced initial size, shrinks compactly on scroll */}
        <div className="flex items-center">
          <h1
            className={`font-display-serif font-bold tracking-tight text-[#1C1B24] transition-all duration-300 ease-in-out origin-left select-none ${
              isScrolled
                ? 'text-lg sm:text-xl'
                : 'text-2xl sm:text-3xl lg:text-4xl'
            }`}
          >
            Agentic AI Workbench
          </h1>
        </div>

        {/* Right: Retro Backend Mode Switch */}
        <div className="flex items-center gap-2 px-3 py-1.5 rounded-xl bg-[#FAF8F4] border border-[#DCD7CE] shadow-2xs flex-shrink-0 transition-all duration-300">
          <Server className="h-4 w-4 text-[#2C2B5B]" />
          <span className="text-[#666370] font-medium text-xs hidden xs:inline">
            Backend:
          </span>
          <span className="font-mono text-xs font-semibold text-[#2C2B5B]">
            {isMockMode ? 'Demo Mock' : apiBase}
          </span>

          <button
            onClick={() => onToggleMockMode(!isMockMode)}
            className="ml-1 flex items-center text-[#2C2B5B] hover:text-[#1C1B24] transition-colors focus-visible:ring-2 focus-visible:ring-[#2C2B5B] rounded"
            title={isMockMode ? 'Switch to Live FastAPI Backend' : 'Switch to Demo Mock Mode'}
          >
            {isMockMode ? (
              <ToggleLeft className="h-5 w-5 text-[#2C2B5B]" />
            ) : (
              <ToggleRight className="h-5 w-5 text-[#2C2B5B]" />
            )}
          </button>
        </div>
      </div>
    </header>
  );
};
