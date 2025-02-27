document.addEventListener("DOMContentLoaded", function () {
    const navItems = document.querySelectorAll(".nav-item");

    // Восстанавливаем активный раздел из localStorage
    const activePage = localStorage.getItem("activeNav");
    if (activePage) {
        navItems.forEach(nav => nav.classList.remove("active"));
        document.querySelector(`.nav-item[href="${activePage}"]`)?.classList.add("active");
    }

    navItems.forEach(item => {
        item.addEventListener("click", function () {
            navItems.forEach(nav => nav.classList.remove("active")); // Удаляем у всех
            this.classList.add("active"); // Добавляем активный

            // Сохраняем в localStorage
            localStorage.setItem("activeNav", this.getAttribute("href"));
        });
    });
});
