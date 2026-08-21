import os
import re
from typing import Optional
from dotenv import load_dotenv
from schemas.agent_schemas import TriageResponse

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '../../.env'))

class TriageAgent:
    def __init__(self):
        # Precise components updated to match Milestone 3 requested list
        self.components = {
            "Authentication": ["auth", "oauth", "jwt", "token", "login", "credentials", "session", "cookie"],
            "User Management": ["user", "profile", "account", "register", "signup", "role", "permission"],
            "Payment": ["payment", "checkout", "stripe", "paypal", "charge", "card", "transaction", "billing", "invoice"],
            "Dashboard": ["dashboard", "home", "widget", "metrics", "chart", "graph", "telemetry", "summary"],
            "Inventory": ["inventory", "stock", "product", "item", "warehouse", "catalog", "quantity"],
            "Reports": ["report", "analytics", "csv export", "pdf export", "download report", "statistics"],
            "Database": ["database", "sql", "query", "mongoose", "mongodb", "connection pool", "postgres", "db", "deadlock"],
            "API": ["api", "endpoint", "route", "controller", "payload", "post", "get", "request", "response"],
            "Security": ["security", "csrf", "unauthorized", "permission denied", "exploit", "bypass", "vulnerability", "encryption", "decrypt"],
            "Notifications": ["notification", "email", "sms", "alert", "push", "message broker", "smtp"],
            "Search": ["search", "query resolver", "filter", "elastic", "find", "search index", "faiss"]
        }

    def _local_triage(self, title: str, description: str, environment: str = "Production") -> TriageResponse:
        combined_text = f"{title} {description}".lower()
        
        # 1. Classify Severity
        severity = "Medium"
        confidence = 75
        severity_reason = "No high-severity crash signatures found; defaulted to Medium severity."
        
        if any(kw in combined_text for kw in ["nullpointer", "nullreference", "null pointer", "outofmemory", "oom", "crash", "fatal", "bypass", "vulnerability", "exploit"]):
            severity = "Critical"
            confidence = 95
            severity_reason = f"Application crashes or security vulnerability detected. Keywords match critical signature."
        elif any(kw in combined_text for kw in ["security", "unauthorized", "sql", "timeout", "deadlock", "refused", "connection pool", "502", "bad gateway", "gateway", "503", "unavailable"]):
            severity = "High"
            confidence = 85
            severity_reason = f"System operations blocked or restricted due to exceptions matching high severity rules."
        elif any(kw in combined_text for kw in ["filenotfound", "ioerror", "warning", "deprecated", "typo", "spelling", "validation", "form fields", "schema validator"]):
            severity = "Low"
            confidence = 80
            severity_reason = f"Minor file warning or deprecation check. Non-blocking error logs."
        else:
            severity = "Medium"
            confidence = 70
            severity_reason = f"Default triage classification applied for general unhandled system warnings."
            
        # 2. Classify Component
        matched_component = "API"  # Default fallback if no matches
        max_score = -1
        
        for comp, keywords in self.components.items():
            score = 0
            if comp.lower() in combined_text:
                score += 15
            for kw in keywords:
                if kw in combined_text:
                    score += 5
            if score > max_score and score > 0:
                max_score = score
                matched_component = comp

        # 3. Determine Priority (P1, P2, P3, P4)
        priority = "P3"
        priority_reason = "Priority aligned to P3 for general Medium severity bugs."
        
        if severity == "Critical":
            priority = "P1"
            priority_reason = "Critical severity exception escalated priority to P1."
        elif severity == "High":
            if environment.lower() == "production":
                priority = "P1"
                priority_reason = "High severity bug in Production environment escalated priority to P1."
            else:
                priority = "P2"
                priority_reason = "High severity bug in non-production environment mapped priority to P2."
        elif severity == "Medium":
            priority = "P3"
            priority_reason = "Medium severity bug mapped priority to P3."
        elif severity == "Low":
            priority = "P4"
            priority_reason = "Low severity bug mapped priority to P4."
            
        # 4. Generate Reasoning
        reasons = [
            f"AI triaged defect category to '{matched_component}' (score: {max_score if max_score > 0 else 0}).",
            severity_reason,
            priority_reason
        ]
        reasoning = " ".join(reasons)
        
        return TriageResponse(
            triage_component=matched_component,
            severity=severity,
            priority=priority,
            confidence=confidence,
            reasoning=reasoning,
            severity_reason=severity_reason,
            priority_reason=priority_reason
        )

    def triage(self, title: str, description: str, environment: str = "Production") -> TriageResponse:
        api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
        if not api_key:
            return self._local_triage(title, description, environment)

        try:
            from langchain_google_genai import ChatGoogleGenerativeAI
            from langchain_core.prompts import ChatPromptTemplate
            
            llm = ChatGoogleGenerativeAI(
                model="gemini-1.5-flash",
                google_api_key=api_key,
                temperature=0.0
            )
            
            prompt = ChatPromptTemplate.from_messages([
                ("system", "You are an expert software QA engineer. Analyze the bug details and classify: "
                           "triage_component (Authentication, User Management, Payment, Dashboard, Inventory, Reports, Database, API, Security, Notifications, or Search), "
                           "severity (Critical, High, Medium, Low), "
                           "priority (P1, P2, P3, P4), "
                           "confidence score (0-100), reasoning, severity_reason, and priority_reason."),
                ("human", "Bug Title: {title}\nDescription: {description}\nEnvironment: {environment}")
            ])
            
            structured_llm = llm.with_structured_output(TriageResponse)
            chain = prompt | structured_llm
            res = chain.invoke({"title": title, "description": description, "environment": environment})
            return res
            
        except Exception as e:
            print(f"Gemini API Triage Agent error: {e}. Falling back to local analyzer.")
            return self._local_triage(title, description, environment)

triage_agent = TriageAgent()
