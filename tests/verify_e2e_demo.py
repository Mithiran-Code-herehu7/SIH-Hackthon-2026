import asyncio
import json
from httpx import ASGITransport, AsyncClient

from app.main import app


async def main():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        print("\n--- 1. SOVEREIGN HEALTH PROBE ---")
        health = await client.get("/api/v1/health")
        print(f"Status: {health.status_code}")
        print(json.dumps(health.json(), indent=2))

        print("\n--- 2. OPERATOR PROCESS QUERY (GROUNDED RAG) ---")
        chat_op = await client.post(
            "/api/v1/chat",
            headers={"X-User-Role": "OPERATOR", "X-User-ID": "mrpl_operator_01"},
            json={
                "message": "What are the main stages and fractions of the CDU?",
                "file_id": "7e1d2a76-6829-4629-a375-079f2e20e4d0",
            },
        )
        print(f"Status: {chat_op.status_code}")
        op_res = chat_op.json()
        print(f"Tool Executed: {op_res.get('tool')}")
        print(f"Response: {op_res.get('response')[:250]}...")
        op_request_id = op_res.get("request_id")

        print("\n--- 3. ENGINEER INDUSTRIAL CALCULATION ---")
        chat_eng = await client.post(
            "/api/v1/chat",
            headers={"X-User-Role": "ENGINEER", "X-User-ID": "mrpl_engineer_07"},
            json={"message": "calculate efficiency of 850 output and 1000 input"},
        )
        print(f"Status: {chat_eng.status_code}")
        eng_res = chat_eng.json()
        print(f"Tool Executed: {eng_res.get('tool')}")
        print(f"Calculation Result: {eng_res.get('tool_result')}")
        print(f"Response: {eng_res.get('response')}")

        print("\n--- 4. RBAC VIOLATION DEFENSE (OPERATOR ATTEMPTS CALCULATION) ---")
        chat_blocked = await client.post(
            "/api/v1/chat",
            headers={"X-User-Role": "OPERATOR", "X-User-ID": "mrpl_operator_01"},
            json={"message": "calculate efficiency of 850 output and 1000 input"},
        )
        print(f"Status: {chat_blocked.status_code} (Expected 403)")
        print(f"Error Message: {chat_blocked.json()}")

        print("\n--- 5. AUDITOR CRYPTOGRAPHIC CHAIN VERIFICATION ---")
        verify_res = await client.get(
            "/api/v1/audit/verify/chain",
            headers={"X-User-Role": "AUDITOR", "X-User-ID": "mrpl_auditor_compliance"},
        )
        print(f"Status: {verify_res.status_code}")
        print(json.dumps(verify_res.json(), indent=2))

        print("\n--- 6. AUDITOR LOG INSPECTION & TAMPER-EVIDENT HASH VERIFICATION ---")
        audit_records = await client.get(
            f"/api/v1/audit/{op_request_id}",
            headers={"X-User-Role": "AUDITOR"},
        )
        print(f"Status: {audit_records.status_code}")
        print(json.dumps(audit_records.json(), indent=2))


if __name__ == "__main__":
    asyncio.run(main())

