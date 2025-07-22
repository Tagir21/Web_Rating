document.addEventListener("DOMContentLoaded", async () => {
    try {
        const response = await fetch("localhost:8000/get_all_akademy_grades");
        const data = await response.json();

        const table_body = document.getElementById('grades_table_body');

        if (data.akademy_grades && data.akademy_grades.length > 0) { // Пока что только для академика
            let html = '';
            data.grades.forEach((akademy_grade, index) => {
                html += '
                    <tr>
                        <th scope="row">${index + 1}></th>
                        <td>{akademy_grade.user_id}</td>
                        <td>{akademy_grade.grade}</td>
                    </tr>
                ';
            });
            table_body.innerHTML = html;
        } else {
            table_body.innerHTML = '
                <tr>
                    <td cosplan="3" class="text-center">Нет данных о студентах</td>
                </tr>
            ';
        }
    } catch (error) {
        console.error("Ошибка загрузки:", error);
        document.getElementById("grades_table_body").innerHTML = '
            <tr>
                <td cosplan="3" class="text-center">Ошибка загрузки данных</td>
            </tr>
        ';
    }
}