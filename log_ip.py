import urllib.request
import logging
import threading
import os
import time

logger = logging.getLogger("passivbot")


def _fetch_public_ip(timeout=5):
    with urllib.request.urlopen("https://api.ipify.org", timeout=timeout) as resp:
        return resp.read().decode("utf-8").strip()


def log_current_ip_async(retries=3, timeout=5, backoff=2.0):
    """
    Fetch the public IP and log it to the configured logger without blocking startup.

    - Runs in a background daemon thread so it won't delay bot startup.
    - Can be disabled by setting env DISABLE_LOG_IP=1 or true.
    """
    if os.environ.get("DISABLE_LOG_IP", "") in ("1", "true", "True"):
        logger.debug("log_current_ip_async: disabled via DISABLE_LOG_IP")
        return

    def _worker():
        attempt = 0
        while attempt < retries:
            try:
                ip = _fetch_public_ip(timeout=timeout)
                sep = "=" * 50
                logger.info("\n%s\n🌐 [RAILWAY OUTBOUND IP] Current IP Address: %s\n%s\n", sep, ip, sep)
                return
            except Exception as e:
                attempt += 1
                logger.warning("⚠️ [RAILWAY OUTBOUND IP] Attempt %d/%d failed: %s", attempt, retries, e)
                if attempt < retries:
                    time.sleep(backoff * attempt)
        logger.error("⚠️ [RAILWAY OUTBOUND IP] Could not fetch IP after %d attempts", retries)

    thread = threading.Thread(target=_worker, daemon=True)
    thread.start()
    return thread
