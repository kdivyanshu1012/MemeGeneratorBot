# AI Meme Generator

A modern web application that generates memes using AI. The application uses Hugging Face's transformers for text generation and Stable Diffusion for image generation.

## Features

- Generate meme text based on user prompt and emotion
- Create custom images using Stable Diffusion
- Modern, responsive UI
- Download and share generated memes
- Mobile-friendly design

## Tech Stack

- Backend:
  - Python
  - FastAPI
  - Hugging Face Transformers
  - Stable Diffusion
  - Pillow for image processing

- Frontend:
  - HTML5
  - CSS3
  - Vanilla JavaScript
  - Font Awesome icons

## Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd meme-generator
```

2. Set up the Python environment:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. Run the backend server:
```bash
uvicorn main:app --reload
```

4. Open the frontend:
- Simply open the `frontend/index.html` file in your browser
- Or serve it using a local server:
```bash
python -m http.server 3000
```

## Deployment

The application is configured for deployment on Vercel:

1. Install Vercel CLI:
```bash
npm install -g vercel
```

2. Deploy to Vercel:
```bash
vercel
```

3. Follow the prompts to complete the deployment

## Usage

1. Enter a prompt describing what you want your meme to be about
2. Select an emotion from the dropdown menu
3. Click "Generate Meme"
4. Wait for the AI to generate your custom meme
5. Download or share your meme using the provided buttons

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details. 