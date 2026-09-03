'use client';

import React from 'react';
import { Sparkles, Play, Presentation, FileSpreadsheet, MessageSquare, ShieldCheck } from 'lucide-react';
import { DEMO_SCENARIOS } from '@/lib/mockData';
import { DemoScenario, TaskMode } from '@/lib/types';

interface DemoButtonsProps {
  onSelectScenario: (query: string, mode: TaskMode) => void;
}

export const DemoButtons: React.FC<DemoButtonsProps> = ({
  onSelectScenario,
}) => {
  const getScenarioIcon = (mode: TaskMode) => {
    switch (mode) {
      case 'generate_ppt':
        return <Presentation className="h-4 w-4 text-amber-400" />;
      case 'generate_excel':
        return <FileSpreadsheet className="h-4 w-4 text-emerald-400" />;
      case 'generate_report':
        return <ShieldCheck className="h-4 w-4 text-cyan-400" />;
      default:
        return <MessageSquare className="h-4 w-4 text-blue-400" />;
    }
  };

  return (
    <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-4 glass-panel mt-4">
      <div className="flex items-center gap-2 mb-3">
        <Sparkles className="h-4 w-4 text-amber-400" />
        <h2 className="text-sm font-semibold text-slate-200">
          Demo Scenarios & Task Presets
        </h2>
      </div>
      <p className="text-xs text-slate-400 mb-3">
        Click any task preset below to auto-fill the query & select mode for rapid judge evaluation:
      </p>

      <div className="space-y-2">
        {DEMO_SCENARIOS.map((scenario: DemoScenario) => (
          <button
            key={scenario.id}
            onClick={() => onSelectScenario(scenario.query, scenario.mode)}
            className="w-full text-left p-2.5 rounded-lg bg-slate-950/70 border border-slate-800 hover:border-blue-500/50 hover:bg-slate-900 transition-all group flex items-start justify-between gap-2"
          >
            <div className="flex items-start gap-2.5 min-w-0">
              <div className="p-1.5 rounded-md bg-slate-900 border border-slate-800 group-hover:border-slate-700 mt-0.5">
                {getScenarioIcon(scenario.mode)}
              </div>
              <div className="min-w-0">
                <div className="flex items-center gap-1.5 flex-wrap">
                  <span className="text-xs font-semibold text-slate-200 group-hover:text-blue-300 transition-colors">
                    {scenario.title}
                  </span>
                  <span className="text-[9px] font-mono px-1.5 py-0.2 rounded bg-slate-800 text-slate-400 border border-slate-700">
                    {scenario.badge}
                  </span>
                </div>
                <p className="text-[11px] text-slate-400 mt-0.5 line-clamp-1">
                  {scenario.description}
                </p>
              </div>
            </div>

            <div className="flex items-center gap-1 text-[10px] font-semibold text-blue-400 group-hover:translate-x-0.5 transition-transform flex-shrink-0 mt-1">
              <span>Run</span>
              <Play className="h-3 w-3 fill-blue-400" />
            </div>
          </button>
        ))}
      </div>
    </div>
  );
};
