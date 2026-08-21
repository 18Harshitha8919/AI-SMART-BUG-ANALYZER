const express = require('express');
const router = express.Router();
const axios = require('axios');
const db = require('../db');
const logger = require('../logger');

const PYTHON_AI_URL = process.env.PYTHON_AI_URL || "http://localhost:8000";

// POST /api/knowledge/add
router.post('/knowledge/add', async (req, res) => {
    try {
        const {
            bugId,
            title,
            description,
            stackTrace,
            rootCause,
            fixAction,
            severity,
            priority,
            category,
            component
        } = req.body;

        if (!bugId || !title || !description || !rootCause || !fixAction) {
            return res.status(400).json({ error: "Missing required fields for knowledge entry." });
        }

        logger.info(`Processing Knowledge Growth for Bug ${bugId}...`);

        // 1. Semantic Similarity Search in FAISS
        let isDuplicateKnowledge = false;
        let matchedId = null;
        let topScore = 0;

        try {
            const searchDoc = `${title} ${description}`;
            const aiSearchRes = await axios.post(`${PYTHON_AI_URL}/search`, {
                query: searchDoc,
                k: 3
            });
            const matches = aiSearchRes.data?.results || [];
            if (matches.length > 0) {
                topScore = matches[0].score;
                if (topScore > 0.90) {
                    isDuplicateKnowledge = true;
                    matchedId = matches[0].bug_id;
                }
            }
        } catch (e) {
            logger.warn(`Failed to query vector similarity during knowledge growth: ${e.message}`);
        }

        // 2. Threshold branch: If similarity > 90%, update existing knowledge
        if (isDuplicateKnowledge && matchedId) {
            logger.info(`Similarity score ${(topScore * 100).toFixed(1)}% exceeds 90% threshold. Updating existing knowledge ${matchedId}.`);
            
            const updatedEntry = await db.updateKnowledge(matchedId, {
                rootCause,
                fixAction,
                severity: severity || "Medium",
                priority: priority || "P3",
                category: category || "General",
                component: component || "General",
                resolutionDate: new Date()
            });

            // Update FAISS metadata
            try {
                await axios.post(`${PYTHON_AI_URL}/knowledge/update`, {
                    bug_id: matchedId,
                    updates: {
                        root_cause: rootCause,
                        resolution: fixAction,
                        severity,
                        priority
                    }
                });
            } catch (faissErr) {
                logger.warn(`Failed to update FAISS vector metadata: ${faissErr.message}`);
            }

            return res.json({
                success: true,
                action: "updated",
                bugId: matchedId,
                similarity: (topScore * 100).toFixed(1),
                message: `Semantic similarity ${(topScore * 100).toFixed(1)}% > 90%. Updated existing historical knowledge item ${matchedId}.`,
                entry: updatedEntry
            });
        }

        // 3. Otherwise, create new knowledge entry
        logger.info(`Similarity score ${(topScore * 100).toFixed(1)}% <= 90%. Creating new knowledge entry ${bugId}.`);
        
        const newKnowledge = await db.insertKnowledge({
            bugId,
            title,
            description,
            stackTrace: stackTrace || "",
            rootCause,
            fixAction,
            severity: severity || "Medium",
            priority: priority || "P3",
            category: category || "General",
            component: component || "General",
            verified: true,
            resolutionDate: new Date()
        });

        // Insert embedding into FAISS
        try {
            const indexDoc = `${title}\n${description}\n${stackTrace || ''}`;
            await axios.post(`${PYTHON_AI_URL}/index`, {
                items: [{
                    document: indexDoc,
                    metadata: {
                        bug_id: bugId,
                        project: "BugSense",
                        component: component || "General",
                        severity: severity || "Medium",
                        priority: priority || "P3",
                        description,
                        root_cause: rootCause,
                        resolution: fixAction,
                        status: "resolved",
                        source: "knowledge_base"
                    }
                }]
            });
            logger.info(`Vector embeddings indexed inside FAISS vector store for ${bugId}.`);
        } catch (idxErr) {
            logger.warn(`Failed to index knowledge embeddings in FAISS: ${idxErr.message}`);
        }

        return res.json({
            success: true,
            action: "created",
            bugId,
            similarity: (topScore * 100).toFixed(1),
            message: `New knowledge entry indexed in FAISS vector store.`,
            entry: newKnowledge
        });

    } catch (err) {
        logger.error(`Knowledge Base Growth error: ${err.message}`);
        res.status(500).json({ error: "Failed to process knowledge base entry" });
    }
});

// POST /api/knowledge/verify
router.post('/knowledge/verify', async (req, res) => {
    try {
        const { bugId, verified } = req.body;
        if (!bugId) {
            return res.status(400).json({ error: "Missing bugId" });
        }

        const updated = await db.updateKnowledge(bugId, { verified: verified !== false });
        res.json({ success: true, entry: updated });
    } catch (err) {
        logger.error(`Knowledge verification error: ${err.message}`);
        res.status(500).json({ error: "Failed to verify knowledge entry" });
    }
});

// GET /api/knowledge/history
router.get('/knowledge/history', async (req, res) => {
    try {
        const entries = await db.getKnowledge();
        res.json(entries);
    } catch (err) {
        logger.error(`Knowledge history fetch error: ${err.message}`);
        res.status(500).json({ error: "Failed to retrieve knowledge history" });
    }
});

// GET /api/knowledge/stats
router.get('/knowledge/stats', async (req, res) => {
    try {
        const entries = await db.getKnowledge();
        
        let faissRecordsCount = entries.length;
        try {
            const pythonHealth = await axios.get(`${PYTHON_AI_URL}/`);
            faissRecordsCount = pythonHealth.data?.faiss_records ?? entries.length;
        } catch (err) {
            logger.warn(`Failed to query Python AI health for FAISS count: ${err.message}`);
        }

        const total = faissRecordsCount;
        const verified = entries.filter(e => e.verified).length;
        const unverified = entries.filter(e => !e.verified).length;
        const verifiedRate = total > 0 ? Math.round((verified / total) * 100) : 100;

        res.json({
            total,
            verified,
            unverified,
            verifiedRate
        });
    } catch (err) {
        logger.error(`Knowledge stats error: ${err.message}`);
        res.status(500).json({ error: "Failed to compute knowledge stats" });
    }
});

module.exports = router;
