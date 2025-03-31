// Countdown timer for leaderboard
function updateCountdown() {
    const countdownElement = document.getElementById('countdown');
    if (!countdownElement) return;
    
    // Get the current time
    const now = new Date();
    
    // Set the end time to midnight
    const end = new Date();
    end.setHours(23, 59, 59, 999);
    
    // Calculate the time difference in seconds
    let diff = Math.floor((end - now) / 1000);
    
    // Calculate hours, minutes, and seconds
    const hours = Math.floor(diff / 3600);
    diff -= hours * 3600;
    const minutes = Math.floor(diff / 60);
    diff -= minutes * 60;
    const seconds = diff;
    
    // Update the countdown
    countdownElement.textContent = `${hours.toString().padStart(2, '0')} : ${minutes.toString().padStart(2, '0')} : ${seconds.toString().padStart(2, '0')}`;
}

// Update the countdown every second
setInterval(updateCountdown, 1000);
updateCountdown();

// Mobile menu toggle
const mobileMenuToggle = document.querySelector('.mobile-menu-toggle');
const sidebar = document.querySelector('.sidebar');

if (mobileMenuToggle && sidebar) {
    mobileMenuToggle.addEventListener('click', () => {
        sidebar.classList.toggle('active');
    });
}

// Notification button
const notificationButton = document.querySelector('.notification-btn');
const notificationPanel = document.querySelector('.notification-panel');

if (notificationButton && notificationPanel) {
    notificationButton.addEventListener('click', () => {
        notificationPanel.classList.toggle('active');
    });
    
    // Close notification panel when clicking outside
    document.addEventListener('click', (event) => {
        if (!notificationButton.contains(event.target) && !notificationPanel.contains(event.target)) {
            notificationPanel.classList.remove('active');
        }
    });
}