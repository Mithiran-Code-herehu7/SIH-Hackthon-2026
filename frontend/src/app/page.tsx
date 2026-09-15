'use client';

import React, { useState, useRef, useEffect } from 'react';
import { BrandHeader } from '@/components/BrandHeader';
import { IntroSection } from '@/components/IntroSection';
import { ChatMessageUser } from '@/components/ChatMessageUser';
import { AssistantResult } from '@/components/AssistantResult';
import { EmptyConversation } from '@/components/EmptyConversation';
import { ChatComposer } from '@/components/ChatComposer';
import { DocumentDropzone } from '@/components/DocumentDropzone';
import { WorkflowCard } from '@/components/WorkflowCard';
import { ProcessJournal } from '@/components/ProcessJournal';
import { NotificationToast } from '@/components/NotificationToast';
import { IngestionStatusPanel } from '@/components/IngestionStatusPanel';
import {
  ChatMessageItem,
  IngestResponse,
  TaskMode,
  ToastMessage,
} from '@/lib/types';
import { INITIAL_CHAT_MESSAGES } from '@/lib/mockData';
import { getRagStatus, sendQuery, setMockMode } from '@/lib/api';

export default function Home() {
  const [messages, setMessages] = useState<ChatMessageItem[]>(INITIAL_CHAT_MESSAGES);
  const [selectedMode, setSelectedMode] = useState<TaskMode>('chat');
  const [inputQuery, setInputQuery] = useState<string>('');
  const [isQueryLoading, setIsQueryLoading] = useState<boolean>(false);
  const [isMockMode, setIsMockModeState] = useState<boolean>(false);
  const [activeExplanationId, setActiveExplanationId] = useState<string | null>(null);
  const [ingestStats, setIngestStats] = useState<{ files: number; chunks: number }>({
    files: 3,
    chunks: 42,
  });
  const [ragStatus, setRagStatus] = useState<any>({
    indexPath: 'data/faiss_index/documents.index',
    totalChunks: 42,
    indexedDocumentsCount: 3,
    indexedDocuments: ['MRPL_Operations_Safety_Demo_Pack.md', 'HSE_Report_2025.pdf', 'SOP_Operations.docx'],
    lastIngestionTime: 'Just now',
    latestQueryRetrieval: {
      query: 'Why is Pump P-204B considered a critical priority?',
      retrievedCount: 4,
      status: 'Success',
      sources: [
        { file: 'MRPL_Operations_Safety_Demo_Pack.md', section: '2.2 Key operating parameters' },
        { file: 'MRPL_Operations_Safety_Demo_Pack.md', section: '3.1 Incident and near-miss register', ids: ['INC-01', 'INC-07', 'INC-13'] },
        { file: 'MRPL_Operations_Safety_Demo_Pack.md', section: '4.1 Pump P-204B recurring vibration' },
        { file: 'MRPL_Operations_Safety_Demo_Pack.md', section: '6 Corrective action plan', ids: ['CAP-01', 'CAP-02'] },
      ],
    },
  });
  const [toasts, setToasts] = useState<ToastMessage[]>([]);

  const chatContainerRef = useRef<HTMLDivElement>(null);

  // Fetch live RAG status on load
  useEffect(() => {
    const fetchStatus = async () => {
      try {
        const status = await getRagStatus();
        setRagStatus((prev: any) => ({
          ...prev,
          indexPath: status.index_path,
          totalChunks: status.total_chunks,
          indexedDocumentsCount: status.indexed_documents_count,
          indexedDocuments: status.indexed_documents,
        }));
      } catch (err) {
        console.warn('Failed to fetch initial RAG status:', err);
      }
    };
    fetchStatus();
  }, []);

  // Auto-scroll conversation view to bottom
  useEffect(() => {
    if (chatContainerRef.current) {
      chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight;
    }
  }, [messages, isQueryLoading]);

  const addToast = (
    type: 'success' | 'error' | 'info' | 'warning',
    title: string,
    message: string
  ) => {
    const id = Math.random().toString(36).substring(2, 9);
    setToasts((prev) => [...prev, { id, type, title, message }]);
    setTimeout(() => {
      setToasts((prev) => prev.filter((t) => t.id !== id));
    }, 6000);
  };

  const removeToast = (id: string) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  };

  const handleToggleMockMode = (enabled: boolean) => {
    setIsMockModeState(enabled);
    setMockMode(enabled);
    addToast(
      'info',
      enabled ? 'Demo Mock Mode Active' : 'Live FastAPI Backend Mode Active',
      enabled
        ? 'Using local simulated AI responses for evaluation.'
        : 'Connecting directly to HTTP FastAPI backend.'
    );
  };

  const handleSendQuery = async (queryText: string, mode: TaskMode) => {
    if (!queryText.trim() || isQueryLoading) return;

    const userMsgId = `usr-${Date.now()}`;
    const assistantMsgId = `ast-${Date.now()}`;

    const newTime = new Date().toLocaleTimeString([], {
      hour: '2-digit',
      minute: '2-digit',
    });

    const userMsg: ChatMessageItem = {
      id: userMsgId,
      role: 'user',
      content: queryText,
      timestamp: newTime,
      mode,
    };

    const loadingAssistantMsg: ChatMessageItem = {
      id: assistantMsgId,
      role: 'assistant',
      content: '',
      timestamp: newTime,
      mode,
      isLoading: true,
    };

    setMessages((prev) => [...prev, userMsg, loadingAssistantMsg]);
    setInputQuery('');
    setIsQueryLoading(true);

    try {
      const response = await sendQuery(queryText, mode);

      setMessages((prev) =>
        prev.map((msg) =>
          msg.id === assistantMsgId
            ? {
                ...msg,
                isLoading: false,
                content: response.answer,
                title: response.title,
                comparison: response.comparison,
                sources: response.sources,
                uncertainties: response.uncertainties,
                files: response.files,
                request_id: response.request_id,
              }
            : msg
        )
      );

      // Update RAG retrieval debug trace
      setRagStatus((prev: any) => ({
        ...prev,
        latestQueryRetrieval: {
          query: queryText,
          retrievedCount: response.sources ? response.sources.length : 0,
          status: response.sources && response.sources.length > 0 ? 'Success' : 'No evidence found',
          sources: response.sources || [],
        },
      }));

      if (response.request_id) {
        setActiveExplanationId(response.request_id);
      }
    } catch (err: any) {
      console.error('Error sending query:', err);
      const errorMsg = err.message || 'Processing failed.';

      setMessages((prev) =>
        prev.map((msg) =>
          msg.id === assistantMsgId
            ? {
                ...msg,
                isLoading: false,
                error: errorMsg,
                content: `⚠️ **Task Execution Failure**: Could not get response from backend.`,
              }
            : msg
        )
      );

      addToast('error', 'Query Processing Error', errorMsg);
    } finally {
      setIsQueryLoading(false);
    }
  };

  const handleIngestSuccess = (res: IngestResponse) => {
    setIngestStats((prev) => ({
      files: prev.files + res.files_ingested,
      chunks: prev.chunks + res.chunks_created,
    }));

    // Refresh RAG Status Panel
    getRagStatus()
      .then((status) => {
        setRagStatus((prev: any) => ({
          ...prev,
          indexPath: status.index_path,
          totalChunks: status.total_chunks,
          indexedDocumentsCount: status.indexed_documents_count,
          indexedDocuments: status.indexed_documents,
          lastIngestionTime: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        }));
      })
      .catch(() => {});

    addToast(
      'success',
      'Documents Ingested',
      `Your workspace is up to date: ${res.files_ingested} file(s) ingested, ${res.chunks_created} vector chunks created.`
    );
  };

  const handleSelectScenario = (query: string, mode: TaskMode) => {
    setInputQuery(query);
    setSelectedMode(mode);
    addToast(
      'info',
      'Workflow Loaded',
      `Selected "${mode.replace('generate_', '')}" action mode. Click Send or press Enter.`
    );
  };

  const handleStartWithDocument = () => {
    const dropzoneEl = document.getElementById('document-dropzone-card');
    if (dropzoneEl) {
      dropzoneEl.scrollIntoView({ behavior: 'smooth' });
    }
  };

  const handleTryGuidedDemo = () => {
    const workflowEl = document.getElementById('guided-workflows-card');
    if (workflowEl) {
      workflowEl.scrollIntoView({ behavior: 'smooth' });
    }
  };

  return (
    <div className="min-h-screen flex flex-col bg-[#F5F2EB] text-[#1C1B24] font-sans selection:bg-[#2C2B5B] selection:text-white">
      {/* 1. Brand Header */}
      <BrandHeader
        isMockMode={isMockMode}
        onToggleMockMode={handleToggleMockMode}
      />

      {/* 2. Intro Section */}
      <IntroSection
        onStartWithDocument={handleStartWithDocument}
        onTryGuidedDemo={handleTryGuidedDemo}
      />

      {/* 3. Main Workspace */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-8 pb-12 space-y-6">
        {/* DOCUMENT DROPZONE ON TOP */}
        <DocumentDropzone
          onIngestSuccess={handleIngestSuccess}
          onError={(err) => addToast('error', 'Ingestion Failure', err)}
        />

        {/* INGESTION & RETRIEVAL DEBUG STATUS PANEL */}
        <IngestionStatusPanel
          indexPath={ragStatus.indexPath}
          totalChunks={ragStatus.totalChunks}
          indexedDocumentsCount={ragStatus.indexedDocumentsCount}
          indexedDocuments={ragStatus.indexedDocuments}
          lastIngestionTime={ragStatus.lastIngestionTime}
          latestQueryRetrieval={ragStatus.latestQueryRetrieval}
        />

        {/* CHAT CONVERSATION WORKSPACE CONTAINER */}
        <div className="surface-card rounded-2xl overflow-hidden min-h-[500px] flex flex-col w-full">
          {/* Conversation Bar Header */}
          <div className="flex items-center justify-between px-6 py-4 border-b border-[#DCD7CE] bg-[#F5F2EB]/80">
            <div className="flex items-center gap-2.5">
              <div className="h-2.5 w-2.5 rounded-full bg-[#2C2B5B] animate-pulse"></div>
              <h3 className="font-display-serif text-base font-bold text-[#1C1B24]">
                Conversation Workspace
              </h3>
              <span className="text-xs text-[#666370] font-mono">
                ({messages.length} messages)
              </span>
            </div>

            <button
              onClick={() => setMessages(INITIAL_CHAT_MESSAGES)}
              className="text-xs font-semibold text-[#666370] hover:text-[#1C1B24] px-3 py-1.5 rounded-xl bg-[#FAF8F4] border border-[#DCD7CE] hover:bg-[#EAE5DC] transition-colors"
              title="Reset conversation"
            >
              Reset Chat
            </button>
          </div>

          {/* Scrollable Conversation View */}
          <div
            ref={chatContainerRef}
            className="flex-1 overflow-y-auto p-4 sm:p-6 space-y-4 max-h-[calc(100vh-320px)] min-h-[360px]"
          >
            {messages.length === 0 ? (
              <EmptyConversation onTriggerDemo={handleTryGuidedDemo} />
            ) : (
              messages.map((msg) =>
                msg.role === 'user' ? (
                  <ChatMessageUser key={msg.id} message={msg} />
                ) : (
                  <AssistantResult
                    key={msg.id}
                    message={msg}
                    onViewExplanation={setActiveExplanationId}
                  />
                )
              )
            )}
          </div>

          {/* Anchored Chat Composer */}
          <ChatComposer
            onSend={handleSendQuery}
            isLoading={isQueryLoading}
            selectedMode={selectedMode}
            onModeChange={setSelectedMode}
            inputQuery={inputQuery}
            onQueryChange={setInputQuery}
          />
        </div>

        {/* TRY A WORKFLOW (2x2 Grid under Chat) */}
        <WorkflowCard onSelectScenario={handleSelectScenario} />

        {/* BEHIND THE ANSWER PROCESS JOURNAL */}
        {activeExplanationId && (
          <ProcessJournal
            requestId={activeExplanationId}
            onClose={() => setActiveExplanationId(null)}
          />
        )}
      </main>

      {/* Global Notification Toast Stack */}
      <NotificationToast toasts={toasts} onDismiss={removeToast} />
    </div>
  );
}
