export type TaskMode = 'chat' | 'generate_ppt' | 'generate_excel' | 'generate_report';

export interface SourceItem {
  file: string;
  page?: number;
  section?: string;
}

export interface GeneratedFile {
  type: 'ppt' | 'excel' | 'word' | 'report' | string;
  name: string;
  download_url: string;
}

export interface IngestResponse {
  status: string;
  files_ingested: number;
  chunks_created: number;
}

export interface QueryRequest {
  query: string;
  mode: TaskMode;
}

export interface QueryResponse {
  answer: string;
  sources: SourceItem[];
  files: GeneratedFile[];
  request_id: string;
}

export interface ToolCalled {
  name: string;
  args: Record<string, any>;
}

export interface ExplanationResponse {
  request_id: string;
  query: string;
  retrieved_docs: SourceItem[];
  tools_called: ToolCalled[];
  answer_summary: string;
}

export interface ChatMessageItem {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
  mode?: TaskMode;
  sources?: SourceItem[];
  files?: GeneratedFile[];
  request_id?: string;
  isLoading?: boolean;
  error?: string;
}

export interface ToastMessage {
  id: string;
  type: 'success' | 'error' | 'info' | 'warning';
  title: string;
  message: string;
}

export interface DemoScenario {
  id: string;
  title: string;
  description: string;
  query: string;
  mode: TaskMode;
  badge: string;
}
