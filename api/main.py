"""
念念 - FastAPI 应用入口
模块化版本：路由分拆到 routers/ 目录
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path

# Import helpers (all shared code)
from .app_helpers import init_db

# Import routers
from .routers import auth, admin, lovedones, media, chat, memorial, billing, proactive, memorial_services, voice_clone

app = FastAPI(
    title="念念 API",
    description="AI思念亲人平台 - 念念不忘，ta一直在",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all routers (with deduplication)
_routers = [
    auth.router, admin.router, lovedones.router, media.router,
    chat.router, memorial.router, billing.router, proactive.router,
    memorial_services.router, voice_clone.router
]
_seen_routes = set()
for _r in _routers:
    # Filter out duplicate routes
    _filtered = []
    for _route in _r.routes:
        if hasattr(_route, 'methods'):
            for _m in _route.methods:
                if _m not in ('HEAD', 'OPTIONS'):
                    _key = f"{_m} {_route.path}"
                    if _key not in _seen_routes:
                        _seen_routes.add(_key)
                        _filtered.append(_route)
                        break
        else:
            _filtered.append(_route)
    _r.routes = _filtered
    app.include_router(_r)

# Mount static files
BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"
ASSETS_DIR = FRONTEND_DIR / "assets"
DATA_DIR = BASE_DIR / "memorial_data" / "media"

# Serve frontend assets (photos, videos, etc.)
if ASSETS_DIR.exists():
    app.mount("/assets", StaticFiles(directory=str(ASSETS_DIR)), name="assets")

# Serve uploaded media files
DATA_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/media", StaticFiles(directory=str(DATA_DIR)), name="media")

# Serve frontend CSS and JS
CSS_DIR = FRONTEND_DIR / "css"
JS_DIR = FRONTEND_DIR / "js"
if CSS_DIR.exists():
    app.mount("/css", StaticFiles(directory=str(CSS_DIR)), name="css")
if JS_DIR.exists():
    app.mount("/js", StaticFiles(directory=str(JS_DIR)), name="js")

@app.on_event("startup")
async def startup_event():
    init_db()
    try:
        from .proactive import proactive_worker_loop
        import threading
        t = threading.Thread(target=proactive_worker_loop, daemon=True)
        t.start()
    except Exception:
        pass
