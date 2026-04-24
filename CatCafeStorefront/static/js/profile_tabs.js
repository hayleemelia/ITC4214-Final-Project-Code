document.addEventListener('DOMContentLoaded', function () {
    const hash = window.location.hash;

    if (hash) {
        const tabButton = document.querySelector(`[data-bs-target="${hash}"]`);

        if (tabButton) {
            const tab = new bootstrap.Tab(tabButton);
            tab.show();
        }
    }

    const tabButtons = document.querySelectorAll('[data-bs-toggle="pill"]');

    tabButtons.forEach(function (button) {
        button.addEventListener('shown.bs.tab', function () {
            const target = button.getAttribute('data-bs-target');

            if (target) {
                history.replaceState(null, '', target);
            }
        });
    });
});