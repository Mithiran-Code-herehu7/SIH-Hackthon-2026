import json
import re
from app.llm.base import LLMProvider


class MockLLMProvider(LLMProvider):

    def generate(
        self,
        prompt: str,
    ) -> str:
        prompt_lower = prompt.lower()

        # 1. If this is an intent classification prompt, return structured JSON
        if "choose exactly one allowed intent" in prompt_lower or "allowed intent/tool pairs" in prompt_lower:
            # Extract user request from prompt
            req_match = re.search(r"User request:\s*(.*)", prompt, flags=re.DOTALL | re.IGNORECASE)
            user_req = req_match.group(1).strip() if req_match else ""
            u_lower = user_req.lower()

            if any(w in u_lower for w in ("excel", ".xlsx", "spreadsheet", "incident register", "create an excel", "generate excel")):
                return json.dumps({"intent": "generate_excel", "tool": "generate_excel", "reason": "Excel generation request identified.", "arguments": {}})
            if any(w in u_lower for w in ("report", "generate report", "create report")):
                return json.dumps({"intent": "report_generation", "tool": "report_generation", "reason": "Report request identified.", "arguments": {}})
            if any(w in u_lower for w in ("percent", "%", "divided by", "ratio", "efficiency", "convert")):
                from app.agent.orchestrator import _calculator_arguments
                calc_args = _calculator_arguments(user_req)
                if calc_args:
                    return json.dumps({"intent": "calculation", "tool": "industrial_calculator", "reason": "Calculation request.", "arguments": calc_args})
                return json.dumps({"intent": "general_question", "tool": None, "reason": "Calculation request.", "arguments": {}})
            if any(w in u_lower for w in ("safety", "hazard", "ppe", "alarm")):
                return json.dumps({"intent": "safety_analysis", "tool": "safety_analysis", "reason": "Safety request.", "arguments": {}})
            if any(w in u_lower for w in ("procedure", "sop", "shutdown", "emergency")):
                return json.dumps({"intent": "procedure_lookup", "tool": "procedure_lookup", "reason": "Procedure request.", "arguments": {}})
            if any(w in u_lower for w in ("document", "find", "search", "read", "file")):
                return json.dumps({"intent": "document_question", "tool": "document_search", "reason": "Document search.", "arguments": {}})

            return json.dumps({"intent": "general_question", "tool": None, "reason": "General query.", "arguments": {}})

        # 2. Extract user question from generation prompt
        q_match = re.search(r"User question:\s*(.*?)(?=\n\n|\n[A-Z]|\Z)", prompt, flags=re.DOTALL | re.IGNORECASE)
        question = q_match.group(1).strip() if q_match else prompt.strip()

        # 3. Check for document evidence in RAG prompt
        context_blocks = re.findall(
            r"--- BEGIN UNTRUSTED RETRIEVED DOCUMENT EVIDENCE ---\s*Source File:\s*(.*?)\nContent:\s*(.*?)\s*--- END UNTRUSTED RETRIEVED DOCUMENT EVIDENCE ---",
            prompt,
            flags=re.DOTALL
        )

        if context_blocks:
            evidence_summary = []
            for filename, text in context_blocks:
                clean_text = " ".join(text.strip().split())
                evidence_summary.append(f"- **Source (`{filename}`)**: \"{clean_text[:300]}...\"")
            
            summary_str = "\n".join(evidence_summary)
            return (
                f"### Analysis from Ingested Documents\n\n"
                f"Based on the retrieved document evidence for your question **\"{question}\"**:\n\n"
                f"{summary_str}\n\n"
                f"**Synthesized Finding**: Documented procedures and operational evidence have been synthesized directly from your uploaded workspace files."
            )

        # 4. Handle simple math/percentage queries
        pct_match = re.search(r"(\d+(?:\.\d+)?)\s*%\s+of\s+(\d+(?:\.\d+)?)", question, flags=re.IGNORECASE)
        if pct_match:
            pct, val = float(pct_match.group(1)), float(pct_match.group(2))
            res = (pct / 100.0) * val
            return f"**Calculation**: {pct}% of {val} = **{res:g}**."

        # 5. General intelligent conversational response
        return (
            f"Based on the processed document context, here is the synthesis for **\"{question}\"**:\n\n"
            f"All findings have been cross-referenced with your uploaded operational SOPs and safety documents."
        )