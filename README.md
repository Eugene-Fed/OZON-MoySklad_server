## OZON-MoySklad_server

### Последовательность запуска в Cron.
- Добавить в папку */api-keys/* секретный файл **api-keys.json**
- Далее запускаем скрипты по очереди:
    - **moysklad_import_ids.py** - *достаточно запустить один раз* и далее не использовать. Запуск задается параметром в файле *main.py*
    - **moysklad_retail_shifts.py** - запуск ежедневно в 03:00 по Москве. если будет прощуен запуск - это не приводит к ошибке, т.к. каждый раз проверяются все заказы за последние 45 дней (настраивается в файле *settings.json*). Они просто будут выгружены в последнюю открытую смену без привязки к реальной дате оформления и выкупа.
    - **ozon_import.py** - запускается из *main.py*
    - **moysklad_export.py** - запускается из *main.py*

### Задачи
- [x] Добавить функцию закрытия смены - для этого открываем список всех смен, проверяем каждую на наличие даты закрытия смены. Если дата отсутсвует, значит смена еще открыта, значит необходимо внести в нее изменение (указать дату/время закрытия смены).
- [x] Вынести количество дней для загрузки заказов с ОЗОН в отдельный файл настроек дабы не лезть в код ради изменения параметров.
- [ ] Вынести обработку 'Unexpected Error' в отдельный модуль, чтобы не дублировать код с выводом ошибки и выходом из программы.
- [ ] Вынести параметр "Запуск скрипта **moysklad_import_ids.py**" в файл *settings.json*.
- [ ] Получить из консоли флаг FIRST_START при запуске main.py
- [ ] Переписать в модуль скрипт **moysklad_import_ids.py**
- [ ] Переписать в модуль скрипт **ozon_import.py**
- [ ] Переписать в модуль скрипт **moysklad_export.py**
- [ ] Добавить в проект библиотеку Requests и Pandas при необходимости
- [ ] Преобразовать скрипт ozon_import.py в класс с методами, чтобы вызывать его из скрипта moysklad_export.py для получения всех доставленных заказов за последние N дней.
- [ ] Создать класс (или функцию), который будет проверять список смен, открывать смены, закрывать смены, выдавать статус (открыта/закрыта) последней созданной смены.
- [ ] ПРЕДУПРЕЖДЕНИЕ - прежде, чем заменить "виртуальное" время заказа на реальное, необходимо научиться проставлять статусы заказов, выугружать их все и по мере необходимости менять их значение на delivered. Тогда будет возможно открывать старые заказы в закрытых сменах и вносить в них изменение. На данный момент мы можем сегодня выгрузить заказ недельной давности, который только вчера получил статус **delivered**.
- [ ] Выбрать какое-либо поле в заказах на МойСклад, в которое можно будет сохранять **номер** заказа из системы ОЗОН
- [ ] Выбрать какое-либо поле в заказах на МойСклад, в которое можно будет сохранять **статус** заказа из системы ОЗОН
- [ ] Выгрузить в МойСклад все заказы с прочими статусами, кроме **delivering**
- [ ] Создать управляющий скрипт, который будет вызывать функцию открытия смены и закрытия смены.
- [ ] Создать скрипт, который будет получать из МойСклад все ранее выгруженные закзаы со статусом *delivering*, *awaiting_deliver* и *awaiting_pachaging* за 45 дней. Далее необходимо найти их среди заказов ОЗОН за последние 45 дней и проверить не изменился ли статус. Если статус обновился - обновить его и в МойСклад.
- [ ] Создать полноценный модуль регулярной обработки полученных из OZON заказов, и отправки их в открытую смену.
- [ ] Использовать файл *data/product-id_corr-table.json* для того, чтобы отредактировать товары на МойСклад, заменив КодТовара на артикул из ОЗОН. **Первоначально проверить, есть ли 100% соответствие с ШК ВБ!!!**
- [ ] Пока не заметил, чтобы поле *cost* в json-запросе создания розничной Продажи МойСклал, как-то влияло на финансовые показатели. По этой причине считать и отправлять это значение смысла не вижу.
- [ ] Попробовать при создании Розничной продажи МойСклад в поле **'payedSum'** значение из 'sum' минус накладные расходи ('cost'). Сейчас 'payedSum' явно приравнивается к 'sum'

### Файлы-шаблоны для МойСклад
- **/scheme/templates/retailDemand_create.json** - Шаблон json для создания смены
- **/scheme/templates/retailShift_create.json** - Шаблон json для создания розничной продажи

### Скрытые файлы
- Схема файлов с апи ключами и секретными мета-данными, скрытых в .gitignore находится в папке **/scheme/**
- тильда в названии папок *~api-keys* обозначает, что рабочие версии этих папок (без тильды в названии) указаны в .gitignore
- папка *data* содержит резервную копию (шаблон) рабочих файлов данных на случай необходимости их восстановления после утраты

### Словарь параметров API МойСклад
- **organization** - мета-данные юрлица
- **store** - мета-данные склада
- **retailStore** - мета-данные точки продаж
- **retailShift** - мета-данные смены для розничной продажи: открываю смену через API, получаю эти мета-данные
- **name** - номер смены, порядковое пятизначное число с ведущими нулями, которое назначается сервером автоматически при создании смены. имеет сквозную нумерацию.

### Словарь параметров API OZON
Структура Json заказов - [0] в структуре означает наличие индексированного списка
- response['result'][0]['order_id] - **Номер заказа**
- response['result'][0]['products'][0]['offer_id'] - **Артикул товара в заказе**
- response['result'][0]['products'][0]['created_at'] - **Время оформления заказа**
- response['result'][0]['products'][0]['price'] - **Цена продажи товара**
- response['result'][0]['products'][0]['sku'] - **SKU** - он же product_id из financial_data
- response['result'][0]['financial_data']['products'][0]['product_id'] - **product_id** - он же SKU в списке товаров в заказе
- response['result'][0]['financial_data']['products'][0]['commission_amount'] - **Комиссия с продажи товара (в руб.)**
- response['result'][0]['financial_data']['products'][0]['item_services']{нужно забрать все значения из словаря} - **Списания ОЗОН за логистику** и т.п. (в минус руб.)

### Доступные статусы заказа OZON
- delivered - Доставлен
- cancelled - Отменен
- delivering - Отгружен
- awaiting_deliver - Собран
- awaiting_packaging - Новый
