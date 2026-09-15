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
  slide_count?: number;
  sheets?: string[];
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

export interface ComparisonItem {
  area: string;
  issues: string[];
  evidence_ids?: string[];
  risk_level: 'High' | 'Medium' | 'Low' | string;
  priority_reason: string;
}

export interface QueryResponse {
  answer: string;
  title?: string;
  comparison?: ComparisonItem[];
  sources: SourceItem[];
  uncertainties?: string[];
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
  title?: string;
  timestamp: string;
  mode?: TaskMode;
  comparison?: ComparisonItem[];
  sources?: SourceItem[];
  uncertainties?: string[];
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
