// Инициализация Date Range Picker
function initDateRangePicker() {
    // Получаем элементы
    const dateRangePicker = document.getElementById('dateRangePicker');
    const dateRangeDropdown = document.querySelector('.date-range-dropdown');
    const customRangePicker = document.querySelector('.custom-range-picker');
    const dateFromInput = document.querySelector('input[name="date_from"]');
    const dateToInput = document.querySelector('input[name="date_to"]');

    if (!dateRangePicker || !dateRangeDropdown || !customRangePicker || !dateFromInput || !dateToInput) {
        console.error('Не все необходимые элементы найдены');
        return;
    }

    // Инициализация Flatpickr для кастомного выбора дат
    const dateFromPicker = flatpickr(dateFromInput, {
        locale: 'ru',
        dateFormat: 'Y-m-d',
        onChange: function(selectedDates) {
            updateDateRangeDisplay();
        }
    });

    const dateToPicker = flatpickr(dateToInput, {
        locale: 'ru',
        dateFormat: 'Y-m-d',
        onChange: function(selectedDates) {
            updateDateRangeDisplay();
        }
    });

    // Функция обновления отображения выбранного диапазона дат
    function updateDateRangeDisplay() {
        if (dateFromInput.value && dateToInput.value) {
            const startDate = new Date(dateFromInput.value);
            const endDate = new Date(dateToInput.value);
            dateRangePicker.value = `${startDate.toLocaleDateString('ru-RU')} - ${endDate.toLocaleDateString('ru-RU')}`;
            customRangePicker.classList.remove('show');
        }
    }

    // Обработка клика по полю выбора даты
    dateRangePicker.addEventListener('click', function(e) {
        e.stopPropagation();
        dateRangeDropdown.classList.toggle('show');
    });

    // Закрытие выпадающего списка при клике вне его
    document.addEventListener('click', function(e) {
        if (!dateRangePicker.contains(e.target)) {
            dateRangeDropdown.classList.remove('show');
            customRangePicker.classList.remove('show');
        }
    });

    // Обработка выбора предустановленного периода
    document.querySelectorAll('.date-range-option').forEach(option => {
        option.addEventListener('click', function() {
            const range = this.dataset.range;
            const today = new Date();
            let startDate = new Date();
            let endDate = new Date();

            switch(range) {
                case 'today':
                    break;
                case 'last-week':
                    startDate.setDate(today.getDate() - 7);
                    break;
                case 'last-month':
                    startDate.setMonth(today.getMonth() - 1);
                    break;
                case 'current-month':
                    startDate.setDate(1);
                    break;
                case 'last-quarter':
                    startDate.setMonth(today.getMonth() - 3);
                    break;
                case 'current-quarter':
                    const currentQuarter = Math.floor(today.getMonth() / 3) * 3;
                    startDate.setMonth(currentQuarter);
                    startDate.setDate(1);
                    break;
                case 'last-6-months':
                    startDate.setMonth(today.getMonth() - 6);
                    break;
                case 'current-year':
                    startDate.setMonth(0);
                    startDate.setDate(1);
                    break;
                case 'last-year':
                    startDate.setFullYear(today.getFullYear() - 1);
                    endDate.setFullYear(today.getFullYear() - 1);
                    break;
                case 'all-time':
                    startDate = new Date(0);
                    break;
                case 'custom':
                    dateRangeDropdown.classList.remove('show');
                    customRangePicker.classList.add('show');
                    return;
            }

            if (range !== 'custom') {
                dateFromPicker.setDate(startDate);
                dateToPicker.setDate(endDate);
                dateRangePicker.value = `${startDate.toLocaleDateString('ru-RU')} - ${endDate.toLocaleDateString('ru-RU')}`;
                dateRangeDropdown.classList.remove('show');
            }
        });
    });
}

// Инициализация после загрузки DOM
document.addEventListener('DOMContentLoaded', initDateRangePicker); 