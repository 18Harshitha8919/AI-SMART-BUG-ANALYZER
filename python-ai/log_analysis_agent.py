import re

class LogAnalysisAgent:
    def __init__(self):
        # Common exception type regex patterns
        self.exception_patterns = [
            (r"([a-zA-Z0-9\._]*NullPointerException)", "NullPointerException"),
            (r"([a-zA-Z0-9\._]*KeyError)", "KeyError"),
            (r"([a-zA-Z0-9\._]*TimeoutError|sqlalchemy\.exc\.TimeoutError|TimeoutException)", "TimeoutError"),
            (r"([a-zA-Z0-9\._]*MemoryError|OutOfMemoryError)", "MemoryError"),
            (r"([a-zA-Z0-9\._]*DatabaseError|SQLException|QueryException|ConnectionRefusedError)", "DatabaseError"),
            (r"([a-zA-Z0-9\._]*IndexOutOfBoundsException|IndexError)", "IndexOutOfBoundsException"),
            (r"([a-zA-Z0-9\._]*AttributeError)", "AttributeError"),
            (r"([a-zA-Z0-9\._]*TypeError)", "TypeError"),
            (r"([a-zA-Z0-9\._]*AssertionError)", "AssertionError"),
            (r"([a-zA-Z0-9\._]*SyntaxError)", "SyntaxError")
        ]

        # Stack trace line matchers
        # 1. Java: at org.example.Class.method(File.java:123)
        self.java_trace_re = re.compile(r"at\s+([a-zA-Z0-9_\.\<\>\$]+)\.([a-zA-Z0-9_\<\>\$]+)\s*\(([a-zA-Z0-9_\.]+):(\d+)\)")
        
        # 2. Python: File "app.py", line 12, in index
        self.python_trace_re = re.compile(r"File\s+\"([^\"]+)\",\s+line\s+(\d+),\s+in\s+([a-zA-Z0-9_]+)")
        
        # 3. Node/JS: at method (c:\app\index.js:12:4)
        self.js_trace_re = re.compile(r"at\s+([a-zA-Z0-9_\.\<\>\$ \[\@\]]+)\s*\(([^\:]+):(\d+):(\d+)\)")

    def analyze(self, trace_text: str, log_text: str = "") -> dict:
        combined = f"{trace_text}\n{log_text}"
        
        # 1. Identify Exception Type
        exception_type = "UnknownException"
        for pattern, exc_name in self.exception_patterns:
            if re.search(pattern, combined):
                exception_type = exc_name
                break
                
        # If no strict match, check if there is general "Error: " or "Exception: "
        if exception_type == "UnknownException":
            exc_match = re.search(r"([a-zA-Z0-9_]+Exception|[a-zA-Z0-9_]+Error)", combined)
            if exc_match:
                exception_type = exc_match.group(1)

        # 2. Parse Call Stack Path
        affected_path = []
        failure_point = "Unknown Failure Point"
        confidence = 0.50
        
        # Try Python traces (usually has multiple lines, last line in Traceback is the leaf frame)
        py_matches = self.python_trace_re.findall(combined)
        if py_matches:
            confidence = 0.95
            for file, line, method in py_matches:
                affected_path.append(f"File '{os.path.basename(file)}', line {line} in {method}()")
            # In Python, the last frame in traceback is the failing line
            if py_matches:
                last_file, last_line, last_method = py_matches[-1]
                failure_point = f"{os.path.basename(last_file)}:{last_line} ({last_method})"
                
        # Try Java traces
        java_matches = self.java_trace_re.findall(combined)
        if not py_matches and java_matches:
            confidence = 0.95
            for cls, method, file, line in java_matches:
                affected_path.append(f"at {cls}.{method}({file}:{line})")
            # In Java, the first match (top of trace) is the failing line
            if java_matches:
                cls, method, file, line = java_matches[0]
                failure_point = f"{file}:{line} ({cls}.{method})"
                
        # Try JS traces
        js_matches = self.js_trace_re.findall(combined)
        if not py_matches and not java_matches and js_matches:
            confidence = 0.90
            for method, file, line, col in js_matches:
                affected_path.append(f"at {method} ({os.path.basename(file)}:{line}:{col})")
            if js_matches:
                method, file, line, col = js_matches[0]
                failure_point = f"{os.path.basename(file)}:{line} ({method})"

        # Fallback: check if there's any file:line references
        if failure_point == "Unknown Failure Point":
            file_line_match = re.search(r"([a-zA-Z0-9_\.-]+\.[a-zA-Z0-9]{1,4}):(\d+)", combined)
            if file_line_match:
                failure_point = f"{file_line_match.group(1)}:line {file_line_match.group(2)}"
                confidence = 0.70

        # Build Explanation
        explanation = ""
        if exception_type != "UnknownException":
            explanation = f"Detected runtime occurrence of '{exception_type}'."
        else:
            explanation = "An unclassified runtime exception occurred in the call stack."
            
        if failure_point != "Unknown Failure Point":
            explanation += f" The exception crashed execution inside thread context at failing instruction: '{failure_point}'."
            
        if affected_path:
            explanation += f" Reconstructed sequence of {len(affected_path)} call frame nodes in trace stack."
        else:
            explanation += " No standard traceback call frames could be extracted from input lines."
            
        return {
            "exception_type": exception_type,
            "failure_point": failure_point,
            "affected_code_path": affected_path,
            "confidence_score": confidence,
            "explanation": explanation
        }

log_analysis_agent = LogAnalysisAgent()
import os
