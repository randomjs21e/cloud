// Cloud - main JS
document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('[data-dismiss]').forEach(function (el) {
        setTimeout(function () {
            el.style.transition = 'opacity 0.3s';
            el.style.opacity = '0';
            setTimeout(function () { el.remove(); }, 300);
        }, 4000);
    });
});
