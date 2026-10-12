// Landing Page Specific Scripts - 3D Interactive Canvas & Parallax

document.addEventListener('DOMContentLoaded', () => {
    // 1. Initialize 3D Particle Canvas
    init3DParticleCanvas();

    // 2. Initialize 3D Mouse Parallax
    init3DParallax();

    // 3. Animate counters when they come into view
    const statsSection = document.querySelector('.stats-section');
    if (statsSection) {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    animateAllCounters();
                    observer.unobserve(entry.target);
                }
            });
        }, { threshold: 0.3 });
        
        observer.observe(statsSection);
    }

    // 4. Newsletter form
    const newsletterForm = document.querySelector('.newsletter-form');
    if (newsletterForm) {
        newsletterForm.addEventListener('submit', (e) => {
            e.preventDefault();
            const email = newsletterForm.querySelector('input[type="email"]').value;
            const btn = newsletterForm.querySelector('button');
            const originalText = btn.textContent;
            btn.textContent = 'Subscribed! ✓';
            btn.disabled = true;
            
            setTimeout(() => {
                newsletterForm.reset();
                btn.textContent = originalText;
                btn.disabled = false;
            }, 3000);
        });
    }
});

/* =======================================================
   3D PARTICLE CONSTELLATION CANVAS
   ======================================================= */
function init3DParticleCanvas() {
    const canvas = document.getElementById('hero-particle-canvas');
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    let width = canvas.width = canvas.parentElement.offsetWidth;
    let height = canvas.height = canvas.parentElement.offsetHeight;

    window.addEventListener('resize', () => {
        if (!canvas.parentElement) return;
        width = canvas.width = canvas.parentElement.offsetWidth;
        height = canvas.height = canvas.parentElement.offsetHeight;
    });

    const particles = [];
    const particleCount = Math.min(Math.floor((width * height) / 18000), 65);
    const mouse = { x: null, y: null, radius: 140 };

    window.addEventListener('mousemove', (e) => {
        const rect = canvas.getBoundingClientRect();
        mouse.x = e.clientX - rect.left;
        mouse.y = e.clientY - rect.top;
    });

    window.addEventListener('mouseleave', () => {
        mouse.x = null;
        mouse.y = null;
    });

    class Particle {
        constructor() {
            this.x = Math.random() * width;
            this.y = Math.random() * height;
            this.z = Math.random() * 1.5 + 0.5; // Depth factor
            this.vx = (Math.random() - 0.5) * 0.6 * this.z;
            this.vy = (Math.random() - 0.5) * 0.6 * this.z;
            this.radius = (Math.random() * 2 + 1.2) * this.z;
            this.color = Math.random() > 0.3 ? 'rgba(16, 185, 129, ' : 'rgba(245, 158, 11, ';
            this.baseAlpha = (Math.random() * 0.4 + 0.2) * this.z;
            this.pulse = Math.random() * Math.PI * 2;
        }

        update() {
            this.pulse += 0.03;
            this.x += this.vx;
            this.y += this.vy;

            if (this.x < 0) this.x = width;
            if (this.x > width) this.x = 0;
            if (this.y < 0) this.y = height;
            if (this.y > height) this.y = 0;

            // Mouse interaction
            if (mouse.x !== null && mouse.y !== null) {
                const dx = mouse.x - this.x;
                const dy = mouse.y - this.y;
                const dist = Math.sqrt(dx * dx + dy * dy);
                if (dist < mouse.radius) {
                    const force = (1 - dist / mouse.radius) * 1.2;
                    this.x -= (dx / dist) * force * 2;
                    this.y -= (dy / dist) * force * 2;
                }
            }
        }

        draw() {
            const alpha = this.baseAlpha + Math.sin(this.pulse) * 0.15;
            ctx.beginPath();
            ctx.arc(this.x, this.y, this.radius, 0, Math.PI * 2);
            ctx.fillStyle = this.color + Math.max(0.1, alpha) + ')';
            ctx.shadowBlur = 10 * this.z;
            ctx.shadowColor = 'rgba(16, 185, 129, 0.6)';
            ctx.fill();
            ctx.shadowBlur = 0; // reset
        }
    }

    for (let i = 0; i < particleCount; i++) {
        particles.push(new Particle());
    }

    function connect() {
        for (let a = 0; a < particles.length; a++) {
            for (let b = a + 1; b < particles.length; b++) {
                const dx = particles[a].x - particles[b].x;
                const dy = particles[a].y - particles[b].y;
                const dist = Math.sqrt(dx * dx + dy * dy);

                if (dist < 110) {
                    const alpha = (1 - dist / 110) * 0.22;
                    ctx.beginPath();
                    ctx.strokeStyle = `rgba(16, 185, 129, ${alpha})`;
                    ctx.lineWidth = 0.8;
                    ctx.moveTo(particles[a].x, particles[a].y);
                    ctx.lineTo(particles[b].x, particles[b].y);
                    ctx.stroke();
                }
            }
        }
    }

    function animate() {
        ctx.clearRect(0, 0, width, height);
        particles.forEach(p => {
            p.update();
            p.draw();
        });
        connect();
        requestAnimationFrame(animate);
    }

    animate();
}

/* =======================================================
   3D MOUSE PARALLAX TILT
   ======================================================= */
function init3DParallax() {
    const hero = document.getElementById('hero-section');
    if (!hero) return;

    const bgImg = hero.querySelector('.hero-bg-3d-img');
    const floatCards = hero.querySelectorAll('.hero-float-card');
    const heroContent = hero.querySelector('.hero-content');

    let targetX = 0, targetY = 0;
    let currentX = 0, currentY = 0;

    hero.addEventListener('mousemove', (e) => {
        const rect = hero.getBoundingClientRect();
        const x = (e.clientX - rect.left) / rect.width - 0.5;
        const y = (e.clientY - rect.top) / rect.height - 0.5;

        targetX = x;
        targetY = y;
    });

    hero.addEventListener('mouseleave', () => {
        targetX = 0;
        targetY = 0;
    });

    function updateParallax() {
        currentX += (targetX - currentX) * 0.08;
        currentY += (targetY - currentY) * 0.08;

        if (bgImg) {
            bgImg.style.transform = `scale(1.04) translate(${currentX * -30}px, ${currentY * -30}px)`;
        }

        if (heroContent) {
            heroContent.style.transform = `perspective(1000px) rotateY(${currentX * 6}deg) rotateX(${currentY * -6}deg)`;
        }

        floatCards.forEach((card, idx) => {
            const depth = (idx % 2 === 0 ? 1 : -1) * (20 + idx * 8);
            card.style.transform = `translate(${currentX * depth}px, ${currentY * depth}px) rotateY(${currentX * 10}deg)`;
        });

        requestAnimationFrame(updateParallax);
    }

    updateParallax();
}

/* =======================================================
   COUNTERS
   ======================================================= */
function animateAllCounters() {
    const counters = document.querySelectorAll('[data-count]');
    counters.forEach(counter => {
        const target = parseInt(counter.dataset.count);
        const duration = 2000;
        const start = Date.now();
        
        const updateCounter = () => {
            const elapsed = Date.now() - start;
            const progress = Math.min(elapsed / duration, 1);
            const value = Math.floor(progress * target);
            counter.textContent = value.toLocaleString();
            
            if (progress < 1) {
                requestAnimationFrame(updateCounter);
            }
        };
        
        updateCounter();
    });
}

