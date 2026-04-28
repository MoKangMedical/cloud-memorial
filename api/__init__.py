"""念念 API"""
# Lazy import to avoid circular dependencies
def get_app():
    from .main import app
    return app
