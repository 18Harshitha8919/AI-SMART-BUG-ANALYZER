const mongoose = require('mongoose');
const fs = require('fs');
const path = require('path');
const logger = require('./logger');

const MONGODB_URI = process.env.MONGODB_URI || "mongodb://localhost:27017/bugsense";
const DATA_DIR = path.join(__dirname, 'data');
const JSON_DB_PATH = path.join(DATA_DIR, 'bugs.json');

// Ensure local data directory exists for fallback JSON storage
if (!fs.existsSync(DATA_DIR)) {
    fs.mkdirSync(DATA_DIR, { recursive: true });
}
if (!fs.existsSync(JSON_DB_PATH)) {
    fs.writeFileSync(JSON_DB_PATH, JSON.stringify([], null, 2), 'utf-8');
}

let isFallback = false;

// Define Mongoose Schema
const BugSchema = new mongoose.Schema({
    bugId: { type: String, required: true, unique: true },
    title: { type: String, required: true },
    description: { type: String, required: true },
    severity: { type: String, required: true },
    priority: { type: String, required: true },
    environment: { type: String, required: true },
    module: { type: String, required: true },
    reporterName: { type: String, required: true },
    stackTrace: { type: String, default: "" },
    errorLog: { type: String, default: "" },
    cleanedDocument: { type: String, default: "" },
    attachments: { type: Array, default: [] },
    agentInsights: {
        bug_id: { type: String },
        triage: {
            triage_component: { type: String },
            severity: { type: String },
            priority: { type: String },
            confidence: { type: Number },
            reasoning: { type: String },
            severity_reason: { type: String },
            priority_reason: { type: String }
        },
        log_analysis: {
            exception_type: { type: String },
            error_message: { type: String },
            failed_class: { type: String },
            failed_method: { type: String },
            timestamp: { type: String },
            failure_reason: { type: String },
            file: { type: String },
            line: { type: Number },
            function: { type: String },
            root_cause: { type: String },
            affected_code_path: { type: Array, default: [] }
        },
        root_cause: {
            root_cause: { type: String },
            confidence: { type: Number },
            supporting_evidence: { type: Array, default: [] },
            explanation: { type: String }
        },
        duplicates: [{
            bug_id: { type: String },
            similarity: { type: Number },
            summary: { type: String },
            resolution: { type: String }
        }],
        remediation: {
            immediate_fix: { type: String },
            long_term: { type: String },
            best_practices: { type: Array, default: [] }
        },
        timestamp: { type: String },
        status: { type: String }
    },
    createdAt: { type: Date, default: Date.now }
});

const BugModel = mongoose.model('Bug', BugSchema);

const db = {
    connect: async () => {
        logger.info("Attempting to connect to MongoDB database...");
        try {
            // Wait max 3 seconds for MongoDB connection to avoid hanging backend startup
            await mongoose.connect(MONGODB_URI, {
                serverSelectionTimeoutMS: 3000
            });
            logger.info("Successfully connected to MongoDB server.");
            isFallback = false;
        } catch (e) {
            logger.warn(`Failed to connect to MongoDB (${e.message}). Falling back to local file JSON database.`);
            isFallback = true;
        }
    },
    
    insertBug: async (bugData) => {
        if (!isFallback) {
            try {
                const doc = new BugModel(bugData);
                return await doc.save();
            } catch (e) {
                logger.error(`MongoDB insert error: ${e.message}. Attempting fallback writing.`);
            }
        }
        
        // Local File Fallback
        try {
            const dataStr = fs.readFileSync(JSON_DB_PATH, 'utf-8');
            const list = JSON.parse(dataStr);
            const entry = {
                ...bugData,
                _id: new Date().getTime().toString(),
                createdAt: new Date()
            };
            list.push(entry);
            fs.writeFileSync(JSON_DB_PATH, JSON.stringify(list, null, 2), 'utf-8');
            logger.info(`Inserted Bug ${bugData.bugId} inside local JSON fallback database.`);
            return entry;
        } catch (e) {
            logger.error(`Fallback database write failed: ${e.message}`);
            throw e;
        }
    },

    getBugs: async () => {
        if (!isFallback) {
            try {
                return await BugModel.find().sort({ createdAt: -1 });
            } catch (e) {
                logger.error(`MongoDB list error: ${e.message}. Using fallback reading.`);
            }
        }
        
        // Local File Fallback
        try {
            const dataStr = fs.readFileSync(JSON_DB_PATH, 'utf-8');
            const list = JSON.parse(dataStr);
            // Sort by createdAt descending
            return list.sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt));
        } catch (e) {
            logger.error(`Fallback database list reading failed: ${e.message}`);
            return [];
        }
    },

    getBugById: async (id) => {
        if (!isFallback) {
            try {
                const bug = await BugModel.findOne({ bugId: id });
                if (bug) return bug;
            } catch (e) {
                logger.error(`MongoDB lookup error: ${e.message}. Using fallback reading.`);
            }
        }
        
        // Local File Fallback
        try {
            const dataStr = fs.readFileSync(JSON_DB_PATH, 'utf-8');
            const list = JSON.parse(dataStr);
            return list.find(b => b.bugId === id) || null;
        } catch (e) {
            logger.error(`Fallback database query failed: ${e.message}`);
            return null;
        }
    },
    
    getIsFallback: () => isFallback
};

module.exports = db;
