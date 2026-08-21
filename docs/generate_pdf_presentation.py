import sys
import os
from fpdf import FPDF

class BugSensePresentation(FPDF):
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
        self.cell(100, 5, "BugSense AI - Technical Presentation")
        
        self.set_xy(260, 204)
        self.cell(20, 5, f"Slide {page_num}", align="R")

    def draw_bullet(self, x, y, text, indent=0):
        # Draw a custom bullet list item
        self.set_xy(x + indent, y)
        self.set_fill_color(16, 185, 129) # Emerald bullet
        self.ellipse(x + indent + 1.5, y + 2, 2, 2, "F")
        
        self.set_xy(x + indent + 6, y)
        self.set_font("helvetica", "", 13)
        self.set_text_color(200, 200, 200)
        # Use MultiCell to wrap long bullets
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
            # Draw box background
            self.set_fill_color(30, 30, 30)
            self.set_draw_color(16, 185, 129)
            self.set_line_width(0.8)
            self.rect(x, y_box, 52, 16, "DF")
            
            # Label
            self.set_xy(x, y_box + 4.5)
            self.set_font("helvetica", "B", 10)
            self.set_text_color(240, 240, 240)
            self.cell(52, 6, text, align="C")

            # Draw arrow if not the last box
            if x != 220:
                self.set_draw_color(100, 100, 100)
                self.set_line_width(0.6)
                self.line(x + 52, y_box + 8, x + 65, y_box + 8)
                # Arrow head
                self.line(x + 62, y_box + 6, x + 65, y_box + 8)
                self.line(x + 62, y_box + 10, x + 65, y_box + 8)

        self.slide_footer(1)

def build_pdf(filename="presentation.pdf"):
    pdf = BugSensePresentation()
    
    # ----------------------------------------------------
    # SLIDE 1: Title
    # ----------------------------------------------------
    pdf.add_page()
    pdf.draw_title_slide()

    # ----------------------------------------------------
    # SLIDE 2: Introduction
    # ----------------------------------------------------
    pdf.add_page()
    pdf.slide_header("Slide 2: Introduction")
    y = 38
    y = pdf.draw_bullet(15, y, "Defect resolution represents a critical bottleneck in the software lifecycle, historically requiring intensive manual code tracing.")
    y = pdf.draw_bullet(15, y, "Developers traditionally search historical reports, code databases, and reference manuals to isolate root cause anomalies.")
    y = pdf.draw_bullet(15, y, "Runtime traces contain verbose logs where identifying the critical failure methods and calling chains is complex.")
    y = pdf.draw_bullet(15, y, "BugSense AI automates diagnostic parsing and serves immediate fix recommendations by linking logs directly with RAG vector store playbooks.")
    pdf.slide_footer(2)

    # ----------------------------------------------------
    # SLIDE 3: Problem Statement
    # ----------------------------------------------------
    pdf.add_page()
    pdf.slide_header("Slide 3: Problem Statement")
    
    # Text bullets on the left
    y = 38
    pdf.draw_bullet(15, y, "Traditional debugging demands manual stack line inspections.", indent=0)
    pdf.draw_bullet(15, y + 12, "Lack of knowledge reuse leads to fixing similar defects repeatedly.", indent=0)
    pdf.draw_bullet(15, y + 24, "Sifting through massive log files creates cognitive overload.", indent=0)
    pdf.draw_bullet(15, y + 36, "Diagnostic details remain siloed in developer communications.", indent=0)

    # Draw visual workflow boxes on the right
    # Traditional
    pdf.set_fill_color(30, 10, 10)
    pdf.set_draw_color(220, 50, 50)
    pdf.rect(170, 38, 110, 60, "DF")
    pdf.set_xy(175, 42)
    pdf.set_font("helvetica", "B", 12)
    pdf.set_text_color(255, 100, 100)
    pdf.cell(100, 6, "TRADITIONAL DEBBUGGING", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("helvetica", "", 10)
    pdf.set_text_color(200, 150, 150)
    pdf.set_xy(175, 52)
    pdf.multi_cell(100, 5, "- Inspect raw logs manually row-by-row\n- Manual web searches & API searches\n- Guess root causes by code trials\n- Fixes are undocumented & repeated later")

    # AI Assisted
    pdf.set_fill_color(10, 30, 20)
    pdf.set_draw_color(16, 185, 129)
    pdf.rect(170, 115, 110, 60, "DF")
    pdf.set_xy(175, 119)
    pdf.set_font("helvetica", "B", 12)
    pdf.set_text_color(100, 255, 150)
    pdf.cell(100, 6, "AI-ASSISTED DEBUGGING", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("helvetica", "", 10)
    pdf.set_text_color(150, 200, 170)
    pdf.set_xy(175, 129)
    pdf.multi_cell(100, 5, "- Automated agent parser extracts traces\n- Vector similarity queries historical fixes\n- Gemini LLM isolates probable root causes\n- Closed-loop verify indexing database saves playbooks")

    pdf.slide_footer(3)

    # ----------------------------------------------------
    # SLIDE 4: Objectives
    # ----------------------------------------------------
    pdf.add_page()
    pdf.slide_header("Slide 4: Project Objectives")
    y = 38
    y = pdf.draw_bullet(15, y, "Automate Defect Diagnostics: Analyze submitted bug tickets and runtime traces to classify categories and severity levels.")
    y = pdf.draw_bullet(15, y, "Semantic Defect Retrieval: Query the FAISS vector database to retrieve historical bug reports using cosine similarity.")
    y = pdf.draw_bullet(15, y, "Log Information Extraction: Parse stack traces to isolate exception classes, error logs, and timestamps.")
    y = pdf.draw_bullet(15, y, "Contextual Remediation: Generate immediately actionable code recommendations and engineering checklists.")
    y = pdf.draw_bullet(15, y, "Self-Growing Knowledge Base: Support resolution confirmation loops to continuously update vector database playbooks.")
    pdf.slide_footer(4)

    # ----------------------------------------------------
    # SLIDE 5: Proposed Solution
    # ----------------------------------------------------
    pdf.add_page()
    pdf.slide_header("Slide 5: Proposed Solution Workflow")
    
    # Custom flow diagram
    steps = [
        "1. Submission", "2. Vector Query", "3. Duplicate Check", 
        "4. Triage Node", "5. Log Analyzer", "6. Root Cause", 
        "7. Remediation", "8. Verification", "9. KB Growth"
    ]
    
    y_start = 50
    for idx, step in enumerate(steps):
        row = idx // 3
        col = idx % 3
        x = 25 + (col * 85)
        y = y_start + (row * 42)
        
        # Draw box
        pdf.set_fill_color(30, 30, 30)
        pdf.set_draw_color(16, 185, 129)
        pdf.set_line_width(0.7)
        pdf.rect(x, y, 70, 18, "DF")
        
        # Label
        pdf.set_xy(x, y + 5)
        pdf.set_font("helvetica", "B", 11)
        pdf.set_text_color(240, 240, 240)
        pdf.cell(70, 6, step, align="C")

        # Arrows
        pdf.set_draw_color(100, 100, 100)
        pdf.set_line_width(0.6)
        if col < 2 and idx < len(steps) - 1: # Horizontal arrow
            pdf.line(x + 70, y + 9, x + 85, y + 9)
            pdf.line(x + 82, y + 7, x + 85, y + 9)
            pdf.line(x + 82, y + 11, x + 85, y + 9)
        elif col == 2 and row < 2 and idx < len(steps) - 1: # Downward connector
            pdf.line(x + 35, y + 18, x + 35, y_start + ((row + 1) * 42) - 3)
            # Arrow head pointing left for next row start or just down
            pdf.line(x + 35, y + 18, x + 35, y + 24)

    pdf.slide_footer(5)

    # ----------------------------------------------------
    # SLIDE 6: System Architecture
    # ----------------------------------------------------
    pdf.add_page()
    pdf.slide_header("Slide 6: System Architecture Components")
    
    # 3 Pillars
    subsystems = [
        ("FRONTEND PORTAL", ["React.js client interface", "Vite build configurations", "Tailwind CSS dashboard utilities", "Axios proxy connections"], 15),
        ("API GATEWAY SERVER", ["Node.js + Express.js APIs", "Multer multi-part attachments", "Winston file logging wrapper", "Mongoose MongoDB database connections"], 105),
        ("AI SERVICE CORE", ["FastAPI service wrapper", "LangGraph orchestrator machine", "FAISS similarity check algorithms", "Google Gemini reasoning engine"], 195)
    ]
    
    for title, desc_list, x in subsystems:
        pdf.set_fill_color(25, 25, 25)
        pdf.set_draw_color(40, 40, 40)
        pdf.rect(x, 40, 85, 140, "DF")
        
        # Header banner
        pdf.set_fill_color(35, 35, 35)
        pdf.rect(x, 40, 85, 15, "F")
        pdf.set_xy(x, 44)
        pdf.set_font("helvetica", "B", 11)
        pdf.set_text_color(16, 185, 129)
        pdf.cell(85, 6, title, align="C")
        
        # Bullet list inside box
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

    pdf.slide_footer(6)

    # ----------------------------------------------------
    # SLIDE 7: Technology Stack
    # ----------------------------------------------------
    pdf.add_page()
    pdf.slide_header("Slide 7: Technical Stack Details")
    
    # Table headers
    headers = [("Layer", 45), ("Technology", 95), ("Purpose", 125)]
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
        ("Frontend client", "React, Vite, Tailwind CSS, Lucide Icons", "Render diagnostic grids, charts & telemetry UI"),
        ("API gateway", "Node.js, Express.js, Multer, Winston", "REST request proxy, log trace handling & routing"),
        ("Database persistence", "MongoDB (Mongoose), local JSON files", "Saves bugs, verified resolutions & stats fallback"),
        ("AI Microservice", "Python 3.10, FastAPI", "Wraps embeddings, similarity matches & agents"),
        ("Vector database", "FAISS, NumPy vector fallback", "Maintains dense vectors for semantic similarity query"),
        ("Agent runtime", "LangChain, LangGraph StateGraph", "Orchestrates transition state logic between agents"),
        ("LLM Framework", "Google Gemini API", "Core inference engine for logs and recommendations"),
        ("Document Parsing", "PyPDF2, python-docx, pandas", "Parses uploaded logs and structured bug files"),
        ("Container topology", "Docker, Docker Compose", "Bundles multi-tier containers for fast setups")
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

    pdf.slide_footer(7)

    # ----------------------------------------------------
    # SLIDE 8: RAG & Semantic Retrieval
    # ----------------------------------------------------
    pdf.add_page()
    pdf.slide_header("Slide 8: RAG & Semantic Retrieval Ingestion")
    y = 38
    y = pdf.draw_bullet(15, y, "Vector Representation: Maps raw defect reports and log strings into a dense 384-dimensional space.")
    y = pdf.draw_bullet(15, y, "FAISS Similarity Lookups: Calculates Euclidean distance metrics on embedding indexes to yield similar profiles.")
    y = pdf.draw_bullet(15, y, "RAG Context Fusion: Enriches LLM generation by appending retrieved historical solutions to the prompt context.")
    y = pdf.draw_bullet(15, y, "Keyword-Independent Retrieval: Bridges syntactic gaps, matching 'deadlock' logs against 'transaction exhaustion' vectors.")
    pdf.slide_footer(8)

    # ----------------------------------------------------
    # SLIDE 9: Multi-Agent Diagnosis
    # ----------------------------------------------------
    pdf.add_page()
    pdf.slide_header("Slide 9: Multi-Agent LangGraph Node Transition")
    
    # Visual grid of agents
    agents = [
        ("Triage Agent", "Component category, severity rating & priority index"),
        ("Log Analysis Agent", "Extracts exceptions, call frame classes & methods"),
        ("Duplicate Agent", "FAISS similarity scans for prior ticket links"),
        ("Root Cause Agent", "Hypothesizes defects by comparative evidence mapping"),
        ("Remediation Agent", "Immediate code patches & best practice guides")
    ]
    
    y_start = 45
    for idx, (name, role) in enumerate(agents):
        x = 20 + (idx % 2) * 130
        y = y_start + (idx // 2) * 45
        
        pdf.set_fill_color(25, 25, 25)
        pdf.set_draw_color(16, 185, 129)
        pdf.rect(x, y, 115, 34, "DF")
        
        pdf.set_xy(x + 5, y + 4)
        pdf.set_font("helvetica", "B", 12)
        pdf.set_text_color(255, 255, 255)
        pdf.cell(100, 6, name, new_x="LMARGIN", new_y="NEXT")
        
        pdf.set_xy(x + 5, y + 12)
        pdf.set_font("helvetica", "", 10)
        pdf.set_text_color(180, 180, 180)
        pdf.multi_cell(105, 5, role)

    # Text block about Orchestration on the bottom-right
    pdf.set_fill_color(30, 30, 40)
    pdf.set_draw_color(100, 100, 255)
    pdf.rect(150, 135, 115, 34, "DF")
    pdf.set_xy(155, 139)
    pdf.set_font("helvetica", "B", 11)
    pdf.set_text_color(120, 120, 255)
    pdf.cell(100, 5, "Orchestration Control Node", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("helvetica", "", 9)
    pdf.set_text_color(180, 180, 210)
    pdf.set_xy(155, 147)
    pdf.multi_cell(105, 4, "State variables and log buffers are maintained across the LangGraph workspace state dictionary.")

    pdf.slide_footer(9)

    # ----------------------------------------------------
    # SLIDE 10: Knowledge Base Growth
    # ----------------------------------------------------
    pdf.add_page()
    pdf.slide_header("Slide 10: Knowledge Base Growth Loop")
    y = 38
    y = pdf.draw_bullet(15, y, "Verification Gate: Submissions are never directly stored. Developers must confirm fixes via Resolution Verification.")
    y = pdf.draw_bullet(15, y, "Threshold checking: A 90% cosine similarity threshold checks if the verified defect is already registered.")
    
    # Enrichment/Creation paths
    pdf.set_fill_color(10, 35, 20)
    pdf.set_draw_color(16, 185, 129)
    pdf.rect(15, 95, 125, 75, "DF")
    pdf.set_xy(20, 100)
    pdf.set_font("helvetica", "B", 12)
    pdf.set_text_color(100, 255, 150)
    pdf.cell(115, 6, "PATH A: Similarity > 90%", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("helvetica", "", 10)
    pdf.set_text_color(170, 210, 180)
    pdf.set_xy(20, 110)
    pdf.multi_cell(115, 5, "- The incoming defect matches an existing record.\n- The system enriches the existing verified entry rather than creating duplicates.\n- Overwrites matching FAISS index labels and updates metadata variables.")

    pdf.set_fill_color(30, 30, 30)
    pdf.set_draw_color(100, 100, 100)
    pdf.rect(150, 95, 125, 75, "DF")
    pdf.set_xy(155, 100)
    pdf.set_font("helvetica", "B", 12)
    pdf.set_text_color(240, 240, 240)
    pdf.cell(115, 6, "PATH B: Similarity <= 90%", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("helvetica", "", 10)
    pdf.set_text_color(180, 180, 180)
    pdf.set_xy(155, 110)
    pdf.multi_cell(115, 5, "- Represents a new software failure pattern.\n- Creates a new unique vector entry and inserts the document into MongoDB.\n- Regenerates FAISS index indices to add the new RAG playbook mapping.")

    pdf.slide_footer(10)

    # ----------------------------------------------------
    # SLIDE 11: Defect Pattern Analytics
    # ----------------------------------------------------
    pdf.add_page()
    pdf.slide_header("Slide 11: Defect Pattern Analytics Dashboard")
    y = 38
    y = pdf.draw_bullet(15, y, "Aggregation Routines: Group database documents by component category, priority queues, and timestamps.")
    y = pdf.draw_bullet(15, y, "Category distribution: Reveals components with high defect frequency.")
    y = pdf.draw_bullet(15, y, "Timelines & exception signatures: Captures recurrence trends and recurring log exceptions.")
    y = pdf.draw_bullet(15, y, "Metric Exports: Compiles the structured analytics into CSV files for historical diagnostic audits.")
    pdf.slide_footer(11)

    # ----------------------------------------------------
    # SLIDE 12: Complete End-to-End Workflow
    # ----------------------------------------------------
    pdf.add_page()
    pdf.slide_header("Slide 12: End-to-End Ingestion Workflow")
    
    steps = [
        "1. Submit log files & traces to React frontend portal.",
        "2. Express router validates inputs and saves initial documents to DB.",
        "3. AI service maps fields into sentence embeddings via SentenceTransformers.",
        "4. FAISS index executes similarity search, returning similar bug records.",
        "5. Triage Agent maps Component, Severity, and Priority rating tags.",
        "6. Log Analysis Agent parses logs to extract exception stack details.",
        "7. Root Cause and Remediation Agents output hypotheses and patches.",
        "8. Dashboard inspect drawer renders complete diagnostics.",
        "9. Developer fixes bug and confirms via Resolution Verification.",
        "10. Index growth loop enriches existing files or indexes new vectors."
    ]
    
    y = 36
    pdf.set_font("helvetica", "", 10.5)
    pdf.set_text_color(220, 220, 220)
    for step in steps:
        pdf.set_xy(15, y)
        pdf.cell(0, 5, step)
        y += 15
        
    pdf.slide_footer(12)

    # ----------------------------------------------------
    # SLIDE 13: Testing & Results
    # ----------------------------------------------------
    pdf.add_page()
    pdf.slide_header("Slide 13: Testing & Evaluation Metrics")
    
    # 3 KPI Cards
    kpis = [
        ("ACCURACY", "100.0%", "12/12 Defect Cases Passed", 15),
        ("LATENCY", "22.9 ms", "Avg FAISS Response", 105),
        ("CONFIDENCE", "85.4%", "Avg Agent certainty", 195)
    ]
    
    for title, score, details, x in kpis:
        pdf.set_fill_color(25, 25, 25)
        pdf.set_draw_color(16, 185, 129)
        pdf.set_line_width(0.8)
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

    # Metrics Table
    pdf.set_xy(15, 95)
    pdf.set_fill_color(30, 30, 30)
    pdf.set_draw_color(40, 40, 40)
    pdf.rect(15, 95, 267, 10, "F")
    
    pdf.set_font("helvetica", "B", 10)
    pdf.set_text_color(16, 185, 129)
    pdf.set_xy(20, 97)
    pdf.cell(90, 6, "Metric Tested")
    pdf.cell(90, 6, "Calculated Result")
    pdf.cell(87, 6, "Benchmark Standard")
    
    test_rows = [
        ("Precision", "100.0%", ">= 90.0%"),
        ("Recall", "100.0%", ">= 90.0%"),
        ("F1 Score", "100.0%", ">= 90.0%"),
        ("Knowledge Growth Actions", "12 Created, 0 Updated", "Self-growth verified")
    ]
    
    y_tbl = 107
    for metric, score, benchmark in test_rows:
        pdf.set_draw_color(40, 40, 40)
        pdf.line(15, y_tbl, 282, y_tbl)
        
        pdf.set_xy(20, y_tbl + 2.5)
        pdf.set_font("helvetica", "B", 9)
        pdf.set_text_color(240, 240, 240)
        pdf.cell(90, 5, metric)
        
        pdf.set_font("helvetica", "", 9)
        pdf.set_text_color(200, 200, 200)
        pdf.cell(90, 5, score)
        
        pdf.set_text_color(140, 140, 140)
        pdf.cell(87, 5, benchmark)
        y_tbl = pdf.get_y() + 2.5

    pdf.slide_footer(13)

    # ----------------------------------------------------
    # SLIDE 14: Conclusion & Future Scope
    # ----------------------------------------------------
    pdf.add_page()
    pdf.slide_header("Slide 14: Conclusion & Future Enhancements")
    
    # Conclusion left
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
    pdf.multi_cell(118, 6.5, "- Automates defect categorizations & environmental triage ratings.\n- Bridges syntax discrepancies using RAG-based context retrieval.\n- Coordinates deep log trace extraction via specialized agents.\n- Self-grow knowledge base updates enrich historical memory stores.\n- Evaluated diagnostic results reached a 100% E2E test pass rate.")

    # Future scope right
    pdf.rect(154, 36, 128, 145, "DF")
    pdf.set_xy(159, 42)
    pdf.set_font("helvetica", "B", 14)
    pdf.set_text_color(16, 185, 129)
    pdf.cell(118, 6, "Future Enhancements", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("helvetica", "", 11)
    pdf.set_text_color(200, 200, 200)
    pdf.set_xy(159, 52)
    pdf.multi_cell(118, 6.5, "- IDE Plugins: Native connectors to submit stack frames directly inside VS Code and PyCharm.\n- Real-Time log streams: Interfacing directly with Datadog/ELK agent pipelines.\n- RBAC controls: Enforcing user role permissions on verified resolutions.\n- Code-level repair: Extending immediate fix suggestions to auto-patch generation models.")

    pdf.slide_footer(14)

    # ----------------------------------------------------
    # SLIDE 15: Thank You Slide
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
    
    pdf.slide_footer(15)

    # Save output PDF file
    pdf.output(filename)
    print(f"Successfully generated beautiful PDF presentation at: {filename}")

if __name__ == "__main__":
    out_file = sys.argv[1] if len(sys.argv) > 1 else "presentation.pdf"
    build_pdf(out_file)
