from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from transformers import pipeline
from diffusers import StableDiffusionPipeline
import torch
from PIL import Image, ImageDraw, ImageFont
import io
import base64
from pydantic import BaseModel
import os

app = FastAPI()

# Enable CORS with more specific origins for security
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:8000",
        "https://*.vercel.app"  # Allow Vercel preview deployments
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize models - lazy loading for Vercel's serverless environment
text_generator = None
image_generator = None

def init_models():
    global text_generator, image_generator
    if text_generator is None:
        text_generator = pipeline('text-generation', model='gpt2')
    if image_generator is None:
        image_generator = StableDiffusionPipeline.from_pretrained(
            "CompVis/stable-diffusion-v1-4",
            torch_dtype=torch.float32
        )

class MemeRequest(BaseModel):
    prompt: str
    emotion: str

@app.post("/api/generate-meme")
async def generate_meme(request: MemeRequest):
    try:
        # Initialize models on first request
        init_models()
        
        # Generate meme text based on emotion and prompt
        prompt_text = f"Generate a {request.emotion} meme about {request.prompt}"
        generated_text = text_generator(prompt_text, max_length=50, num_return_sequences=1)[0]['generated_text']
        
        # Generate image using Stable Diffusion
        image = image_generator(prompt_text).images[0]
        
        # Add text to image
        draw = ImageDraw.Draw(image)
        # Use a default font if arial.ttf is not available
        try:
            font = ImageFont.truetype("arial.ttf", 36)
        except:
            font = ImageFont.load_default()
        
        # Position text at the top of the image
        text_position = (10, 10)
        draw.text(text_position, generated_text, font=font, fill="white", stroke_width=2, stroke_fill="black")
        
        # Convert image to base64
        buffered = io.BytesIO()
        image.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        
        return JSONResponse({
            "status": "success",
            "meme_text": generated_text,
            "meme_image": f"data:image/png;base64,{img_str}"
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# For local development
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 