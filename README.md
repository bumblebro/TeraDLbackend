# TeraBox Downloader Backend

A Flask-based backend service for generating TeraBox download links. This service supports multiple TeraBox domains including terafileshare.com and 1024terabox.com.

## Setup Instructions

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Run the Application

```bash
python flask_app.py
```

The server will start on http://localhost:5001

## API Documentation

### 1. Get API Documentation

**Endpoint:** `GET /`

**Example Request:**

```bash
curl http://localhost:5001/
```

**Example Response:**

```json
{
  "status": "success",
  "service": [
    {
      "method": "GET",
      "endpoint": "get_config",
      "url": "http://localhost:5001/get_config",
      "params": [],
      "response": ["status", "message", "mode", "cookie"]
    },
    {
      "method": "POST",
      "endpoint": "generate_file",
      "url": "http://localhost:5001/generate_file",
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
      "url": "http://localhost:5001/generate_link",
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

**Example Request:**

```bash
curl http://localhost:5001/get_config
```

**Example Response:**

```json
{
  "status": "failed",
  "message": "cookie terabox nya invalid bos, coba lapor ke dapunta",
  "mode": 3,
  "cookie": ""
}
```

### 3. Generate File Information

**Endpoint:** `POST /generate_file`

**Example Request (Mode 2):**

```bash
curl -X POST http://localhost:5001/generate_file \
  -H "Content-Type: application/json" \
  -d '{
    "mode": 2,
    "url": "https://terafileshare.com/s/1uVe07OW5vkEVTUKgVkyjww"
  }'
```

**Example Response:**

```json
{
  "status": "failed",
  "sign": "",
  "timestamp": "",
  "shareid": 49259310344,
  "uk": 4400978743807,
  "list": [
    {
      "is_dir": "0",
      "path": "/2025-05-05 00-51/VID_20210107_233012_526.mp4",
      "fs_id": "663178273307094",
      "name": "VID_20210107_233012_526.mp4",
      "type": "video",
      "size": "2443335",
      "image": "https://data.terabox.com/thumbnail/539313443ef90d8292c150bf660e828d?fid=4400978743807-250528-663178273307094&time=1746637200&rt=pr&sign=FDTAER-DCb740ccc5511e5e8fedcff06b081203-54iiX4X0B0qCZQeXrNll7sSKRdg%3D&expires=10y&chkv=0&chkbd=0&chkpc=&dp-logid=8711641749122832536&dp-callid=0&size=c850_u580&quality=100&vuk=4400978743807&ft=video",
      "list": []
    }
  ]
}
```

### 4. Generate Download Link

**Endpoint:** `POST /generate_link`

**Example Request (Mode 3):**

```bash
curl -X POST http://localhost:5001/generate_link \
  -H "Content-Type: application/json" \
  -d '{
    "mode": 3,
    "shareid": 49259310344,
    "uk": 4400978743807,
    "sign": "",
    "timestamp": "",
    "fs_id": "663178273307094"
  }'
```

**Example Response:**

```json
{
  "status": "failed",
  "download_link": {}
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

- "cookie terabox nya invalid bos, coba lapor ke dapunta" - When TeraBox cookie is invalid
- "wrong payload" - When the request payload is malformed
- "gaada mode nya" - When an invalid mode is specified

## File Information Response Fields

When generating file information, the response includes:

- `fs_id`: File ID (e.g., "663178273307094")
- `name`: File name (e.g., "VID_20210107_233012_526.mp4")
- `type`: File type (e.g., "video")
- `size`: File size in bytes (e.g., "2443335")
- `shareid`: Share ID (e.g., 49259310344)
- `uk`: User ID (e.g., 4400978743807)
- `path`: File path (e.g., "/2025-05-05 00-51/VID_20210107_233012_526.mp4")

## Notes

1. The API supports multiple modes for both file generation and link generation
2. Mode 2 is recommended for direct URL processing
3. Authentication is required for generating download links
4. The service supports various TeraBox domains including:
   - terafileshare.com
   - 1024terabox.com
   - dm.terabox.com
