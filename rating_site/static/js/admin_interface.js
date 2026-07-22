document.addEventListener('DOMContentLoaded', function () {
    const groupButtonsContainer = document.getElementById("groupButtons");
    const adminInterface = document.getElementById("adminInterface");

    const saveWeightsUrl = adminInterface.dataset.saveWeightsUrl;

    let activeGroup = "";
    let activeGroupId = null;
    let allGroupsSelected = false;

    const selectedGroupText = document.getElementById('selectedGroupText');
    const selectedGroupBadge = document.getElementById('selectedGroupBadge');
    const ratingSection = document.getElementById('ratingSection');
    const pendingButton = document.getElementById('pendingAchievementsButton');
    const saveButton = document.getElementById('saveWeightsButton');
    const toast = document.getElementById('adminToast');
    const table = document.getElementById('adminRatingTable');
    let toastTimer = null;

    function getGroupButtons() {
        return Array.from(
            groupButtonsContainer.querySelectorAll(".group-button"),
        );
    }

    function showToast(message) {
        toast.textContent = message;
        toast.classList.add('show');
        window.clearTimeout(toastTimer);
        toastTimer = window.setTimeout(function () {
            toast.classList.remove('show');
        }, 2200);
    }

    function filterRowsByGroup(groupName) {
        const rows = document.querySelectorAll('#grades_table_body tr[data-group]');

        rows.forEach(function (row) {
            row.hidden = row.dataset.group !== groupName;
        });
    }

    function selectGroup(button) {
        const groupButtons = getGroupButtons()

        groupButtons.forEach(function (item) {
            item.classList.remove('active');
            item.setAttribute('aria-pressed', 'false');
        });

        button.classList.add('active');
        button.setAttribute('aria-pressed', 'true');

        activeGroup = button.dataset.group;
        allGroupsSelected = button.dataset.allGroups === "true";

        const params = new URLSearchParams();

        if (allGroupsSelected) {
            activeGroupId = "all";

            params.set("all_groups", "1");
        } else {
            activeGroupId = Number(button.dataset.groupId);

            params.set("group_id", String(activeGroupId));
            params.set("group_name", activeGroup);
        }

        selectedGroupText.textContent = activeGroup;
        selectedGroupBadge.textContent = activeGroup;

        window.history.replaceState(null, "", "?" + params.toString());

        document.dispatchEvent(new CustomEvent('rating:group-change', {
            detail: {
                group: activeGroup,
                groupId: activeGroupId,
                allGroups: allGroupsSelected,
            },
        }));
    }

    function initializeGroupSelection() {
        const groupButtons = getGroupButtons();

        if (groupButtons.length === 0) {
            return;
        }

        const params = new URLSearchParams(
            window.location.search,
        );

        const allGroupsFromUrl = params.get("all_groups") === "1";
        const groupIdFromUrl = params.get("group_id");

        let initialButton = null;

        if (allGroupsFromUrl) {
            initialButton = groupButtons.find(
                function(button) {
                    return (button.dataset.allGroups === "true");
                }
            );
        } else if (groupIdFromUrl) {
            initialButton = groupButtons.find(
                function(button) {
                    return (button.dataset.groupId === groupIdFromUrl);
                }
            );
        }

        if (!initialButton) {
            initialButton = groupButtons[0];
        }

        selectGroup(initialButton);
    }

    groupButtonsContainer.addEventListener(
        "click",
        function (event) {
            const button = event.target.closest(".group-button");

            if (!button) {
                return;
            }

            selectGroup(button);

            if (button.dataset.allGroups === "true") {
                showToast("Выбраны все группы");
            } else {
                showToast("Выбрана группа: " + button.dataset.group);
            }
        },
    );

    document.addEventListener(
        "groups:loaded",
        function () {
            initializeGroupSelection();
        },
    );

    initializeGroupSelection();

    pendingButton.addEventListener('click', function () {
        ratingSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
        showToast('Открыт список студентов и достижений для проверки');

        document.dispatchEvent(new CustomEvent('rating:pending-open'));
    });

    saveButton.addEventListener("click", async function () {
        const weights = {
            academic: Number(
                document.getElementById("academicWeight").value
            ),
            science: Number(
                document.getElementById("scienceWeight").value
            ),
            social: Number(
                document.getElementById("socialWeight").value
            ),
            cultural: Number(
                document.getElementById("culturalWeight").value
            ),
        };

        const invalidValue = Object.values(weights).some(
            function (value) {
                return !Number.isFinite(value) || value < 0;
            }
        );

        if (invalidValue) {
            showToast("Вес должен быть числом не меньше нуля");
            return;
        }

        const csrfToken = document.querySelector(
            "#csrfTokenForm input[name='csrfmiddlewaretoken']"
        ).value;

        saveButton.disabled = true;
        saveButton.textContent = "Сохранение...";

        try {
            const response = await fetch(
                saveWeightsUrl,
                {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        "X-CSRFToken": csrfToken,
                    },
                    body: JSON.stringify(weights),
                }
            );

            const result = await response.json();

            if (!response.ok) {
                throw new Error(
                    result.message ||
                    `Ошибка HTTP ${response.status}`
                );
            }

            saveButton.textContent = "Сохранено";
            saveButton.classList.remove("btn-primary");
            saveButton.classList.add("btn-success");

            showToast(result.message);

            document.dispatchEvent(
                new CustomEvent("rating:weights-save", {
                    detail: {
                        group: activeGroup,
                        groupId: activeGroupId,
                        weights: weights,
                    },
                })
            );

            window.setTimeout(function () {
                saveButton.textContent = "Сохранить";
                saveButton.classList.remove("btn-success");
                saveButton.classList.add("btn-primary");
            }, 1800);

        } catch (error) {
            console.error("Ошибка сохранения весов:", error);

            saveButton.textContent = "Сохранить";
            showToast(error.message);

        } finally {
            saveButton.disabled = false;
        }

    });

    table.querySelectorAll('thead th.sortable').forEach(function (header) {
        let ascending = true;

        header.addEventListener('click', function () {
            const columnIndex = Number(header.dataset.column);
            const tbody = table.querySelector('tbody');
            const rows = Array.from(tbody.querySelectorAll('tr')).filter(function (row) {
                return row.cells.length > columnIndex && !row.querySelector('td[colspan]');
            });

            rows.sort(function (firstRow, secondRow) {
                const firstValue = firstRow.cells[columnIndex].textContent.trim();
                const secondValue = secondRow.cells[columnIndex].textContent.trim();
                const firstNumber = Number(firstValue.replace(',', '.'));
                const secondNumber = Number(secondValue.replace(',', '.'));

                if (Number.isFinite(firstNumber) && Number.isFinite(secondNumber)) {
                    return ascending ? firstNumber - secondNumber : secondNumber - firstNumber;
                }

                return ascending
                    ? firstValue.localeCompare(secondValue, 'ru')
                    : secondValue.localeCompare(firstValue, 'ru');
            });

            rows.forEach(function (row) {
                tbody.appendChild(row);
            });

            ascending = !ascending;
        });
    });
});