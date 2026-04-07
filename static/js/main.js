// GSIF — Main JavaScript

// ─── NAVBAR TOGGLE ───
document.getElementById('navToggle')?.addEventListener('click', () => {
    document.getElementById('navLinks').classList.toggle('open');
});

// ─── ACCORDION ───
function toggleAccordion(el) {
    el.classList.toggle('open');
    const answer = el.nextElementSibling;
    answer.classList.toggle('open');
}

// ─── AUTO-DISMISS FLASH MESSAGES ───
setTimeout(() => {
    document.querySelectorAll('.flash').forEach(f => {
        f.style.opacity = '0';
        f.style.transition = 'opacity 0.5s';
        setTimeout(() => f.remove(), 500);
    });
}, 5000);

// ─── SMOOTH SCROLL for anchor links ───
document.querySelectorAll('a[href^="#"]').forEach(a => {
    a.addEventListener('click', e => {
        const target = document.querySelector(a.getAttribute('href'));
        if (target) { e.preventDefault(); target.scrollIntoView({ behavior: 'smooth' }); }
    });
});

// ─── SCROLL ANIMATIONS ───
const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.style.opacity = '1';
            entry.target.style.transform = 'translateY(0)';
        }
    });
}, { threshold: 0.1 });

document.querySelectorAll('.card, .card-dark, .timeline-item').forEach(el => {
    el.style.opacity = '0';
    el.style.transform = 'translateY(20px)';
    el.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
    observer.observe(el);
});
