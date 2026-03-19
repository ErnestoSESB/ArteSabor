document.addEventListener("DOMContentLoaded", function() {
    const container = document.querySelector('.floating-emojis');
    if (!container) return;

    const emojis = ['🍩', '🧁', '🍰', '🍪', '🍫', '🍬', '🎂', '🍭', '🥐'];
    const maxBubbles = 15;

    for (let i = 0; i < maxBubbles; i++) {
        createBubble();
    }

    function createBubble() {
        const bubble = document.createElement('div');
        bubble.classList.add('floating-emoji');

        bubble.innerText = emojis[Math.floor(Math.random() * emojis.length)];

        bubble.style.left = `${Math.random() * 100}%`;
        
        // Random size
        const size = 1.5 + Math.random() * 2;
        bubble.style.fontSize = `${size}rem`;

        const duration = 10 + Math.random() * 15; 
        const delay = Math.random() * 10;
        
        bubble.style.animationDuration = `${duration}s`;
        bubble.style.animationDelay = `${delay}s`;

        bubble.addEventListener('animationiteration', () => {
            bubble.style.left = `${Math.random() * 100}%`;
            bubble.innerText = emojis[Math.floor(Math.random() * emojis.length)];
        });

        container.appendChild(bubble);
    }
});