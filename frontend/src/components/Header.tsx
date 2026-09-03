'use client';

import React from 'react';
import { ShieldCheck, Server, ToggleLeft, ToggleRight, Database } from 'lucide-react';
import { getApiBaseUrl } from '@/lib/api';

interface HeaderProps {
  isMockMode: boolean;
  onToggleMockMode: (enabled: boolean) => void;
  chunksCount?: number;
  ingestedFilesCount?: number;
}

export const Header: React.FC<HeaderProps> = ({
  isMockMode,
  onToggleMockMode,
  chunksCount = 42,
  ingestedFilesCount = 3,
}) => {
  const apiBase = getApiBaseUrl();

  return (
    <header className="w-full border-b border-[#E5E2DC] bg-[#FAF9F6]/90 backdrop-blur-md sticky top-0 z-30 px-4 sm:px-6 lg:px-8 py-5">
      <div className="max-w-[1240px] mx-auto flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        {/* Left: Editorial Header Title & Tagline */}
        <div>
          <div className="flex items-center gap-3">
            <div className="h-9 w-9 rounded-xl bg-[#312E81] text-white flex items-center justify-center shadow-md shadow-indigo-900/10 flex-shrink-0">
              <ShieldCheck className="h-5 w-5 text-amber-300" />
            </div>
            <div>
              <div className="flex items-center gap-2.5 flex-wrap">
                <h1 className="font-serif-display text-2xl sm:text-3xl font-bold tracking-tight text-[#111318]">
                  Agentic AI Workbench
                </h1>
                <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[11px] font-semibold bg-[#EEF2FF] text-[#312E81] border border-[#C7D2FE]">
                  <span className="w-1.5 h-1.5 rounded-full bg-[#4338CA]"></span>
                  Air-Gapped Node
                </span>
              </div>
            </div>
          </div>
          <p className="text-xs sm:text-sm text-[#525663] mt-1 font-sans">
            Private, offline intelligence for refineries, PSUs, and defense installations.
          </p>
        </div>

        {/* Right: Security & Network Telemetry Controls */}
        <div className="flex items-center gap-3 text-xs self-start md:self-auto">
          {/* Vector DB Metrics */}
          <div className="hidden sm:flex items-center gap-2 px-3.5 py-2 rounded-xl bg-white border border-[#E5E2DC] text-[#434752] shadow-xs font-medium">
            <Database className="h-3.5 w-3.5 text-[#312E81]" />
            <span>
              <strong className="text-[#111318]">{ingestedFilesCount}</strong> Docs ({chunksCount} chunks)
            </span>
          </div>

          {/* Backend Status / Mode Toggle */}
          <div className="flex items-center gap-2.5 px-3.5 py-2 rounded-xl bg-white border border-[#E5E2DC] shadow-xs">
            <Server className={`h-3.5 w-3.5 ${isMockMode ? 'text-amber-600' : 'text-emerald-600'}`} />
            <span className="text-[#525663] font-medium hidden xs:inline">
              Backend:
            </span>
            <span className={`font-mono text-[11px] font-semibold ${isMockMode ? 'text-amber-700' : 'text-emerald-700'}`}>
              {isMockMode ? 'Demo Mock' : apiBase}
            </span>

            <button
              onClick={() => onToggleMockMode(!isMockMode)}
              className="ml-1 flex items-center gap-1 text-[#525663] hover:text-[#111318] transition-colors"
              title={isMockMode ? 'Switch to Live FastAPI Backend' : 'Switch to Offline Demo Mock Mode'}
            >
              {isMockMode ? (
                <ToggleLeft className="h-5 w-5 text-amber-600" />
              ) : (
                <ToggleRight className="h-5 w-5 text-indigo-700" />
              )}
            </button>
          </div>
        </div>
      </div>
    </header>
  );
};
