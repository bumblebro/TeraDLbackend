# TeraBox Downloader Backend

A Flask-based backend service for generating TeraBox download links.

## Setup Instructions

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Run the Application

```bash
python flask_app.py
```

The server will start on http://localhost:5000

## API Documentation

### 1. Get API Documentation

**Endpoint:** `GET /`

**Response:**

```json
{
  "status": "success",
  "service": [
    {
      "method": "GET",
      "endpoint": "get_config",
      "url": "http://localhost:5000/get_config",
      "params": [],
      "response": ["status", "message", "mode", "cookie"]
    },
    {
      "method": "POST",
      "endpoint": "generate_file",
      "url": "http://localhost:5000/generate_file",
      "params": ["mode", "url"],
      "response": [
        "status",
        "js_token",
        "browser_id",
        "cookie",
        "sign",
        "timestamp",
        "shareid",
        "uk",
        "list"
      ]
    },
    {
      "method": "POST",
      "endpoint": "generate_link",
      "url": "http://localhost:5000/generate_link",
      "params": {
        "mode1": [
          "mode",
          "js_token",
          "cookie",
          "sign",
          "timestamp",
          "shareid",
          "uk",
          "fs_id"
        ],
        "mode2": ["mode", "url"],
        "mode3": ["mode", "shareid", "uk", "sign", "timestamp", "fs_id"]
      },
      "response": ["status", "download_link"]
    }
  ],
  "message": "hayo mau ngapain?"
}
```

### 2. Get Configuration

**Endpoint:** `GET /get_config`

**Response:**

```json
{
  "status": "success",
  "mode": 3,
  "cookie": "your_cookie_here"
}
```

### 3. Generate File Information

**Endpoint:** `POST /generate_file`

**Request Body:**

```json
{
  "url": "https://1024terabox.com/s/1eBHBOzcEI-VpUGA_xIcGQg"
}
```

**Response:**

```json
{
  "status": "success",
  "js_token": "token_value",
  "browser_id": "browser_id_value",
  "cookie": "cookie_value",
  "sign": "sign_value",
  "timestamp": "timestamp_value",
  "shareid": "shareid_value",
  "uk": "uk_value",
  "list": [
    {
      "fs_id": "file_id",
      "filename": "example.mp4",
      "size": "1024000"
    }
  ]
}
```

### 4. Generate Download Link

**Endpoint:** `POST /generate_link`

#### Mode 1 Request:

```json
{
  "mode": 1,
  "fs_id": "file_id",
  "uk": "uk_value",
  "shareid": "shareid_value",
  "timestamp": "timestamp_value",
  "sign": "sign_value",
  "js_token": "token_value",
  "cookie": "cookie_value"
}
```

#### Mode 2 Request:

```json
{
  "mode": 2,
  "url": "https://1024terabox.com/s/1eBHBOzcEI-VpUGA_xIcGQg"
}
```

#### Mode 3 Request:

```json
{
  "mode": 3,
  "shareid": "shareid_value",
  "uk": "uk_value",
  "sign": "sign_value",
  "timestamp": "timestamp_value",
  "fs_id": "file_id"
}
```

**Response (for all modes):**

```json
{
  "status": "success",
  "download_link": "https://download-link-here.com/file.mp4"
}
```

## Error Responses

All endpoints may return error responses in the following format:

```json
{
  "status": "failed",
  "message": "error message here"
}
```

Common error messages:

- "invalid params" - When required parameters are missing
- "cookie terabox nya invalid bos, coba lapor ke dapunta" - When TeraBox cookie is invalid
- "wrong payload" - When the request payload is malformed
- "gaada mode nya" - When an invalid mode is specified

## Example Usage with curl

1. Get API Documentation:

```bash
curl http://localhost:5000/
```

2. Get Configuration:

```bash
curl http://localhost:5000/get_config
```

3. Generate File Info:

```bash
curl -X POST http://localhost:5000/generate_file \
  -H "Content-Type: application/json" \
  -d '{"url": "https://1024terabox.com/s/1eBHBOzcEI-VpUGA_xIcGQg"}'
```

4. Generate Download Link (Mode 3):

```bash
curl -X POST http://localhost:5000/generate_link \
  -H "Content-Type: application/json" \
  -d '{
    "mode": 3,
    "shareid": "your_shareid",
    "uk": "your_uk",
    "sign": "your_sign",
    "timestamp": "your_timestamp",
    "fs_id": "your_fs_id"
  }'
```
