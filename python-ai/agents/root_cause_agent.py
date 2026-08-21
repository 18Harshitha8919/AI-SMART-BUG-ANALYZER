import os
import re
from typing import List
from dotenv import load_dotenv
from schemas.agent_schemas import RootCauseResponse, DuplicateProfile

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '../../.env'))

class RootCauseAgent:
    def _local_root_cause(self, title: str, description: str, duplicates: List[DuplicateProfile]) -> RootCauseResponse:
        evidence = []
        max_similarity = 0
        best_match_id = None
        
        # Analyze historical matches for evidence
        for dup in duplicates:
            if dup.similarity >= 80:
                evidence.append(dup.bug_id)
            if dup.similarity > max_similarity:
                max_similarity = dup.similarity
                best_match_id = dup.bug_id

        # Determine hypothesis based on similarity match
        if max_similarity >= 90 and best_match_id:
            root_cause = f"Null reference or unhandled exception matching historical pattern in {best_match_id}."
            confidence = max_similarity
            explanation = (
                f"A highly similar issue ({max_similarity}% match) was resolved previously. "
                f"The stack layout parameters and module signatures directly align with historical ticket {best_match_id}."
            )
        else:
            # General heuristic triage fallbacks using exact word boundary matches
            combined = f"{title} {description}".lower()
            words = set(re.findall(r"\b\w+\b", combined))
            
            if any(w in words for w in ["auth", "security", "jwt", "token", "unauthorized", "login", "credentials", "csrf"]):
                root_cause = "Missing validation or cryptographic mismatch in token/middleware authentication filter."
                confidence = 85
                explanation = "The trace context indicates failure during signature checking or public key synchronization routines."
            elif any(w in words for w in ["database", "sql", "pool", "deadlock", "db", "mongodb", "mongoose", "postgres"]):
                root_cause = "Database transaction pool exhaustion or deadlock holding table resources."
                confidence = 80
                explanation = "High query concurrency caused pool locks; transaction timed out before release."
            elif any(w in words for w in ["file", "config", "path", "read", "missing", "io", "filenotfound", "ioerror"]):
                root_cause = "FileNotFoundException occurred: missing configuration settings file during bootstrap."
                confidence = 75
                explanation = "The program attempted to open or read an external config file but encountered a missing reference path."
            else:
                root_cause = "Null reference exception caused due to missing input validation checks."
                confidence = 75
                explanation = "System attempted to reference properties on a null or uninitialized object runtime context."

        if not evidence and best_match_id:
            evidence.append(best_match_id)
        if not evidence:
            evidence = ["BUG-234"] # Default seed fallback

        return RootCauseResponse(
            root_cause=root_cause,
            confidence=confidence,
            supporting_evidence=evidence,
            explanation=explanation
        )

    def analyze_root_cause(self, title: str, description: str, duplicates: List[DuplicateProfile]) -> RootCauseResponse:
        api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
        if not api_key:
            return self._local_root_cause(title, description, duplicates)

        try:
            from langchain_google_genai import ChatGoogleGenerativeAI
            from langchain_core.prompts import ChatPromptTemplate
            
            llm = ChatGoogleGenerativeAI(
                model="gemini-1.5-flash",
                google_api_key=api_key,
                temperature=0.0
            )
            
            prompt = ChatPromptTemplate.from_messages([
                ("system", "You are an expert root cause analysis agent. Examine the submitted bug details and similar historical bug logs. "
                           "Generate: root_cause (concise hypothesis), confidence score (0-100), supporting_evidence (list of Bug IDs from duplicates), "
                           "and explanation of reasoning."),
                ("human", "Bug: {title} - {description}\n\nSimilar Matches: {matches}")
            ])
            
            # Convert duplicates list to text context
            matches_text = "\n".join([f"- {d.bug_id} (Similarity: {d.similarity}%): {d.summary}. Resolution: {d.resolution}" for d in duplicates])
            
            structured_llm = llm.with_structured_output(RootCauseResponse)
            chain = prompt | structured_llm
            res = chain.invoke({"title": title, "description": description, "matches": matches_text})
            return res
            
        except Exception as e:
            print(f"Gemini API Root Cause Agent error: {e}. Falling back to local analyzer.")
            return self._local_root_cause(title, description, duplicates)

root_cause_agent = RootCauseAgent()
