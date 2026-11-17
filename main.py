from fastapi import FastAPI

from api.server import initServer, lifespan

app = FastAPI(title="API Watchbox",
              description="Ceci est l'API de l'application Watchbox",
              version="1.0.0",
              lifespan=lifespan)

initServer(app)
