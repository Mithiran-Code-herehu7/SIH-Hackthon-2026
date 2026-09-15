import { ChatMessageItem, DemoScenario, ExplanationResponse, QueryResponse } from './types';

export const INITIAL_CHAT_MESSAGES: ChatMessageItem[] = [
  {
    id: 'msg-welcome',
    role: 'assistant',
    content: `### Welcome to the On-Premise Agentic AI Workbench 🛡️

I am your private enterprise AI assistant, optimized for refineries, PSUs, and defense installations. All data processing occurs locally within your isolated network environment.

#### Quick Start Guide:
1. **Ingest Confidential Documents**: Upload PDFs, DOCX, XLSX, or TXT files using the document dropzone above.
2. **Select Task Mode**: Choose between standard Chat, PPT Presentation, Excel Spreadsheet, or formal Safety Report generation.
3. **Execute AI Workflows**: Try one of the pre-configured scenarios below or ask custom domain queries.

*Audit trails and source references are automatically appended to every AI output for full regulatory compliance.*`,
    timestamp: '09:00 AM',
  },
];

export const DEMO_SCENARIOS: DemoScenario[] = [
  {
    id: 'scenario-1',
    title: 'Summarize safety incidents → PPT',
    description: 'Extract HSE incidents, hazard containment stats & generate executive slide deck',
    query: 'Summarize safety incidents from the uploaded docs and create a PPT presentation deck with key metrics.',
    mode: 'generate_ppt',
    badge: 'Executive Briefing',
  },
  {
    id: 'scenario-2',
    title: 'Analyze machine logs → Excel + report',
    description: 'Process sensor anomaly records & create audit spreadsheet with anomaly breakdown',
    query: 'Analyze machine telemetry logs for vibration anomalies and output an Excel spreadsheet with detailed incident timestamps.',
    mode: 'generate_excel',
    badge: 'Data Analysis',
  },
  {
    id: 'scenario-3',
    title: 'Answer from SOPs only',
    description: 'Strict RAG lookup against standard operating procedures without external assumptions',
    query: 'What is the mandatory emergency shutdown protocol (ESD Step 3) for the crude distillation column in case of cooling water loss?',
    mode: 'chat',
    badge: 'SOP Compliance',
  },
  {
    id: 'scenario-4',
    title: 'Generate Comprehensive Safety Audit Report',
    description: 'Formulate a structured PDF/Word report for PSU regulatory submission',
    query: 'Generate a comprehensive quarterly HSE audit compliance report highlighting risk mitigations and team action items.',
    mode: 'generate_report',
    badge: 'Gov/PSU Audit',
  },
];

export const MOCK_EXPLANATIONS: Record<string, ExplanationResponse> = {
  req_demo_safety_ppt: {
    request_id: 'req_demo_safety_ppt',
    query: 'Summarize safety incidents from the uploaded docs and create a PPT presentation deck with key metrics.',
    retrieved_docs: [
      { file: 'HSE_Report_2025.pdf', page: 3 },
      { file: 'HSE_Report_2025.pdf', page: 12 },
      { file: 'SOP_Operations.docx', section: '4.2' },
    ],
    tools_called: [
      {
        name: 'query_docs',
        args: {
          query: 'safety incidents hazard containment PPE adherence',
          top_k: 5,
        },
      },
      {
        name: 'generate_ppt',
        args: {
          title: 'HSE Safety Incident Executive Summary 2025',
          num_slides: 6,
          theme: 'Enterprise Dark Navy',
        },
      },
    ],
    answer_summary: 'Retrieved 3 high-confidence text chunks from HSE_Report_2025.pdf (Pages 3, 12) and SOP_Operations.docx (Section 4.2). Extracted incident metrics, verified ESD compliance, and invoked the Python slide generation agent to assemble safety_summary_q1_2025.pptx.',
  },
};

export function getMockQueryResponse(query: string, mode: string): QueryResponse {
  const reqId = `req_${Math.random().toString(36).substring(2, 9)}`;
  const qLower = (query || '').toLowerCase();

  let title = 'Document Corpus Intelligence Overview';
  let answer = '';
  let uncertainties: string[] = [];
  let sources = [
    { file: 'HSE_Report_2025.pdf', page: 3 },
    { file: 'SOP_Operations.docx', section: '4.2' },
  ];
  let files: { type: string; name: string; download_url: string }[] = [];

  if (qLower.includes('monetary')) {
    title = 'Information Not Available in Corpus';
    answer = 'The uploaded document does not provide a monetary-loss figure for Pump P-204B.';
    uncertainties = ['The uploaded document does not provide a monetary-loss figure for Pump P-204B.'];
  } else if (qLower.includes('recordable incidents')) {
    title = 'Incident Analysis';
    answer = 'Based on the uploaded documents, there were **3 recordable incidents**.';
  } else if (qLower.includes('corrective action') || qLower.includes('cap-')) {
    title = 'Open Corrective Action Items';
    answer = `The open corrective action items identified in the document are:

- **CAP-01**: High-pressure hydrocracker relief valve calibration.
- **CAP-02**: Thermographic flange gasket seal replacement in Cracker Block.
- **CAP-03**: Bi-weekly inspection frequency upgrade for sulfur recovery loop seals.
- **CAP-04**: Emergency ESD Step 3 cooling water loss drill for Crude Distillation Unit.
- **CAP-05**: Pressure gauge re-certification for Unit 4B containment.
- **CAP-07**: Update PPE compliance tracking across night shifts.
- **CAP-08**: Calibration of relief valves in sulfur recovery unit.`;
  } else if (mode === 'generate_ppt' || qLower.includes('powerpoint') || qLower.includes('ppt') || qLower.includes('slide')) {
    const titleMatch = query.match(/titled\s+["']?(.*?)["']?(?:\.|\s+|$)/i);
    const pptTitle = titleMatch ? titleMatch[1].trim() : 'July–August 2026 Operations Safety Review';
    const fileName = `${pptTitle.replace(/\s+/g, '_').replace(/–/g, '-')}.pptx`;

    title = 'Executive Presentation Deck Synthesized';
    answer = `An executive PowerPoint presentation deck titled **${pptTitle}** has been created.

**Presentation Structure:**
- **Slide 1**: Executive Summary & Operations Overview
- **Slide 2**: Key Operational & Safety Adherence Metrics
- **Slide 3**: Incident Breakdown & Hazard Containment
- **Slide 4**: Open Corrective Action Items & Timelines
- **Slide 5**: Compliance Scorecard & Recommendations`;

    files.push({
      type: 'ppt',
      name: fileName,
      download_url: `/files/${fileName}`,
    });
  } else if (mode === 'generate_excel' || qLower.includes('excel') || qLower.includes('.xlsx') || qLower.includes('incident register')) {
    title = 'Incident register workbook created';
    answer = 'I created an Excel workbook containing the complete incident register and a summary sheet.';
    sources = [
      { file: 'MRPL_Operations_Safety_Demo_Pack.md', section: '3.1 Incident and near-miss register' },
      { file: 'MRPL_Operations_Safety_Demo_Pack.md', section: '3.2 Event summary by category' },
    ];
    files.push({
      type: 'excel',
      name: 'MRPL_Operations_Safety_Demo_Pack_Incident_Register.xlsx',
      download_url: '/files/MRPL_Operations_Safety_Demo_Pack_Incident_Register.xlsx',
    });
  } else if (mode === 'generate_report') {
    title = 'Structured Technical Compliance Report';
    answer = `A formal technical compliance report has been compiled and saved to your workspace.

**Executive Summary:**
The report synthesizes operational incident logs, equipment condition assessments, and safety compliance metrics. All findings have been verified against local site operating procedures.`;

    files.push({
      type: 'report',
      name: `Technical_Compliance_Audit_Report_${Date.now().toString().slice(-4)}.docx`,
      download_url: `/files/Technical_Compliance_Audit_Report_${Date.now().toString().slice(-4)}.docx`,
    });
  } else {
    title = 'Document Analysis Synthesis';
    answer = `Based on the verified on-premise document index, the requested operating limits and procedure compliance metrics fall within nominal safety tolerances. All findings have been cross-referenced with your uploaded SOP documents.`;
  }

  // Save mock explanation for audit trace UI
  MOCK_EXPLANATIONS[reqId] = {
    request_id: reqId,
    query,
    retrieved_docs: sources,
    tools_called: [
      { name: 'query_docs', args: { query, top_k: 4 } },
      ...(mode !== 'chat' ? [{ name: mode, args: { format: mode.replace('generate_', '') } }] : []),
    ],
    answer_summary: `Synthesized answer from 2 indexed documents. Successfully executed RAG workflow and ${mode} tool pipeline.`,
  };

  return {
    answer,
    title,
    sources,
    uncertainties,
    files,
    request_id: reqId,
  };
}
