document.addEventListener('DOMContentLoaded', function () {
    const ratingForm = document.querySelector('#rating-form');
    if (!ratingForm) return;

    const starInputs = ratingForm.querySelectorAll('input[name="score"]');
    const csrfToken = ratingForm.querySelector('[name=csrfmiddlewaretoken]').value;

    const averageRatingText = document.querySelector('#average-rating-text');
    const ratingCountText = document.querySelector('#rating-count-text');
    const userRatingText = document.querySelector('#user-rating-text');
    const ratingStatus = document.querySelector('#rating-status');

    starInputs.forEach(input => {
        input.addEventListener('change', function () {
            const selectedScore = this.value;

            const formData = new FormData();
            formData.append('score', selectedScore);

            fetch(ratingForm.action, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrfToken,
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    if (data.average_rating !== null) {
                        averageRatingText.classList.remove('d-none');
                        averageRatingText.innerHTML = `<strong>${data.average_rating}/5</strong> average rating`;

                        ratingCountText.textContent =
                            `Based on ${data.rating_count} rating${data.rating_count === 1 ? '' : 's'}`;
                    } else {
                        averageRatingText.classList.add('d-none');
                        averageRatingText.innerHTML = '';
                        ratingCountText.textContent = 'No ratings yet.';
                    }

                    userRatingText.textContent = `Your current rating: ${data.user_rating}/5`;
                    ratingStatus.textContent = 'Rating saved!';
                } else {
                    ratingStatus.textContent = data.error || 'Something went wrong.';
                }
            })
            .catch(() => {
                ratingStatus.textContent = 'Could not save rating. Please try again.';
            });
        });
    });
});