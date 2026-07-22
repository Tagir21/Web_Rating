document.addEventListener("DOMContentLoaded", function () {
    const tableBody = document.getElementById("grades_table_body");

    let lastRequestedGroup = null;

    function getGroupFromUrl() {
        const params = new URLSearchParams(window.location.search);
        return params.get("group_id");
    }

    function escapeHtml(value) {
        const element = document.createElement("div");
        element.textContent = String(value ?? "");
        return element.innerHTML;
    }

    function formatNumber(value) {
        const number = Number(value);

        if (!Number.isFinite(number)) {
            return "0";
        }

        return number.toFixed(2).replace(/\.00$/, "");
    }

    function showMessage(message) {
        tableBody.innerHTML = `
            <tr>
                <td colspan="8" class="text-center py-4">
                    ${message}
                </td>
            </tr>
        `;
    }

    function renderRatingTable(users) {
        if (!Array.isArray(users) || users.length === 0) { //Пока что только для академика// Уже нет))
                showMessage("В этой группе нет студентов");
                return;
            }

            let html = "";

            users.forEach(function (user, index) {
                html += `
                    <tr>
                        <th scope="row">${index + 1}</th>
                        <td><strong>${escapeHtml(user.user_name)}</strong></td>
                        <td>${formatNumber(user.grade_group_by_activity.study_activity)}</td>
                        <td>${formatNumber(user.grade_group_by_activity.science_activity)}</td>
                        <td>${formatNumber(user.grade_group_by_activity.social_activity)}</td>
                        <td>${formatNumber(user.grade_group_by_activity.culture_activity)}</td>
                        <td><strong>${formatNumber(user.grade_group_by_activity.general_rating)}</strong></td>
                        <td><strong>${formatNumber(user.weighted_grade_group_by_activity.general_weighted_rating)}</strong></td>
                    </tr>
                `;
            });

            tableBody.innerHTML = html;
    }

    async function loadRating(groupId, forceReload=false) {
        if (!groupId) {
            showMessage("Группа не выбрана");
            return;
        }

        if (!forceReload && groupId === lastRequestedGroup) {
            return;
        }

        showMessage("Загрузка данных...");
        lastRequestedGroup = groupId;

        try {
            const response = await fetch(`${window.API_BASE_URL}/get_api_users_rating_by_group/${encodeURIComponent(groupId)}`);

            const data = await response.json();

            if (!response.ok) {
                throw new Error(`Ошибка HTTP: ${response.status}`);
            }


            const users = data.users;

            renderRatingTable(users);

        } catch(error) {
            console.error("Ошибка загрузки:", error);
            lastRequestedGroup = null;
            showMessage("Не удалось загрузить таблицу рейтинга");
        }
    }

    const initialGroup = getGroupFromUrl();

    if (initialGroup) {
        loadRating(initialGroup);
    }

    document.addEventListener(
        "rating:group-change",
        function(event) {
            const groupId = event.detail.groupId;
            loadRating(groupId);
        }
    );

    document.addEventListener(
        "rating:weights-save",
        function(event) {
            const groupId = event.detail.groupId || getGroupFromUrl();
            loadRating(groupId, true);
        }
    );
});