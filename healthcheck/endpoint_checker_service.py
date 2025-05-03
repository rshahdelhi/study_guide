import win32serviceutil
import win32service
import win32event
import servicemanager  # Optional, but we will avoid using it
import logging
import socket
import threading
import uvicorn
from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
import httpx

app = FastAPI()
HOST = "0.0.0.0"
PORT = 8000

# Create logging to a file
logging.basicConfig(
    filename="service.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

@app.get("/check")
async def check_endpoint(url: str = Query(..., description="The URL to check")):
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(url)
            if response.status_code == 200:
                return JSONResponse(content={"status": "up"})
            else:
                return JSONResponse(content={"status": "down", "code": response.status_code})
    except Exception as e:
        return JSONResponse(content={"status": "down", "error": str(e)})

class EndpointCheckerService(win32serviceutil.ServiceFramework):
    _svc_name_ = "EndpointCheckerService"
    _svc_display_name_ = "HTTP Endpoint Checker Service"
    _svc_description_ = "Runs a FastAPI HTTP server to check health of other endpoints."

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        socket.setdefaulttimeout(60)
        self.server_thread = None

    def SvcStop(self):
        logging.info("Service stopping...")
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)
        # Uvicorn does not expose stop cleanly in threading, so we rely on manual kill or restart
        logging.info("Service stopped.")

    def SvcDoRun(self):
        logging.info("Service is starting...")
        self.server_thread = threading.Thread(
            target=uvicorn.run,
            kwargs={
                "app": app,
                "host": HOST,
                "port": PORT,
                "log_level": "info"
            }
        )
        self.server_thread.start()
        win32event.WaitForSingleObject(self.hWaitStop, win32event.INFINITE)

if __name__ == '__main__':
    win32serviceutil.HandleCommandLine(EndpointCheckerService)
