document.addEventListener("DOMContentLoaded", async () => {
    const groupId = window.currentUserGroup
    try {
        const response = await fetch(`${window.API_BASE_URL}/get_api_users_rating_by_group/${encodeURIComponent(groupId)}`);
        const data = await response.json();

        const table_body = document.getElementById('grades_table_body');

        if (data.users && data.users.length > 0) { //Пока что только для академика// Уже нет))
            let html = '';
            data.users.forEach((user, index) => {
                html += `
                    <tr>
                        <th scope="row">${index + 1}</th>
                        <td><strong>${user.user_name}</strong></td>
                        <td>${user.weighted_grade_group_by_activity.study_activity}</td>
                        <td>${user.weighted_grade_group_by_activity.science_activity}</td>
                        <td>${user.weighted_grade_group_by_activity.social_activity}</td>
                        <td>${user.weighted_grade_group_by_activity.culture_activity}</td>
                        <td><strong>${user.weighted_grade_group_by_activity.general_weighted_rating}</strong></td>
                    </tr>
                `;
            });
            table_body.innerHTML = html;
        } else {
            table_body.innerHTML = `
                <tr>
                    <td colspan="7" class="text-center">Нет данных о студентах</td>
                </tr>
            `;
        }
    } catch (error) {
        console.error("Ошибка загрузки:", error);
        document.getElementById("grades_table_body").innerHTML = `
            <tr>
                <td colspan="7" class="text-center">Ошибка загрузки данных</td>
            </tr>
        `;
    }
});