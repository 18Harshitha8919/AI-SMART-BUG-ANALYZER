const winston = require('winston');
const path = require('path');
const fs = require('fs');

// Ensure logs directory exists
const logDirectory = path.join(__dirname, '../logs');
if (!fs.existsSync(logDirectory)) {
    fs.mkdirSync(logDirectory, { recursive: true });
}

const logger = winston.createLogger({
    level: 'info',
    format: winston.format.combine(
        winston.format.timestamp({ format: 'YYYY-MM-DD HH:mm:ss' }),
        winston.format.json()
    ),
    transports: [
        // Write all logs with level 'error' and below to error.log
        new winston.transports.File({ 
            filename: path.join(logDirectory, 'error.log'), 
            level: 'error' 
        }),
        // Write all logs with level 'info' and below to server.log
        new winston.transports.File({ 
            filename: path.join(logDirectory, 'server.log') 
        })
    ]
});

// If we are in development, log to the console with simpler format
if (process.env.NODE_ENV !== 'production') {
    logger.add(new winston.transports.Console({
        format: winston.format.combine(
            winston.format.colorize(),
            winston.format.printf(({ timestamp, level, message }) => {
                return `[${timestamp}] ${level}: ${message}`;
            })
        )
    }));
}

module.exports = logger;
