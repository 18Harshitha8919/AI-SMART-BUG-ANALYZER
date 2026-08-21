import os
from typing import List
from dotenv import load_dotenv
from schemas.agent_schemas import RemediationResponse, RootCauseResponse, DuplicateProfile

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '../../.env'))

class RemediationAgent:
    def _local_remediation(self, title: str, description: str, rc: RootCauseResponse) -> RemediationResponse:
        combined = f"{title} {description}".lower()
        
        # Heuristics based on issue type
        if "auth" in combined or "security" in combined or "jwt" in combined:
            immediate_fix = "Validate token header signatures and check public keystore sync states before JWT validation."
            long_term = "Implement centralized authentication validation middleware and automate keystore updates."
            best_practices = [
                "Always use exception handling around cryptography.",
                "Incorporate centralized token validation check blocks.",
                "Establish strict integration tests for authentication bypass vectors.",
                "Implement secure metadata token logging."
            ]
        elif "database" in combined or "sql" in combined or "connection" in combined:
            immediate_fix = "Optimize locked transaction statement execution plans and configure deadlock retries."
            long_term = "Centralize connection pool parameters and expand maximum pool sizes to match concurrency requirements."
            best_practices = [
                "Ensure pool locks are released inside try-finally blocks.",
                "Monitor query latency metrics dynamically.",
                "Establish transaction boundary unit tests.",
                "Prevent select-for-update statement leaks."
            ]
        elif "frontend" in combined or "canvas" in combined or "ui" in combined:
            immediate_fix = "Validate drawing boundary values and verify layout parameters are initialized before surface redrawing."
            long_term = "Establish standardized canvas viewport checking routines and coordinate page boundary updates."
            best_practices = [
                "Implement fallback rendering buffers.",
                "Establish GUI regression tests.",
                "Track viewport scale metrics.",
                "Log canvas boundary exception trace dumps."
            ]
        else:
            immediate_fix = "Validate null inputs and object states before dereferencing variables in active methods."
            long_term = "Adopt robust static analysis check utilities and establish structural defensive programming standards."
            best_practices = [
                "Adopt strict null checking assertions.",
                "Incorporate verbose log traces.",
                "Expand code coverage with unit testing tools.",
                "Perform standard regression checking."
            ]

        return RemediationResponse(
            immediate_fix=immediate_fix,
            long_term=long_term,
            best_practices=best_practices
        )

    def generate_remediation(self, title: str, description: str, rc: RootCauseResponse, duplicates: List[DuplicateProfile]) -> RemediationResponse:
        api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
        if not api_key:
            return self._local_remediation(title, description, rc)

        try:
            from langchain_google_genai import ChatGoogleGenerativeAI
            from langchain_core.prompts import ChatPromptTemplate
            
            llm = ChatGoogleGenerativeAI(
                model="gemini-1.5-flash",
                google_api_key=api_key,
                temperature=0.0
            )
            
            prompt = ChatPromptTemplate.from_messages([
                ("system", "You are an expert remediation recommender. Given the bug, logs, root cause, and similar matches, "
                           "generate a response containing: immediate_fix (actionable sentence), long_term (architectural recommendations), "
                           "and best_practices (list of engineering rules)."),
                ("human", "Bug: {title}\nRoot Cause: {root_cause}\nMatches: {matches}")
            ])
            
            matches_text = "\n".join([f"- {d.bug_id}: {d.resolution}" for d in duplicates])
            
            structured_llm = llm.with_structured_output(RemediationResponse)
            chain = prompt | structured_llm
            res = chain.invoke({"title": title, "root_cause": rc.root_cause, "matches": matches_text})
            return res
            
        except Exception as e:
            print(f"Gemini API Remediation Agent error: {e}. Falling back to local recommender.")
            return self._local_remediation(title, description, rc)

remediation_agent = RemediationAgent()
