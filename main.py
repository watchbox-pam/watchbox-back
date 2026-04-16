from fastapi import FastAPI

# DO NOT TOUCH THE IMPORT - Jean Fourest :)
# This import avoids circular imports (i know it's weird but it works) 
# and allows to have all the models registered in the Base.metadata
import database.models.index

from api.server import initServer

app = FastAPI(title="API Watchbox",
              description="Ceci est l'API de l'application Watchbox",
              version="1.0.0")

initServer(app)
