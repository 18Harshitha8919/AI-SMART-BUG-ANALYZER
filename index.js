const express = require('express');
const cors = require('cors');
const path = require('path');
const db = require('./db');
const logger = require('./logger');
const bugsRouter = require('./routes/bugs');
const analyticsRouter = require('./routes/analytics');
const knowledgeRouter = require('./routes/knowledge');

const app = express();
const PORT = process.env.PORT || 5000;

// Enable CORS
app.use(cors());

// Body Parser Middleware
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Log incoming API Requests
app.use((req, res, next) => {
    logger.info(`${req.method} request received for path: ${req.url}`);
    next();
});

// Hook API Routes
app.use('/api', bugsRouter);
app.use('/api', analyticsRouter);
app.use('/api', knowledgeRouter);

// Serve uploads folder as static assets
const UPLOADS_DIR = path.join(__dirname, '../uploads');
app.use('/uploads', express.static(UPLOADS_DIR));

// Start server after database connection is initialized
async function startServer() {
    await db.connect();
    
    app.listen(PORT, () => {
        logger.info(`Express gateway server listening on port ${PORT}`);
        logger.info(`Environment: ${process.env.NODE_ENV || 'development'}`);
        logger.info(`Using database fallback: ${db.getIsFallback()}`);
    });
}

startServer();
