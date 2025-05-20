import time
import logging
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

# Настройка базового логгера
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware для логирования каждого запроса и времени его обработки."""
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        start_time = time.time()
        logger.info(f"Request started: {request.method} {request.url.path}")

        try:
            response = await call_next(request)
            process_time = time.time() - start_time
            response.headers["X-Process-Time"] = str(process_time) # Добавляем заголовок с временем
            logger.info(
                f"Request finished: {request.method} {request.url.path} "
                f"- Status: {response.status_code} - Duration: {process_time:.4f}s"
            )
        except Exception as e:
             process_time = time.time() - start_time
             logger.error(
                 f"Request failed: {request.method} {request.url.path} "
                 f"- Error: {e} - Duration: {process_time:.4f}s",
                 exc_info=True # Добавляем traceback в лог
             )
             # Важно перевыбросить исключение, чтобы FastAPI обработал его дальше
             raise e
        return response