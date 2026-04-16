document.addEventListener("DOMContentLoaded", async () => {
    try {
        const response = await fetch("http://127.0.0.1:8000/get_api_all_users");
        const data = await response.json();

        const table_body = document.getElementById('grades_table_body');

        if (data.users && data.users.length > 0) { //Пока что только для академика// Уже нет))
            let html = '';
            data.users.forEach((user, index) => {
                html += `
                    <tr>
                        <th scope="row">${index + 1}</th>
                        <td>${user.user_name}</td>
                        <td>${user.grade}</td>
                    </tr>
                `;
            });
            table_body.innerHTML = html;
        } else {
            table_body.innerHTML = `
                <tr>
                    <td colspan="7" class="text-center">Нет данных о студенте</td>
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