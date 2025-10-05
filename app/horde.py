import asyncio, httpx, time
from typing import Optional

HORDE_API = "https://stablehorde.net/api/v2"

class HordeClient:
    def __init__(self, api_key: Optional[str] = None):
        self.headers = {"apikey": api_key} if api_key else {}

    async def generate(self, prompt: str, steps=28, width=768, height=768, cfg_scale=7.0, sampler_name="k_euler"):
        payload = {
            "prompt": prompt,
            "params": {"steps": steps,"sampler_name": sampler_name,"cfg_scale": cfg_scale,"width": width,"height": height,"n": 1,"karras": True},
            "nsfw": False
        }
        async with httpx.AsyncClient(timeout=120) as client:
            r = await client.post(f"{HORDE_API}/generate/async", json=payload, headers=self.headers)
            r.raise_for_status()
            return r.json()["id"]

    async def wait_for_result(self, req_id: str, timeout_sec: int = 420):
        start = time.time()
        async with httpx.AsyncClient(timeout=120) as client:
            while True:
                r = await client.get(f"{HORDE_API}/generate/check/{req_id}", headers=self.headers)
                r.raise_for_status()
                if r.json().get("done"):
                    rr = await client.get(f"{HORDE_API}/generate/status/{req_id}", headers=self.headers)
                    rr.raise_for_status()
                    return rr.json()
                if time.time() - start > timeout_sec:
                    raise TimeoutError("Генерация заняла слишком долго")
                await asyncio.sleep(2)
