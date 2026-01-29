import logging
import sys
from pathlib import Path


def setupLogger(
    name: str = "carmResearchAgent",
    logLevel: str = "INFO",
    logFile: str = None
) -> logging.Logger:
    """
    Set up and configure logger.
    
    Args:
        name: Logger name
        logLevel: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        logFile: Optional log file path
    
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, logLevel.upper()))
    
    if logger.handlers:
        return logger
    
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    consoleHandler = logging.StreamHandler(sys.stdout)
    consoleHandler.setFormatter(formatter)
    logger.addHandler(consoleHandler)
    
    if logFile:
        logPath = Path(logFile)
        logPath.parent.mkdir(parents=True, exist_ok=True)
        fileHandler = logging.FileHandler(logFile)
        fileHandler.setFormatter(formatter)
        logger.addHandler(fileHandler)
    
    return logger


def getLogger(name: str = "carmResearchAgent") -> logging.Logger:
    """Get existing logger or create new one."""
    return logging.getLogger(name)
