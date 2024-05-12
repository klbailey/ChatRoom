// Store>static>js>index.js
document.addEventListener('DOMContentLoaded', function () {
    const buyButtons = document.querySelectorAll('.product button[id^="buy_button_"]');
    console.log('Buy buttons found:', buyButtons.length);
    
    buyButtons.forEach(button => {
        button.addEventListener('click', function () {
            console.log('Button clicked!');
            const productId = this.id.split('_')[2];
            console.log('Product ID:', productId);
        });
    });
});
