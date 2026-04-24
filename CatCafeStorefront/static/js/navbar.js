document.addEventListener('DOMContentLoaded', function () {
    const navLogo = document.querySelector('#nav-logo');
    const navLinks = document.querySelector('#primary-navigation');

    if (!navLogo || !navLinks) return;

    navLogo.addEventListener('click', function () {
        navLinks.classList.toggle('active');

        const isOpen = navLinks.classList.contains('active');
        navLogo.setAttribute('aria-expanded', isOpen);
    });
});