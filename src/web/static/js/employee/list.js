document.addEventListener('DOMContentLoaded', () => {
    const employees = [];
    let currentPage = 1;
    let perPage = 10;

    const tbody = document.getElementById('employeeTableBody');
    const paginationControls = document.getElementById('paginationControls');
    const searchInput = document.getElementById('searchInput');
    const maleCheckbox = document.getElementById('filterMale');
    const femaleCheckbox = document.getElementById('filterFemale');
    const ageFromField = document.getElementById('ageFrom');
    const ageToField = document.getElementById('ageTo');
    const perPageButtons = document.querySelectorAll('.per-page-btn');
    const showDraftsCheckbox = document.getElementById('showDrafts');

    const API_BASE = "/api/v1/employees";
    const API_SATIC = "static";
    const IMAGE_MINI_DEFAULT = 'images/default/default_mini.png';
    const IMAGE_DEFAULT = 'images/default/default.png';

    perPageButtons.forEach(btn => {
        btn.addEventListener('click', (e) => {
            // Убираем active у всех
            perPageButtons.forEach(b => b.classList.remove('active'));
            // Ставим active на текущую кнопку
            e.currentTarget.classList.add('active');
            // Меняем perPage
            perPage = parseInt(e.currentTarget.dataset.perPage);
            // Сбрасываем на первую страницу
            currentPage = 1;
            applyFiltersAndRender();
        });
    });

    function debounce(fn, delay) {
        let timer;
        return function(...args) {
            clearTimeout(timer);
            timer = setTimeout(() => fn.apply(this, args), delay);
        };
    }

    showDraftsCheckbox.addEventListener('change', () => {
        currentPage = 1;
        applyFiltersAndRender();
    });

    maleCheckbox.addEventListener('change', () => {
        currentPage = 1;
        applyFiltersAndRender();
    });
    
    femaleCheckbox.addEventListener('change', () => {
        currentPage = 1;
        applyFiltersAndRender();
    });

    searchInput.addEventListener('input', debounce(() => {
        currentPage = 1;
        applyFiltersAndRender();
    }, 300));

    ageFromField.addEventListener('change', () => {
        currentPage = 1;
        applyFiltersAndRender();
    });

    ageToField.addEventListener('change', () => {
        currentPage = 1;
        applyFiltersAndRender();
    });

    async function applyFiltersAndRender() {
        const search = searchInput.value.trim(); //.toLowerCase()
        const showMale = maleCheckbox.checked;
        const showFemale = femaleCheckbox.checked;
        const showDrafts = showDraftsCheckbox.checked;
        const ageFrom = ageFromField.value;
        const ageTo = ageToField.value;
        const data = await fetchEmployees( currentPage,
                                           perPage, 
                                           showDrafts,
                                           showMale,
                                           showFemale,
                                           ageFrom,
                                           ageTo,
                                           search);
        const total =data.total;        
        renderTable(data.employees);
        renderPagination(total, currentPage);
    }

    function renderTable(data) {
        if (data.length === 0) {
            tbody.innerHTML = `<tr><td colspan="7" style="text-align:center; padding:40px; color:#94a3b8;">Сотрудники не найдены</td></tr>`;
            return;
        }

        tbody.innerHTML = data.map(emp => {
            const sexClass = emp.sex === 'муж.' ? 'sex-male' : 'sex-female';
            const isDraft = emp.draft === true;
            const draftClass = isDraft ? 'draft-row' : '';
            return `
            <tr class="${draftClass}">
                <td>${emp.id}</td>
                <td>
                    <div class="avatar-wrapper">
                        <img src="${API_SATIC}/${emp.image_mini}" alt="Фото" loading="lazy">
                    </div>
                </td>
                <td><strong>${emp.full_name}</strong></td>
                <td>${emp.age ? `${emp.age} лет` : ''}</td>
                <td>${emp.phone}</td>
                <td class="${sexClass}">${emp.sex}</td>
                <td>
                    <div class="actions">
                        <button class="btn-icon edit-btn" data-id="${emp.id}">✏️</button>
                        <button class="btn-icon delete-btn" data-id="${emp.id}">🗑️</button>
                    </div>
                </td>
            </tr>
        `}).join('');

        // Обработчики для кнопок удаления
        document.querySelectorAll('.delete-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const id = parseInt(e.currentTarget.dataset.id);
                if (confirm(`Вы уверены, что хотите удалить сотрудника #${id}?`)) {
                    deleteEmployee(id);
                }
            });
        });

        // Обработчики для кнопок редактирования
        document.querySelectorAll('.edit-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const id = parseInt(e.currentTarget.dataset.id);
                window.location.href = `/${id}`;
            });
        });
    }


    

    //  Кнопки страниц
    function renderPagination(totalItems, current) {
        
        const totalPages = Math.ceil(totalItems / perPage) || 1;
    
        let html = '';
    
        // Кнопка "Назад"
        html += `<button class="page-btn" data-page="${current - 1}" ${current <= 1 ? 'disabled' : ''}>←</button>`;
    
        // Номера страниц
        for (let i = 1; i <= totalPages; i++) {
            html += `<button class="page-btn ${i === current ? 'active' : ''}" data-page="${i}">${i}</button>`;
        }
    
        // Кнопка "Вперёд"let filteredEmployees = [...employees];
        html += `<button class="page-btn" data-page="${current + 1}" ${current >= totalPages ? 'disabled' : ''}>→</button>`;
    
        paginationControls.innerHTML = html;
    
        // Обработчики для всех кнопок (кроме disabled)
        document.querySelectorAll('.page-btn:not([disabled])').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const page = parseInt(e.currentTarget.dataset.page);
                if (page && page !== current) {
                    currentPage = page;
                    applyFiltersAndRender();
                }
            });
        });
    }

    // Эвент на добавление сотрудников
    document.getElementById('addBtn').addEventListener('click', async () => {
        const response = await fetch(`/api/v1/employees/`, {method: "POST"});

      if (!response.ok) throw new Error('Что-то пошло не так');
      const emp = await response.json();
     window.location.href = `/${emp.id}`;

    });


    async function deleteEmployee(id) {
        const url = `${API_BASE}/${id}`;
    
        try {
            const response = await fetch(url, {
                method: "DELETE",
                headers: {
                    "Content-Type": "application/json",
                },
            });
            if (!response.ok) {
                const errorText = await response.text();
                throw new Error(`Ошибка удаления: ${response.status} - ${errorText}`);
            }
            // Если удаление успешно — перезагружаем список
            applyFiltersAndRender();
        } catch (error) {
            alert(`Не удалось удалить сотрудника #${id}: ${error.message}`);
        }
    }

    // функция загрузки списка сотрудников
    async function fetchEmployees(page = 1, 
                                  perPage = 10,
                                  showDrafts = false,
                                  showMale = true,
                                  showFemale = true,
                                  ageFrom = null,
                                  ageTo = null,
                                  search = '') {
        var url = `${API_BASE}?page=${page}&per_page=${perPage}&show_drafts=${showDrafts}&show_male=${showMale}&show_female=${showFemale}&search=${search}`;
        
        if (ageFrom){
            url = url + `&age_from=${ageFrom}`
        }
        if (ageTo){
            url = url + `&age_to=${ageTo}`
        }
    
        try {
            const response = await fetch(url);
    
            if (!response.ok) {
                throw new Error(`Ошибка HTTP: ${response.status}`);
            }
    
            const data = await response.json();
    
            // Ожидаемая структура: { items: [...], total: 42, page: 1, total_pages: 5, per_page: 10 }
            return {
                employees: data.items || [],
                total: data.total || 0,
                page: data.page || 1,
                totalPages: data.total_pages || 1,
                perPage: data.per_page || 10,
            };
        } catch (error) {
            console.error("Ошибка загрузки сотрудников:", error);
            return {
                employees: [],
                total: 0,
                page: 1,
                totalPages: 1,
                perPage: 10,
            };
        }
    }

    applyFiltersAndRender();
});