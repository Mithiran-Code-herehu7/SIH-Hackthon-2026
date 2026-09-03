'use client';

import React from 'react';
import { AlertCircle, CheckCircle2, Info, AlertTriangle, X } from 'lucide-react';
import { ToastMessage } from '@/lib/types';

interface ToastProps {
  toasts: ToastMessage[];
  onDismiss: (id: string) => void;
}

export const NotificationToast: React.FC<ToastProps> = ({ toasts, onDismiss }) => {
  if (!toasts || toasts.length === 0) return null;

  return (
    <div className="fixed bottom-4 right-4 z-50 flex flex-col gap-2 max-w-md w-full px-4 sm:px-0">
      {toasts.map((toast) => {
        const getIcon = () => {
          switch (toast.type) {
            case 'success':
              return <CheckCircle2 className="h-5 w-5 text-emerald-400 flex-shrink-0" />;
            case 'error':
              return <AlertCircle className="h-5 w-5 text-rose-400 flex-shrink-0" />;
            case 'warning':
              return <AlertTriangle className="h-5 w-5 text-amber-400 flex-shrink-0" />;
            default:
              return <Info className="h-5 w-5 text-blue-400 flex-shrink-0" />;
          }
        };

        const getBorderColor = () => {
          switch (toast.type) {
            case 'success':
              return 'border-emerald-800/80 bg-slate-900/95';
            case 'error':
              return 'border-rose-800/80 bg-slate-900/95';
            case 'warning':
              return 'border-amber-800/80 bg-slate-900/95';
            default:
              return 'border-blue-800/80 bg-slate-900/95';
          }
        };

        return (
          <div
            key={toast.id}
            className={`flex items-start justify-between p-3 rounded-xl border shadow-xl backdrop-blur-md transition-all animate-fadeIn ${getBorderColor()}`}
          >
            <div className="flex items-start gap-3">
              {getIcon()}
              <div>
                <h4 className="text-xs font-bold text-slate-100">{toast.title}</h4>
                <p className="text-[11px] text-slate-300 mt-0.5 leading-normal">
                  {toast.message}
                </p>
              </div>
            </div>
            <button
              onClick={() => onDismiss(toast.id)}
              className="text-slate-400 hover:text-slate-200 p-1 transition-colors"
            >
              <X className="h-4 w-4" />
            </button>
          </div>
        );
      })}
    </div>
  );
};
