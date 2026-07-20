document.addEventListener("DOMContentLoaded", function () => {
    const tableBody = document.getElementById("grades_table_body");

    function showMessage(message) {
        tableBody.innerHTML = `
            <tr>
                <td colspan="8" class="text-center" py="4">
                    ${message}
                </td>
            </tr>
        `;
    }

    async function loadRating(groupName) {
        if (!groupName) {
            showMessage("Группа не выбрана");
            return;
        }

        showMessage("Загрузка данных...");

        try {
            const response = await fetch(`http://127.0.0.1:8000/get_api_admin_users_rating_by_group/${encodeURIComponent(groupId)}`);
            if (!response.ok) {
                throw new Error(`Ошибка HTTP: ${response.status}`);
            }

            const data = await response.json();
            const users = data.users;

            if (!Array.isArray(groups) || groups.length === 0) { //Пока что только для академика// Уже нет))
                showMessage("В этой группе нет студентов");
                return;
            }

            let html = "";

            users.forEach(function (user, index) {
                html += `
                    <tr>
                        <th scope="row">${index + 1}</th>
                        <td><strong>${user.user_name}</strong></td>
                        <td>${user.grade_group_by_activity.study_activity}</td>
                        <td>${user.grade_group_by_activity.science_activity}</td>
                        <td>${user.grade_group_by_activity.social_activity}</td>
                        <td>${user.grade_group_by_activity.culture_activity}</td>
                        <td><strong>${user.grade_group_by_activity.general_rating}</strong></td>
                        <td><strong>${user.grade_group_by_activity.weighted_rating}</strong></td>
                    </tr>
                `;
            });

            tableBody.innerHTML = html;
        } catch(error) {
            console.error("Ошибка загрузки:", error);
            showMessage("Не удалось загрузить таблицу рейтинга");
        }
    }

    document.addEventListener(
        "rating:group-change",
        function(event) {
            const groupName = event.detail.group;

            loadRating(groupName);
        }
    );

    const groupFromUrl = new URLSearchParams(
        window.location.search
    ).get("group")

    if (groupFromUrl) {
        loadRating(groupFromUrl);
    }
});