'use client';

import React from 'react';
import { Sparkles, Presentation, FileSpreadsheet, MessageSquare, ShieldCheck, ArrowRight } from 'lucide-react';
import { DEMO_SCENARIOS } from '@/lib/mockData';
import { DemoScenario, TaskMode } from '@/lib/types';

interface DemoScenariosCardProps {
  onSelectScenario: (query: string, mode: TaskMode) => void;
}

export const DemoScenariosCard: React.FC<DemoScenariosCardProps> = ({
  onSelectScenario,
}) => {
  const getScenarioIcon = (mode: TaskMode) => {
    switch (mode) {
      case 'generate_ppt':
        return <Presentation className="h-4 w-4 text-amber-700" />;
      case 'generate_excel':
        return <FileSpreadsheet className="h-4 w-4 text-emerald-700" />;
      case 'generate_report':
        return <ShieldCheck className="h-4 w-4 text-indigo-700" />;
      default:
        return <MessageSquare className="h-4 w-4 text-[#312E81]" />;
    }
  };

  return (
    <div className="card-editorial bg-white p-6 mt-5">
      {/* Title */}
      <div className="flex items-center gap-2 mb-4">
        <Sparkles className="h-4 w-4 text-[#312E81]" />
        <h2 className="font-serif-display text-xl font-bold text-[#111318] tracking-tight">
          Try these
        </h2>
      </div>

      <div className="space-y-3">
        {DEMO_SCENARIOS.map((scenario: DemoScenario) => (
          <button
            key={scenario.id}
            onClick={() => onSelectScenario(scenario.query, scenario.mode)}
            className="w-full text-left p-3.5 rounded-xl bg-[#FAF9F6] border border-[#E5E2DC] hover:border-[#312E81] hover:bg-white hover:-translate-y-1 hover:shadow-md transition-all duration-200 group flex items-start justify-between gap-3"
          >
            <div className="flex items-start gap-3 min-w-0">
              <div className="p-2 rounded-lg bg-white border border-[#E2DDD5] group-hover:border-[#C7D2FE] transition-colors mt-0.5">
                {getScenarioIcon(scenario.mode)}
              </div>
              <div className="min-w-0">
                <div className="flex items-center gap-2 flex-wrap">
                  <span className="text-xs font-bold text-[#111318] group-hover:text-[#312E81] transition-colors">
                    {scenario.title}
                  </span>
                  <span className="text-[9px] font-mono font-semibold px-1.5 py-0.2 rounded bg-[#EEF2FF] text-[#312E81] border border-[#C7D2FE]">
                    {scenario.badge}
                  </span>
                </div>
                <p className="text-[11px] text-[#525663] mt-1 line-clamp-1 leading-normal font-sans">
                  {scenario.description}
                </p>
              </div>
            </div>

            <div className="flex items-center text-xs font-semibold text-[#312E81] group-hover:translate-x-1 transition-transform flex-shrink-0 mt-1">
              <ArrowRight className="h-4 w-4" />
            </div>
          </button>
        ))}
      </div>
    </div>
  );
};
