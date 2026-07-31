import asyncio
from aiohttp import web
import json
import logging
import os

logger = logging.getLogger("passivbot.status")

async def _status_app_factory(bot, token=None):
    app = web.Application()

    async def health(request):
        return web.json_response({"status": "ok"})

    async def status(request):
        # optional token protection
        if token:
            auth = request.headers.get("Authorization", "")
            if not auth.startswith("Bearer ") or auth.split(" ", 1)[1] != token:
                return web.json_response({"error": "unauthorized"}, status=401)
        try:
            st = bot.get_status()
            return web.Response(text=json.dumps(st, default=str), content_type="application/json")
        except Exception as e:
            logger.exception("failed to build status response")
            return web.json_response({"error": str(e)}, status=500)

    app.add_routes([web.get("/health", health), web.get("/status", status)])
    return app


async def start_status_server(bot, host="0.0.0.0", port=8080):
    """
    Start the aiohttp status server. Returns the AppRunner so caller can cleanup later.
    Honors STATUS_TOKEN env var for optional bearer token protection.
    """
    token = os.environ.get("STATUS_TOKEN")
    app = await _status_app_factory(bot, token=token)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, host, port)
    await site.start()
    logger.info(f"Status server started on http://{host}:{port} (token_protected={bool(token)})")
    return runner
