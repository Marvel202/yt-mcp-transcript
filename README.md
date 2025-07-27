# 🎬 YouTube Transcript MCP Server

A comprehensive YouTube transcript extraction tool that provides three different interfaces:

1. **🤖 Model Context Protocol (MCP) Server** - For AI assistants and tools
2. **⚡ FastAPI HTTP Server** - For automation tools like n8n
3. **🌐 Gradio Web Interface** - For easy browser-based access

## ✨ Features

- 📺 Extract transcripts from YouTube videos using video IDs or URLs
- 🌍 Support for multiple subtitle languages
- 💾 Automatic file saving with timestamps
- 🔄 Multiple interface options for different use cases
- 🛡️ Robust error handling and validation

## 📦 Installation

### 🔧 Prerequisites

- 🐍 Python 3.8+
- 📦 uv package manager (recommended) or pip

### 🚀 Using uv (recommended)

```bash
# Clone the repository
git clone https://github.com/Marvel202/yt-mcp-transcript.git
cd yt-mcp-transcript

# Create virtual environment and install dependencies
uv sync
```

### 🐍 Using pip

```bash
# Clone the repository
git clone https://github.com/Marvel202/yt-mcp-transcript.git
cd yt-mcp-transcript

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -e .
```

## 🚀 Usage

### 1. 🤖 MCP Server Mode (for AI Assistants)

#### VS Code MCP Integration

To use with VS Code MCP, update your `mcp.json` configuration file:

```json
{
  "servers": {
    "youtube": {
      "type": "stdio",
      "command": "uv",
      "args": [
        "run",
        "--directory",
        "/path/to/your/yt-mcp-transcript",
        "python", 
        "src/mcp_youtube.py"
      ]
    }
  }
}
```

> 💡 **Note**: Replace `/path/to/your/yt-mcp-transcript` with your actual project directory path.

#### Manual MCP Server Start

Start the MCP server manually:

```bash
# With uv
uv run python src/mcp_youtube.py --mode mcp

# With pip
python src/mcp_youtube.py --mode mcp
```

#### 🛠️ Available MCP Tools

- 📝 `get_transcript` - Extract transcript from a YouTube video
- 💾 `save_transcript_to_file` - Save transcript to a file with timestamp

### 2. ⚡ FastAPI HTTP Server Mode (for n8n and automation)

Start the HTTP server on port 8080 with 60-second timeout:

```bash
# 🚀 With uv
uv run python src/mcp_youtube.py --mode fastapi

# 🐍 With pip
python src/mcp_youtube.py --mode fastapi
```

#### 🌐 Available HTTP Endpoints

**📥 GET /transcript/{video_id}**

- 📝 Extract transcript by video ID
- 💡 Example: `GET http://localhost:8080/transcript/pebgrFQ-C7M`

**📮 POST /transcript**

- 📝 Extract transcript from URL or video ID
- 📋 Request body: `{"video_url": "https://youtube.com/watch?v=pebgrFQ-C7M"}` or `{"video_id": "pebgrFQ-C7M"}`

**💾 POST /transcript/save**

- 💾 Extract and save transcript to file
- 📋 Request body: `{"video_url": "https://youtube.com/watch?v=pebgrFQ-C7M", "filename": "my_transcript.txt"}`

**🏥 GET /health**

- ✅ Server health check

#### 🔧 Example with curl

```bash
# 📥 Get transcript by video ID
curl http://localhost:8080/transcript/pebgrFQ-C7M

# 📮 Get transcript from URL
curl -X POST http://localhost:8080/transcript \
  -H "Content-Type: application/json" \
  -d '{"video_url": "https://youtube.com/watch?v=pebgrFQ-C7M"}'

# 💾 Save transcript to file
curl -X POST http://localhost:8080/transcript/save \
  -H "Content-Type: application/json" \
  -d '{"video_url": "https://youtube.com/watch?v=pebgrFQ-C7M", "filename": "study_session.txt"}'
```

### 3. 🌐 Gradio Web Interface (Browser-based)

Start the web interface:

```bash
# 🚀 First, start the FastAPI server in one terminal
uv run python src/mcp_youtube.py --mode fastapi

# 🌐 Then start the Gradio interface in another terminal
uv run python gradio_interface.py
```

🌐 Open your browser to `http://localhost:7860` to use the web interface.

## ⚙️ Configuration

### 🔗 Configuration for n8n

When using with **n8n** (especially in Docker), configure the HTTP Request node:

#### 💾 For saving transcripts to local directory:
- **Method**: `POST`
- **URL**: `http://host.docker.internal:8080/transcript/save`
- **Body**: JSON with `{"video_url": "YOUR_YOUTUBE_URL", "filename": "optional_filename.txt"}`
- **Timeout**: `60000ms` (60 seconds)

#### 📝 For transcript extraction only (no save):
- **Method**: `POST`
- **URL**: `http://host.docker.internal:8080/transcript`
- **Body**: JSON with `{"video_url": "YOUR_YOUTUBE_URL"}`
- **Timeout**: `60000ms` (60 seconds)

> 💡 **Note**: Use `host.docker.internal` when n8n is running in Docker to access your local server.

### 🎬 Supported YouTube URL Formats

- 📺 `https://www.youtube.com/watch?v=VIDEO_ID`
- 🔗 `https://youtu.be/VIDEO_ID`
- 📱 `https://m.youtube.com/watch?v=VIDEO_ID`
- 🎯 Just the video ID: `VIDEO_ID`

## 📁 File Structure

```bash
yt-mcp-transcript/
├── src/
│   ├── __init__.py
│   └── mcp_youtube.py          # 🚀 Main server application
├── gradio_interface.py         # 🌐 Web interface
├── transcript/                 # 📁 Saved transcripts directory
├── pyproject.toml             # ⚙️ Project configuration
├── README.md                  # 📖 This file
└── test_transcript_saving.py  # 🧪 Test script
```

## 📤 API Response Format

All endpoints return JSON responses:

**✅ Success Response:**

```json
{
  "success": true,
  "video_id": "pebgrFQ-C7M",
  "transcript": "Hello everyone\nWelcome to this video...",
  "language": "en",
  "with_timestamps": false
}
```

**❌ Error Response:**

```json
{
  "success": false,
  "error": "No transcript found for this video",
  "video_id": "invalid_id"
}
```

## 🛡️ Error Handling

The server handles various error conditions:

- 🚫 Invalid video IDs or URLs
- 📵 Videos without available transcripts
- 🌐 Network connectivity issues
- ⏱️ Server timeouts (60-second limit for FastAPI mode)

## 🧪 Testing

Test the transcript extraction:

```bash
# 🧪 Test with the target video
uv run python test_transcript_saving.py
```

## 🔧 Development

### 🚀 Running in Development Mode

```bash
# 🤖 MCP mode with auto-reload
uv run python src/mcp_youtube.py --mode mcp

# ⚡ FastAPI mode with auto-reload
uv run python src/mcp_youtube.py --mode fastapi --reload
```

### 📦 Dependencies

- 🤖 `fastmcp>=1.12.2` - MCP server framework
- 📺 `youtube-transcript-api>=1.2.1` - YouTube transcript extraction
- ⚡ `fastapi>=0.116.1` - HTTP API framework
- 🚀 `uvicorn>=0.25.0` - ASGI server
- 🌐 `gradio>=5.38.2` - Web interface framework
- 📋 `pydantic>=2.0.0` - Data validation

## 📄 License

MIT License - see LICENSE file for details.

## 🤝 Contributing

1. 🍴 Fork the repository
2. 🌿 Create a feature branch
3. ✨ Make your changes
4. 🧪 Add tests if applicable
5. 📤 Submit a pull request

## 🆘 Support

For issues or questions:

1. 📋 Check the GitHub Issues page
2. 🐛 Create a new issue with detailed information
3. 📝 Include error messages and steps to reproduce

---

**🎯 Target Video for Testing**: `pebgrFQ-C7M` (2-Hour Study Session with Calm Jazz)
