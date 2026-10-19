// Скрипты веб-интерфейса: подсветка текущего раздела и быстрый поиск по таблице.
document.addEventListener("DOMContentLoaded", () => {
    // 1. Подсветить пункт меню текущего раздела.
    const path = window.location.pathname;
    document.querySelectorAll(".site-nav .nav-link").forEach((link) => {
        const href = link.getAttribute("href");
        const isHome = href === "/";
        if ((isHome && path === "/") || (!isHome && path.startsWith(href))) {
            link.classList.add("active");
        }
    });

    // 2. Фильтрация строк таблицы по введённому тексту (без перезагрузки страницы).
    document.querySelectorAll("[data-table-filter]").forEach((input) => {
        const table = document.querySelector(input.dataset.tableFilter);
        if (!table) return;
        input.addEventListener("input", () => {
            const query = input.value.trim().toLowerCase();
            table.querySelectorAll("tbody tr").forEach((row) => {
                row.hidden = query !== "" && !row.textContent.toLowerCase().includes(query);
            });
        });
    });
});
