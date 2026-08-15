"""Rate limiting para endpoints pblicos."""

from collections import defaultdict
from time import time

from fastapi import HTTPException, Request, status


class SimpleRateLimiter:
    """Limitador de velocidad simple basado en memoria.

    M-003-02/C-003-02/C-003-03: Rate limiting para endpoints pblicos.
    Lmite por defecto: 60 requests per minute per IP.
    """

    def __init__(
        self,
        requests_per_minute: int = 60,
    ):
        self.requests_per_minute = requests_per_minute
        self._requests: dict[str, list[float]] = defaultdict(list)

    async def __call__(self, request: Request) -> None:
        """Verificar si la solicitud excede el lmite."""
        client_ip = self._get_client_ip(request)
        now = time()
        window_start = now - 60  # Ventana de 1 minuto

        # Limpiar solicitudes antiguas
        self._requests[client_ip] = [
            req_time
            for req_time in self._requests[client_ip]
            if req_time > window_start
        ]

        if len(self._requests[client_ip]) >= self.requests_per_minute:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Lmite de solicitudes excedido. Intente nuevamente ms tarde.",
            )

        self._requests[client_ip].append(now)

    def _get_client_ip(self, request: Request) -> str:
        """Obtener la direccin IP del cliente."""
        # Verificar encabezados proxy primero
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()

        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip

        # Finalmente, usar client.host de FastAPI
        if request.client:
            return request.client.host

        return "unknown"


# Instancia global del rate limiter
public_rate_limiter = SimpleRateLimiter(requests_per_minute=60)
