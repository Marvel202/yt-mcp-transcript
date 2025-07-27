import mcp.types as types
from mcp.server.fastmcp import FastMCP

from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import NoTranscriptFound
from youtube_transcript_api._transcripts import Transcript
from urllib.parse import urlparse, parse_qs
import pydantic
import os
from pathlib import Path
from datetime import datetime
import argparse
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse

# Create server instances
server = FastMCP("youtube-transcript")
app = FastAPI(title="YouTube Transcript API", description="Extract transcripts from YouTube videos")

class YoutubeTranscript(pydantic.BaseModel):
    video_url: str
    with_timestamps: bool = False
    language: str = "en"

class TranscriptRequest(pydantic.BaseModel):
    video_id: str = None
    video_url: str = None
    with_timestamps: bool = False
    language: str = "en"

class TranscriptResponse(pydantic.BaseModel):
    success: bool
    transcript: str = None
    error: str = None
    video_id: str = None
    language: str = None
    with_timestamps: bool = False

def extract_video_id(url: str) -> str:
    """Extract video ID from various forms of YouTube URLs."""
    parsed = urlparse(url)
    if parsed.hostname in ('youtu.be', 'www.youtu.be'):
        return parsed.path[1:]
    if parsed.hostname in ('youtube.com', 'www.youtube.com'):
        if parsed.path == '/watch':
            return parse_qs(parsed.query)['v'][0]
        elif parsed.path.startswith('/v/'):
            return parsed.path[3:]
        elif parsed.path.startswith('/shorts/'):
            return parsed.path[8:]
    raise ValueError("Could not extract video ID from URL")

@server.tool()
def get_transcript(video_id: str, with_timestamps: bool = False, language: str = "en") -> str:
    """Get transcript for a video ID and format it as readable text."""
    api = YouTubeTranscriptApi()
    try:
        # Get available transcripts
        transcript_list = api.list(video_id)
        
        # Try to find the requested language
        transcript = None
        try:
            transcript = transcript_list.find_transcript([language])
        except NoTranscriptFound:
            # If requested language not found, get the first available transcript
            for t in transcript_list:
                transcript = t
                break
            else:
                return f"No transcript found for video {video_id}"
        
        # Fetch the actual transcript data
        transcript_data = transcript.fetch()
        
        if with_timestamps:
            def format_timestamp(seconds: float) -> str:
                hours = int(seconds // 3600)
                minutes = int((seconds % 3600) // 60)
                secs = int(seconds % 60)
                if hours > 0:
                    return f"[{hours}:{minutes:02d}:{secs:02d}]"
                return f"[{minutes}:{secs:02d}]"
                
            return "\n".join(f"{format_timestamp(entry.start)} {entry.text}" for entry in transcript_data)
        else:
            return "\n".join(entry.text for entry in transcript_data)
            
    except Exception as e:
        return f"Error fetching transcript for video {video_id}: {str(e)}"

@server.tool()
def save_transcript_to_file(video_id: str, with_timestamps: bool = False, language: str = "en") -> str:
    """Get transcript and save it to a text file in the transcript folder."""
    try:
        # Get the transcript
        transcript_content = get_transcript(video_id, with_timestamps, language)
        
        # Check if transcript extraction was successful
        if transcript_content.startswith("Error") or transcript_content.startswith("No transcript"):
            return transcript_content
        
        # Create the transcript directory path
        current_dir = Path(__file__).parent.parent  # Go up from src to project root
        transcript_dir = current_dir / "transcript"
        transcript_dir.mkdir(exist_ok=True)
        
        # Create filename with timestamp info
        timestamp_suffix = "_with_timestamps" if with_timestamps else "_no_timestamps"
        filename = f"{video_id}_{language}{timestamp_suffix}.txt"
        file_path = transcript_dir / filename
        
        # Write transcript to file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(f"YouTube Video ID: {video_id}\n")
            f.write(f"Language: {language}\n")
            f.write(f"With Timestamps: {with_timestamps}\n")
            f.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("-" * 50 + "\n\n")
            f.write(transcript_content)
        
        return f"✅ Transcript saved successfully to: {file_path}"
        
    except Exception as e:
        return f"Error saving transcript: {str(e)}"

# FastAPI endpoints
@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "YouTube Transcript API",
        "version": "1.0.0",
        "endpoints": {
            "POST /transcript": "Get transcript for a YouTube video",
            "POST /transcript/save": "Get transcript and save to file",
            "GET /health": "Health check"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.post("/transcript", response_model=TranscriptResponse)
async def get_transcript_api(request: TranscriptRequest):
    """Get transcript for a YouTube video via API."""
    try:
        # Extract video ID from URL if provided
        video_id = request.video_id
        if request.video_url and not video_id:
            try:
                video_id = extract_video_id(request.video_url)
            except ValueError as e:
                raise HTTPException(status_code=400, detail=str(e))
        
        if not video_id:
            raise HTTPException(status_code=400, detail="Either video_id or video_url must be provided")
        
        # Get transcript
        transcript = get_transcript(video_id, request.with_timestamps, request.language)
        
        # Check if transcript extraction failed
        if transcript.startswith("Error") or transcript.startswith("No transcript"):
            return TranscriptResponse(
                success=False,
                error=transcript,
                video_id=video_id,
                language=request.language,
                with_timestamps=request.with_timestamps
            )
        
        return TranscriptResponse(
            success=True,
            transcript=transcript,
            video_id=video_id,
            language=request.language,
            with_timestamps=request.with_timestamps
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.post("/transcript/save")
async def save_transcript_api(request: TranscriptRequest):
    """Get transcript and save it to a file."""
    try:
        # Extract video ID from URL if provided
        video_id = request.video_id
        if request.video_url and not video_id:
            try:
                video_id = extract_video_id(request.video_url)
            except ValueError as e:
                raise HTTPException(status_code=400, detail=str(e))
        
        if not video_id:
            raise HTTPException(status_code=400, detail="Either video_id or video_url must be provided")
        
        # Save transcript
        result = save_transcript_to_file(video_id, request.with_timestamps, request.language)
        
        if result.startswith("✅"):
            return {"success": True, "message": result, "video_id": video_id}
        else:
            return {"success": False, "error": result, "video_id": video_id}
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

def main():
    parser = argparse.ArgumentParser(description="YouTube Transcript Server")
    parser.add_argument("--mode", choices=["mcp", "fastapi"], default="mcp", 
                       help="Run in MCP mode or FastAPI mode (default: mcp)")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind FastAPI server (default: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=8080, help="Port to bind FastAPI server (default: 8080)")
    
    args = parser.parse_args()
    
    if args.mode == "fastapi":
        print(f"Starting FastAPI server on {args.host}:{args.port}")
        print(f"API documentation available at: http://{args.host}:{args.port}/docs")
        uvicorn.run(
            app, 
            host=args.host, 
            port=args.port,
            timeout_keep_alive=60,
            timeout_graceful_shutdown=60
        )
    else:
        print("Starting MCP server...")
        server.run()

if __name__ == "__main__":
    main()