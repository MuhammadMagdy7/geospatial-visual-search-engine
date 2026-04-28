# from fastapi.middleware.cors import CORSMiddleware
# from ..config import settings

# def setup_cors(app):
#     app.add_middleware(
#         CORSMiddleware,
#         allow_origins=settings.CORS_ORIGINS,
#         allow_credentials=True,
#         allow_methods=["*"],
#         allow_headers=["*"],
#     )


from fastapi.middleware.cors import CORSMiddleware
from ..config import settings

def setup_cors(app):
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,  # ← استخدم property
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )