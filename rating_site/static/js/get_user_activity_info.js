document.addEventListener("DOMContentLoaded", async () => {
    const login = window.currentUserLogin
    try {
        const response = await fetch(`${window.API_BASE_URL}/get_api_users_activity_info_by_login/${encodeURIComponent(login)}`);
        const data = await response.json();

        const user_activity = data.user_activity_info

        document.getElementById("user_general_rating").textContent = user_activity.general_rating ?? "Нет данных";

        document.getElementById("user_study_activity").textContent = user_activity.study_activity ?? "Нет данных";
        document.getElementById("user_science_activity").textContent = user_activity.science_activity ?? "Нет данных";
        document.getElementById("user_social_activity").textContent = user_activity.social_activity ?? "Нет данных";
        document.getElementById("user_culture_activity").textContent = user_activity.culture_activity ?? "Нет данных";

    } catch (error) {
        console.error("Ошибка загрузки:", error);
        document.getElementById("achievements_table_body").innerHTML = `
            <tr>
                <td colspan="7" class="text-center">Ошибка загрузки данных</td>
            </tr>
        `;
    }
});