document.addEventListener("DOMContentLoaded", async () => {
    const login = window.currentUserLogin
    try {
        const response = await fetch(`${window.API_BASE_URL}/get_api_user_achievements_by_login/${encodeURIComponent(login)}`);
        const data = await response.json();

        const table_body = document.getElementById('achievements_table_body');

        if (data.achievements && data.achievements.length > 0) { //Пока что только для академика// Уже нет))
            let html = '';
            data.achievements.forEach((achievement, index) => {
                html += `
                    <tr>
                        <th scope="row">${index + 1}</th>
                        <td>${achievement.categories}</td>
                        <td>${achievement.status}</td>
                        <td>${achievement.grade}</td>
                        <td>${achievement.weighted_grade}</td>
                    </tr>
                `;
            });
            table_body.innerHTML = html;
        } else {
            table_body.innerHTML = `
                <tr>
                    <td colspan="7" class="text-center">Нет данных о достижениях</td>
                </tr>
            `;
        }
    } catch (error) {
        console.error("Ошибка загрузки:", error);
        document.getElementById("achievements_table_body").innerHTML = `
            <tr>
                <td colspan="7" class="text-center">Ошибка загрузки данных</td>
            </tr>
        `;
    }
});