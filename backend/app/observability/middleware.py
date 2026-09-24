"""FastAPI middleware for Prometheus metrics."""
import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.routing import Match
from app.observability.metrics import (
    API_REQUESTS,
    API_DURATION,
    API_ERRORS,
    API_ACTIVE_REQUESTS,
)

class PrometheusMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Exclude metrics endpoint to avoid noise
        if request.url.path == "/metrics":
            return await call_next(request)

        # Normalize the path template (e.g. /api/v1/training/runs/{run_id})
        route_template = request.url.path
        try:
            if "route" in request.scope:
                route = request.scope["route"]
                route_template = route.path
            else:
                for route in request.app.routes:
                    match, scope = route.matches(request.scope)
                    if match == Match.FULL:
                        route_template = route.path
                        break
        except AttributeError:
            pass

        method = request.method
        
        API_ACTIVE_REQUESTS.labels(method=method, route=route_template).inc()
        start_time = time.time()
        status_code = 500

        try:
            response = await call_next(request)
            status_code = response.status_code
            return response
        except Exception as e:
            status_code = 500
            raise e
        finally:
            duration = time.time() - start_time
            API_ACTIVE_REQUESTS.labels(method=method, route=route_template).dec()
            
            # Record total and duration
            API_REQUESTS.labels(method=method, route=route_template, status_code=status_code).inc()
            API_DURATION.labels(method=method, route=route_template, status_code=status_code).observe(duration)
            
            if status_code >= 400:
                API_ERRORS.labels(method=method, route=route_template, status_code=status_code).inc()
