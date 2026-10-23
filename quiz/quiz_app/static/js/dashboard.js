const button = document.getElementById("hamburger");
const menu = document.getElementById("nav-links");

button.addEventListener("click", function () {
    menu.classList.toggle("show");

    const isOpen = menu.classList.contains("show");
    button.setAttribute("aria-expanded", isOpen);
    button.textContent = isOpen ? "✕" : "☰";
});