import re

class TriageAgent:
    def __init__(self):
        # Define component match keywords
        self.components = {
            "Database": ["sql", "query", "mongoose", "mongodb", "connection pool", "timeout", "locked", "postgres", "select", "db"],
            "Frontend": ["css", "html", "canvas", "rendering", "display", "mobile", "react", "ui", "align", "view", "layout", "pixel"],
            "Auth": ["jwt", "oauth", "token", "unauthorized", "login", "session", "cookie", "security", "credentials", "auth"],
            "Worker": ["celery", "worker", "background", "job", "queue", "amqp", "redis", "task", "process"],
            "Backend": []  # Default fallback
        }

        # Severity indicators
        self.severity_rules = [
            (r"(out of memory|oom|heap|segfault|segmentation fault|panic|core dumped|crash|fatal|vulnerability|exploit|security bypass)", "Critical", 0.95),
            (r"(timeout|deadlock|locked|unauthorized|permission denied|exception|refused|connection failed|failed to connect)", "High", 0.85),
            (r"(invalid|incorrect|alignment|ui|scaling|rendering|warning|css|broken style|misaligned)", "Medium", 0.75),
            (r"(deprecate|minor|typo|spelling|unused|deprecation warning|info)", "Low", 0.70)
        ]

    def triage(self, title: str, description: str, environment: str = "Production") -> dict:
        combined_text = f"{title} {description}".lower()
        
        # 1. Determine Severity
        severity = "Medium"  # Default
        base_conf = 0.75
        matched_trigger = None
        
        for pattern, sev_level, conf in self.severity_rules:
            match = re.search(pattern, combined_text)
            if match:
                severity = sev_level
                base_conf = conf
                matched_trigger = match.group(0)
                break
                
        # 2. Determine Component (highest match frequency)
        matched_component = "Backend"
        max_hits = 0
        comp_scores = {}
        
        for comp, keywords in self.components.items():
            if comp == "Backend":
                continue
            hits = sum(1 for kw in keywords if kw in combined_text)
            comp_scores[comp] = hits
            if hits > max_hits:
                max_hits = hits
                matched_component = comp
                
        # 3. Determine Priority (Aligns with severity, upgraded if environment is Production)
        priority = severity
        if environment.lower() == "production" and severity in ["Critical", "High"]:
            priority = "Critical"
            
        # 4. Generate Reasoning & Adjust Confidence
        reasons = []
        if matched_trigger:
            reasons.append(f"Detected exception signature '{matched_trigger}' which correlates to a '{severity}' severity classification.")
        else:
            reasons.append(f"No high-severity crash signatures found; defaulted to '{severity}' severity.")
            
        if matched_component != "Backend":
            reasons.append(f"Mapped to component '{matched_component}' due to occurrence of module keywords like: "
                           f"'{', '.join([k for k in self.components[matched_component] if k in combined_text][:3])}'.")
        else:
            reasons.append("No specialized database, frontend, auth, or worker triggers detected; defaulted component classification to 'Backend Core API'.")
            
        if environment.lower() == "production" and priority == "Critical":
            reasons.append("Upgraded priority to Critical/Immediate because the defect was reported in the active Production environment tier.")
            base_conf = min(1.0, base_conf + 0.05)
            
        reasoning = " ".join(reasons)
        
        return {
            "severity": severity,
            "priority": priority,
            "component": matched_component,
            "confidence_score": round(base_conf, 2),
            "reasoning": reasoning
        }

triage_agent = TriageAgent()
