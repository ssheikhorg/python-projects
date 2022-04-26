#! /usr/bin/env python3.10

import uvicorn
from server.app.settings.config import settings


if __name__ == "__main__":
    uvicorn.run(
        "server.app.app:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug_mode
    )
