document.addEventListener("DOMContentLoaded", async () => {
    const login = window.currentUserLogin
    try {
        const response = await fetch(`${window.API_BASE_URL}/get_api_user_data/${encodeURIComponent(login)}`);
        const data = await response.json();

        document.getElementById("user_fio").textContent = data.user_fio || "Нет данных";
        document.getElementById("user_group").textContent = data.user_group || "Нет данных";
        const telegramsContainer = document.getElementById("linked_telegrams");

        if (data.linked_telegrams && Array.isArray(data.linked_telegrams) &&
         data.linked_telegrams.length > 0) {
         let html = '<ul class="list-unstyled mb-0">';
         data.linked_telegrams.forEach(tg => {
            const safeTg = tg.replace(/[&<>]/g, function(m) {
                if (m === '&') return '&amp;';
                if (m === '<') return '&lt;';
                if (m === '>') return '&gt;';
                return m;
            });
            html += `<li>${safeTg}</li>`;
         });
         html += '</ul>';
         telegramsContainer.innerHTML = html;
         } else {
            telegramsContainer.textContent = "Нет данных";
         }

    } catch (error) {
        console.error("Ошибка загрузки:", error);

    }
});