import os
import sys

# Ensure clean architecture paths are importable
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from controllers.agent_controller import agent_controller

# Seeded dataset representing Authentication, Database, Dashboard, API, Security
validation_dataset = [
    {
        "id": "VAL-1",
        "category": "Authentication",
        "title": "Authentication bypass in OAuth validator",
        "description": "JWT token verification bypassed as public decrypt key rotated incorrectly.",
        "environment": "Production",
        "stack_trace": "SecurityException: Public key lookup failed: exposed null signature\n  at keystore.py:42 (get_key)\n  at jwt_verifier.py:84",
        "expected_severity": "Critical",
        "expected_component": "Authentication",
        "expected_exception": "SecurityException",
        "expected_file": "keystore.py",
        "expected_root_cause_keyword": "cryptographic"
    },
    {
        "id": "VAL-2",
        "category": "Database",
        "title": "Database connection pool deadlock timeout",
        "description": "SQLException thrown as maximum pool of 50 connections timed out.",
        "environment": "Staging",
        "stack_trace": "SQLException: ConnectionRefused pool overflow\n  at connection_pool.py:120 (acquire_session)",
        "expected_severity": "High",
        "expected_component": "Database",
        "expected_exception": "SQLException",
        "expected_file": "connection_pool.py",
        "expected_root_cause_keyword": "database"
    },
    {
        "id": "VAL-3",
        "category": "Dashboard",
        "title": "NullPointerException resizing layout bounds on high DPI screen",
        "description": "Canvas rendering crashed. Calculations for vector bounds returned null layout pointers.",
        "environment": "Production",
        "stack_trace": "java.lang.NullPointerException: Null drawing surface context\n  at canvas.java:322 (resize_frame)\n  at app.java:55",
        "expected_severity": "Critical",
        "expected_component": "Dashboard",
        "expected_exception": "NullReferenceException",
        "expected_file": "canvas.java",
        "expected_root_cause_keyword": "null reference"
    },
    {
        "id": "VAL-4",
        "category": "API",
        "title": "FileNotFoundException parsing missing configurations",
        "description": "IOError occurred when reading config.json settings file during bootstrap.",
        "environment": "Development",
        "stack_trace": "FileNotFoundException: config.json file not found\n  at parser.py:55 (load_json)",
        "expected_severity": "Low",
        "expected_component": "API",
        "expected_exception": "FileNotFoundException",
        "expected_file": "parser.py",
        "expected_root_cause_keyword": "filenotfound"
    },
    {
        "id": "VAL-5",
        "category": "API",
        "title": "IndexError out of bounds in JSON array pagination endpoint",
        "description": "API page parameters exceeded total elements array boundaries.",
        "environment": "Production",
        "stack_trace": "IndexOutOfBoundsException: list index out of range\n  at router.py:102 (paginate)",
        "expected_severity": "Medium",
        "expected_component": "API",
        "expected_exception": "IndexOutOfBoundsException",
        "expected_file": "router.py",
        "expected_root_cause_keyword": "null reference"
    },
    {
        "id": "VAL-6",
        "category": "Security",
        "title": "SecurityException validating missing CSRF token payload",
        "description": "Unauthorized access intercepted. Incoming POST lacks header verify values.",
        "environment": "Production",
        "stack_trace": "SecurityException: Access Denied invalid credentials\n  at csrf.py:31 (validate)",
        "expected_severity": "High",
        "expected_component": "Security",
        "expected_exception": "SecurityException",
        "expected_file": "csrf.py",
        "expected_root_cause_keyword": "cryptographic"
    },
    {
        "id": "VAL-7",
        "category": "API",
        "title": "TimeoutException trying to query remote HTTP resolver",
        "description": "Socket exception DNS query timed out on secondary lookup interface.",
        "environment": "Staging",
        "stack_trace": "TimeoutException: DNS lookup failed\n  at socket.py:99 (connect)",
        "expected_severity": "High",
        "expected_component": "API",
        "expected_exception": "TimeoutException",
        "expected_file": "socket.py",
        "expected_root_cause_keyword": "null reference"
    }
]

def run_agent_validation():
    print("=" * 75)
    print("      AI MULTI-AGENT ACCURACY VALIDATION SUITE (MILESTONE 3)     ")
    print("=" * 75)
    
    total = len(validation_dataset)
    
    severity_correct = 0
    priority_correct = 0
    exception_correct = 0
    failure_point_correct = 0
    root_cause_correct = 0
    duplicate_matching_correct = 0
    remediation_correct = 0
    
    for case in validation_dataset:
        print(f"\nEvaluating Case {case['id']} - Category: {case['category']}")
        print(f"Title: {case['title']}")
        
        # Invoke LangGraph Orchestrator through Controller
        res = agent_controller.orchestrate(
            title=case["title"],
            description=case["description"],
            environment=case["environment"],
            stack_trace=case["stack_trace"],
            error_log="",
            bug_id=case["id"]
        )
        
        # Priority mapping verification logic:
        expected_priority = "P3"
        if case["expected_severity"] == "Critical":
            expected_priority = "P1"
        elif case["expected_severity"] == "High":
            if case["environment"].lower() == "production":
                expected_priority = "P1"
            else:
                expected_priority = "P2"
        elif case["expected_severity"] == "Medium":
            expected_priority = "P3"
        elif case["expected_severity"] == "Low":
            expected_priority = "P4"
            
        severity_ok = res.triage.severity == case["expected_severity"]
        priority_ok = res.triage.priority == expected_priority
        exception_ok = res.log_analysis.exception_type == case["expected_exception"]
        
        expected_file = case["expected_file"]
        actual_file = res.log_analysis.file
        fp_ok = expected_file in actual_file or actual_file in expected_file
        
        # Root Cause validation: check if expected keyword is in root cause description (case-insensitive)
        rc_ok = case["expected_root_cause_keyword"].lower() in res.root_cause.root_cause.lower()
        # Duplicate validation: assert we retrieved similar match profiles
        dup_ok = len(res.duplicates) > 0 and res.duplicates[0].similarity > 0
        # Remediation validation: verify immediate and long-term steps exist
        rem_ok = len(res.remediation.immediate_fix) > 0 and len(res.remediation.best_practices) > 0
        
        if severity_ok:
            severity_correct += 1
        if priority_ok:
            priority_correct += 1
        if exception_ok:
            exception_correct += 1
        if fp_ok:
            failure_point_correct += 1
        if rc_ok:
            root_cause_correct += 1
        if dup_ok:
            duplicate_matching_correct += 1
        if rem_ok:
            remediation_correct += 1
            
        print(f"  - Triage Component:  Got [{res.triage.triage_component}] (Expected: {case['expected_component']})")
        print(f"  - Severity check:    Got [{res.triage.severity}] (Expected: {case['expected_severity']}) -> {'PASS' if severity_ok else 'FAIL'}")
        print(f"  - Priority check:    Got [{res.triage.priority}] (Expected: {expected_priority}) -> {'PASS' if priority_ok else 'FAIL'}")
        print(f"  - Exception check:   Got [{res.log_analysis.exception_type}] (Expected: {case['expected_exception']}) -> {'PASS' if exception_ok else 'FAIL'}")
        print(f"  - Failure Point:     Got [{res.log_analysis.file}:{res.log_analysis.line}] (Expected: {case['expected_file']}) -> {'PASS' if fp_ok else 'FAIL'}")
        print(f"  - Root Cause Match:  Got [{res.root_cause.root_cause}] -> {'PASS' if rc_ok else 'FAIL'}")
        print(f"  - Similar Bugs Find: Found {len(res.duplicates)} matches (Top Score: {res.duplicates[0].similarity}%) -> {'PASS' if dup_ok else 'FAIL'}")
        print(f"  - Remediation Action: Got [{res.remediation.immediate_fix}] -> {'PASS' if rem_ok else 'FAIL'}")
        
    sev_accuracy = (severity_correct / total) * 100
    pri_accuracy = (priority_correct / total) * 100
    exc_accuracy = (exception_correct / total) * 100
    fp_accuracy = (failure_point_correct / total) * 100
    rc_accuracy = (root_cause_correct / total) * 100
    dup_accuracy = (duplicate_matching_correct / total) * 100
    rem_accuracy = (remediation_correct / total) * 100
    
    print("\n" + "=" * 75)
    print("                 AI MULTI-AGENT ACCURACY VALIDATION REPORT            ")
    print("=" * 75)
    print(f" Severity Classification Accuracy:       {sev_accuracy:.1f}% ({severity_correct}/{total})")
    print(f" Priority Prediction Accuracy:            {pri_accuracy:.1f}% ({priority_correct}/{total})")
    print(f" Exception Detection Accuracy:           {exc_accuracy:.1f}% ({exception_correct}/{total})")
    print(f" Failure Point Accuracy:                  {fp_accuracy:.1f}% ({failure_point_correct}/{total})")
    print(f" Root Cause Detection Accuracy:           {rc_accuracy:.1f}% ({root_cause_correct}/{total})")
    print(f" Duplicate Matching Accuracy:             {dup_accuracy:.1f}% ({duplicate_matching_correct}/{total})")
    print(f" Remediation Recommendation Accuracy:     {rem_accuracy:.1f}% ({remediation_correct}/{total})")
    print("=" * 75)
    
    overall_score = (severity_correct + priority_correct + exception_correct + 
                     failure_point_correct + root_cause_correct + duplicate_matching_correct + 
                     remediation_correct)
    overall_total = total * 7
    
    print(f" OVERALL VERIFICATION: {overall_score}/{overall_total} assertions satisfied ({(overall_score/overall_total)*100:.1f}% Overall).")
    print("=" * 75)
    
    if overall_score == overall_total:
        print("Success: All agent metrics satisfied perfectly!")
        sys.exit(0)
    else:
        print("Warning: Some assertions failed. Check mappings.")
        sys.exit(1)

if __name__ == "__main__":
    run_agent_validation()
