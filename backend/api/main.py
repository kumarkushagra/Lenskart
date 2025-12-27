from fastapi import FastAPI, HTTPException
from image import ImageAnalyzer
import json
import uvicorn

app = FastAPI()

analyzer = ImageAnalyzer()

@app.get("/analyze/{image_url:path}")
async def analyze_image(image_url: str):
    try:
        result_json = await analyzer.run(image_url)
        return json.loads(result_json)

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


if __name__ == "__main__":
    uvicorn.run("main:app",host="0.0.0.0",port=8000,reload=True,)
