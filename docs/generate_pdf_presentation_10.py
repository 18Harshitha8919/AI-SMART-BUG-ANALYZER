import sys
import os
from fpdf import FPDF

class BugSensePresentation10(FPDF):
    def __init__(self):
        super().__init__(orientation="landscape", unit="mm", format="A4")
        self.set_margin(15)
        self.set_auto_page_break(False)

    def draw_background(self):
        # Draw premium dark grey background
        self.set_fill_color(18, 18, 18) # #121212
        self.rect(0, 0, 297, 210, "F")
        
        # Draw header thin cyan line
        self.set_fill_color(16, 185, 129) # Emerald #10b981
        self.rect(0, 0, 297, 3, "F")

        # Draw footer grey line
        self.set_fill_color(30, 30, 30)
        self.rect(0, 203, 297, 7, "F")

    def slide_header(self, title):
        self.draw_background()
        
        # Header text
        self.set_xy(15, 12)
        self.set_text_color(255, 255, 255)
        self.set_font("helvetica", "B", 24)
        self.cell(0, 10, title, new_x="LMARGIN", new_y="NEXT")

        # Draw separator line below title
        self.set_draw_color(40, 40, 40)
        self.set_line_width(0.5)
        self.line(15, 25, 282, 25)

    def slide_footer(self, page_num):
        self.set_xy(15, 204)
        self.set_font("helvetica", "I", 8)
        self.set_text_color(120, 120, 120)
        self.cell(100, 5, "BugSense AI - Technical Presentation (10-Slide Edition)")
        
        self.set_xy(260, 204)
        self.cell(20, 5, f"Slide {page_num}", align="R")

    def draw_bullet(self, x, y, text, indent=0):
        self.set_xy(x + indent, y)
        self.set_fill_color(16, 185, 129) # Emerald bullet
        self.ellipse(x + indent + 1.5, y + 2, 2, 2, "F")
        
        self.set_xy(x + indent + 6, y)
        self.set_font("helvetica", "", 13)
        self.set_text_color(200, 200, 200)
        self.multi_cell(250 - indent, 6, text)
        return self.get_y() + 2

    def draw_title_slide(self):
        self.draw_background()
        
        # Large title text
        self.set_xy(15, 50)
        self.set_font("helvetica", "B", 28)
        self.set_text_color(255, 255, 255)
        self.multi_cell(0, 12, "CREATION OF INTELLIGENT BUG DIAGNOSIS PLATFORM\nWITH FIX RECOMMENDATION ASSISTANCE GROUP", align="C")

        # Subtitle
        self.set_xy(15, 82)
        self.set_font("helvetica", "B", 22)
        self.set_text_color(16, 185, 129)
        self.cell(0, 10, "BugSense AI", align="C", new_x="LMARGIN", new_y="NEXT")

        # Draw flowchart boxes
        y_box = 125
        boxes = [
            ("Software Bug", 25),
            ("AI Triage", 90),
            ("Root Cause", 155),
            ("Fix Recommender", 220)
        ]
        
        for text, x in boxes:
            self.set_fill_color(30, 30, 30)
            self.set_draw_color(16, 185, 129)
            self.set_line_width(0.8)
            self.rect(x, y_box, 52, 16, "DF")
            
            # Label
            self.set_xy(x, y_box + 4.5)
            self.set_font("helvetica", "B", 10)
            self.set_text_color(240, 240, 240)
            self.cell(52, 6, text, align="C")

            # Draw arrow
            if x != 220:
                self.set_draw_color(100, 100, 100)
                self.set_line_width(0.6)
                self.line(x + 52, y_box + 8, x + 65, y_box + 8)
                self.line(x + 62, y_box + 6, x + 65, y_box + 8)
                self.line(x + 62, y_box + 10, x + 65, y_box + 8)

        self.slide_footer(1)

def build_pdf_10(filename="presentation_10.pdf"):
    pdf = BugSensePresentation10()
    
    # ----------------------------------------------------
    # SLIDE 1: Title
    # ----------------------------------------------------
    pdf.add_page()
    pdf.draw_background()
    
    # Large title text
    pdf.set_xy(15, 50)
    pdf.set_font("helvetica", "B", 28)
    pdf.set_text_color(255, 255, 255)
    pdf.multi_cell(0, 12, "CREATION OF INTELLIGENT BUG DIAGNOSIS PLATFORM\nWITH FIX RECOMMENDATION ASSISTANCE GROUP", align="C")

    # Subtitle
    pdf.set_xy(15, 82)
    pdf.set_font("helvetica", "B", 22)
    pdf.set_text_color(16, 185, 129)
    pdf.cell(0, 10, "BugSense AI", align="C", new_x="LMARGIN", new_y="NEXT")

    # Core Flow Visual (Bug -> Triage -> Diagnosis -> Fix)
    y_box = 125
    boxes = [
        ("Software Bug", 25),
        ("AI Triage", 90),
        ("Root Cause", 155),
        ("Fix Recommender", 220)
    ]
    for text, x in boxes:
        pdf.set_fill_color(30, 30, 30)
        pdf.set_draw_color(16, 185, 129)
        pdf.set_line_width(0.8)
        pdf.rect(x, y_box, 52, 16, "DF")
        
        pdf.set_xy(x, y_box + 4.5)
        pdf.set_font("helvetica", "B", 10)
        pdf.set_text_color(240, 240, 240)
        pdf.cell(52, 6, text, align="C")

        if x != 220:
            pdf.set_draw_color(100, 100, 100)
            pdf.set_line_width(0.6)
            pdf.line(x + 52, y_box + 8, x + 65, y_box + 8)
            pdf.line(x + 62, y_box + 6, x + 65, y_box + 8)
            pdf.line(x + 62, y_box + 10, x + 65, y_box + 8)
            
    pdf.slide_footer(1)

    # ----------------------------------------------------
    # SLIDE 2: Problem Statement & Objectives
    # ----------------------------------------------------
    pdf.add_page()
    pdf.slide_header("Slide 2: Problem Statement & Objectives")
    
    # Left Box (Challenges)
    pdf.set_fill_color(25, 25, 25)
    pdf.set_draw_color(220, 50, 50)
    pdf.rect(15, 36, 128, 145, "DF")
    pdf.set_xy(20, 42)
    pdf.set_font("helvetica", "B", 14)
    pdf.set_text_color(255, 100, 100)
    pdf.cell(118, 6, "Challenges in Defect Diagnosis", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("helvetica", "", 11)
    pdf.set_text_color(200, 200, 200)
    pdf.set_xy(20, 52)
    pdf.multi_cell(118, 7, "- Manual stack trace parsing is slow and complex.\n- Siloed resolutions lead to fixing the same bug repeatedly.\n- Developers lack immediate, contextual fix recommendations.\n- Verbose log files create severe cognitive overload.")

    # Right Box (Objectives)
    pdf.set_fill_color(25, 25, 25)
    pdf.set_draw_color(16, 185, 129)
    pdf.rect(154, 36, 128, 145, "DF")
    pdf.set_xy(159, 42)
    pdf.set_font("helvetica", "B", 14)
    pdf.set_text_color(16, 185, 129)
    pdf.cell(118, 6, "Core Project Objectives", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("helvetica", "", 11)
    pdf.set_text_color(200, 200, 200)
    pdf.set_xy(159, 52)
    pdf.multi_cell(118, 7, "- Automate triage (severity, priority, component) and log parsing.\n- Implement RAG search to leverage past solved bug patterns.\n- Isolate failing file traces, methods, and stack frame classes.\n- Generate fix recommendations and prevention guidelines.\n- Create a closed-loop self-growing vector database mechanism.")

    pdf.slide_footer(2)

    # ----------------------------------------------------
    # SLIDE 3: Proposed Solution & Workflow
    # ----------------------------------------------------
    pdf.add_page()
    pdf.slide_header("Slide 3: Proposed Solution Workflow")
    
    # Draw linear flowchart sequence
    steps = [
        "1. Ingestion", "2. Semantic Query", "3. Duplicate Scan",
        "4. Triage Node", "5. Log Analyzer", "6. Root Cause",
        "7. Remediation", "8. Verification", "9. KB Growth"
    ]
    y_start = 50
    for idx, step in enumerate(steps):
        row = idx // 3
        col = idx % 3
        x = 25 + (col * 85)
        y = y_start + (row * 42)
        
        pdf.set_fill_color(30, 30, 30)
        pdf.set_draw_color(16, 185, 129)
        pdf.rect(x, y, 70, 18, "DF")
        
        pdf.set_xy(x, y + 5)
        pdf.set_font("helvetica", "B", 11)
        pdf.set_text_color(240, 240, 240)
        pdf.cell(70, 6, step, align="C")

        # Connectors
        pdf.set_draw_color(100, 100, 100)
        pdf.set_line_width(0.6)
        if col < 2:
            pdf.line(x + 70, y + 9, x + 85, y + 9)
            pdf.line(x + 82, y + 7, x + 85, y + 9)
            pdf.line(x + 82, y + 11, x + 85, y + 9)
        elif col == 2 and row < 2:
            pdf.line(x + 35, y + 18, x + 35, y_start + ((row + 1) * 42) - 3)

    # Small footnote summary details at the bottom of Slide 3
    pdf.set_xy(25, 178)
    pdf.set_font("helvetica", "I", 9.5)
    pdf.set_text_color(150, 150, 150)
    pdf.cell(0, 5, "* Log Ingestion: Developer uploads logs. Agent Diagnosis: Pipeline evaluates root causes. Self-Growth: Developer verifies the resolved bug, triggering the knowledge-base update process.")

    pdf.slide_footer(3)

    # ----------------------------------------------------
    # SLIDE 4: System Architecture
    # ----------------------------------------------------
    pdf.add_page()
    pdf.slide_header("Slide 4: System Subsystem Topology")
    
    subsystems = [
        ("FRONTEND VIEW PORTAL", ["React.js client interface", "Vite build configurations", "Tailwind CSS dashboard grids", "Axios proxy connections"], 15),
        ("BACKEND API GATEWAY", ["Node.js + Express.js APIs", "Multer multi-part attachments", "Winston file logging wrapper", "MongoDB / local JSON fallback"], 105),
        ("AI SERVICE CORE", ["FastAPI service wrappers", "LangGraph orchestrator machine", "FAISS similarity check algorithms", "Google Gemini reasoning engine"], 195)
    ]
    for title, desc_list, x in subsystems:
        pdf.set_fill_color(25, 25, 25)
        pdf.set_draw_color(40, 40, 40)
        pdf.rect(x, 40, 85, 140, "DF")
        
        pdf.set_fill_color(35, 35, 35)
        pdf.rect(x, 40, 85, 15, "F")
        pdf.set_xy(x, 44)
        pdf.set_font("helvetica", "B", 11)
        pdf.set_text_color(16, 185, 129)
        pdf.cell(85, 6, title, align="C")
        
        y_bullet = 65
        for desc in desc_list:
            pdf.set_xy(x + 5, y_bullet)
            pdf.set_fill_color(16, 185, 129)
            pdf.ellipse(x + 6.5, y_bullet + 2, 1.5, 1.5, "F")
            
            pdf.set_xy(x + 11, y_bullet)
            pdf.set_font("helvetica", "", 10)
            pdf.set_text_color(200, 200, 200)
            pdf.multi_cell(70, 5, desc)
            y_bullet = pdf.get_y() + 4

    pdf.slide_footer(4)

    # ----------------------------------------------------
    # SLIDE 5: Technology Stack
    # ----------------------------------------------------
    pdf.add_page()
    pdf.slide_header("Slide 5: Technology Stack Matrix")
    
    # Table headers
    pdf.set_xy(15, 36)
    pdf.set_fill_color(30, 30, 30)
    pdf.set_draw_color(50, 50, 50)
    pdf.rect(15, 36, 267, 10, "F")
    
    pdf.set_font("helvetica", "B", 10)
    pdf.set_text_color(16, 185, 129)
    pdf.set_xy(20, 38)
    pdf.cell(45, 6, "Layer")
    pdf.cell(95, 6, "Technology")
    pdf.cell(127, 6, "Key Purpose")

    rows = [
        ("Frontend client", "React, Vite, Tailwind CSS, Axios", "Render diagnostic grids, charts & telemetry UI"),
        ("API gateway", "Node.js, Express.js, Multer, Winston", "REST request proxy, log trace handling & routing"),
        ("Database persistence", "MongoDB (Mongoose), local JSON files", "Saves bugs, verified resolutions & stats fallback"),
        ("AI Microservice", "Python 3.10, FastAPI", "Wraps embeddings, similarity matches & agents"),
        ("Vector database", "FAISS, NumPy vector fallback", "Maintains dense vectors for semantic similarity query"),
        ("Agent runtime", "LangChain, LangGraph StateGraph", "Orchestrates transition state logic between agents"),
        ("LLM Framework", "Google Gemini API", "Core inference engine for logs and recommendations")
    ]
    y = 48
    for layer, tech, purp in rows:
        pdf.set_draw_color(40, 40, 40)
        pdf.line(15, y, 282, y)
        
        pdf.set_xy(20, y + 2.5)
        pdf.set_font("helvetica", "B", 9)
        pdf.set_text_color(240, 240, 240)
        pdf.cell(45, 5, layer)
        
        pdf.set_font("helvetica", "", 9)
        pdf.set_text_color(200, 200, 200)
        pdf.cell(95, 5, tech)
        
        pdf.set_text_color(160, 160, 160)
        pdf.multi_cell(127, 5, purp)
        y = pdf.get_y() + 2.5

    pdf.slide_footer(5)

    # ----------------------------------------------------
    # SLIDE 6: RAG & Semantic Retrieval
    # ----------------------------------------------------
    pdf.add_page()
    pdf.slide_header("Slide 6: RAG & Semantic Retrieval Ingestion")
    y = 38
    y = pdf.draw_bullet(15, y, "Vectorization Model: Computes 384-dimensional dense embeddings using sentence-transformers (all-MiniLM-L6-v2).")
    y = pdf.draw_bullet(15, y, "FAISS Index Query: Scans indexed historical records using cosine similarity metrics to retrieve top 5 matching bug resolutions.")
    y = pdf.draw_bullet(15, y, "RAG Context Appending: Fuses historical diagnostic details and resolutions directly into the LLM inference prompt.")
    y = pdf.draw_bullet(15, y, "Keyword-Independent Match: Matches related defects even when code variables and keywords differ, bridging syntax discrepancies.")
    pdf.slide_footer(6)

    # ----------------------------------------------------
    # SLIDE 7: Multi-Agent Diagnosis
    # ----------------------------------------------------
    pdf.add_page()
    pdf.slide_header("Slide 7: Multi-Agent Node Transition")
    
    # Horizontal flow blocks for agents
    agents = [
        ("Triage Agent", "Component component, severity level, and priority evaluators.", 15),
        ("Log Analysis Agent", "Parses stack traces to identify exceptions, failing classes, and methods.", 68),
        ("Duplicate Agent", "Queries FAISS vector index to locate duplicate matches.", 121),
        ("Root Cause Agent", "Hypothesizes failures from log stack traces and RAG history.", 174),
        ("Remediation Agent", "Generates fix recommendations and prevention guidelines.", 227)
    ]
    
    for name, resp, x in agents:
        pdf.set_fill_color(25, 25, 25)
        pdf.set_draw_color(16, 185, 129)
        pdf.set_line_width(0.7)
        pdf.rect(x, 50, 50, 110, "DF")
        
        # Agent header banner
        pdf.set_fill_color(35, 35, 35)
        pdf.rect(x, 50, 50, 15, "F")
        
        pdf.set_xy(x, 55)
        pdf.set_font("helvetica", "B", 10)
        pdf.set_text_color(255, 255, 255)
        pdf.cell(50, 5, name, align="C", new_x="LMARGIN", new_y="NEXT")
        
        pdf.set_xy(x + 4, 72)
        pdf.set_font("helvetica", "", 9.5)
        pdf.set_text_color(200, 200, 200)
        pdf.multi_cell(42, 6, resp)

        # Connector arrow
        if x != 227:
            pdf.set_draw_color(100, 100, 100)
            pdf.set_line_width(0.5)
            pdf.line(x + 50, 105, x + 53, 105)
            pdf.line(x + 51, 103, x + 53, 105)
            pdf.line(x + 51, 107, x + 53, 105)

    pdf.slide_footer(7)

    # ----------------------------------------------------
    # SLIDE 8: Knowledge Base Growth & Verification
    # ----------------------------------------------------
    pdf.add_page()
    pdf.slide_header("Slide 8: Knowledge Base Growth & Verification")
    y = 38
    y = pdf.draw_bullet(15, y, "Developer-Verified Gate: Resolved defects require confirmation on the dashboard. No logs are indexed immediately.")
    
    # 90% threshold banner block
    pdf.set_fill_color(25, 25, 30)
    pdf.set_draw_color(16, 185, 129)
    pdf.rect(15, 62, 267, 16, "DF")
    pdf.set_xy(20, 67)
    pdf.set_font("helvetica", "B", 12)
    pdf.set_text_color(16, 185, 129)
    pdf.cell(257, 6, "Decision Mechanism: FAISS Similarity Index Threshold (90%)", align="C")

    # Enrichment box
    pdf.set_fill_color(10, 35, 20)
    pdf.set_draw_color(16, 185, 129)
    pdf.rect(15, 95, 125, 75, "DF")
    pdf.set_xy(20, 100)
    pdf.set_font("helvetica", "B", 12)
    pdf.set_text_color(100, 255, 150)
    pdf.cell(115, 6, "Similarity > 90% -> Update Existing", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("helvetica", "", 10)
    pdf.set_text_color(170, 210, 180)
    pdf.set_xy(20, 110)
    pdf.multi_cell(115, 5, "- Matches an existing database pattern.\n- Enriches existing resolved metadata rather than creating redundant entries.\n- Overwrites matching FAISS index labels and updates metadata fields.")

    # Creation box
    pdf.set_fill_color(30, 30, 30)
    pdf.set_draw_color(100, 100, 100)
    pdf.rect(150, 95, 125, 75, "DF")
    pdf.set_xy(155, 100)
    pdf.set_font("helvetica", "B", 12)
    pdf.set_text_color(240, 240, 240)
    pdf.cell(115, 6, "Similarity <= 90% -> Create New", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("helvetica", "", 10)
    pdf.set_text_color(180, 180, 180)
    pdf.set_xy(155, 110)
    pdf.multi_cell(115, 5, "- Represents a new software failure mode.\n- Creates a new unique vector node and inserts the playbook into MongoDB.\n- Rebuilds FAISS index indices to add the new RAG mapping.")

    pdf.slide_footer(8)

    # ----------------------------------------------------
    # SLIDE 9: Testing & Validation Results
    # ----------------------------------------------------
    pdf.add_page()
    pdf.slide_header("Slide 9: Project Validation Results")
    
    # 3 KPI Cards
    kpis = [
        ("ACCURACY", "100.0%", "12/12 Defect Cases Passed", 15),
        ("LATENCY", "22.9 ms", "Avg FAISS Response", 105),
        ("CONFIDENCE", "85.4%", "Avg Agent certainty", 195)
    ]
    for title, score, details, x in kpis:
        pdf.set_fill_color(25, 25, 25)
        pdf.set_draw_color(16, 185, 129)
        pdf.rect(x, 40, 85, 45, "DF")
        
        pdf.set_xy(x, 46)
        pdf.set_font("helvetica", "B", 10)
        pdf.set_text_color(160, 160, 160)
        pdf.cell(85, 5, title, align="C", new_x="LMARGIN", new_y="NEXT")
        
        pdf.set_xy(x, 54)
        pdf.set_font("helvetica", "B", 24)
        pdf.set_text_color(255, 255, 255)
        pdf.cell(85, 10, score, align="C", new_x="LMARGIN", new_y="NEXT")
        
        pdf.set_xy(x, 68)
        pdf.set_font("helvetica", "I", 9)
        pdf.set_text_color(120, 120, 120)
        pdf.cell(85, 5, details, align="C")

    # Table of metrics
    pdf.set_xy(15, 95)
    pdf.set_fill_color(30, 30, 30)
    pdf.rect(15, 95, 267, 10, "F")
    pdf.set_font("helvetica", "B", 10)
    pdf.set_text_color(16, 185, 129)
    pdf.set_xy(20, 97)
    pdf.cell(130, 6, "Metric Tested")
    pdf.cell(137, 6, "Calculated Validation Result")
    
    test_rows = [
        ("Precision", "100.0%"),
        ("Recall", "100.0%"),
        ("F1 Score", "100.0%"),
        ("Knowledge Growth Actions", "12 Created, 0 Updated (Successful growth validation)")
    ]
    y_tbl = 107
    for metric, score in test_rows:
        pdf.set_draw_color(40, 40, 40)
        pdf.line(15, y_tbl, 282, y_tbl)
        
        pdf.set_xy(20, y_tbl + 2.5)
        pdf.set_font("helvetica", "B", 9)
        pdf.set_text_color(240, 240, 240)
        pdf.cell(130, 5, metric)
        
        pdf.set_font("helvetica", "", 9)
        pdf.set_text_color(200, 200, 200)
        pdf.cell(137, 5, score)
        y_tbl = pdf.get_y() + 2.5

    pdf.slide_footer(9)

    # ----------------------------------------------------
    # SLIDE 10: Conclusion & Future Scope
    # ----------------------------------------------------
    pdf.add_page()
    pdf.slide_header("Slide 10: Conclusion & Future Enhancements")
    
    # Left box (Conclusion)
    pdf.set_fill_color(25, 25, 25)
    pdf.set_draw_color(40, 40, 40)
    pdf.rect(15, 36, 128, 145, "DF")
    pdf.set_xy(20, 42)
    pdf.set_font("helvetica", "B", 14)
    pdf.set_text_color(16, 185, 129)
    pdf.cell(118, 6, "Conclusion", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("helvetica", "", 11)
    pdf.set_text_color(200, 200, 200)
    pdf.set_xy(20, 52)
    pdf.multi_cell(118, 6.5, "- Automates defect triage and parsed log analysis.\n- Bridges semantic syntax variations via RAG search query matching.\n- Coordinates state graph parsing via multi-agent pipelines.\n- Self-growing vector storage matches B.Tech thesis guidelines.\n- Reached 100% E2E verification test case coverage successfully.")

    # Right box (Future Scope)
    pdf.rect(154, 36, 128, 145, "DF")
    pdf.set_xy(159, 42)
    pdf.set_font("helvetica", "B", 14)
    pdf.set_text_color(16, 185, 129)
    pdf.cell(118, 6, "Future Enhancements", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("helvetica", "", 11)
    pdf.set_text_color(200, 200, 200)
    pdf.set_xy(159, 52)
    pdf.multi_cell(118, 6.5, "- Native VS Code / PyCharm diagnostic triggers.\n- Stream real-time logs from ELK, Splunk, or Datadog agent collectors.\n- Enforce RBAC user roles during Resolution Verification.\n- Integrate auto-patching and code repair ML algorithms (Automated Code Repair planned as Future Work).")

    pdf.slide_footer(10)

    # ----------------------------------------------------
    # SLIDE 11: Thank You
    # ----------------------------------------------------
    pdf.add_page()
    pdf.draw_background()
    
    pdf.set_xy(15, 75)
    pdf.set_font("helvetica", "B", 36)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(0, 15, "THANK YOU", align="C", new_x="LMARGIN", new_y="NEXT")

    pdf.set_xy(15, 95)
    pdf.set_font("helvetica", "B", 18)
    pdf.set_text_color(16, 185, 129)
    pdf.cell(0, 10, "Questions & Discussions", align="C")
    
    pdf.slide_footer(11)

    # Save output PDF file
    pdf.output(filename)
    print(f"Successfully generated 10-slide PDF presentation at: {filename}")

if __name__ == "__main__":
    out_file = sys.argv[1] if len(sys.argv) > 1 else "presentation_10.pdf"
    build_pdf_10(out_file)
