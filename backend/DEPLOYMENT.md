# Sovereign On-Premise Agentic AI Workbench — Deployment & Operations Guide

**SIH 2026 Problem Statement 26117**  
**Target Organization:** Mangalore Refinery and Petrochemicals Limited (MRPL)  
**System Classification:** Confidential Industrial Work — 100% Air-Gapped Sovereign AI  

---

## 1. Executive Summary & Sovereignty Architecture

The **Sovereign AI Workbench** is an on-premise, air-gapped agentic AI workbench engineered specifically for confidential refinery and petrochemical operations. The platform operates under a strict **Zero-Cloud, Zero-Internet** security architecture:
- **Local Open-Weight LLM:** Qwen3:8B running completely offline via local Ollama.
- **Local Dense Embeddings:** `all-MiniLM-L6-v2` executed via Sentence Transformers with offline environment variables (`TRANSFORMERS_OFFLINE=1`, `HF_HUB_OFFLINE=1`).
- **Local Vector Database:** FAISS running in-process with deterministic top-$k$ Euclidean/inner-product search.
- **Local Relational Storage:** SQLite with `aiosqlite` async pooling for document metadata and audit logs.
- **Tamper-Evident Audit Logging:** Cryptographic HMAC-SHA256 chaining on every agent invocation, tool execution, and document operation.
- **Role-Based Access Control (RBAC):** Native privilege segregation across `OPERATOR`, `ENGINEER`, `AUDITOR`, and `ADMIN` personas.

---

## 2. Hardware & Operating Environment Specifications

| Component | Minimum Specification | Recommended Production Specification |
| :--- | :--- | :--- |
| **Operating System** | Ubuntu 22.04 LTS / RHEL 9 / Windows Server 2022 | Ubuntu 24.04 LTS / RHEL 9.2 (Air-gapped) |
| **CPU** | 8 Cores (x86_64 or ARM64) | 16+ Cores (Intel Xeon / AMD EPYC) |
| **System Memory (RAM)** | 16 GB | 32 GB – 64 GB DDR5 |
| **GPU Acceleration** | Optional (CPU inference supported) | NVIDIA RTX 4090 (24GB) or A5000 / A100 |
| **Storage** | 100 GB NVMe SSD | 500 GB NVMe RAID-1 (Encrypted Volume) |
| **Network Interface** | Isolated Industrial LAN (No WAN / No Internet Gateway) | Dual NIC (Refinery SCADA LAN + DMZ Gateway) |

---

## 3. Air-Gapped Packaging & Pre-Provisioning Procedure

In strict air-gapped refinery facilities, internet access is physically unavailable. Preparation must occur on a connected staging machine prior to transfer to the secured production enclave.

### Step 3.1: Download Python Wheels Offline
On an internet-connected staging machine with matching OS and Python 3.11:
```bash
mkdir -p sovereign-bundle/wheels
pip download -r requirements.txt -d sovereign-bundle/wheels
```

### Step 3.2: Export Pre-Trained Open-Weight Models
1. **Ollama LLM Weights (`qwen3:8b`):**
   ```bash
   ollama pull qwen3:8b
   # Copy Ollama storage manifests and blobs:
   # Linux: /usr/share/ollama/.ollama or ~/.ollama
   # Windows: %USERPROFILE%\.ollama
   tar -czvf sovereign-bundle/ollama-qwen3-8b.tar.gz ~/.ollama
   ```
2. **Hugging Face Sentence Transformers (`all-MiniLM-L6-v2`):**
   ```bash
   python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"
   tar -czvf sovereign-bundle/hf-cache.tar.gz ~/.cache/huggingface
   ```

### Step 3.3: Transfer via Secure Media
Transfer `sovereign-bundle/` to the air-gapped refinery server using verified encrypted storage media in accordance with MRPL cybersecurity standard operating procedures.

---

## 4. Air-Gapped Installation & Deployment

### Option A: Bare-Metal / Native Virtual Environment Installation

1. **Extract Model Caches & Dependencies:**
   ```bash
   tar -xzvf ollama-qwen3-8b.tar.gz -C ~/
   tar -xzvf hf-cache.tar.gz -C ~/
   ```
2. **Create Python 3.11 Virtual Environment:**
   ```bash
   python3.11 -m venv .venv
   source .venv/bin/activate   # On Windows: .venv\Scripts\activate
   ```
3. **Install Wheels in Offline Mode:**
   ```bash
   pip install --no-index --find-links=./wheels -r requirements.txt
   ```
4. **Configure Air-Gapped Environment (`.env`):**
   ```bash
   cp .env.example .env
   ```
   Ensure the following settings are active:
   ```ini
   AIR_GAPPED_MODE=true
   ALLOWED_LOCAL_HOSTS=localhost,127.0.0.1,::1
   LLM_PROVIDER=ollama
   OLLAMA_BASE_URL=http://localhost:11434
   OLLAMA_MODEL=qwen3:8b
   ENABLE_DOCS=false
   ENFORCE_RBAC=true
   TRANSFORMERS_OFFLINE=1
   HF_HUB_OFFLINE=1
   ```
5. **Start Local Ollama Service:**
   ```bash
   ollama serve
   ```
6. **Launch Sovereign AI Backend:**
   ```bash
   uvicorn app.main:app --host 127.0.0.1 --port 8000 --workers 4
   ```

---

### Option B: Docker Compose Air-Gapped Deployment

1. **Load Container Images Offline:**
   ```bash
   docker load -i sovereign-backend.tar
   docker load -i ollama.tar
   ```
2. **Start Services:**
   ```bash
   docker compose up -d
   ```
3. **Verify Service Health:**
   ```bash
   docker compose ps
   curl -s http://127.0.0.1:8000/api/v1/health | jq .
   ```

---

## 5. Security Architecture & Boundary Verification

### 5.1 Outbound Network Enforcement (Sovereign Validator)
The workbench actively prevents data exfiltration. Any attempt to reach external IP addresses, cloud endpoints (e.g., `api.openai.com`, `google.com`), or unapproved ports triggers an immediate `AirGappedSecurityViolation` (HTTP 403) and generates an audit alarm.

### 5.2 Document Vault & Path Traversal Protection
All document uploads and downloads are subject to:
- Filename sanitization (`\x00` stripped, directory traversal sequences removed, illegal characters sanitized).
- Strict containment verification against `settings.data_dir / "vault"`.
- Upload size limits (`MAX_DOCUMENT_SIZE_BYTES`, default 50 MB).

### 5.3 Prompt Injection Isolation
Retrieved document content is treated as untrusted external evidence. Evidence chunks are bound inside explicit containment barriers:
```
--- BEGIN UNTRUSTED RETRIEVED DOCUMENT EVIDENCE ---
Source File: distillation_column_sop.pdf
Content: ...
--- END UNTRUSTED RETRIEVED DOCUMENT EVIDENCE ---
```
Prompt directives explicitly command the local LLM to ignore any instructions, system prompt overrides, or tool invocation triggers embedded in document texts.

---

## 6. Role-Based Access Control (RBAC) Specification

Authentication is enforced via enterprise gateway headers (`X-User-Role` and `X-User-ID`).

| Role | Permitted Capabilities | Prohibited Capabilities |
| :--- | :--- | :--- |
| **OPERATOR** | Document search, process analysis, safety analysis, procedure lookup, general Q&A. | Document upload/delete, industrial calculations, report generation, audit log inspection. |
| **ENGINEER** | All Operator capabilities + Industrial calculator, equipment analysis, report generation, image analysis. | Document ingestion, document deletion, audit log inspection. |
| **AUDITOR** | Read-only audit log inspection (`GET /api/v1/audit/{request_id}`), cryptographic chain verification (`GET /api/v1/audit/verify/chain`). | Chat execution, document upload, document deletion, tool execution. |
| **ADMIN** | Full system capabilities: document ingestion, document deletion, health inspection, chain verification. | None. |

---

## 7. Cryptographic Audit Trail Verification

Every operation produces an immutable audit record linked via linear HMAC-SHA256 chaining:

$$\text{record\_hash}_i = \text{HMAC}_{\text{secret}}(\text{record\_hash}_{i-1} \parallel \text{request\_id}_i \parallel \text{action}_i \parallel \text{status}_i \parallel \text{details}_i \parallel \text{created\_at}_i)$$

### Verifying Chain Authenticity:
```bash
curl -H "X-User-Role: AUDITOR" http://127.0.0.1:8000/api/v1/audit/verify/chain
```
**Expected Response:**
```json
{
  "valid": true,
  "total_records": 42,
  "verified_records": 42,
  "tampered_ids": [],
  "status": "verified_authentic"
}
```
If any database record is tampered with, deleted, or inserted out of order, the endpoint flags the exact record ID and returns `"valid": false`.

---

## 8. Sovereign Health & Readiness Verification

Run the safe health probe:
```bash
curl http://127.0.0.1:8000/api/v1/health
```
**Sample Output:**
```json
{
  "status": "ok",
  "service": "Sovereign AI Workbench",
  "version": "1.0.0",
  "air_gapped_mode": true,
  "sovereignty_posture": "enforced_air_gapped",
  "llm_provider": "ollama",
  "llm_model": "qwen3:8b",
  "embedding_provider": "local_sentence_transformers (all-MiniLM-L6-v2)",
  "multimodal_provider": "ollama",
  "database_status": "connected",
  "vector_store_status": "ready",
  "indexed_chunks": 6,
  "audit_chain_status": "verified_authentic"
}
```

---

## 9. Backup & Disaster Recovery

The complete state of the workbench resides in the `data/` directory:
- `data/db/workbench.db` (SQLite relational store + audit logs)
- `data/vault/` (Raw encrypted uploaded documents)
- `data/faiss_index/` (FAISS index + chunk metadata)
- `data/extracted/` (Sanitized text extracts)
- `data/visuals/` (Extracted visual artifacts)

**Automated Cold Backup:**
```bash
sqlite3 data/db/workbench.db ".backup 'backup/workbench_$(date +%Y%m%d).db'"
tar -czvf "backup/workbench_data_$(date +%Y%m%d).tar.gz" data/
```

