from fastapi import FastAPI
from routes.events import router as router_events
from routes.users import router as router_users

app=FastAPI()
app.include_router(router_events)
app.include_router(router_users)

