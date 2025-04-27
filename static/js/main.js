// Main JavaScript file for Learning Platform

document.addEventListener('DOMContentLoaded', function() {
  // Initialize tooltips
  const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
  tooltipTriggerList.map(function (tooltipTriggerEl) {
    return new bootstrap.Tooltip(tooltipTriggerEl);
  });

  // Initialize popovers
  const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
  popoverTriggerList.map(function (popoverTriggerEl) {
    return new bootstrap.Popover(popoverTriggerEl);
  });

  // Handle lesson completion
  const completeButtons = document.querySelectorAll('.complete-lesson-btn');
  completeButtons.forEach(button => {
    button.addEventListener('click', function() {
      const lessonId = this.getAttribute('data-lesson-id');
      completeLesson(lessonId);
    });
  });

  // Handle video progress
  const videoElement = document.getElementById('lesson-video');
  if (videoElement) {
    // If we're embedding a YouTube video, we need to listen for the YouTube API
    // This will be called once the YouTube iframe API is loaded
    window.onYouTubeIframeAPIReady = function() {
      const videoId = videoElement.getAttribute('data-video-id');
      if (!videoId) return;
      
      new YT.Player('lesson-video', {
        videoId: videoId,
        events: {
          'onStateChange': onPlayerStateChange
        }
      });
    };
    
    // Load YouTube iframe API
    const tag = document.createElement('script');
    tag.src = "https://www.youtube.com/iframe_api";
    const firstScriptTag = document.getElementsByTagName('script')[0];
    firstScriptTag.parentNode.insertBefore(tag, firstScriptTag);
  }
});

// Handle YouTube video state changes
function onPlayerStateChange(event) {
  // If video ended (state = 0), suggest marking lesson as complete
  if (event.data === 0) {
    const completeBtn = document.querySelector('.complete-lesson-btn');
    if (completeBtn && !completeBtn.disabled) {
      completeBtn.classList.add('btn-pulse');
      
      // Show a notification
      const toast = new bootstrap.Toast(document.getElementById('lesson-complete-toast'));
      toast.show();
    }
  }
}

// Function to complete a lesson
function completeLesson(lessonId) {
  const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');
  
  // Show loading state
  const completeBtn = document.querySelector(`.complete-lesson-btn[data-lesson-id="${lessonId}"]`);
  const originalText = completeBtn.innerHTML;
  completeBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Processing...';
  completeBtn.disabled = true;
  
  fetch(`/complete_lesson/${lessonId}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': csrfToken
    }
  })
  .then(response => response.json())
  .then(data => {
    if (data.success) {
      // Update UI
      completeBtn.innerHTML = 'Completed ✓';
      completeBtn.classList.remove('btn-primary');
      completeBtn.classList.add('btn-success');
      
      // Show XP gained
      document.getElementById('xp-gained').textContent = data.xpGained;
      
      // Update progress
      const progressBar = document.querySelector('.progress-bar');
      if (progressBar) {
        progressBar.style.width = `${data.courseProgress}%`;
        progressBar.setAttribute('aria-valuenow', data.courseProgress);
        progressBar.textContent = `${Math.round(data.courseProgress)}%`;
      }
      
      // Update level info if provided
      if (data.currentLevel) {
        document.getElementById('current-level').textContent = data.currentLevel;
      }
      if (data.currentXP) {
        document.getElementById('current-xp').textContent = data.currentXP;
      }
      
      // Show completion modal
      const completionModal = new bootstrap.Modal(document.getElementById('lesson-completion-modal'));
      completionModal.show();
      
      // If level up occurred, show celebration
      if (data.levelUp) {
        document.getElementById('level-up-alert').classList.remove('d-none');
        triggerConfetti();
      }
      
      // If reward was given, show it
      if (data.reward) {
        document.getElementById('reward-alert').classList.remove('d-none');
        document.getElementById('reward-name').textContent = data.reward;
      }
      
      // If course completed, show special celebration
      if (data.courseCompleted) {
        document.getElementById('course-completed-alert').classList.remove('d-none');
        triggerConfetti();
      }
      
      // Show next lesson button if available
      const nextLessonBtn = document.getElementById('next-lesson-btn');
      if (nextLessonBtn) {
        nextLessonBtn.classList.remove('d-none');
      }
    } else {
      // Reset button on failure
      completeBtn.innerHTML = originalText;
      completeBtn.disabled = false;
      
      // Show error message
      alert('Failed to complete lesson: ' + (data.message || 'Unknown error'));
    }
  })
  .catch(error => {
    console.error('Error:', error);
    completeBtn.innerHTML = originalText;
    completeBtn.disabled = false;
    alert('An error occurred while completing the lesson.');
  });
}

// Function to trigger confetti animation
function triggerConfetti() {
  const canvas = document.getElementById('confetti-canvas');
  if (!canvas) return;
  
  // Make canvas visible
  canvas.style.display = 'block';
  
  // Set canvas dimensions
  canvas.width = window.innerWidth;
  canvas.height = window.innerHeight;
  
  // Start confetti
  const confetti = new JSConfetti({ canvas });
  confetti.addConfetti({
    confettiColors: ['#ff0a54', '#ff477e', '#ff7096', '#ff85a1', '#fbb1bd', '#f9bec7'],
    confettiRadius: 3,
    confettiNumber: 500,
  });
  
  // Remove canvas after animation
  setTimeout(() => {
    canvas.style.display = 'none';
  }, 5000);
}

// Function to share achievement
function shareAchievement(achievementName) {
  if (navigator.share) {
    navigator.share({
      title: 'I earned an achievement!',
      text: `I just earned the "${achievementName}" achievement on Learning Platform! Join me on my learning journey!`,
      url: window.location.origin
    })
    .then(() => console.log('Successful share'))
    .catch((error) => console.log('Error sharing:', error));
  } else {
    // Fallback for browsers that don't support Web Share API
    const shareText = `I just earned the "${achievementName}" achievement on Learning Platform! Join me on my learning journey! ${window.location.origin}`;
    
    // Create a temporary input to copy the text
    const input = document.createElement('input');
    input.setAttribute('value', shareText);
    document.body.appendChild(input);
    input.select();
    document.execCommand('copy');
    document.body.removeChild(input);
    
    alert('Share text copied to clipboard!');
  }
}

// Handle display of countdown timer for streak
function updateStreakCountdown() {
  const streakTimer = document.getElementById('streak-timer');
  if (!streakTimer) return;
  
  const lastLogin = new Date(streakTimer.getAttribute('data-last-login'));
  const now = new Date();
  const timeDiff = 24 * 60 * 60 * 1000 - (now - lastLogin);
  
  if (timeDiff <= 0) {
    streakTimer.textContent = "Log in today to maintain your streak!";
    return;
  }
  
  const hours = Math.floor(timeDiff / (60 * 60 * 1000));
  const minutes = Math.floor((timeDiff % (60 * 60 * 1000)) / (60 * 1000));
  
  streakTimer.textContent = `${hours}h ${minutes}m remaining to maintain streak`;
  
  // Update every minute
  setTimeout(updateStreakCountdown, 60000);
}

// Start countdown if element exists
if (document.getElementById('streak-timer')) {
  updateStreakCountdown();
}
