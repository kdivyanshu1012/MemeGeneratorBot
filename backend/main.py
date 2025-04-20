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

# Predefined prompts for different emotions
PROMPTS = {
    "funny": [
        "trying to code at 3 AM",
        "debugging without console.log",
        "when the code works on first try",
        "finding a semicolon error after 2 hours",
        "using Stack Overflow for the 100th time today",
        "when someone says they'll fix the bug later",
        "forgetting to save the file",
        "when the client says it's a small change"
    ],
    "sarcastic": [
        "meetings that could have been emails",
        "documentation that's totally up to date",
        "perfectly commented code",
        "code review feedback",
        "project deadlines",
        "agile planning",
        "testing in production",
        "legacy code maintenance"
    ],
    "wholesome": [
        "helping junior developers",
        "successfully fixing a bug",
        "team collaboration",
        "learning new technologies",
        "code that runs smoothly",
        "positive code reviews",
        "clean code practices",
        "celebrating project milestones"
    ],
    "ironic": [
        "writing temporary code",
        "saying you'll document later",
        "promising to refactor soon",
        "backup plans",
        "code optimization",
        "following best practices",
        "meeting estimations",
        "work-life balance"
    ],
    "dramatic": [
        "production server crashes",
        "losing unsaved work",
        "merge conflicts",
        "database migrations",
        "deadline approaching",
        "missing semicolons",
        "infinite loops",
        "memory leaks"
    ]
}

def generate_meme_text(emotion: str) -> tuple[str, str]:
    """Generate meme text based on templates and random selection."""
    try:
        templates = {
            "funny": [
                "When {prompt} and you can't even...",
                "Nobody:\nAbsolutely nobody:\nMe when {prompt}:",
                "That moment when {prompt} hits different",
                "POV: {prompt}",
            ],
            "sarcastic": [
                "Oh sure, because {prompt} always works out great...",
                "Yeah, {prompt} is exactly what we needed...",
                "Me pretending {prompt} isn't a problem",
                "When someone mentions {prompt} one more time...",
            ],
            "wholesome": [
                "When {prompt} makes your whole day better",
                "Finding joy in {prompt}",
                "Spreading happiness with {prompt}",
                "When {prompt} brings people together",
            ],
            "ironic": [
                "Trying to avoid {prompt}\nAlso me: *does exactly that*",
                "Plot twist: {prompt} was the solution all along",
                "Me: I'm done with {prompt}\nLife: Are you sure about that?",
                "When {prompt} becomes your personality",
            ],
            "dramatic": [
                "BREAKING NEWS: {prompt} changes everything!",
                "Top 10 anime betrayals: {prompt} edition",
                "When {prompt} is just too much to handle",
                "The saga of {prompt} continues...",
            ]
        }

        # Default to funny if emotion not found
        templates_for_emotion = templates.get(emotion.lower(), templates["funny"])
        prompts_for_emotion = PROMPTS.get(emotion.lower(), PROMPTS["funny"])
        
        template = random.choice(templates_for_emotion)
        prompt = random.choice(prompts_for_emotion)
        
        return template.format(prompt=prompt), prompt
    except Exception as e:
        logger.error(f"Error in generate_meme_text: {str(e)}")
        raise

def generate_gradient_background(width: int, height: int, emotion: str) -> Image.Image:
    """Generate a gradient background based on emotion."""
    try:
        # Color schemes for different emotions
        color_schemes = {
            "funny": ((255, 255, 150), (255, 200, 100)),  # Yellow to Orange
            "sarcastic": ((200, 150, 255), (150, 100, 200)),  # Purple tones
            "wholesome": ((150, 255, 200), (100, 200, 255)),  # Green to Blue
            "ironic": ((255, 150, 150), (200, 100, 150)),  # Pink tones
            "dramatic": ((150, 150, 255), (100, 100, 200))   # Blue tones
        }

        # Get color scheme or default to funny
        color1, color2 = color_schemes.get(emotion.lower(), color_schemes["funny"])
        
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
        logger.info(f"Generating meme with emotion: {request.emotion}")
        
        # Generate meme text
        meme_text, prompt = generate_meme_text(request.emotion)
        logger.info(f"Generated text: {meme_text}")
        
        # Create background image
        width, height = 800, 600
        image = generate_gradient_background(width, height, request.emotion)
        draw = ImageDraw.Draw(image)
        
        # Get font
        font = get_font(36)
        
        try:
            # Calculate text position and wrap text
            margin = 20
            max_width = width - 2 * margin
            words = meme_text.split()
            lines = []
            current_line = []
            
            for word in words:
                current_line.append(word)
                text = ' '.join(current_line)
                # Use a basic text width calculation if getlength is not available
                text_width = font.getlength(text) if hasattr(font, 'getlength') else len(text) * (font.size // 2)
                
                if text_width > max_width:
                    if len(current_line) == 1:
                        lines.append(word)
                        current_line = []
                    else:
                        current_line.pop()
                        lines.append(' '.join(current_line))
                        current_line = [word]
            
            if current_line:
                lines.append(' '.join(current_line))
            
            # Draw text with outline effect
            y = margin
            for line in lines:
                # Calculate center position for each line
                text_width = font.getlength(line) if hasattr(font, 'getlength') else len(line) * (font.size // 2)
                x = (width - text_width) // 2
                
                # Draw text outline
                outline_color = "black"
                outline_width = 2
                for dx in [-outline_width, outline_width]:
                    for dy in [-outline_width, outline_width]:
                        draw.text((x + dx, y + dy), line, font=font, fill=outline_color)
                
                # Draw main text
                draw.text((x, y), line, font=font, fill="white")
                y += font.size + 10

            # Convert image to base64
            buffered = io.BytesIO()
            image.save(buffered, format="PNG")
            img_str = base64.b64encode(buffered.getvalue()).decode()
            
            logger.info("Meme generated successfully")
            
            return JSONResponse({
                "status": "success",
                "meme_text": meme_text,
                "prompt": prompt,
                "meme_image": f"data:image/png;base64,{img_str}"
            })
            
        except Exception as e:
            logger.error(f"Error in text rendering: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error rendering text: {str(e)}")
            
    except Exception as e:
        logger.error(f"Error generating meme: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 