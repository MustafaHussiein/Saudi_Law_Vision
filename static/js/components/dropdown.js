// Dropdown Component
function initDropdowns() {
    document.querySelectorAll('[data-dropdown]').forEach(dropdown => {
        const button = dropdown.querySelector('[data-dropdown-button]');
        const menu = dropdown.querySelector('[data-dropdown-menu]');
        
        button?.addEventListener('click', () => {
            menu?.classList.toggle('hidden');
        });
    });
}

document.addEventListener('DOMContentLoaded', initDropdowns);
