document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('editForm');
    const employeeId = document.getElementById('employeeId').value;

    const lastName = document.getElementById('lastName');
    const firstName = document.getElementById('firstName');
    const middleName = document.getElementById('middleName');
    const phone = document.getElementById('phone');
    const birthDate = document.getElementById('birthDate');
    const sex = document.getElementById('sex');
    const photoInput = document.getElementById('photo');
    const photoPreview = document.getElementById('photoPreviewImg');
    const avatarImg = document.getElementById('avatarImage');
    const status = document.getElementById('employeeStatus');


    const saveBtn = document.getElementById('saveBtn');
    const saveDraftBtn = document.getElementById('saveDraftBtn');
    const cancelBtn = document.getElementById('cancelBtn');


    const deleteBtn = document.getElementById('deleteBtn');

    const locationRedirect = '/';
    const API_BASE = '/api/v1/employees';
    const API_STATIC = '/static'
    const IMAGE_MINI_DEFAULT = 'images/default/default_mini.png';
    const IMAGE_DEFAULT = 'images/default/default.png';

    

deleteBtn.addEventListener('click', async () => {
    const confirmed = confirm('Вы уверены, что хотите удалить этого сотрудника?');
    if (!confirmed) return;

    try {
        const response = await fetch(`${API_BASE}/${employeeId}`, {
            method: 'DELETE',
        });

        if (!response.ok) {
            const error = await response.text();
            throw new Error(error || 'Ошибка удаления');
        }

        window.location.href = locationRedirect;
    } catch (error) {
        alert(error.message);
    }
    });



    // --- Загрузка данных сотрудника ---
    async function loadEmployee() {
        try {
            const response = await fetch(`${API_BASE}/${employeeId}`);
            if (!response.ok) throw new Error('Сотрудник не найден');
            const emp = await response.json();

            lastName.value = emp.last_name || '';
            firstName.value = emp.first_name || '';
            middleName.value = emp.middle_name || '';
            phone.value = emp.phone || '';
            birthDate.value = emp.birth_date || '';
            sex.value = emp.sex || '';
        
            if (emp.image) {
                avatarImg.src = `${API_STATIC}/${emp.image}`;
                
                }

            if (emp.draft) {
                    status.textContent = 'Черновик';
                    status.className = 'employee-status draft';
            } else {
                    status.textContent = 'Опубликован';
                    status.className = 'employee-status published';
            }
        } catch (error) {
            console.error('Ошибка загрузки:', error);
            alert('Не удалось загрузить данные сотрудника');
            window.location.href = locationRedirect;
        }
    }

    // --- Превью фото ---
    photoInput.addEventListener('change', (e) => {
        const file = e.target.files[0];
        if (!file) return;

        if (file.size > 200 * 1024) {
            alert('Размер фото не должен превышать 200 КБ');
            photoInput.value = '';
            return;
        }

        const reader = new FileReader();
        reader.onload = (ev) => {
            photoPreview.src = ev.target.result;
            photoPreview.style.display = 'block';
        };
        reader.readAsDataURL(file);
    });

    // --- Отправка формы ---
    async function submitForm(draft = false) {
        const data = {
            last_name: lastName.value,
            first_name: firstName.value,
            middle_name: middleName.value,
            sex: sex.value,
            phone: phone.value,
            birth_date: birthDate.value || null,
            draft: draft,
        };
        
        try {
            const response = await fetch(`${API_BASE}/${employeeId}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data),
            });

            if (!response.ok) {
                const error = await response.text();
                throw new Error(error || 'Ошибка сохранения');
            }

            const photoFile = photoInput.files[0];
            if (photoFile) {
                const formData = new FormData();
                formData.append('file', photoFile);
    
                const photoResponse = await fetch(`/api/v1/employees/${employeeId}/upload-photo`, {
                    method: 'POST',
                    body: formData,
                });
    
                if (!photoResponse.ok) {
                    const error = await photoResponse.text();
                    throw new Error(error || 'Ошибка загрузки фото');
                }
            }

            window.location.href = locationRedirect;
        } catch (error) {
            console.error('Ошибка:', error);
            alert(error.message);
        }
    }

    // --- События ---
    form.addEventListener('submit', (e) => {
        e.preventDefault();
        submitForm(false);
    });

    saveDraftBtn.addEventListener('click', () => {
        submitForm(true);
    });

    cancelBtn.addEventListener('click', () => {
        if (confirm('Вы уверены, что хотите отменить изменения?')) {
            window.location.href = locationRedirect;
        }
    });

    // --- Загрузка данных при старте ---
    loadEmployee();
});