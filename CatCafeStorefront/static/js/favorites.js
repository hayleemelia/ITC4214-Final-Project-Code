document.addEventListener('DOMContentLoaded', function () {
    const favoriteButtons = document.querySelectorAll('.favorite-btn, .favorite-card-btn');
    if (!favoriteButtons.length) return;

    const csrfInput = document.querySelector('[name=csrfmiddlewaretoken]');
    let popupTimeout;

    function showDetailPopup(message, type) {
        const favoritePopup = document.querySelector('#favorite-popup');
        if (!favoritePopup) return;

        favoritePopup.textContent = message;
        favoritePopup.classList.remove('success', 'error', 'show');
        favoritePopup.classList.add(type);

        void favoritePopup.offsetWidth;

        favoritePopup.classList.add('show');

        clearTimeout(popupTimeout);
        popupTimeout = setTimeout(function () {
            favoritePopup.classList.remove('show');
        }, 2500);
    }

    favoriteButtons.forEach(function (button) {
        button.addEventListener('click', function () {
            if (button.tagName.toLowerCase() === 'a') return;

            const url = button.dataset.url;
            const formData = new FormData();

            fetch(url, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrfInput.value,
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    const heart = button.querySelector('.favorite-heart');

                    if (data.is_favorited) {
                        button.classList.add('favorited');
                        button.setAttribute('data-tooltip', 'Remove item from favorites');
                        if (heart) {
                            heart.textContent = '♥';
                        }
                    } else {
                        button.classList.remove('favorited');
                        button.setAttribute('data-tooltip', 'Save item to favorites');
                        if (heart) {
                            heart.textContent = '♡';
                        }
                    }

                    if (button.classList.contains('favorite-btn')) {
                        if (data.is_favorited) {
                            showDetailPopup('Item saved to favorites.', 'success');
                        } else {
                            showDetailPopup('Item removed from favorites.', 'success');
                        }
                    }
                }
            })
            .catch(function () {
                if (button.classList.contains('favorite-btn')) {
                    showDetailPopup('Could not update favorites. Please try again.', 'error');
                }
            });
        });
    });
});