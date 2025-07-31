// static/js/main.js
document.addEventListener('DOMContentLoaded', function () {
    // --- Mobile Menu Toggle ---
    const menuToggle = document.getElementById('menuToggle');
    const navLinks = document.getElementById('navLinks');

    if (menuToggle) {
        menuToggle.addEventListener('click', () => {
            navLinks.classList.toggle('active');
        });
    }

    document.querySelectorAll('.nav-links a').forEach(link => {
        link.addEventListener('click', () => {
            navLinks.classList.remove('active');
        });
    });

    // --- Smooth Scroll ---
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            if (this.getAttribute('href').startsWith('#') && this.getAttribute('href').length > 1) {
                e.preventDefault();
                const target = document.querySelector(this.getAttribute('href'));
                if (target) {
                    window.scrollTo({
                        top: target.offsetTop - 80,
                        behavior: 'smooth'
                    });
                }
            }
        });
    });

    // --- Active Nav Highlight ---
    function highlightActiveLink() {
        const sections = document.querySelectorAll('section');
        const navLinks = document.querySelectorAll('.nav-links a');

        let current = '';
        sections.forEach(section => {
            if (window.scrollY >= (section.offsetTop - 150)) {
                current = section.getAttribute('id');
            }
        });

        navLinks.forEach(link => {
            link.classList.remove('active');
            if (link.getAttribute('href').substring(1) === current) {
                link.classList.add('active');
            }
        });
    }

    highlightActiveLink();
    window.addEventListener('scroll', highlightActiveLink);

    // --- Scroll-based Animations ---
    function animateOnScroll() {
        const elements = document.querySelectorAll(
            '.project-card, .timeline-item, .skill-category, .certification-card'
        );

        elements.forEach(el => {
            const position = el.getBoundingClientRect();
            if (position.top < window.innerHeight - 100 && position.bottom >= 0) {
                el.style.opacity = 1;
                el.style.transform = 'translateY(0)';
            }
        });
    }

    document.querySelectorAll(
        '.project-card, .timeline-item, .skill-category, .certification-card'
    ).forEach(el => {
        el.style.opacity = 0;
        el.style.transform = 'translateY(20px)';
        el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
    });

    animateOnScroll();
    window.addEventListener('scroll', animateOnScroll);

    // --- Contact Form Handler ---
    const contactForm = document.getElementById('contactForm');
    if (contactForm) {
        contactForm.addEventListener('submit', function (e) {
            e.preventDefault();

            const submitBtn = this.querySelector('.submit-btn');
            const originalText = submitBtn.textContent;

            submitBtn.textContent = 'Sending...';
            submitBtn.disabled = true;

            setTimeout(() => {
                submitBtn.textContent = 'Message Sent!';
                submitBtn.style.backgroundColor = '#10b981';
                this.reset();

                setTimeout(() => {
                    submitBtn.textContent = originalText;
                    submitBtn.disabled = false;
                    submitBtn.style.backgroundColor = '';
                }, 3000);
            }, 1000);
        });
    }

    // --- Auto Remove Flash Messages ---
    setTimeout(() => {
        document.querySelectorAll('.alert').forEach(flash => {
            flash.style.opacity = '0';
            setTimeout(() => flash.remove(), 500);
        });
    }, 3000);

    // === 🔠 Improved Name Animation ===
    const name = document.querySelector('.name-animation');
    if (name) {
        const nameText = name.textContent;
        name.innerHTML = '';

        nameText.split('').forEach((letter, index) => {
            const span = document.createElement('span');
            span.textContent = letter;
            span.style.display = 'inline-block';
            span.style.marginRight = '2px'; // Adjust spacing between letters
            span.style.opacity = '0';
            span.style.transform = 'translateY(20px)';
            span.style.transition = 'opacity 0.4s ease, transform 0.4s ease';
            span.style.transitionDelay = `${0.2 + index * 0.06}s`;
            name.appendChild(span);
        });

        // Trigger animation after a slight delay
        setTimeout(() => {
            name.querySelectorAll('span').forEach(span => {
                span.style.opacity = '1';
                span.style.transform = 'translateY(0)';
            });
        }, 50);
    }

    // === 🖼️ Profile Image Hover Effect ===
    const profileImg = document.querySelector('.profile-img-container');
    if (profileImg) {
        profileImg.addEventListener('mousemove', (e) => {
            const x = e.offsetX;
            const y = e.offsetY;
            const centerX = profileImg.offsetWidth / 2;
            const centerY = profileImg.offsetHeight / 2;

            const angleX = (y - centerY) / 10;
            const angleY = (centerX - x) / 10;

            profileImg.style.transform = `perspective(1000px) rotateX(${angleX}deg) rotateY(${angleY}deg)`;
        });

        profileImg.addEventListener('mouseleave', () => {
            profileImg.style.transform = 'perspective(1000px) rotateX(0) rotateY(0)';
        });
    }
});
