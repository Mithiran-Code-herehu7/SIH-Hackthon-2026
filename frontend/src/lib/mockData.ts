import { ChatMessageItem, DemoScenario, ExplanationResponse, QueryResponse } from './types';

export const INITIAL_CHAT_MESSAGES: ChatMessageItem[] = [
  {
    id: 'msg-welcome',
    role: 'assistant',
    content: `### Welcome to the On-Premise Agentic AI Workbench 🛡️

I am your private enterprise AI assistant, optimized for refineries, PSUs, and defense installations. All data processing occurs locally within your isolated network environment.

#### Quick Start Guide:
1. **Ingest Confidential Documents**: Upload PDFs, DOCX, XLSX, or TXT files using the document dropzone on the right.
2. **Select Task Mode**: Choose between standard Chat, PPT Presentation, Excel Spreadsheet, or formal Safety Report generation.
3. **Execute AI Workflows**: Try one of the pre-configured demo scenarios below or ask custom domain queries.

*Audit trails and source references are automatically appended to every AI output for full regulatory compliance.*`,
    timestamp: '09:00 AM',
  },
  {
    id: 'msg-sample-user',
    role: 'user',
    content: 'Summarize recent safety incidents from the HSE 2025 report and generate an executive PowerPoint presentation deck.',
    timestamp: '09:02 AM',
    mode: 'generate_ppt',
  },
  {
    id: 'msg-sample-assistant',
    role: 'assistant',
    content: `### Safety Incidents & Hazard Analysis Summary (HSE 2025)

Based on the ingested **HSE_Report_2025.pdf** and **SOP_Operations.docx**, here is the synthesized executive summary:

#### Key Findings:
- **Pressure Release Valve Malfunction (Unit 4B)**: Occurred on March 14, 2025. Zero casualties reported due to secondary containment triggering within 12 seconds.
- **Flange Gasket Leakage (Cracker Block)**: Detected during routine thermographic inspection. Immediate isolation performed as per SOP Section 4.2.
- **Safety Compliance Metric**: 98.4% adherence to mandatory PPE protocols across all operational shifts.

#### Recommendations:
1. Schedule mandatory quarter-end calibration for relief valves in High-Pressure Hydrocracker units.
2. Upgrade seal inspection frequency to bi-weekly for sulfur recovery loops.

I have generated an executive slide presentation summarizing these findings with high-visibility charts and compliance matrices.`,
    timestamp: '09:03 AM',
    mode: 'generate_ppt',
    sources: [
      { file: 'HSE_Report_2025.pdf', page: 3 },
      { file: 'HSE_Report_2025.pdf', page: 12 },
      { file: 'SOP_Operations.docx', section: '4.2' },
    ],
    files: [
      {
        type: 'ppt',
        name: 'safety_summary_q1_2025.pptx',
        download_url: '/files/safety_summary_q1_2025.pptx',
      },
      {
        type: 'report',
        name: 'HSE_Incident_Audit_Report.docx',
        download_url: '/files/HSE_Incident_Audit_Report.docx',
      },
    ],
    request_id: 'req_demo_safety_ppt',
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

  let answer = '';
  let sources = [
    { file: 'HSE_Report_2025.pdf', page: 3 },
    { file: 'SOP_Operations.docx', section: '4.2' },
  ];
  let files: { type: string; name: string; download_url: string }[] = [];

  if (mode === 'generate_ppt') {
    answer = `### 📊 Executive Presentation Generated

I have analyzed your query: **"${query}"** and constructed a structured PowerPoint deck aligned with PSU/Refinery reporting standards.

#### Key Highlights Included in Deck:
- **Slide 1**: Executive Overview & Scope
- **Slide 2**: Quantitative Incident Breakdown & Risk Matrix
- **Slide 3**: Root Cause Analysis & Containment Response
- **Slide 4**: Operational SOP Compliance Rates
- **Slide 5**: Corrective Action Plan & Timeline

You can download the generated presentation file directly below.`;
    files.push({
      type: 'ppt',
      name: `AI_Generated_Deck_${Date.now().toString().slice(-4)}.pptx`,
      download_url: `/files/AI_Generated_Deck_${Date.now().toString().slice(-4)}.pptx`,
    });
  } else if (mode === 'generate_excel') {
    answer = `### 📈 Audit Spreadsheet & Telemetry Workbook Generated

Processed data chunks and structured telemetry observations for query: **"${query}"**.

#### Dataset Summary:
- **Total Rows Computed**: 428 records
- **Calculated KPIs**: Mean Time Between Failures (MTBF), Peak Temp Variances, Inspection Frequencies
- **Formulas applied**: \`SUMIF\`, \`VLOOKUP\`, and conditional anomaly highlighting.

Click below to download the compiled Excel workbook.`;
    files.push({
      type: 'excel',
      name: `Telemetry_Audit_${Date.now().toString().slice(-4)}.xlsx`,
      download_url: `/files/Telemetry_Audit_${Date.now().toString().slice(-4)}.xlsx`,
    });
  } else if (mode === 'generate_report') {
    answer = `### 📜 Compliance & Audit Document Compiled

Formulated formal technical report for: **"${query}"**.

#### Document Structure:
1. **Executive Summary & Operational Context**
2. **Detailed Analytical Findings & References**
3. **Regulatory Adherence Matrix (IS 18001 / ISO 45001)**
4. **Sign-off Checklist for Shift Engineers**

The formal document file is ready for download below.`;
    files.push({
      type: 'report',
      name: `Audit_Report_${Date.now().toString().slice(-4)}.docx`,
      download_url: `/files/Audit_Report_${Date.now().toString().slice(-4)}.docx`,
    });
  } else {
    answer = `### 🤖 Analysis & Response

Based on the verified on-premise document index, here is the factual synthesis for your request:

> **Query**: *"${query}"*

#### Key Information:
- **Primary Source**: \`HSE_Report_2025.pdf\` (Page 3 & Section 4.2)
- **Status**: Verified by vector similarity score (0.94 cosine metric).
- **Compliance Status**: All extracted operating limits fall within nominal PSU safety tolerances.

Feel free to ask follow-up questions or request a PPT/Excel export.`;
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
    sources,
    files,
    request_id: reqId,
  };
}
