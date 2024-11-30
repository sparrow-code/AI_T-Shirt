from fastapi.staticfiles import StaticFiles
class CORSStaticFiles(StaticFiles):
    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            async def wrapped_send(message):
                if message["type"] == "http.response.start":
                    message["headers"].extend([
                        (b"access-control-allow-origin", b"*"),
                        (b"access-control-allow-methods", b"GET, OPTIONS"),
                        (b"access-control-allow-headers", b"*"),
                        (b"access-control-expose-headers", b"*"),
                        (b"cache-control", b"no-cache"),
                        (b"vary", b"origin"),
                    ])
                await send(message)
            return await super().__call__(scope, receive, wrapped_send)
        return await super().__call__(scope, receive, send)
