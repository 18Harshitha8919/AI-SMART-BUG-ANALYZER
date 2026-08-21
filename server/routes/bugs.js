const express = require('express');
const router = express.Router();
const multer = require('multer');
const path = require('path');
const fs = require('fs');
const axios = require('axios');
const db = require('../db');
const logger = require('../logger');

const UPLOADS_DIR = path.join(__dirname, '../../uploads');
const PYTHON_AI_URL = process.env.PYTHON_AI_URL || "http://localhost:8000";

// Ensure uploads folder exists
if (!fs.existsSync(UPLOADS_DIR)) {
    fs.mkdirSync(UPLOADS_DIR, { recursive: true });
}

// Multer Config
const storage = multer.diskStorage({
    destination: (req, file, cb) => {
        cb(null, UPLOADS_DIR);
    },
    filename: (req, file, cb) => {
        const uniqueSuffix = Date.now() + '-' + Math.round(Math.random() * 1e9);
        cb(null, uniqueSuffix + '-' + file.originalname);
    }
});

const upload = multer({ 
    storage,
    limits: { fileSize: 10 * 1024 * 1024 } // 10 MB file size limit
});

// Helper to preprocess text (Module 2)
function preprocessText(title, description, stackTrace = "", errorLog = "") {
    let combined = `${title}\n${description}\n${stackTrace}\n${errorLog}`;
    // Remove duplicate spaces and normalize newlines
    combined = combined.replace(/\s+/g, ' ');
    // Remove non-printable ascii character signatures
    combined = combined.replace(/[^\x20-\x7E\n]/g, '');
    return combined.trim();
}

// POST /submitBug (Module 1, 2, 4, 5)
router.post('/submitBug', async (req, res) => {
    logger.info("Received request: POST /api/submitBug");
    const { 
        title, 
        description, 
        severity, 
        priority, 
        environment, 
        moduleName, 
        reporterName, 
        stackTrace, 
        errorLog,
        attachments 
    } = req.body;

    // Validate fields
    if (!title || !description || !severity || !priority || !environment || !moduleName || !reporterName) {
        logger.error("SubmitBug validation failed: Missing required fields");
        return res.status(400).json({ error: "Missing required fields. Title, description, severity, priority, environment, moduleName, and reporterName are required." });
    }

    try {
        // Preprocess (Module 2)
        const cleanedDoc = preprocessText(title, description, stackTrace, errorLog);

        // Generate Bug ID (e.g. BUG-1001)
        const list = await db.getBugs();
        const nextNum = list.length + 1001;
        const bugId = `BUG-${nextNum}`;

        // RAG Pipeline (Module 4) - Search similar bugs in FAISS database
        let similarBugs = [];
        let duplicateStatus = "New Issue";
        
        try {
            logger.info(`Sending query to Python AI service: ${PYTHON_AI_URL}/search`);
            const aiRes = await axios.post(`${PYTHON_AI_URL}/search`, {
                query: cleanedDoc,
                k: 5
            });
            similarBugs = aiRes.data.results || [];
            
            // Duplicate Detection (Module 5)
            // If the highest similarity score is > 90% (0.90)
            if (similarBugs.length > 0 && similarBugs[0].score > 0.90) {
                duplicateStatus = "Potential Duplicate Bug";
            }
        } catch (e) {
            logger.warn(`Failed to connect to Python AI search service: ${e.message}. RAG results will be empty.`);
        }

        // Multi-Agent Orchestration (Milestone 2 & 3)
        let agentInsights = {
            bug_id: bugId,
            triage: {
                triage_component: moduleName,
                severity: severity,
                priority: priority === "Critical" ? "P1" : (priority === "High" ? "P2" : (priority === "Medium" ? "P3" : "P4")),
                confidence: 70,
                reasoning: "Defaults applied. Agent offline.",
                severity_reason: "Defaults applied. Agent offline.",
                priority_reason: "Defaults applied. Agent offline."
            },
            log_analysis: {
                exception_type: "UnknownException",
                error_message: "Log analysis defaulted. Agent offline.",
                failed_class: "Unknown",
                failed_method: "Unknown",
                timestamp: new Date().toISOString(),
                failure_reason: "Log analysis defaulted. Agent offline.",
                file: "Unknown",
                line: 0,
                function: "Unknown",
                root_cause: "Log analysis defaulted. Agent offline.",
                affected_code_path: []
            },
            root_cause: {
                root_cause: "Root cause analysis defaulted. Agent offline.",
                confidence: 50,
                supporting_evidence: ["BUG-234"],
                explanation: "No agent logs processed."
            },
            duplicates: [],
            remediation: {
                immediate_fix: "Validate code paths and check parameter bounds.",
                long_term: "Establish defensive validation middleware.",
                best_practices: ["Use exception handling.", "Add logging.", "Improve unit testing.", "Perform regression testing."]
            },
            timestamp: new Date().toISOString(),
            status: "failed"
        };

        try {
            logger.info(`Sending query to Python Multi-Agent Orchestrator: ${PYTHON_AI_URL}/agent/orchestrate`);
            const agentRes = await axios.post(`${PYTHON_AI_URL}/agent/orchestrate`, {
                title,
                description,
                environment,
                stack_trace: stackTrace || "",
                error_log: errorLog || "",
                bug_id: bugId
            });
            if (agentRes.data && agentRes.data.triage) {
                const t = agentRes.data.triage;
                const l = agentRes.data.log_analysis;
                const r = agentRes.data.root_cause;
                const d = agentRes.data.duplicates || [];
                const rem = agentRes.data.remediation;

                agentInsights = {
                    bug_id: agentRes.data.bug_id || bugId,
                    triage: {
                        triage_component: t.triage_component,
                        severity: t.severity,
                        priority: t.priority,
                        confidence: t.confidence,
                        reasoning: t.reasoning,
                        severity_reason: t.severity_reason || "Analyzed by AI Triage Agent.",
                        priority_reason: t.priority_reason || "Analyzed by AI Triage Agent."
                    },
                    log_analysis: {
                        exception_type: l.exception_type,
                        error_message: l.error_message || "Exception trace parsed successfully.",
                        failed_class: l.failed_class || "UnknownClass",
                        failed_method: l.failed_method || "UnknownMethod",
                        timestamp: l.timestamp || new Date().toISOString(),
                        failure_reason: l.failure_reason || "Stack trace execution halted.",
                        file: l.file,
                        line: l.line,
                        function: l.function,
                        root_cause: l.root_cause,
                        affected_code_path: l.affected_code_path
                    },
                    root_cause: {
                        root_cause: r.root_cause,
                        confidence: r.confidence,
                        supporting_evidence: r.supporting_evidence,
                        explanation: r.explanation || r.reasoning || "Reasoning processed."
                    },
                    duplicates: d.map(item => ({
                        bug_id: item.bug_id,
                        similarity: item.similarity,
                        summary: item.summary,
                        resolution: item.resolution
                    })),
                    remediation: {
                        immediate_fix: rem.immediate_fix,
                        long_term: rem.long_term,
                        best_practices: rem.best_practices
                    },
                    timestamp: agentRes.data.timestamp || new Date().toISOString(),
                    status: agentRes.data.status || "completed"
                };
            }
        } catch (agentErr) {
            logger.warn(`Failed to connect to Python Orchestrate Agent: ${agentErr.message}`);
        }

        // Store inside DB (Module 1)
        const bugEntry = {
            bugId,
            title,
            description,
            severity,
            priority,
            environment,
            module: moduleName,
            reporterName,
            stackTrace: stackTrace || "",
            errorLog: errorLog || "",
            cleanedDocument: cleanedDoc,
            attachments: attachments || [],
            agentInsights,
            createdAt: new Date()
        };

        const savedBug = await db.insertBug(bugEntry);

        logger.info(`Bug created successfully: ${bugId}. Duplicate status: ${duplicateStatus}`);

        return res.status(201).json({
            message: "Bug report submitted successfully.",
            bugId,
            duplicateStatus,
            bug: savedBug,
            similarBugs
        });

    } catch (e) {
        logger.error(`Error submitting bug: ${e.message}`);
        return res.status(500).json({ error: "Internal Server Error" });
    }
});

// POST /upload (Module 1, 8) - Uploads file, extracts text via Python service
router.post('/upload', (req, res, next) => {
    upload.single('file')(req, res, (err) => {
        if (err instanceof multer.MulterError) {
            if (err.code === 'LIMIT_FILE_SIZE') {
                logger.error("File upload failed: File exceeds 10 MB limit.");
                return res.status(400).json({ error: "File exceeds 10 MB size limit." });
            }
            logger.error(`Multer upload error: ${err.message}`);
            return res.status(400).json({ error: err.message });
        } else if (err) {
            logger.error(`Upload error: ${err.message}`);
            return res.status(500).json({ error: "Upload failed." });
        }
        next();
    });
}, async (req, res) => {
    logger.info("Received request: POST /api/upload");
    if (!req.file) {
        return res.status(400).json({ error: "No file uploaded" });
    }

    const filePath = req.file.path;
    logger.info(`Saved uploaded file: ${req.file.originalname} -> ${filePath}`);

    try {
        // Build multipart data to forward to Python AI Service
        const FormData = require('form-data');
        const form = new FormData();
        form.append('file', fs.createReadStream(filePath), req.file.originalname);

        logger.info(`Forwarding file to Python AI text extractor: ${PYTHON_AI_URL}/process-file`);
        const pythonRes = await axios.post(`${PYTHON_AI_URL}/process-file`, form, {
            headers: {
                ...form.getHeaders()
            }
        });

        // Clean up uploaded file from local uploads after text is extracted to avoid clutter
        // (But we can keep it if needed. The prompt says "Store attachments". We'll keep it.)
        
        return res.status(200).json({
            message: "File uploaded and parsed successfully",
            filename: req.file.originalname,
            filePath: filePath,
            extractedText: pythonRes.data.extracted_text
        });

    } catch (e) {
        logger.error(`Failed to parse file via Python Service: ${e.message}`);
        
        // Fallback: read file as text directly inside Express if Python is offline
        try {
            const ext = path.extname(req.file.originalname).toLowerCase();
            if (ext === '.txt' || ext === '.log') {
                const text = fs.readFileSync(filePath, 'utf-8');
                return res.status(200).json({
                    message: "File parsed successfully via Node fallback",
                    filename: req.file.originalname,
                    filePath: filePath,
                    extractedText: text
                });
            }
            return res.status(200).json({
                message: "File uploaded successfully (binary fallback)",
                filename: req.file.originalname,
                filePath: filePath,
                extractedText: `[Binary File parsing requires Python AI Service online. Extracted text fallback omitted for: ${ext}]`
            });
        } catch (readErr) {
            return res.status(500).json({ error: `File save succeeded but parsing failed: ${readErr.message}` });
        }
    }
});

// GET /bugs
router.get('/bugs', async (req, res) => {
    logger.info("Received request: GET /api/bugs");
    try {
        const bugs = await db.getBugs();
        return res.status(200).json(bugs);
    } catch (e) {
        logger.error(`Failed to list bugs: ${e.message}`);
        return res.status(500).json({ error: "Internal Server Error" });
    }
});

// GET /similar/:id
router.get('/similar/:id', async (req, res) => {
    const bugId = req.params.id;
    logger.info(`Received request: GET /api/similar/${bugId}`);
    try {
        const bug = await db.getBugById(bugId);
        if (!bug) {
            return res.status(404).json({ error: "Bug report not found" });
        }

        // Query Python service to vector search FAISS
        const aiRes = await axios.post(`${PYTHON_AI_URL}/search`, {
            query: bug.cleanedDocument,
            k: 5
        });

        return res.status(200).json({
            bugId: bug.bugId,
            title: bug.title,
            similarBugs: aiRes.data.results || []
        });
    } catch (e) {
        logger.error(`Failed to find similar bugs: ${e.message}`);
        return res.status(500).json({ error: "Internal Server Error" });
    }
});

// POST /bugs/resolve
router.post('/bugs/resolve', async (req, res) => {
    const { bugId } = req.body;
    logger.info(`Received request: POST /api/bugs/resolve for Bug ${bugId}`);
    try {
        const updated = await db.updateBug(bugId, { "agentInsights.status": "resolved" });
        if (!updated) {
            return res.status(404).json({ error: "Bug not found" });
        }
        return res.status(200).json({ success: true, bug: updated });
    } catch (e) {
        logger.error(`Failed to mark bug as resolved: ${e.message}`);
        return res.status(500).json({ error: "Internal Server Error" });
    }
});

// POST /bugs/clear
router.post('/bugs/clear', async (req, res) => {
    logger.info("Received request: POST /api/bugs/clear");
    try {
        await db.clearBugs();
        await db.clearKnowledge();
        
        // Also call Python service to clear FAISS
        try {
            await axios.post(`${PYTHON_AI_URL}/clear`);
            logger.info("FAISS vector database cleared successfully.");
        } catch (aiErr) {
            logger.warn(`Failed to clear Python AI vector store: ${aiErr.message}`);
        }
        
        return res.status(200).json({ message: "Successfully deleted all ingested defect tickets and cleared vector memory." });
    } catch (e) {
        logger.error(`Failed to clear defect database: ${e.message}`);
        return res.status(500).json({ error: "Failed to delete defect tickets" });
    }
});

module.exports = router;
