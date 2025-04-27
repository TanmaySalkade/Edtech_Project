// JSConfetti implementation
// A lightweight confetti animation for milestone celebrations

class JSConfetti {
  constructor(options = {}) {
    this.canvas = options.canvas || document.createElement('canvas');
    this.canvas.style.position = 'fixed';
    this.canvas.style.top = '0';
    this.canvas.style.left = '0';
    this.canvas.style.width = '100%';
    this.canvas.style.height = '100%';
    this.canvas.style.pointerEvents = 'none';
    this.canvas.style.zIndex = '1000';
    this.canvas.id = 'confetti-canvas';
    
    if (!options.canvas) {
      document.body.appendChild(this.canvas);
    }
    
    this.ctx = this.canvas.getContext('2d');
    this.confettiElements = [];
    this.animationId = null;
  }
  
  // Add confetti to the canvas
  addConfetti({
    confettiColors = ['#ff0a54', '#ff477e', '#ff7096', '#ff85a1', '#fbb1bd', '#f9bec7'],
    confettiRadius = 5,
    confettiNumber = 250
  } = {}) {
    // Clear any existing animation
    cancelAnimationFrame(this.animationId);
    this.canvas.width = window.innerWidth;
    this.canvas.height = window.innerHeight;
    
    // Create new confetti elements
    this.confettiElements = [];
    
    for (let i = 0; i < confettiNumber; i++) {
      const color = confettiColors[Math.floor(Math.random() * confettiColors.length)];
      
      this.confettiElements.push({
        color,
        radius: Math.random() * confettiRadius + 1,
        x: Math.random() * this.canvas.width,
        y: -20, // Start above the screen
        velocity: {
          x: (Math.random() - 0.5) * 8,
          y: Math.random() * 3 + 2
        },
        rotation: Math.random() * 2 * Math.PI,
        rotationSpeed: Math.random() * 0.2 - 0.1
      });
    }
    
    // Start animation
    this.animate();
  }
  
  // Animate the confetti
  animate() {
    this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
    
    this.confettiElements.forEach(confetti => {
      // Update position
      confetti.x += confetti.velocity.x;
      confetti.y += confetti.velocity.y;
      
      // Apply gravity
      confetti.velocity.y += 0.05;
      
      // Apply air resistance
      confetti.velocity.x *= 0.99;
      
      // Update rotation
      confetti.rotation += confetti.rotationSpeed;
      
      // Draw confetti piece
      this.ctx.save();
      this.ctx.translate(confetti.x, confetti.y);
      this.ctx.rotate(confetti.rotation);
      
      // Draw a square
      this.ctx.fillStyle = confetti.color;
      this.ctx.fillRect(-confetti.radius, -confetti.radius, confetti.radius * 2, confetti.radius * 2);
      
      this.ctx.restore();
    });
    
    // Remove confetti that's off-screen
    this.confettiElements = this.confettiElements.filter(confetti => {
      return confetti.y < this.canvas.height + 20;
    });
    
    // Continue animation if there are still elements
    if (this.confettiElements.length > 0) {
      this.animationId = requestAnimationFrame(this.animate.bind(this));
    } else {
      this.animationId = null;
      // Remove canvas if it was auto-created
      if (!this.canvas.parentElement && this.canvas.parentElement === document.body) {
        document.body.removeChild(this.canvas);
      }
    }
  }
  
  // Clear all confetti
  clearConfetti() {
    cancelAnimationFrame(this.animationId);
    this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
    this.confettiElements = [];
    this.animationId = null;
  }
}
