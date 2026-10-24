
document.addEventListener("DOMContentLoaded", function () {

    const hamburger = document.getElementById("hamburger-menu");
    const menu = document.getElementById("dashboard-menu");

    if (!hamburger || !menu) {
        return;
    }

    hamburger.addEventListener("click", function () {

        const isOpen = menu.classList.toggle("show");

        hamburger.classList.toggle("active", isOpen);
        hamburger.setAttribute("aria-expanded", String(isOpen));

    });

    // Close menu after clicking a navigation link
    menu.querySelectorAll("a").forEach(function (link) {

        link.addEventListener("click", function () {

            menu.classList.remove("show");
            hamburger.classList.remove("active");
            hamburger.setAttribute("aria-expanded", "false");

        });

    });

});

