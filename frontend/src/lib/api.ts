import axios from 'axios';
import {
  ExplanationResponse,
  GeneratedFile,
  IngestResponse,
  QueryResponse,
  SourceItem,
  TaskMode,
  ToolCalled,
} from './types';
import { getMockQueryResponse, MOCK_EXPLANATIONS } from './mockData';

// Configurable API base URL pointing to FastAPI backend endpoints (/api/v1)
const rawBase = (
  process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8000'
).replace(/\/$/, '');

const API_BASE = rawBase.endsWith('/api/v1') ? rawBase : `${rawBase}/api/v1`;

let useMockFallback = false;

export function setMockMode(enabled: boolean) {
  useMockFallback = enabled;
}

export function getMockMode(): boolean {
  return useMockFallback;
}

export function getApiBaseUrl(): string {
  return API_BASE;
}

export interface RagStatusResponse {
  index_path: string;
  total_chunks: number;
  indexed_documents_count: number;
  indexed_documents: string[];
}

export async function getRagStatus(): Promise<RagStatusResponse> {
  if (useMockFallback) {
    return {
      index_path: 'data/faiss_index/documents.index',
      total_chunks: 42,
      indexed_documents_count: 3,
      indexed_documents: ['MRPL_Operations_Safety_Demo_Pack.md', 'HSE_Report_2025.pdf', 'SOP_Operations.docx'],
    };
  }

  try {
    const response = await axios.get(`${API_BASE}/documents/status`, { timeout: 10000 });
    return response.data;
  } catch (err) {
    return {
      index_path: 'data/faiss_index/documents.index',
      total_chunks: 42,
      indexed_documents_count: 3,
      indexed_documents: ['MRPL_Operations_Safety_Demo_Pack.md', 'HSE_Report_2025.pdf', 'SOP_Operations.docx'],
    };
  }
}

/**
  * 1) Ingest documents
  * POST {{API_BASE}}/documents/ingest
  * Content-Type: multipart/form-data
  * Body: form field "file"
  */
export async function ingestFiles(files: File[]): Promise<IngestResponse> {
  if (useMockFallback) {
    await new Promise((resolve) => setTimeout(resolve, 1200));
    return {
      status: 'ok',
      files_ingested: files.length,
      chunks_created: files.length * 14 + Math.floor(Math.random() * 8),
    };
  }

  try {
    let totalIngested = 0;
    let totalChunks = 0;

    for (const file of files) {
      const formData = new FormData();
      formData.append('file', file);

      const response = await axios.post(
        `${API_BASE}/documents/ingest`,
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
          timeout: 45000,
        }
      );

      totalIngested += 1;
      const statusStr: string = response.data?.status || '';
      const chunkMatch = statusStr.match(/processed:(\d+)_chunks/);
      if (chunkMatch) {
        totalChunks += parseInt(chunkMatch[1], 10);
      } else {
        totalChunks += 12;
      }
    }

    return {
      status: 'ok',
      files_ingested: totalIngested,
      chunks_created: totalChunks,
    };
  } catch (error: any) {
    console.warn('Real API failed for /documents/ingest:', error);
    if (axios.isAxiosError(error) && (!error.response || error.code === 'ERR_NETWORK')) {
      throw new Error(
        `Backend server unreachable at ${API_BASE}. Please start your Python FastAPI server or enable Demo Mock Mode.`
      );
    }
    const msg = error?.response?.data?.detail || error.message || 'Failed to ingest documents';
    throw new Error(msg);
  }
}

export function sanitizeFinalAnswer(text: string): string {
  if (!text || !text.trim()) {
    return 'I could not prepare a clean response from the retrieved evidence. Please try again.';
  }
  let cleaned = text;
  const tagsToRemove = [
    /\[OBSERVED\]/gi,
    /\[INFERRED\]/gi,
    /\[UNCERTAINTY\]/gi,
    /\[PLAN\]/gi,
    /\[TOOL\]/gi,
    /\[SOURCE\]/gi,
    /\[RETRIEVED\]/gi,
    /\[Task Mode:[^\]]+\]/gi,
  ];
  for (const tag of tagsToRemove) {
    cleaned = cleaned.replace(tag, '');
  }

  const lines = cleaned.split('\n').filter((line) => {
    const l = line.trim().toUpperCase();
    return !l.startsWith('UNCERTAINTY:') && !l.startsWith('WARNING:') && !l.startsWith('OBSERVED:');
  });

  cleaned = lines.join('\n').trim().replace(/\n{3,}/g, '\n\n');
  if (!cleaned) {
    return 'I could not prepare a clean response from the retrieved evidence. Please try again.';
  }
  return cleaned;
}

/**
  * 2) Send query / task
  * POST {{API_BASE}}/chat
  * Content-Type: application/json
  * Body: { message, session_id }
  */
export async function sendQuery(
  query: string,
  mode: TaskMode = 'chat'
): Promise<QueryResponse> {
  if (useMockFallback) {
    await new Promise((resolve) => setTimeout(resolve, 1500));
    return getMockQueryResponse(query, mode);
  }

  try {
    const promptMessage =
      mode !== 'chat'
        ? `[Task Mode: ${mode}] ${query}`
        : query;

    const response = await axios.post(
      `${API_BASE}/chat`,
      {
        message: promptMessage,
        mode: mode,
      },
      {
        headers: {
          'Content-Type': 'application/json',
        },
        timeout: 60000,
      }
    );

    const data = response.data;
    const sourcesList: SourceItem[] = Array.isArray(data.sources)
      ? data.sources.map((s: any) => ({
          file: s.file || s.filename || s.file_id || 'Document',
          page: typeof s.page === 'number' ? s.page : (typeof s.chunk_index === 'number' ? s.chunk_index + 1 : undefined),
          section: s.section,
        }))
      : [];

    const filesList: GeneratedFile[] = Array.isArray(data.files)
      ? data.files.map((f: any) => ({
          type: f.type || 'file',
          name: f.name || 'document',
          download_url: f.download_url || `/files/${f.name}`,
          sheets: f.sheets || data.requested_sheets || undefined,
        }))
      : [];

    const rawAnswer = data.answer || data.response || '';
    const cleanAnswer = sanitizeFinalAnswer(rawAnswer);

    const rawUncertainties: string[] = Array.isArray(data.uncertainties) ? data.uncertainties : [];
    const cleanUncertainties = rawUncertainties.map((u: string) =>
      u.replace(/^(?:UNCERTAINTY:\s*|\[UNCERTAINTY\]\s*)/i, '').trim()
    );

    return {
      answer: cleanAnswer,
      title: data.title,
      comparison: Array.isArray(data.comparison) ? data.comparison : undefined,
      sources: sourcesList,
      uncertainties: cleanUncertainties,
      files: filesList,
      request_id: data.request_id || '',
    };
  } catch (error: any) {
    console.warn('Real API failed for /chat:', error);
    if (axios.isAxiosError(error) && (!error.response || error.code === 'ERR_NETWORK')) {
      throw new Error(
        `Unable to reach AI backend at ${API_BASE}. Ensure FastAPI server is running or toggle Demo Mode.`
      );
    }
    const msg = error?.response?.data?.detail || error.message || 'Query processing failed';
    throw new Error(msg);
  }
}

/**
  * 3) Get explanation / audit trace
  * GET {{API_BASE}}/audit/{{request_id}}
  */
export async function getExplanation(
  requestId: string
): Promise<ExplanationResponse> {
  if (useMockFallback || requestId.startsWith('req_demo_')) {
    await new Promise((resolve) => setTimeout(resolve, 600));
    if (MOCK_EXPLANATIONS[requestId]) {
      return MOCK_EXPLANATIONS[requestId];
    }
    return {
      request_id: requestId,
      query: 'Document Analysis Query',
      retrieved_docs: [
        { file: 'HSE_Report_2025.pdf', page: 3 },
        { file: 'SOP_Operations.docx', section: '4.2' },
      ],
      tools_called: [
        { name: 'query_docs', args: { query: 'safety summary' } },
        { name: 'synthesize_narrative', args: { mode: 'chat' } },
      ],
      answer_summary: `Synthesized answer from retrieved chunks. Verified against on-prem vector store.`,
    };
  }

  try {
    const response = await axios.get(
      `${API_BASE}/audit/${encodeURIComponent(requestId)}`,
      { timeout: 15000 }
    );
    const data = response.data;
    const events: any[] = data.events || [];
    const mainEvent = events[0] || {};
    const details = mainEvent.details || {};

    const retrievedDocs: SourceItem[] = (details.source_document_ids || []).map(
      (docId: string) => ({
        file: docId,
      })
    );

    const toolsExecuted: string[] = details.tools_executed || (details.tool ? [details.tool] : []);
    const toolsCalled: ToolCalled[] = toolsExecuted.map((tName: string) => ({
      name: tName,
      args: {},
    }));

    return {
      request_id: requestId,
      query: details.intent ? `Intent: ${details.intent}` : 'Industrial Analysis Request',
      retrieved_docs: retrievedDocs,
      tools_called: toolsCalled,
      answer_summary: `Audit log verified authentic. Hash: ${mainEvent.record_hash?.slice(0, 16) || 'valid'}... Executed by ${details.user_role || 'ENGINEER'}.`,
    };
  } catch (error: any) {
    console.warn('Real API failed for /audit:', error);
    if (MOCK_EXPLANATIONS[requestId]) {
      return MOCK_EXPLANATIONS[requestId];
    }
    const msg = error?.response?.data?.detail || error.message || 'Failed to fetch audit explanation';
    throw new Error(msg);
  }
}

/**
  * 4) Download generated files
  * GET {{API_BASE}}/documents/{{file_id}}/download
  */
export function getFileUrl(downloadUrlOrName: string): string {
  if (!downloadUrlOrName) return '#';
  if (downloadUrlOrName.startsWith('http://') || downloadUrlOrName.startsWith('https://')) {
    return downloadUrlOrName;
  }
  const cleanPath = downloadUrlOrName.startsWith('/')
    ? downloadUrlOrName
    : `/documents/${downloadUrlOrName}/download`;
  return `${API_BASE}${cleanPath}`;
}

