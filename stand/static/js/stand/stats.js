document.addEventListener("DOMContentLoaded", () => {
    const counters = document.querySelectorAll('.stat-number');
    const observer = new IntersectionObserver((entries, observerInstance) => {
        entries.forEach(entry => {
            if(entry.isIntersecting) {
                animateCounter(entry.target);
                observerInstance.unobserve(entry.target);
            }
        });
    }, { threshold: 0.2 });
    const animateCounter = (counter) => {
        const target = +counter.getAttribute('data-target');
        const append = counter.getAttribute('data-append') || "";
        const duration = 3500;
        const frameRate = 1000 / 60;
        const totalFrames = Math.round(duration / frameRate);
        let frame = 0;
        const count = () => {
            frame++;
            const progress = frame / totalFrames;
            const ease = progress === 1 ? 1 : 
              progress < 0.5 ? Math.pow(2, 20 * progress - 10) / 2 
                             : (2 - Math.pow(2, -20 * progress + 10)) / 2;
            
            const current = Math.round(target * ease);
            
            if(frame < totalFrames) {
                counter.innerText = current.toLocaleString('pt-BR');
                requestAnimationFrame(count);
            } else {
                counter.innerText = target.toLocaleString('pt-BR') + append;
                const icon = counter.closest('.stat-card').querySelector('.stat-icon');
                if (icon) {
                    icon.classList.add('finished');
                }
            }
        };
        requestAnimationFrame(count);
    };
    counters.forEach(counter => {
        observer.observe(counter);
    });
});
