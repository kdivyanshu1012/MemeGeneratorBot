document.addEventListener('DOMContentLoaded', () => {
    const generateBtn = document.getElementById('generate-btn');
    const downloadBtn = document.getElementById('download-btn');
    const shareBtn = document.getElementById('share-btn');
    const anotherBtn = document.getElementById('another-btn');
    const emotionSelect = document.getElementById('emotion');
    const loadingElement = document.getElementById('loading');
    const resultElement = document.getElementById('result');
    const memeImage = document.getElementById('meme-image');

    // Update API URL to work with both local development and production
    const API_URL = window.location.hostname === 'localhost' 
        ? 'http://localhost:8000' 
        : '';  // In production, use relative URL to avoid CORS issues

    async function generateMeme() {
        const emotion = emotionSelect.value;

        try {
            // Show loading state
            loadingElement.classList.remove('hidden');
            resultElement.classList.add('hidden');
            generateBtn.disabled = true;
            anotherBtn.disabled = true;

            const response = await fetch(`${API_URL}/api/generate-meme`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    emotion
                })
            });

            let data;
            const contentType = response.headers.get('content-type');
            if (contentType && contentType.includes('application/json')) {
                data = await response.json();
            } else {
                // If response is not JSON, get the text for error message
                const text = await response.text();
                throw new Error(
                    response.status === 404 
                        ? 'Server not found. Please make sure the backend server is running.'
                        : `Server error: ${text.slice(0, 100)}...`
                );
            }

            if (!response.ok) {
                throw new Error(data.detail || 'Failed to generate meme');
            }
            
            // Update the image
            memeImage.src = data.meme_image;
            
            // Show result
            loadingElement.classList.add('hidden');
            resultElement.classList.remove('hidden');
        } catch (error) {
            console.error('Error:', error);
            loadingElement.classList.add('hidden');
            
            // Show appropriate error message based on the error type
            let errorMessage;
            if (error.message.includes('Failed to fetch')) {
                errorMessage = 'Unable to connect to the server. Please check if the backend server is running and try again.';
            } else if (error.message.includes('Server not found')) {
                errorMessage = error.message;
            } else if (error.message.includes('Server error')) {
                errorMessage = 'The server encountered an error. Please try again or check the server logs.';
            } else {
                errorMessage = error.message;
            }
            
            alert(errorMessage);
        } finally {
            generateBtn.disabled = false;
            anotherBtn.disabled = false;
        }
    }

    // Add error handling for image loading
    memeImage.addEventListener('error', () => {
        console.error('Error loading meme image');
        loadingElement.classList.add('hidden');
        alert('Error loading the generated meme image. Please try again.');
    });

    generateBtn.addEventListener('click', generateMeme);
    anotherBtn.addEventListener('click', generateMeme);

    downloadBtn.addEventListener('click', () => {
        if (!memeImage.src) {
            alert('No meme to download. Please generate one first.');
            return;
        }
        const link = document.createElement('a');
        link.download = 'random-meme.png';
        link.href = memeImage.src;
        link.click();
    });

    shareBtn.addEventListener('click', async () => {
        if (!memeImage.src) {
            alert('No meme to share. Please generate one first.');
            return;
        }
        
        try {
            if (navigator.share) {
                await navigator.share({
                    title: 'Check out this random meme!',
                    text: 'I generated this meme using the Random Meme Generator!',
                    url: memeImage.src
                });
            } else {
                // Fallback for browsers that don't support Web Share API
                const tempInput = document.createElement('input');
                tempInput.value = memeImage.src;
                document.body.appendChild(tempInput);
                tempInput.select();
                document.execCommand('copy');
                document.body.removeChild(tempInput);
                alert('Meme URL copied to clipboard!');
            }
        } catch (error) {
            console.error('Error sharing:', error);
            alert('Failed to share meme: ' + error.message);
        }
    });

    // Don't auto-generate on load to avoid immediate errors
    // generateMeme();
}); 