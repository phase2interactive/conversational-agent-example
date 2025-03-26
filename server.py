import os
import modal
from dotenv import load_dotenv

load_dotenv()
app = modal.App(name="conversational-agent")

image = (modal.Image
         .debian_slim(python_version="3.12")
         .pip_install_from_requirements("requirements.txt")
         .apt_install()
         .add_local_python_source(
             "graphs"
         ).add_local_file(
           "router.py",
           "/root/router.py"
         ))

@app.cls(
    image=image,
    container_idle_timeout=900,
    allow_concurrent_inputs=100,
    keep_warm=1,
    secrets=[modal.Secret.from_name("conversational-agent-secrets")]
)
class ConversationalAgent:
    @modal.asgi_app()
    def fastapi_app(self):
        from fastapi import FastAPI
        from router import router
        from fastapi.middleware.cors import CORSMiddleware

        web_app = FastAPI()

        # Add CORS middleware
        web_app.add_middleware(
            CORSMiddleware,
            allow_origins=[],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        web_app.include_router(router)
        return web_app
