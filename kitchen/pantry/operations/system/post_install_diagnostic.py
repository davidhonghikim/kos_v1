# kitchen/pantry/operations/system/post_install_diagnostic.py
"""
Pantry Ingredient for running post-installation diagnostics.

This ingredient checks the health of the running services after they have
been started by Docker Compose by pinging their health check endpoints.
"""
import time
import requests
from typing import Dict, List, Any

from kitchen.core.logging import get_logger

logger = get_logger(__name__)

# --- Configuration for Services ---
# In a real-world scenario, this should be loaded from a configuration file.
SERVICES_TO_CHECK = {
    "backend": "http://localhost:8000/health",
    "frontend": "http://localhost:5173",
    # Add other services and their health endpoints here
    # "database": "...", # DB checks would require a different method (e.g., trying to connect)
}

def _check_service_health(service_name: str, url: str, timeout: int = 5) -> Dict[str, Any]:
    """
    Pings a single service endpoint to check its health.

    Args:
        service_name: The name of the service being checked.
        url: The health check URL for the service.
        timeout: The timeout in seconds for the request.

    Returns:
        A dictionary containing the status of the service.
    """
    try:
        response = requests.get(url, timeout=timeout)
        if response.ok:
            logger.info(f"Health check PASSED for '{service_name}' at {url} (Status: {response.status_code})")
            return {"service": service_name, "status": "healthy", "statusCode": response.status_code}
        else:
            logger.warning(f"Health check FAILED for '{service_name}' at {url} (Status: {response.status_code})")
            return {"service": service_name, "status": "unhealthy", "statusCode": response.status_code}
    except requests.exceptions.RequestException as e:
        logger.error(f"Health check FAILED for '{service_name}' at {url}. Could not connect: {e}")
        return {"service": service_name, "status": "unreachable", "error": str(e)}


def run_checks(wait_time: int = 120, check_interval: int = 10) -> dict:
    """
    Runs health checks on all configured services, retrying until they are healthy or the wait_time expires.

    Args:
        wait_time: The total number of seconds to wait for services to become healthy.
        check_interval: The number of seconds to wait between check attempts.

    Returns:
        A dictionary with the overall diagnostic results and status of each service.
    """
    logger.info("Executing post-installation diagnostics...")
    start_time = time.time()
    end_time = start_time + wait_time
    
    healthy_services = set()
    final_results = {}

    while time.time() < end_time:
        all_healthy = True
        for service_name, url in SERVICES_TO_CHECK.items():
            if service_name in healthy_services:
                continue # Skip checks for already healthy services

            result = _check_service_health(service_name, url)
            final_results[service_name] = result

            if result["status"] == "healthy":
                healthy_services.add(service_name)
            else:
                all_healthy = False
        
        if all_healthy:
            logger.info("All services are healthy!")
            break

        if time.time() < end_time:
            logger.info(f"Not all services are healthy. Retrying in {check_interval} seconds...")
            time.sleep(check_interval)

    # Final summary
    if len(healthy_services) == len(SERVICES_TO_CHECK):
        logger.info("Diagnostics complete. All services reported as healthy.")
        return {"status": "success", "details": final_results}
    else:
        logger.error("Diagnostics complete. One or more services failed to become healthy.")
        return {"status": "failure", "details": final_results}
