import os
import re
from datetime import datetime
from typing import List
from dotenv import load_dotenv
from schemas.agent_schemas import LogAnalysisResponse

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '../../.env'))

class LogAnalysisAgent:
    def __init__(self):
        # Exception indicators
        self.exception_patterns = [
            (r"([a-zA-Z0-9\._]*NullPointerException|NullReferenceException)", "NullReferenceException"),
            (r"([a-zA-Z0-9\._]*SecurityException|UnauthorizedAccessException|AccessDeniedException)", "SecurityException"),
            (r"([a-zA-Z0-9\._]*SQLException|QueryException|ConnectionRefusedError)", "SQLException"),
            (r"([a-zA-Z0-9\._]*IndexOutOfBoundsException|IndexError)", "IndexOutOfBoundsException"),
            (r"([a-zA-Z0-9\._]*TimeoutError|TimeoutException|sqlalchemy\.exc\.TimeoutError)", "TimeoutException"),
            (r"([a-zA-Z0-9\._]*FileNotFoundException|IOError|OSError)", "FileNotFoundException"),
            (r"([a-zA-Z0-9\._]*KeyError)", "KeyError"),
            (r"([a-zA-Z0-9\._]*AttributeError)", "AttributeError"),
            (r"([a-zA-Z0-9\._]*TypeError)", "TypeError"),
            (r"([a-zA-Z0-9\._]*SyntaxError)", "SyntaxError")
        ]

        # Stack trace line matchers
        self.java_trace_re = re.compile(r"at\s+([a-zA-Z0-9_\.\<\>\$]+)\.([a-zA-Z0-9_\<\>\$]+)\s*\(([a-zA-Z0-9_\.]+):(\d+)\)")
        self.python_trace_re = re.compile(r"File\s+\"([^\"]+)\",\s+line\s+(\d+),\s+in\s+([a-zA-Z0-9_]+)")
        self.js_trace_re = re.compile(r"at\s+([a-zA-Z0-9_\.\<\>\$ \[\@\]]+)\s*\(([^\:]+):(\d+):(\d+)\)")

    def _local_analyze(self, stack_trace: str, error_log: str = "") -> LogAnalysisResponse:
        combined = f"{stack_trace}\n{error_log}"
        
        # 1. Identify Exception Type
        exception_type = "UnknownException"
        for pattern, exc_name in self.exception_patterns:
            if re.search(pattern, combined, re.IGNORECASE):
                exception_type = exc_name
                break
        if exception_type == "UnknownException":
            exc_match = re.search(r"([a-zA-Z0-9_]+Exception|[a-zA-Z0-9_]+Error)", combined)
            if exc_match:
                exception_type = exc_match.group(1)

        # 2. Extract Error Message
        error_message = "An unhandled runtime exception occurred during service execution."
        # Look for ExceptionType: message format
        msg_match = re.search(fr"{exception_type}\s*:\s*([^\n\r]+)", combined, re.IGNORECASE)
        if msg_match:
            error_message = msg_match.group(1).strip()
        else:
            # Fallback scan for fatal error lines
            fatal_match = re.search(r"(fatal|error|exception)\s*[:\-]\s*([^\n\r]+)", combined, re.IGNORECASE)
            if fatal_match:
                error_message = fatal_match.group(2).strip()

        # 3. Parse Code Paths & Failure details
        affected_path = []
        failure_point = "Unknown"
        filename = "Unknown"
        line = 0
        function = "Unknown"
        failed_class = "Unknown"
        failed_method = "Unknown"
        
        # Try Python
        py_matches = self.python_trace_re.findall(combined)
        if py_matches:
            for file, line_num, func in py_matches:
                base_file = os.path.basename(file)
                affected_path.append(base_file)
            if py_matches:
                last_file, last_line, last_func = py_matches[-1]
                filename = os.path.basename(last_file)
                line = int(last_line)
                function = last_func
                failed_method = last_func
                # Capitalize base file name to represent Class in Python context
                failed_class = "".join([part.capitalize() for part in os.path.splitext(filename)[0].split("_")])
                failure_point = f"{filename}:{line}"
                
        # Try Java
        java_matches = self.java_trace_re.findall(combined)
        if not py_matches and java_matches:
            for cls, func, file, line_num in java_matches:
                affected_path.append(file)
            if java_matches:
                cls, func, file, line_num = java_matches[0]
                filename = file
                line = int(line_num)
                function = func
                failed_method = func
                failed_class = cls.split(".")[-1]
                failure_point = f"{filename}:{line}"

        # Try JS
        js_matches = self.js_trace_re.findall(combined)
        if not py_matches and not java_matches and js_matches:
            for func, file, line_num, col in js_matches:
                affected_path.append(os.path.basename(file))
            if js_matches:
                func, file, line_num, col = js_matches[0]
                filename = os.path.basename(file)
                line = int(line_num)
                function = func
                failed_method = func
                failed_class = "JavaScriptModule"
                failure_point = f"{filename}:{line}"

        # Fallback: check if there's any file:line references in raw text
        if failure_point == "Unknown":
            file_line_match = re.search(r"([a-zA-Z0-9_\.-]+\.[a-zA-Z0-9]{1,4}):(\d+)", combined)
            if file_line_match:
                filename = file_line_match.group(1)
                line = int(file_line_match.group(2))
                failure_point = f"{filename}:{line}"
                failed_class = os.path.splitext(filename)[0].capitalize()

        # 4. Formulate Failure Reason and Root Cause
        failure_reason = f"Crashed during invocation of method {failed_method}() in class {failed_class}."
        root_cause = f"Decoded exception {exception_type} inside thread context. The stack failed at line {line} within file {filename} executing function {function}()."
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        return LogAnalysisResponse(
            exception_type=exception_type,
            error_message=error_message,
            failed_class=failed_class,
            failed_method=failed_method,
            timestamp=timestamp,
            failure_reason=failure_reason,
            file=filename,
            line=line,
            function=function,
            root_cause=root_cause,
            affected_code_path=affected_path
        )

    def analyze(self, stack_trace: str, error_log: str = "") -> LogAnalysisResponse:
        api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
        if not api_key:
            return self._local_analyze(stack_trace, error_log)

        try:
            from langchain_google_genai import ChatGoogleGenerativeAI
            from langchain_core.prompts import ChatPromptTemplate
            
            llm = ChatGoogleGenerativeAI(
                model="gemini-1.5-flash",
                google_api_key=api_key,
                temperature=0.0
            )
            
            prompt = ChatPromptTemplate.from_messages([
                ("system", "You are an expert debugging assistant. Analyze the stack trace and error logs to extract: "
                           "exception_type, error_message, failed_class, failed_method, timestamp, failure_reason, "
                           "file, line (as integer), function name, root_cause details, and affected_code_path (list of files in call stack in execution order)."),
                ("human", "Stack Trace: {stack_trace}\nError Log: {error_log}")
            ])
            
            structured_llm = llm.with_structured_output(LogAnalysisResponse)
            chain = prompt | structured_llm
            res = chain.invoke({"stack_trace": stack_trace, "error_log": error_log})
            return res
            
        except Exception as e:
            print(f"Gemini API Log Analysis Agent error: {e}. Falling back to local parser.")
            return self._local_analyze(stack_trace, error_log)

log_analysis_agent = LogAnalysisAgent()
