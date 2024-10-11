// keyboard.js
document.addEventListener('DOMContentLoaded', () => {
    const searchBox = document.getElementById('search-query');
    const keyboardContainer = document.getElementById('keyboard-container');
    let input = [];

    // Show the keyboard when the search box is focused
    searchBox.addEventListener('focus', () => {
        keyboardContainer.style.display = 'block';
    });

    // Add event listeners to each key on the virtual keyboard
    document.querySelectorAll('.key').forEach(key => {
        key.addEventListener('click', (event) => {
            const keyValue = event.target.getAttribute('data-key');

            if (keyValue === 'Backspace') {
                input.pop();
            } else if (keyValue === 'Clear') {
                input = [];
            } else {
                input.push(keyValue);
            }

            // Check if Hangul object is defined
            if (typeof Hangul !== 'undefined') {
                const assembledText = Hangul.assemble(input);
                searchBox.value = assembledText;
            } else {
                console.error('Hangul.js is not defined');
            }
        });
    });

    // Hide the keyboard when clicking outside of it or the search box
    document.addEventListener('click', (event) => {
        if (!keyboardContainer.contains(event.target) && event.target !== searchBox) {
            keyboardContainer.style.display = 'none';
        }
    });

    // Prevent the search box from losing focus when interacting with the keyboard
    keyboardContainer.addEventListener('mousedown', (event) => {
        event.preventDefault();
    });
});
