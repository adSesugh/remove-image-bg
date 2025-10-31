from fastapi import FastAPI, UploadFile, File, HTTPException, Query
from fastapi.responses import Response
from rembg import remove
import requests
import io
import boto3
import os
from starlette.concurrency import run_in_threadpool
from fastapi.middleware.cors import CORSMiddleware
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

origins = [
    os.getenv("FRONTEND_URL", "http://localhost:3000"),  # Allow your frontend to access the API
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

s3 = boto3.client(
    "s3",
    region_name=os.getenv("AWS_REGION"),
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
)

@app.get("/health")
async def health_check():
    return {"status": "ok"}

@app.post("/remove-bg")
async def remove_bg(image_url: str = Query(...), output_key: str | None = None):
    logger.info(f"Received request to remove background for image: {image_url}")
    try:
        # Fetch the image (pre-signed S3 URL)
        res = requests.get(image_url)
        logger.info(f"Fetching image from: {image_url}")
        if res.status_code != 200:
            logger.error(f"Failed to fetch image from {image_url}. Status code: {res.status_code}")
            raise HTTPException(status_code=400, detail=f"Failed to fetch image from URL: {image_url} with status code {res.status_code}")

        logger.info(f"Fetched image content size: {len(res.content)} bytes")
        logger.info(f"Fetched image content type: {res.headers.get('Content-Type')}")

        # Remove background
        input_bytes = io.BytesIO(res.content)
        output_bytes = await run_in_threadpool(remove, input_bytes.read())
        logger.info(f"Rembg output bytes size: {len(output_bytes)} bytes")

        # (Optional) Upload to S3
        # if output_key:
        #     s3.put_object(
        #         Bucket=os.getenv("AWS_BUCKET_NAME"),
        #         Key=output_key,
        #         Body=output_bytes,
        #         ContentType="image/png",
        #         ACL="public-read",
        #     )
        logger.info(f"Successfully processed image and returning response.")
        # Return processed image
        return Response(content=output_bytes, media_type="image/png")

    except requests.exceptions.RequestException as e:
        logger.error(f"Network or request error while fetching image from {image_url}: {e}", exc_info=True)
        raise HTTPException(status_code=400, detail=f"Network or request error: {e}")
    except Exception as e:
        logger.error(f"An unexpected error occurred during background removal: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))  # default 8000 for local dev
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=False)