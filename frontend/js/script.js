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
        : 'https://' + window.location.hostname;

    async function generateMeme() {
        const emotion = emotionSelect.value;

        try {
            // Show loading state
            loadingElement.classList.remove('hidden');
            resultElement.classList.add('hidden');
            generateBtn.disabled = true;

            const response = await fetch(`${API_URL}/api/generate-meme`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    emotion
                })
            });

            if (!response.ok) {
                throw new Error('Failed to generate meme');
            }

            const data = await response.json();
            
            // Update the image
            memeImage.src = data.meme_image;
            
            // Show result
            loadingElement.classList.add('hidden');
            resultElement.classList.remove('hidden');
        } catch (error) {
            console.error('Error:', error);
            alert('Failed to generate meme. Please try again.');
        } finally {
            generateBtn.disabled = false;
        }
    }

    generateBtn.addEventListener('click', generateMeme);
    anotherBtn.addEventListener('click', generateMeme);

    downloadBtn.addEventListener('click', () => {
        const link = document.createElement('a');
        link.download = 'random-meme.png';
        link.href = memeImage.src;
        link.click();
    });

    shareBtn.addEventListener('click', async () => {
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
            alert('Failed to share meme');
        }
    });

    // Generate a meme when the page loads
    generateMeme();
}); 