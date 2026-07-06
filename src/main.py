from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from employee.router import router as employee_router
from web.router import router as web_router
#from endpoints.messages import router as messages_router


app = FastAPI(
    title="Employees"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],  
)

app.include_router(employee_router, prefix='/api/v1')
app.include_router(web_router)

app.mount("/static", StaticFiles(directory="web/static"), name="static")

@app.get("/ping")
def ping():
    return {"result": "pong"}



if __name__ == "__main__":
    import uvicorn
    from sys import argv

    flag = ''
    if len(argv) > 1 and argv[1] == 'docker':
        uvicorn.run("main:app", host="0.0.0.0", port=80, reload=True)
    else:
        uvicorn.run("main:app", host="127.0.0.1", port=8001, reload=True)