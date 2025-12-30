from fastapi import FastAPI, HTTPException
from image import ImageAnalyzer
from image_cache import ImageCache
import json
import os
import uvicorn

from dotenv import load_dotenv
load_dotenv()
# these are the env variables for supabase (CAN BE COMMITTED AS THEY ARE PUBLIC)
# im pushing only the publishable key, not the secret key
cache = ImageCache(supabase_url=os.getenv("SUPABASE_URL","https://lnchdddfspjufmpbxoui.supabase.co"),supabase_key=os.getenv("SUPABASE_KEY","sb_publishable_fuWRuUs0RoyO63TMCCiwiA_-ifl9PHa"))

analyzer = ImageAnalyzer()
app = FastAPI()

@app.get("/analyze/{image_url:path}")
async def analyze_image(image_url: str):
    try:
        if cache.check(image_url):
            cached_result = cache.get(image_url)
            if cached_result is not None:
                return cached_result

        result_json_str = await analyzer.run(image_url)
        result = json.loads(result_json_str)

        if isinstance(result, dict) and "visual_dimensions" in result:
            cache.update(image_url, result)

        return result

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
