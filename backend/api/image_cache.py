import hashlib
from typing import Optional, Dict, Any

# using supabse as DB
from supabase import create_client, Client


class ImageCache:
    def __init__(self, supabase_url: str, supabase_key: str):
        self.client: Client = create_client(supabase_url,supabase_key)

    def hash(self, image_url: str) -> str:
        
        # as of now im returning hashes og the image_url string itself.
        # TODO: Replace later with real image-content hash if needed.
        return hashlib.sha256(image_url.encode("utf-8")).hexdigest()


    def check(self, image_url: str) -> bool:
        image_hash = self.hash(image_url)

        resp = (
            self.client
            .table("image_analysis_cache")
            .select("id")
            .eq("image_hash", image_hash)
            .limit(1)
            .execute()
        )

        return bool(resp.data)

    def get(self, image_url: str) -> Optional[Dict[str, Any]]:
        # to fetch data from the DB
        image_hash = self.hash(image_url)

        resp = (
            self.client
            .table("image_analysis_cache")
            .select("result_json")
            .eq("image_hash", image_hash)
            .limit(1)
            .execute()
        )

        if not resp.data:
            return None

        return resp.data[0]["result_json"]

    def update(self, image_url: str, result_json: Dict[str, Any]) -> None:
        # If we want to re-evaluate a specific image using other models, this method is to update the previous readings
        image_hash = self.hash(image_url)

        payload = {
            "image_url": image_url,
            "image_hash": image_hash,
            "result_json": result_json,
        }

        (
            self.client
            .table("image_analysis_cache")
            .upsert(payload)
            .execute()
        )
