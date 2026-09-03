import axios from 'axios';
import {
  ExplanationResponse,
  IngestResponse,
  QueryResponse,
  TaskMode,
} from './types';
import { getMockQueryResponse, MOCK_EXPLANATIONS } from './mockData';

// Configurable API base URL with fallback to http://localhost:8000
const API_BASE = (
  process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8000'
).replace(/\/$/, '');

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

/**
  * 1) Ingest documents
  * POST {{API_BASE}}/ingest
  * Content-Type: multipart/form-data
  * Body: form field "files" (one or multiple files)
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
    const formData = new FormData();
    files.forEach((file) => {
      formData.append('files', file);
    });

    const response = await axios.post<IngestResponse>(
      `${API_BASE}/ingest`,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        timeout: 30000,
      }
    );

    return response.data;
  } catch (error: any) {
    console.warn('Real API failed for /ingest, checking mock mode fallback...', error);
    // If backend is not running or network failed, fallback gracefully if mock mode or fallback requested
    if (axios.isAxiosError(error) && (!error.response || error.code === 'ERR_NETWORK')) {
      throw new Error(
        `Backend server unreachable at ${API_BASE}. Please start your Python FastAPI server or enable Demo Mock Mode.`
      );
    }
    const msg = error?.response?.data?.detail || error.message || 'Failed to ingest documents';
    throw new Error(msg);
  }
}

/**
  * 2) Send query / task
  * POST {{API_BASE}}/query
  * Content-Type: application/json
  * Body: { query, mode }
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
    const response = await axios.post<QueryResponse>(
      `${API_BASE}/query`,
      { query, mode },
      {
        headers: {
          'Content-Type': 'application/json',
        },
        timeout: 60000,
      }
    );

    return response.data;
  } catch (error: any) {
    console.warn('Real API failed for /query:', error);
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
  * GET {{API_BASE}}/explain/{{request_id}}
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
      answer_summary: `Synthesized answer from 2 retrieved chunks. Verified against on-prem vector store.`,
    };
  }

  try {
    const response = await axios.get<ExplanationResponse>(
      `${API_BASE}/explain/${encodeURIComponent(requestId)}`,
      { timeout: 15000 }
    );
    return response.data;
  } catch (error: any) {
    console.warn('Real API failed for /explain:', error);
    if (MOCK_EXPLANATIONS[requestId]) {
      return MOCK_EXPLANATIONS[requestId];
    }
    const msg = error?.response?.data?.detail || error.message || 'Failed to fetch audit explanation';
    throw new Error(msg);
  }
}

/**
  * 4) Download generated files
  * GET {{API_BASE}}/files/{{filename}}
  * Full download link = `${API_BASE}${file.download_url}` or `${API_BASE}/files/${filename}`
  */
export function getFileUrl(downloadUrlOrName: string): string {
  if (!downloadUrlOrName) return '#';
  if (downloadUrlOrName.startsWith('http://') || downloadUrlOrName.startsWith('https://')) {
    return downloadUrlOrName;
  }
  const cleanPath = downloadUrlOrName.startsWith('/')
    ? downloadUrlOrName
    : `/files/${downloadUrlOrName}`;
  return `${API_BASE}${cleanPath}`;
}
