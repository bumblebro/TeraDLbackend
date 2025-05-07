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

## API Endpoints

1. `GET /` - Get API documentation
2. `GET /get_config` - Get current configuration
3. `POST /generate_file` - Generate file information
   - Required parameters: `url`
4. `POST /generate_link` - Generate download link
   - Required parameters vary by mode:
     - Mode 1: `fs_id`, `uk`, `shareid`, `timestamp`, `sign`, `js_token`, `cookie`
     - Mode 2: `url`
     - Mode 3: `shareid`, `uk`, `sign`, `timestamp`, `fs_id`
