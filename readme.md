# YouTube MCP Server

A Model Context Protocol server that allows you to download subtitles from YouTube and connect them to a LLM. Also provides a FastAPI HTTP server for integration with external tools like n8n, and a user-friendly Gradio web interface.

## Features

- Download transcripts from YouTube videos
- Support for both video IDs and full YouTube URLs
- Timestamps included in transcript
- Save transcripts to text files
- Works with any MCP-compatible client
- **FastAPI HTTP server for external integrations**
- **REST API endpoints for automation tools**
- **Gradio web interface for easy access**
- **Automatic file management and listing**

## Usage

### Option 1: MCP Server Mode

#### In your MCP client configuration:

```json
"servers": {
    "youtube": {
		"type": "stdio",
		"command": "uv",
		"args": [
			"run",
			"--directory",
			"/Users/ritakoon/Desktop/PlayList/yt-mcp-transcript",
			"python", "src/mcp_youtube.py"]
		},
}
```

### Option 2: FastAPI HTTP Server Mode

#### Start the FastAPI server:

```bash
# Navigate to project directory
cd /Users/ritakoon/Desktop/PlayList/yt-mcp-transcript

# Start FastAPI server on port 8080 (default)
uv run python src/mcp_youtube.py --mode fastapi --port 8080

# Or specify custom host and port
uv run python src/mcp_youtube.py --mode fastapi --host 0.0.0.0 --port 8080
```

The server will start with:
- **Base URL**: `http://localhost:8080`
- **API Documentation**: `http://localhost:8080/docs` (Swagger UI)
- **Timeout settings**: 60 seconds for keep-alive and graceful shutdown

#### API Endpoints:

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Root endpoint with API information |
| GET | `/health` | Health check endpoint |
| POST | `/transcript` | Get transcript for a YouTube video |
| POST | `/transcript/save` | Get transcript and save to file |

#### API Usage Examples:

**1. Get transcript with timestamps:**
```bash
curl -X POST "http://localhost:8080/transcript" \
-H "Content-Type: application/json" \
-d '{
  "video_id": "pebgrFQ-C7M",
  "with_timestamps": true,
  "language": "en"
}'
```

**2. Get transcript using video URL:**
```bash
curl -X POST "http://localhost:8080/transcript" \
-H "Content-Type: application/json" \
-d '{
  "video_url": "https://www.youtube.com/watch?v=pebgrFQ-C7M",
  "with_timestamps": false,
  "language": "en"
}'
```

**3. Save transcript to file:**
```bash
curl -X POST "http://localhost:8080/transcript/save" \
-H "Content-Type: application/json" \
-d '{
  "video_id": "pebgrFQ-C7M",
  "with_timestamps": true,
  "language": "en"
}'
```

#### Request Body Schema:

```json
{
  "video_id": "string (optional)",
  "video_url": "string (optional)",
  "with_timestamps": "boolean (default: false)",
  "language": "string (default: 'en')"
}
```

**Note**: Either `video_id` or `video_url` must be provided.

#### Response Schema:

```json
{
  "success": "boolean",
  "transcript": "string (if success)",
  "error": "string (if error)",
  "video_id": "string",
  "language": "string",
  "with_timestamps": "boolean"
}
```

### n8n Integration

For n8n HTTP Request node configuration:

1. **Method**: POST
2. **URL**: `http://localhost:8080/transcript`
3. **Headers**: 
   - `Content-Type`: `application/json`
4. **Body** (JSON):
   ```json
   {
     "video_url": "{{$json.video_url}}",
     "with_timestamps": true,
     "language": "en"
   }
   ```
5. **Timeout**: 60000ms (60 seconds) - recommended for longer videos

### Option 3: Gradio Web Interface

For users who prefer a graphical interface, we provide a comprehensive web-based UI built with Gradio.

#### Starting the Gradio Interface:

1. **First, start the FastAPI server** (required for the interface to work):
```bash
uv run python src/mcp_youtube.py --mode fastapi --port 8080
```

2. **Then start the Gradio interface** (in a new terminal):
```bash
python3 gradio_interface.py
```

The Gradio interface will be available at: **http://localhost:7860**

#### Gradio Interface Features:

- 🎬 **Easy video input**: Enter YouTube URLs or video IDs
- ⚙️ **Configuration options**: Timestamps, language selection, file saving
- 📊 **Server status monitoring**: Real-time FastAPI server health checks
- 📁 **File management**: List and view saved transcript files
- 🎯 **Example videos**: Pre-loaded examples for quick testing
- 🔄 **Auto-refresh**: Automatic file list updates when saving
- 📋 **Copy-to-clipboard**: Easy transcript copying
- 🆘 **Built-in help**: Troubleshooting guide and API documentation

#### Interface Sections:

1. **Input Panel**: Video ID/URL input with options
2. **Server Status**: Real-time monitoring of FastAPI server
3. **File Management**: Browse and list saved transcripts
4. **Output Panel**: Display transcripts with copy functionality
5. **Examples**: Quick-start examples
6. **Documentation**: API endpoints and troubleshooting

#### Usage Workflow:

1. Start FastAPI server on port 8080
2. Launch Gradio interface on port 7860
3. Enter YouTube video ID or URL
4. Configure options (timestamps, language, save to file)
5. Click "Get Transcript" or check "Save to File"
6. View results and manage saved files

## Development

1. Clone the repository

2. Create and activate virtual environment using uv:
```bash
uv venv
source .venv/bin/activate  # On Unix/MacOS
# or .venv\Scripts\activate  # On Windows
```

3. Install dependencies:
```bash
uv sync
```

4. Run the server:

**MCP Mode:**
```bash
uv run python src/mcp_youtube.py
```

**FastAPI Mode:**
```bash
uv run python src/mcp_youtube.py --mode fastapi --port 8080
```

## File Structure

```
yt-mcp-transcript/
├── transcript/                 # Generated transcript files
│   ├── {video_id}_{lang}_with_timestamps.txt
│   └── {video_id}_{lang}_no_timestamps.txt
├── src/
│   └── mcp_youtube.py         # Main application (MCP + FastAPI server)
├── gradio_interface.py        # Web interface using Gradio
├── test_transcript_saving.py  # Test script for verification
├── pyproject.toml             # Dependencies and project config
├── uv.lock                    # Lock file for dependencies
└── readme.md                  # This file
```

## Dependencies

- **mcp**: Model Context Protocol server framework
- **pydantic**: Data validation
- **youtube-transcript-api**: YouTube transcript extraction
- **fastapi**: HTTP API framework
- **uvicorn**: ASGI server
- **gradio**: Web interface framework
- **requests**: HTTP client for API calls

## Quick Start

1. **Install dependencies**:
   ```bash
   uv sync
   ```

2. **Start FastAPI server** (required for Gradio interface):
   ```bash
   uv run python src/mcp_youtube.py --mode fastapi --port 8080
   ```

3. **Start Gradio interface** (in new terminal):
   ```bash
   python3 gradio_interface.py
   ```

4. **Access the web interface**: <http://localhost:7860>

5. **Test with example video**: Use video ID `pebgrFQ-C7M` or any YouTube URL

## License

MIT