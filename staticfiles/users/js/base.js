
document.addEventListener('DOMContentLoaded', function() {
    console.log('TwoMove cargado correctamente');
    

});

window.addEventListener('scroll', function() {
    const header = document.querySelector('header');
    if (window.scrollY > 50) {
        header.style.boxShadow = '0 6px 25px rgba(0,0,0,0.15)';
    } else {
        header.style.boxShadow = '0 4px 20px rgba(0,0,0,0.12)';
    }
});