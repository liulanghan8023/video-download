from fastapi import FastAPI, Request
from pydantic import BaseModel
from typing import List
import uvicorn

from crawlers.download import download_file

app = FastAPI()


class CrawlRequest(BaseModel):
    base_path: str
    product: str
    urls: List[str]


@app.put("/download")
async def crawl(request: CrawlRequest):
    for url in request.urls:
        result = await download_file(request.base_path, request.product, url=url)
        if result['code'] != 200:
            return result
    return {
        "code": 200,
        "msg": "",
    }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
