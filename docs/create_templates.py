import pandas as pd
import os

import xlwt

def create_agile_template():
    print("Creating agile_Template_v0.1.xls...")
    # Initialize xlwt workbook
    wb = xlwt.Workbook()
    ws = wb.add_sheet("Agile Backlog")
    
    headers = [
        "User Story ID", "Epic", "Feature", "Story Title", 
        "Description", "Acceptance Criteria", "Priority", 
        "Story Points", "Assigned To", "Status"
    ]
    for col_idx, header in enumerate(headers):
        ws.write(0, col_idx, header)
        
    data = [
        ["US-101", "Authentication", "User Login", "Secure OAuth Login", 
         "As a user, I want to log in using OAuth so my account is secure.",
         "1. Google & GitHub login buttons available. 2. JWT token returned.",
         "Must Have", 5, "Developer A", "In Progress"],
        ["US-102", "Authentication", "Password Reset", "Self-service Password Reset Link", 
         "As a user, I want to reset my password using a link sent to my email.",
         "1. Password strength validator active. 2. Reset token expires in 1 hour.",
         "Should Have", 3, "Developer B", "To Do"],
        ["US-103", "Bug Submission", "Logs Ingestion", "Support Multi-Format File Ingestion", 
         "As a developer, I want to upload .txt, .log, and .pdf crash logs directly.",
         "1. Multer processes up to 10MB. 2. PDF texts extracted correctly.",
         "Must Have", 8, "Developer A", "Done"],
        ["US-104", "Dashboard UI", "Visual Metrics", "Interactive Dataflow Graph", 
         "As an administrator, I want to view interactive SVG maps of the systems.",
         "1. Node linkages clearly visible. 2. Hover highlights connected paths.",
         "Could Have", 5, "Designer C", "Backlog"],
        ["US-105", "Dashboard UI", "Theme Toggle", "Class-Based Light/Dark Mode", 
         "As a developer, I want to switch between dark and light themes dynamically.",
         "1. Dark mode active by default. 2. Persistent storage in localStorage.",
         "Should Have", 2, "Developer B", "Done"]
    ]
    for row_idx, row_data in enumerate(data):
        for col_idx, val in enumerate(row_data):
            ws.write(row_idx + 1, col_idx, val)
            
    wb.save("agile_Template_v0.1.xls")

def create_defect_tracker():
    print("Creating defect_tracker_template_v0.1.xlsx...")
    data = {
        "Defect ID": ["BUG-1001", "BUG-1002", "BUG-1003", "BUG-1004", "BUG-1005"],
        "Summary": [
            "NullPointerException on canvas resize",
            "Database pool timeout under load",
            "File parser fails on encrypted PDF",
            "CSS layout breaking on mobile views",
            "Incorrect similarity score on short inputs"
        ],
        "Description": [
            "Resizing the window causes layout canvas bounds to compute as null values.",
            "Maximum connection pool of 20 elements exceeded during parallel spikes.",
            "PyPDF2 throws Exception when reading password-protected attachments.",
            "Sidebar container overlays grid layout elements below 768px screens.",
            "Short log inputs yield high cosine similarity percentages improperly."
        ],
        "Steps to Reproduce": [
            "1. Open App. 2. Resize browser window rapidly.",
            "1. Run load test script. 2. Spawn 100 concurrent submit queries.",
            "1. Go to Submit page. 2. Upload locked PDF file.",
            "1. Inspect page in DevTools. 2. Select iPhone SE profile.",
            "1. Submit title 'A' and description 'B'. 2. Compare RAG results."
        ],
        "Severity": ["High", "Critical", "Medium", "Low", "Medium"],
        "Priority": ["Medium", "High", "Low", "Low", "Medium"],
        "Status": ["Fixed", "Assigned", "Open", "Fixed", "Closed"],
        "Reporter": ["QA Engineer Alex", "Dev Leader Jane", "Developer Bob", "QA Tester Emily", "QA Tester Emily"],
        "Assignee": ["Developer Bob", "Developer Bob", "Developer A", "Designer C", "Developer A"],
        "Found in Version": ["v1.0.0-rc1", "v1.0.0-rc1", "v1.0.0", "v1.0.1", "v1.0.1"],
        "Fixed in Version": ["v1.0.0", "", "", "v1.0.2", "v1.0.2"],
        "Resolution Notes": [
            "Added null boundaries safety validation check to canvas.tsx.",
            "",
            "",
            "Changed sidebar position property to fixed on smaller screens.",
            "Adjusted inner-product score calculation to penalize short vectors."
        ]
    }
    df = pd.DataFrame(data)
    df.to_excel("defect_tracker_template_v0.1.xlsx", index=False, engine="openpyxl")

def create_unit_test_plan():
    print("Creating unit_test_plan_v0.1.xlsx...")
    data = {
        "Test Case ID": ["TC-001", "TC-002", "TC-003", "TC-004", "TC-005"],
        "Component/Module": ["Backend Router", "PDF Parser", "FAISS Store", "Sidebar Component", "Theme State Manager"],
        "Description": [
            "Verify POST /api/submitBug successfully inserts valid JSON payloads.",
            "Verify PDF parser extracts valid strings from clean log documents.",
            "Verify FAISS similarity search yields exact top 5 matches.",
            "Verify clicking theme toggle updates class list in documentElement.",
            "Verify dark mode state persists across browser page reloads."
        ],
        "Pre-conditions": [
            "Express port 5000 is open. Database is online.",
            "File parser service is active.",
            "Historical bugs knowledge base seeded with 10 documents.",
            "React client running on port 3000.",
            "LocalStorage is clear."
        ],
        "Input Data": [
            "Valid JSON containing Title, Description, and Severity.",
            "Sample TXT file containing mock Exception logs.",
            "Query: 'MemoryLeak exception in regex match'",
            "Action: Click Toggle Button",
            "Action: Set Theme to Light and Reload Page"
        ],
        "Steps to Execute": [
            "1. POST payload. 2. Verify status code 201. 3. Check JSON response keys.",
            "1. Call /api/upload. 2. Verify extracted text matches file lines.",
            "1. Query vector DB. 2. Verify scores are returned descending.",
            "1. Locate sidebar button. 2. Click button. 3. Check class on html tag.",
            "1. Switch theme. 2. Press reload in browser. 3. Verify class persists."
        ],
        "Expected Result": [
            "Status code 201. Assigned bugId returned. RAG similarBugs array populated.",
            "Success message returned with extracted content strings.",
            "Cosine similarity matches returned sorted by descending similarity.",
            "Class 'dark' is added/removed on <html> element dynamically.",
            "Saved value 'darkMode' in localStorage matches visual state on boot."
        ],
        "Actual Result": [
            "As expected. Code 201 returned with BUG-1002 assigned.",
            "As expected. Text extracted and displayed on frontend page.",
            "As expected. Top matches retrieved with score values.",
            "As expected. Element classes toggled successfully.",
            "As expected. Saved state preserves light mode profile."
        ],
        "Status": ["Pass", "Pass", "Pass", "Pass", "Pass"],
        "Execution Date": ["2026-07-10", "2026-07-10", "2026-07-11", "2026-07-11", "2026-07-11"],
        "Executed By": ["Developer Bob", "Developer Bob", "Developer A", "Designer C", "Developer B"]
    }
    df = pd.DataFrame(data)
    df.to_excel("unit_test_plan_v0.1.xlsx", index=False, engine="openpyxl")

def main():
    create_agile_template()
    create_defect_tracker()
    create_unit_test_plan()
    print("All spreadsheets compiled successfully.")

if __name__ == "__main__":
    main()
