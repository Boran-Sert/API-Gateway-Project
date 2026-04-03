import logging
import json
import os
from logging.handlers import RotatingFileHandler

class JsonFormatter(logging.Formatter):
    """
    Log kayıtlarını JSON formatına dönüştüren özel bir formatter.
    Belirtilen alanları (timestamp, service_name, log_level, message) ve
    ekstra olarak geçirilen tüm alanları JSON çıktısına dahil eder.
    """
    def format(self, record):
        log_record = {
            "timestamp": self.formatTime(record, self.datefmt),
            "service_name": getattr(record, "service_name", "unknown_service"),
            "log_level": record.levelname,
            "message": record.getMessage(),
        }

        # record.__dict__ içindeki tüm ekstra alanları JSON çıktısına ekle
        # Standart logging.LogRecord alanlarını hariç tutarız.
        for key, value in record.__dict__.items():
            if key not in log_record and not key.startswith('_') and key not in [
                'name', 'levelname', 'pathname', 'lineno', 'funcName', 'created',
                'msecs', 'relativeCreated', 'thread', 'threadName', 'processName',
                'process', 'exc_info', 'exc_text', 'stack_info', 'filename',
                'module', 'msg', 'args', 'asctime', 'levelno'
            ]:
                log_record[key] = value

        # Exception bilgilerini JSON çıktısına ekle
        if record.exc_info:
            log_record["exc_info"] = self.formatException(record.exc_info)
        if record.stack_info:
            log_record["stack_info"] = self.formatStack(record.stack_info)

        return json.dumps(log_record)

def setup_logging(service_name: str, log_level: str = "INFO"):
    """
    Belirtilen servis adı için yapılandırılmış bir logger döndürür.
    Loglar hem konsola hem de servise özel bir dosyaya JSON formatında yazılır.
    """
    logger = logging.getLogger(service_name)
    logger.setLevel(log_level)

    # Logger'ın birden fazla kez yapılandırılmasını önlemek için kontrol
    if not logger.handlers:
        # Konsol handler'ı
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(JsonFormatter())
        logger.addHandler(console_handler)

        # Dosya handler'ı (RotatingFileHandler ile log dosyası boyutu yönetimi)
        log_dir = "logs"
        os.makedirs(log_dir, exist_ok=True) # logs dizinini oluştur
        file_handler = RotatingFileHandler(os.path.join(log_dir, f"{service_name}.log"), maxBytes=10 * 1024 * 1024, backupCount=5) # 10MB, 5 yedek
        file_handler.setFormatter(JsonFormatter())
        logger.addHandler(file_handler)

    # LoggerAdapter kullanarak her log kaydına varsayılan olarak service_name ekler
    return logging.LoggerAdapter(logger, {"service_name": service_name})