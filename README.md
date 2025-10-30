# Background Service

This directory contains a FastAPI application that serves as a background service for image processing, specifically for removing image backgrounds.

## Features

- **Background Removal**: Utilizes the `rembg` library to remove backgrounds from images.
- **Image Fetching**: Fetches images from a provided URL (e.g., pre-signed S3 URLs).
- **S3 Integration (Optional)**: Includes commented-out code for uploading processed images to an S3 bucket.
- **Robust Error Handling**: Provides more specific and informative error messages for better debugging.
- **Comprehensive Logging**: Implements detailed logging for requests, responses, and errors.

## Endpoints

### `POST /remove-bg`

Removes the background from an image and returns the processed image.

#### Request Parameters

- `image_url` (query parameter, required): The URL of the image to process. This is typically a pre-signed URL for an image stored in S3.
- `output_key` (query parameter, optional): If provided, the processed image will be uploaded to the specified S3 key. (Currently commented out in the code).

#### Example Usage

```bash
curl -X POST "http://localhost:8090/remove-bg?image_url=YOUR_IMAGE_URL&output_key=OPTIONAL_S3_KEY"
```

#### Response

- Returns the processed image in `image/png` format.
- Returns `400 Bad Request` if the image cannot be fetched or due to network/request errors.
- Returns `500 Internal Server Error` if an unexpected error occurs during processing.

## Setup and Deployment

### Environment Variables

The following environment variables are required:

- `AWS_REGION`: The AWS region for your S3 bucket.
- `AWS_ACCESS_KEY_ID`: Your AWS access key ID.
- `AWS_SECRET_ACCESS_KEY`: Your AWS secret access key.
- `AWS_BUCKET_NAME`: The name of your S3 bucket.
- `FRONTEND_URL`: The URL of your frontend application for CORS configuration (e.g., `http://localhost:3000`).

### Local Development

1.  **Activate Virtual Environment**: 
    ```bash
    source .venv/bin/activate
    ```

2.  **Install dependencies**: 
    ```bash
    pip install -r requirements.txt
    ```

3.  **Run the application**: 
    ```bash
    uvicorn app:app --host 0.0.0.0 --port 8090
    ```

### Production Deployment

For production, it is highly recommended to use Gunicorn to manage Uvicorn workers for better performance, stability, and process management. An example command would be:

```bash
gunicorn -w 4 -k uvicorn.workers.UvicornWorker app:app --bind 0.0.0.0:8090
```

### Docker

A `Dockerfile` is provided for containerizing the application.

1.  **Build the Docker image**:
    ```bash
    docker build -t background-service .
    ```

2.  **Run the Docker container**:
    ```bash
    docker run -p 8090:8090 -e AWS_REGION=your_region -e AWS_ACCESS_KEY_ID=your_key_id -e AWS_SECRET_ACCESS_KEY=your_secret_key -e AWS_BUCKET_NAME=your_bucket_name -e FRONTEND_URL=your_frontend_url background-service
    ```

## Technologies Used

- FastAPI
- rembg
- boto3
- Uvicorn
- Gunicorn (recommended for production)