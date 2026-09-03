# Agentic AI Workbench — Human-Crafted Editorial Frontend
> **SIH 2026 Problem Statement**: SIH26117 — Secure On-Premise AI Workbench for Refineries, PSUs & Defense Organizations.

This is a premium, editorial-styled Next.js (App Router) + TypeScript + Tailwind CSS web application for interacting with an on-premise Agentic AI backend service.

---

## 🎨 Design System & Aesthetic Decisions

The user interface takes strong aesthetic inspiration from editorial & curated product platforms (e.g. *Aardvark Book Club*), moving away from generic AI dark-theme templates toward a warm, trustworthy, and human-crafted presentation suitable for high-stakes enterprise & government defense operations.

### 1. Typography & Hierarchy
* **Headings**: Editorial serif typography using **Playfair Display** (`font-serif-display`) with tight line-heights and high contrast.
  * `H1`: 44–48px editorial headline.
  * `H2`: 28–32px section title.
  * `H3`: 20–22px component header.
* **Body & UI**: Clean, highly readable **Plus Jakarta Sans** (`font-sans-body`) at 16px with comfortable line height (`leading-relaxed`).
* **Code & Metrics**: **JetBrains Mono** (`font-mono-code`) for technical audit IDs, vector chunk counts, and code snippets.

### 2. Palette & Mood
* **Background**: Warm parchment off-white (`#F7F5F2`) giving an organic, confident, non-clinical feel.
* **Text**: Deep near-black (`#111318`) for crisp contrast and warm dark slate (`#525663`) for secondary body prose.
* **Accent**: Deep Indigo (`#312E81` / `#1E1B4B`) for primary action buttons, focused task pills, and user query blocks.
* **Cards**: Crisp white (`#FFFFFF`) cards with soft, subtle multi-layer shadows (`shadow-editorial`) and 16px (`1rem`) rounded corners.

### 3. Customizing Colors & Fonts
All design tokens are defined in [`src/app/globals.css`](file:///c:/Users/balun/OneDrive/Documents/SIH%202026/frontend/src/app/globals.css):
```css
:root {
  --background: #F7F5F2;       /* Warm parchment background */
  --foreground: #111318;       /* Primary text */
  --card-bg: #FFFFFF;          /* Card container background */
  --muted-text: #525663;       /* Secondary body text */
  --accent-indigo: #312E81;    /* Primary indigo accent */
}
```

---

## 🚀 Quick Start

### 1. Prerequisite
- **Node.js**: v18.0.0 or higher
- **npm** or **yarn** or **pnpm**

### 2. Installation
Navigate into the `frontend` directory:

```bash
cd frontend
npm install
```

### 3. Running the App locally
Start the Next.js development server:

```bash
npm run dev
```

Access the app at:
👉 **[http://localhost:3000](http://localhost:3000)** (or `http://localhost:3001` if port 3000 is occupied).

---

## ⚙️ Environment Configuration

Set the backend API address in `.env.local`:

```env
# .env.local
NEXT_PUBLIC_API_BASE=http://localhost:8000
```

> **Note**: Click the **Backend Status** toggle button in the top bar to activate **Demo Mock Mode** if testing offline without a running FastAPI backend.

---

## 📡 API Contract Reference

| Endpoint | Method | Request Body / Parameters | Description |
| :--- | :--- | :--- | :--- |
| `/ingest` | `POST` | `multipart/form-data` with field `files` | Indexes PDF, DOCX, XLSX, TXT files into vector store |
| `/query` | `POST` | `application/json` `{ query, mode }` | Sends task query (`chat`, `generate_ppt`, `generate_excel`, `generate_report`) |
| `/explain/{request_id}` | `GET` | Path variable `request_id` | Returns audit trace (retrieved docs, tools called, story narrative) |
| `/files/{filename}` | `GET` | Relative download path | Downloads generated PPT, Word, or Excel file bytes |
