// Menu responsivo para todos dispositivos
document.addEventListener('DOMContentLoaded', function() {
    const menuIcon = document.querySelector('.menu-icon');
    const navLinks = document.querySelector('.nav-links');
    menuIcon && menuIcon.addEventListener('click', () => {
        navLinks.classList.toggle('active');
        menuIcon.classList.toggle('open');
    });

    // Fecha o menu ao clicar em um link (mobile)
    document.querySelectorAll('.nav-links a').forEach(link => {
        link.addEventListener('click', () => {
            if (window.innerWidth <= 900) {
                navLinks.classList.remove('active');
                menuIcon.classList.remove('open');
            }
        });
    });
});