import winston from 'winston';

export class Logger {
  private winston: winston.Logger;

  constructor(service: string) {
    this.winston = winston.createLogger({
      level: process.env.LOG_LEVEL || 'info',
      format: winston.format.combine(
        winston.format.timestamp(),
        winston.format.errors({ stack: true }),
        winston.format.json()
      ),
      defaultMeta: { service },
      transports: [
        new winston.transports.Console({
          format: winston.format.combine(
            winston.format.colorize(),
            winston.format.simple()
          ),
        }),
      ],
    });

    // Add file transport in production
    if (process.env.NODE_ENV === 'production') {
      this.winston.add(
        new winston.transports.File({
          filename: 'error.log',
          level: 'error',
        })
      );
      this.winston.add(
        new winston.transports.File({
          filename: 'combined.log',
        })
      );
    }
  }

  info(message: string, meta?: any): void {
    this.winston.info(message, meta);
  }

  error(message: string, error?: any): void {
    this.winston.error(message, { error: error?.message || error, stack: error?.stack });
  }

  warn(message: string, meta?: any): void {
    this.winston.warn(message, meta);
  }

  debug(message: string, meta?: any): void {
    this.winston.debug(message, meta);
  }

  metric(name: string, value: number, tags?: Record<string, string>): void {
    this.winston.info('metric', { metric: name, value, tags });
  }
}