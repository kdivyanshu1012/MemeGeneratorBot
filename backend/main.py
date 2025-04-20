from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import PlainTextResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from PIL import Image, ImageDraw, ImageFont
import io
import base64
from pydantic import BaseModel
import os
import sys
import random
from datetime import datetime
import logging
import traceback

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI()

# Enable Gzip compression
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Enable CORS - update with your frontend URL in production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update this with your frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom error handler for all exceptions
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": str(exc.detail)}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    # Log the full error with traceback
    logger.error(f"Unexpected error: {str(exc)}\n{traceback.format_exc()}")
    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected error occurred. Please try again."}
    )

class MemeRequest(BaseModel):
    emotion: str

# Simplified color schemes
COLOR_SCHEMES = {
    "funny": ((255, 255, 150), (255, 200, 100)),     # Yellow to Orange
    "sarcastic": ((200, 150, 255), (150, 100, 200)), # Purple tones
    "wholesome": ((150, 255, 200), (100, 200, 255)), # Green to Blue
    "ironic": ((255, 150, 150), (200, 100, 150)),    # Pink tones
    "dramatic": ((150, 150, 255), (100, 100, 200))   # Blue tones
}

# Simplified templates
TEMPLATES = {
    "funny": [
        "When {prompt}... 😂",
        "Nobody:\nMe when {prompt} 🤣",
        "That moment when {prompt} 😆",
        "POV: {prompt} 😅"
    ],
    "sarcastic": [
        "Oh sure, {prompt}... 🙄",
        "Yeah, {prompt} is great... 😏",
        "Me pretending {prompt} isn't happening 😒",
        "When {prompt} strikes again 🤨"
    ],
    "wholesome": [
        "{prompt} makes everything better 🥰",
        "Finding joy in {prompt} 💖",
        "When {prompt} brings smiles ☺️",
        "Grateful for {prompt} 🙏"
    ],
    "ironic": [
        "Trying to avoid {prompt} 😅",
        "Plot twist: {prompt} 🤔",
        "Me vs {prompt} 😌",
        "Just {prompt} things 🙃"
    ],
    "dramatic": [
        "BREAKING: {prompt}! 😱",
        "When {prompt} hits different 😫",
        "Not {prompt} again! 😩",
        "The drama of {prompt} 😤"
    ]
}

# Simplified prompts
PROMPTS = {
    "funny": [
        "debugging at 3 AM",
        "the code works first try",
        "finding a missing semicolon",
        "Stack Overflow saves the day"
    ],
    "sarcastic": [
        "meetings that could be emails",
        "'well-documented' code",
        "perfect code reviews",
        "'quick' fixes"
    ],
    "wholesome": [
        "helping new developers",
        "fixing the bug",
        "clean code",
        "successful deployment"
    ],
    "ironic": [
        "temporary solutions",
        "'I'll document later'",
        "code optimization",
        "meeting deadlines"
    ],
    "dramatic": [
        "production crashes",
        "merge conflicts",
        "missing backups",
        "deadline approaching"
    ]
}

def generate_meme_text(emotion: str) -> tuple[str, str]:
    """Generate meme text based on templates and random selection."""
    try:
        templates = TEMPLATES.get(emotion.lower(), TEMPLATES["funny"])
        prompts_for_emotion = PROMPTS.get(emotion.lower(), PROMPTS["funny"])
        
        template = random.choice(templates)
        prompt = random.choice(prompts_for_emotion)
        
        return template.format(prompt=prompt), prompt
    except Exception as e:
        logger.error(f"Error in generate_meme_text: {str(e)}")
        raise

def generate_gradient_background(width: int, height: int, emotion: str) -> Image.Image:
    """Generate a gradient background based on emotion."""
    try:
        # Get color scheme or default to funny
        color1, color2 = COLOR_SCHEMES.get(emotion.lower(), COLOR_SCHEMES["funny"])
        
        # Create gradient
        image = Image.new('RGB', (width, height))
        draw = ImageDraw.Draw(image)
        
        for y in range(height):
            r = int(color1[0] + (color2[0] - color1[0]) * y / height)
            g = int(color1[1] + (color2[1] - color1[1]) * y / height)
            b = int(color1[2] + (color2[2] - color1[2]) * y / height)
            draw.line([(0, y), (width, y)], fill=(r, g, b))
        
        return image
    except Exception as e:
        logger.error(f"Error in generate_gradient_background: {str(e)}")
        raise

def get_font(size: int) -> ImageFont.FreeTypeFont:
    """Get the appropriate font based on the operating system."""
    try:
        if sys.platform == "win32":
            font_path = "C:\\Windows\\Fonts\\arial.ttf"
        elif sys.platform == "darwin":
            font_path = "/System/Library/Fonts/Helvetica.ttc"
        else:
            font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

        try:
            font = ImageFont.truetype(font_path, size)
        except OSError:
            logger.warning(f"Could not load font from {font_path}, using default font")
            font = ImageFont.load_default()
            
        return font
    except Exception as e:
        logger.error(f"Error in get_font: {str(e)}")
        raise

@app.get("/")
async def root():
    """Root endpoint to verify the server is running."""
    return {"status": "Server is running", "version": "1.0.0"}

@app.get("/api/health")
async def health_check():
    """Health check endpoint with detailed status."""
    try:
        # Test image creation
        test_image = Image.new('RGB', (100, 100))
        test_draw = ImageDraw.Draw(test_image)
        test_font = get_font(12)
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "checks": {
                "image_creation": "ok",
                "font_loading": "ok",
                "system": sys.platform
            }
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
        )

@app.post("/api/generate-meme")
async def generate_meme(request: MemeRequest):
    try:
        emotion = request.emotion.lower()
        if emotion not in TEMPLATES:
            emotion = "funny"  # Default fallback

        # Generate text
        template = random.choice(TEMPLATES[emotion])
        prompt = random.choice(PROMPTS[emotion])
        meme_text = template.format(prompt=prompt)

        # Create image
        width, height = 800, 600
        image = generate_gradient_background(width, height, emotion)
        draw = ImageDraw.Draw(image)

        # Get font
        font = get_font(48)
        
        # Split text into lines
        words = meme_text.split('\n')
        y = height // 4
        
        for line in words:
            # Simple center alignment
            text_width = font.getlength(line) if hasattr(font, 'getlength') else len(line) * (font.size // 2)
            x = (width - text_width) // 2
            
            # Draw text outline
            outline_color = "black"
            for dx, dy in [(-2,-2), (-2,2), (2,-2), (2,2)]:
                draw.text((x + dx, y + dy), line, font=font, fill=outline_color)
            
            # Draw main text
            draw.text((x, y), line, font=font, fill="white")
            y += font.size + 10

        # Convert to base64
        buffered = io.BytesIO()
        image.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()

        return JSONResponse({
            "status": "success",
            "meme_text": meme_text,
            "prompt": prompt,
            "meme_image": f"data:image/png;base64,{img_str}"
        })

    except Exception as e:
        logger.error(f"Error generating meme: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 