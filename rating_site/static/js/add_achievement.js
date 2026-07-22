function toggleCategory(cardElement) {
        const checkbox = cardElement.querySelector('.category-checkbox');
        checkbox.checked = !checkbox.checked;

        if (checkbox.checked) {
            cardElement.classList.add('selected');
        } else {
            cardElement.classList.remove('selected');
        }
    }

    // Предпросмотр файлов
    const fileInput = document.getElementById('fileInput');
    const fileList = document.getElementById('fileList');
    const emptyPreviewMsg = document.getElementById('emptyPreviewMsg');
    let filesArray = [];

    fileInput.addEventListener('change', function(e) {
        filesArray = Array.from(e.target.files);
        updateFilePreview();
    });

    function updateFilePreview() {
        fileList.innerHTML = '';

        if (filesArray.length === 0) {
            emptyPreviewMsg.style.display = 'block';
            return;
        }

        emptyPreviewMsg.style.display = 'none';

        filesArray.forEach((file, index) => {
            const fileDiv = document.createElement('div');
            fileDiv.className = 'file-item';

            // Определяем иконку по типу файла
            let icon = '📄';
            if (file.type.startsWith('image/')) {
                icon = '🖼️';
            } else if (file.type === 'application/pdf') {
                icon = '📑';
            }

            const fileSize = (file.size / 1024).toFixed(1);

            fileDiv.innerHTML = `
                ${icon} <span class="file-name">${file.name}</span>
                <span class="text-muted small">(${fileSize} КБ)</span>
                <span class="remove-file" data-index="${index}">✕</span>
            `;

            fileList.appendChild(fileDiv);
        });

        // Добавляем обработчики для удаления файлов
        document.querySelectorAll('.remove-file').forEach(btn => {
            btn.addEventListener('click', function() {
                const index = parseInt(this.dataset.index);
                filesArray.splice(index, 1);

                // Обновляем input
                const dataTransfer = new DataTransfer();
                filesArray.forEach(file => dataTransfer.items.add(file));
                fileInput.files = dataTransfer.files;

                updateFilePreview();
            });
        });
    }

// Валидация перед отправкой
let telegramAlreadySelected = false;
let selectedTelegramId = null;

document.getElementById('achievementForm').addEventListener('submit', async function(e) {
    const form = this;
    const selectedCategories = document.querySelectorAll('.category-checkbox:checked');
    const fileInput = document.getElementById('fileInput');
    const selectedUserTgIdInput = document.getElementById('selectedUserTgId');

    if (selectedCategories.length === 0) {
        e.preventDefault();
        alert('Пожалуйста, выберите хотя бы одну категорию достижения');
        return;
    }

    if (fileInput.files.length === 0) {
        e.preventDefault();
        alert('Пожалуйста, прикрепите хотя бы один файл');
        return;
    }

    if (telegramAlreadySelected) {
        return;
    }

    e.preventDefault();

    const login = form.dataset.userLogin;

    try {
        const response = await fetch(`${window.API_BASE_URL}/get_api_users_tg_accounts_by_login/${login}`);
        const data = await response.json();

        if (!data.ok) {
            alert(data.error || 'Ошибка при получении Telegram-аккаунтов');
            return;
        }

        const telegramAccounts = data.telegram_accounts;

        if (telegramAccounts.length === 0) {
            alert('К вашему профилю не привязан Telegram-аккаунт');
            return;
        }

        if (telegramAccounts.length === 1) {
            selectedUserTgIdInput.value = telegramAccounts[0].id;
            telegramAlreadySelected = true;
            form.submit();
            return;
        }

        showTelegramSelectModal(telegramAccounts, form);

    } catch (error) {
        console.error(error);
        alert('Не удалось получить список Telegram-аккаунтов');
    }
});

function showTelegramSelectModal(telegramAccounts, form) {
    const list = document.getElementById('telegramAccountsList');
    const selectedUserTgIdInput = document.getElementById('selectedUserTgId');

    list.innerHTML = '';
    selectedTelegramId = null;

    telegramAccounts.forEach((account, index) => {
        const item = document.createElement('label');
        item.className = 'list-group-item d-flex align-items-center gap-2';
        item.style.cursor = 'pointer';

        item.innerHTML = `
            <input class="form-check-input me-2" type="radio" name="telegram_choice" value="${account.id}">
            <span>${account.tg_name}</span>
        `;

        list.appendChild(item);

        if (index === 0) {
            const radio = item.querySelector('input');
            radio.checked = true;
            selectedTelegramId = account.id;
        }
    });

    list.querySelectorAll('input[name="telegram_choice"]').forEach(radio => {
        radio.addEventListener('change', function() {
            selectedTelegramId = this.value;
        });
    });

    const modalElement = document.getElementById('telegramSelectModal');
    const modal = new bootstrap.Modal(modalElement);

    document.getElementById('confirmTelegramBtn').onclick = function() {
        if (!selectedTelegramId) {
            alert('Выберите Telegram-аккаунт');
            return;
        }

        selectedUserTgIdInput.value = selectedTelegramId;
        telegramAlreadySelected = true;
        modal.hide();
        form.submit();
    };

    modal.show();
}