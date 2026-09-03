'use client';

import React from 'react';
import { Sparkles, Presentation, FileSpreadsheet, MessageSquare, ShieldCheck, ArrowUpRight } from 'lucide-react';
import { DEMO_SCENARIOS } from '@/lib/mockData';
import { DemoScenario, TaskMode } from '@/lib/types';

interface WorkflowCardProps {
  onSelectScenario: (query: string, mode: TaskMode) => void;
}

export const WorkflowCard: React.FC<WorkflowCardProps> = ({
  onSelectScenario,
}) => {
  const getScenarioIcon = (mode: TaskMode) => {
    switch (mode) {
      case 'generate_ppt':
        return <Presentation className="h-4 w-4 text-[#2C2B5B]" />;
      case 'generate_excel':
        return <FileSpreadsheet className="h-4 w-4 text-[#2C2B5B]" />;
      case 'generate_report':
        return <ShieldCheck className="h-4 w-4 text-[#2C2B5B]" />;
      default:
        return <MessageSquare className="h-4 w-4 text-[#2C2B5B]" />;
    }
  };

  const getCustomTitle = (id: string, defaultTitle: string) => {
    switch (id) {
      case 'scenario-1':
        return 'Turn safety reports into a briefing';
      case 'scenario-2':
        return 'Find patterns in machine logs';
      case 'scenario-3':
        return 'Answer from operating procedures';
      case 'scenario-4':
        return 'Build a structured audit report';
      default:
        return defaultTitle;
    }
  };

  return (
    <div id="guided-workflows-card" className="surface-card rounded-2xl p-5 sm:p-6 mt-6 w-full animate-fade-slide-up">
      {/* Title */}
      <div className="flex items-center gap-2 mb-4 text-left">
        <Sparkles className="h-4 w-4 text-[#2C2B5B]" />
        <h3 className="font-display-serif text-xl font-bold text-[#1C1B24] tracking-tight">
          Try a workflow
        </h3>
      </div>

      {/* 2x2 Grid Layout */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3.5">
        {DEMO_SCENARIOS.map((scenario: DemoScenario) => {
          const displayTitle = getCustomTitle(scenario.id, scenario.title);

          return (
            <button
              key={scenario.id}
              onClick={() => onSelectScenario(scenario.query, scenario.mode)}
              className="w-full text-left p-4 rounded-xl bg-[#F5F2EB] border border-[#DCD7CE] hover:border-[#2C2B5B] hover:bg-[#FAF8F4] hover:-translate-y-0.5 hover:shadow-xs transition-all duration-200 group flex items-start justify-between gap-3 focus-visible:ring-2 focus-visible:ring-[#2C2B5B]"
            >
              <div className="flex items-start gap-3 min-w-0">
                <div className="p-2 rounded-lg bg-[#FAF8F4] border border-[#DCD7CE] group-hover:border-[#2C2B5B]/40 transition-colors mt-0.5">
                  {getScenarioIcon(scenario.mode)}
                </div>
                <div className="min-w-0">
                  <div className="flex items-center gap-2 flex-wrap mb-1">
                    <span className="text-xs font-bold text-[#1C1B24] group-hover:text-[#2C2B5B] transition-colors font-sans">
                      {displayTitle}
                    </span>
                  </div>
                  <p className="text-[11px] text-[#666370] line-clamp-2 leading-relaxed font-sans">
                    {scenario.description}
                  </p>
                </div>
              </div>

              <div className="flex items-center text-xs font-semibold text-[#2C2B5B] group-hover:translate-x-0.5 group-hover:-translate-y-0.5 transition-transform flex-shrink-0 mt-0.5">
                <ArrowUpRight className="h-4 w-4" />
              </div>
            </button>
          );
        })}
      </div>
    </div>
  );
};
