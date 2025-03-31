// Handle enter key press to continue
document.addEventListener('keydown', (event) => {
    if (event.key === 'Enter') {
        const continueBtn = document.querySelector('.primary-btn');
        if (continueBtn) {
            window.location.href = continueBtn.getAttribute('href');
        }
    }
    
    if (event.key === 'Escape') {
        const closeBtn = document.querySelector('.close-btn');
        if (closeBtn) {
            window.location.href = closeBtn.getAttribute('href');
        }
    }
});