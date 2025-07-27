#!/usr/bin/env python3
"""
Gradio Interface for YouTube Transcript Server

This script creates a web interface using Gradio to interact with the YouTube transcript FastAPI server.
Make sure the FastAPI server is running before using this interface.

Usage:
    python gradio_interface.py

The interface will be available at http://localhost:7860 by default.
"""

import gradio as gr
import requests
import json
from urllib.parse import urlparse, parse_qs
from pathlib import Path
import os

# Configuration
API_BASE_URL = "http://localhost:8080"
TRANSCRIPT_DIR = Path(__file__).parent / "transcript"

def extract_video_id_from_url(url: str) -> str:
    """Extract video ID from various forms of YouTube URLs."""
    if not url:
        return ""
    
    try:
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
    except:
        pass
    
    # If it's already a video ID (no URL structure), return as is
    if len(url.strip()) == 11 and not url.startswith('http'):
        return url.strip()
    
    return ""

def check_server_health():
    """Check if the FastAPI server is running."""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        return response.status_code == 200
    except:
        return False

def get_transcript(video_input: str, with_timestamps: bool, language: str, save_to_file: bool):
    """Get transcript from the FastAPI server."""
    
    # Check server health first
    if not check_server_health():
        return "❌ Error: FastAPI server is not running. Please start the server first:\n\n" \
               "uv run python src/mcp_youtube.py --mode fastapi --port 8080", None
    
    # Extract video ID
    video_id = extract_video_id_from_url(video_input)
    if not video_id:
        return "❌ Error: Please provide a valid YouTube video ID or URL", None
    
    try:
        # Prepare request data
        endpoint = "/transcript/save" if save_to_file else "/transcript"
        request_data = {
            "video_id": video_id,
            "with_timestamps": with_timestamps,
            "language": language
        }
        
        # Make API request
        response = requests.post(
            f"{API_BASE_URL}{endpoint}",
            json=request_data,
            headers={"Content-Type": "application/json"},
            timeout=60
        )
        
        if response.status_code == 200:
            data = response.json()
            
            if save_to_file:
                # Handle save response
                if data.get("success"):
                    file_info = f"✅ {data.get('message', 'Transcript saved successfully')}"
                    transcript_text = f"Video ID: {video_id}\nFile saved successfully!"
                    return file_info, transcript_text
                else:
                    error_msg = f"❌ Error saving transcript: {data.get('error', 'Unknown error')}"
                    return error_msg, None
            else:
                # Handle transcript response
                if data.get("success"):
                    transcript_text = data.get("transcript", "No transcript data received")
                    info_msg = f"✅ Transcript retrieved successfully!\n" \
                              f"Video ID: {data.get('video_id', 'N/A')}\n" \
                              f"Language: {data.get('language', 'N/A')}\n" \
                              f"With Timestamps: {data.get('with_timestamps', False)}"
                    return info_msg, transcript_text
                else:
                    error_msg = f"❌ Error: {data.get('error', 'Unknown error')}"
                    return error_msg, None
        else:
            error_msg = f"❌ Server error (HTTP {response.status_code}): {response.text}"
            return error_msg, None
            
    except requests.exceptions.Timeout:
        return "❌ Error: Request timed out. The video might be too long or the server is busy.", None
    except requests.exceptions.ConnectionError:
        return "❌ Error: Cannot connect to the FastAPI server. Make sure it's running on port 8080.", None
    except Exception as e:
        return f"❌ Error: {str(e)}", None

def list_saved_transcripts():
    """List all saved transcript files."""
    if not TRANSCRIPT_DIR.exists():
        return "No transcript files found. The transcript directory doesn't exist yet."
    
    files = list(TRANSCRIPT_DIR.glob("*.txt"))
    if not files:
        return "No transcript files found in the transcript directory."
    
    file_list = []
    for file in sorted(files, key=lambda x: x.stat().st_mtime, reverse=True):
        size = file.stat().st_size
        modified = file.stat().st_mtime
        file_list.append(f"📄 {file.name} ({size:,} bytes)")
    
    return f"Found {len(files)} transcript files:\n\n" + "\n".join(file_list)

def create_interface():
    """Create and configure the Gradio interface."""
    
    with gr.Blocks(
        title="YouTube Transcript Extractor",
        theme=gr.themes.Soft(),
        css="""
        .gradio-container {
            max-width: 1200px !important;
        }
        """
    ) as interface:
        
        gr.Markdown(
            """
            # 🎬 YouTube Transcript Extractor
            
            Extract transcripts from YouTube videos using the FastAPI server.
            
            **📋 Instructions:**
            1. Make sure the FastAPI server is running: `uv run python src/mcp_youtube.py --mode fastapi --port 8080`
            2. Enter a YouTube video ID or full URL
            3. Configure your options
            4. Click "Get Transcript" or "Save to File"
            """
        )
        
        with gr.Row():
            with gr.Column(scale=2):
                # Input section
                gr.Markdown("## 📥 Input")
                
                video_input = gr.Textbox(
                    label="YouTube Video ID or URL",
                    placeholder="Enter video ID (e.g., 'pebgrFQ-C7M') or full URL (e.g., 'https://www.youtube.com/watch?v=pebgrFQ-C7M')",
                    lines=2
                )
                
                with gr.Row():
                    with_timestamps = gr.Checkbox(
                        label="Include Timestamps",
                        value=True,
                        info="Add [mm:ss] timestamps to each line"
                    )
                    
                    language = gr.Dropdown(
                        choices=["en", "es", "fr", "de", "it", "pt", "ja", "ko", "zh", "ar"],
                        value="en",
                        label="Language",
                        info="Preferred transcript language"
                    )
                
                save_to_file = gr.Checkbox(
                    label="Save to File",
                    value=False,
                    info="Save transcript to the transcript/ folder"
                )
                
                # Action buttons
                with gr.Row():
                    get_btn = gr.Button("🎯 Get Transcript", variant="primary", scale=2)
                    clear_btn = gr.Button("🧹 Clear", scale=1)
            
            with gr.Column(scale=1):
                # Server status
                gr.Markdown("## 🔧 Server Status")
                
                def check_status():
                    if check_server_health():
                        return "🟢 **Server Status**: Online\n\n✅ FastAPI server is running and ready!"
                    else:
                        return "🔴 **Server Status**: Offline\n\n❌ FastAPI server is not responding.\n\n**To start the server:**\n```bash\nuv run python src/mcp_youtube.py --mode fastapi --port 8080\n```"
                
                status_output = gr.Markdown(value=check_status())
                refresh_btn = gr.Button("🔄 Refresh Status")
                
                # File management
                gr.Markdown("## 📁 Saved Files")
                file_list_btn = gr.Button("📋 List Saved Transcripts")
        
        # Output section
        gr.Markdown("## 📤 Output")
        
        with gr.Row():
            info_output = gr.Textbox(
                label="Status & Information",
                lines=5,
                interactive=False
            )
        
        transcript_output = gr.Textbox(
            label="Transcript Content",
            lines=15,
            max_lines=30,
            interactive=False,
            show_copy_button=True
        )
        
        file_list_output = gr.Textbox(
            label="Saved Transcript Files",
            lines=8,
            interactive=False,
            visible=False
        )
        
        # Event handlers
        def handle_transcript_request(video_input, with_timestamps, language, save_to_file):
            """Handle transcript request and update file list if saved."""
            info, transcript = get_transcript(video_input, with_timestamps, language, save_to_file)
            
            # If file was saved successfully, also update the file list
            if save_to_file and info.startswith("✅"):
                file_list = list_saved_transcripts()
                return info, transcript, file_list, gr.update(visible=True)
            else:
                return info, transcript, gr.update(), gr.update()
        
        get_btn.click(
            fn=handle_transcript_request,
            inputs=[video_input, with_timestamps, language, save_to_file],
            outputs=[info_output, transcript_output, file_list_output, file_list_output]
        )
        
        clear_btn.click(
            fn=lambda: ("", "", ""),
            outputs=[video_input, info_output, transcript_output]
        )
        
        refresh_btn.click(
            fn=check_status,
            outputs=[status_output]
        )
        
        file_list_btn.click(
            fn=list_saved_transcripts,
            outputs=[file_list_output]
        ).then(
            fn=lambda: gr.update(visible=True),
            outputs=[file_list_output]
        )
        
        # Examples
        gr.Markdown("## 🎯 Examples")
        
        gr.Examples(
            examples=[
                ["pebgrFQ-C7M", True, "en", False],
                ["https://www.youtube.com/watch?v=pebgrFQ-C7M", False, "en", True],
                ["https://youtu.be/pebgrFQ-C7M", True, "en", False]
            ],
            inputs=[video_input, with_timestamps, language, save_to_file],
            label="Click on an example to populate the form"
        )
        
        gr.Markdown(
            """
            ---
            
            ## 🔗 API Endpoints
            
            - **Get Transcript**: `POST /transcript`
            - **Save Transcript**: `POST /transcript/save`
            - **Health Check**: `GET /health`
            - **API Docs**: [http://localhost:8080/docs](http://localhost:8080/docs)
            
            ## 🆘 Troubleshooting
            
            - **Server not responding?** Make sure the FastAPI server is running
            - **Invalid video ID?** Check that the YouTube URL or video ID is correct
            - **Long loading times?** Longer videos may take more time to process
            - **Connection error?** Verify the server is running on port 8080
            """
        )
    
    return interface

def main():
    """Main function to launch the Gradio interface."""
    print("🚀 Starting YouTube Transcript Gradio Interface...")
    
    # Check if server is running
    if check_server_health():
        print("✅ FastAPI server detected and running!")
    else:
        print("⚠️  Warning: FastAPI server is not running.")
        print("   Please start it with: uv run python src/mcp_youtube.py --mode fastapi --port 8080")
    
    # Create and launch interface
    interface = create_interface()
    
    # Launch with custom settings
    interface.launch(
        server_name="0.0.0.0",  # Allow external access
        server_port=7860,       # Default Gradio port
        share=False,            # Set to True for public sharing
        show_api=False,         # Hide API docs link
        show_error=True,        # Show detailed errors
        quiet=False             # Show startup logs
    )

# Create a demo variable for Gradio's auto-reload feature
demo = None

if __name__ == "__main__":
    main()
