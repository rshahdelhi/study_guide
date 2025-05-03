from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
import httpx
import uvicorn

app = FastAPI()

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

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)