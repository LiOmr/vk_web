const elements = document.querySelectorAll('question.card, answer.card')

for (const component of elements) {
    const scoreValue = component.querySelector('.rating')
    const voteButtons = component.querySelectorAll('button')

    for (const voteButton of voteButtons) {
        voteButton.addEventListener('click', () => {
            const request = new Request('/vote/', {
                method: 'post',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken'),
                },
                body: JSON.stringify({
                    action: voteButton.dataset.action,
                    type: scoreValue.dataset.component,
                    itemId: Number(scoreValue.dataset.componentId),
                })
            })

            fetch(request)
                .then((response) => response.json())
                .then((data) => scoreValue.innerHTML = data.rating)
        })
    }
}
