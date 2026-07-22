document.addEventListener("DOMContentLoaded", async () => {
    const container = document.getElementById('groupButtons');
    try {
        const response = await fetch(`${window.API_BASE_URL}/get_api_all_groups`, {
            headers: {
                Accept: "application/json",
            },
        });

        const data = await response.json();
        const groups = data.groups;

        if (!Array.isArray(groups) || groups.length === 0) { //Пока что только для академика// Уже нет))
            container.innerHTML = `
                <span class="text-muted">
                    Учебные группы не найдены
                </span>
            `;
        } else {
            container.innerHTML = "";

            groups.forEach((group, index) => {
                const button = document.createElement("button");

                button.type = "button";
                button.className = "btn group-button";
                button.dataset.group = group.name;
                button.dataset.groupId = group.id;
                button.textContent = group.name;
                button.dataset.allGroups = "false";
                button.setAttribute("aria-pressed", "false");

                if (index === 0) {
                    button.classList.add("active");
                    button.setAttribute("aria-pressed", "true");
                }

                container.appendChild(button);
            });

            const allGroupsButton = document.createElement("button");
            allGroupsButton.type = "button";
            allGroupsButton.className = "btn group-button";
            allGroupsButton.textContent = "Все";

            allGroupsButton.dataset.group = "Все";
            allGroupsButton.dataset.groupId = "all";
            allGroupsButton.dataset.allGroups = "true";
            allGroupsButton.setAttribute("aria-pressed", "false");

            container.appendChild(allGroupsButton);


            document.dispatchEvent(
                new CustomEvent("groups:loaded", {
                    detail: {
                        groups: groups,
                    },
                }),
            );
        }
    } catch (error) {
        console.error("Ошибка загрузки групп:", error);
        container.innerHTML = `
            <span class="text-danger">
                Не удалось загрузить учебные группы
            </span>
        `;
    }
});