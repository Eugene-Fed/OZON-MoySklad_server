## OZON-MoySklad_server

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

### Задачи
- [x] Не удалось создать автоматическое соответствие между конкретным товаром в ОЗОН и МойСклад потому что в ОЗОН артикул = полный штрихкод, тогда как в МойСклад - это первые 5 знаков ШК. Кроме того варианты одного товара в МойСклад (размеры, цвета) не имеют собственных артикулов. Чтобы списывать из остатков конкретный размер, нужно ссылаться на товар по его коду в МойСклад, поэтому придется сделать ручную таблицу соответствия ШК ОЗОН и Кода товара МойСкладл.
- [x] В цикле получить все необходимые данные о заказе
- [x] Сформировать json-объект с необходимыми данными для отправки заказа в МойСклад (только заказы со статусом **delivered**).
- [ ] Проверить корректность передаваемых сумм заказа. Ответ сервера выдает корректные значения, однако в админ панели отображаются слишком маленькие суммы продажи.
- [ ] Закрыть смену. Для этого необходимо изменить смену с указанием Даты/Времени закрытия.
- [ ] Выбрать какое-либо поле в заказах на МойСклад, в которое можно будет сохранять **номер** заказа из системы ОЗОН
- [ ] Выбрать какое-либо поле в заказах на МойСклад, в которое можно будет сохранять **статус** заказа из системы ОЗОН
- [ ] Выгрузить в МойСклад все заказы с прочими статусами, кроме **delivering**
- [ ] Создать управляющий скрипт, который будет вызывать функцию открытия смены и закрытия смены.
- [ ] Создать скрипт, который будет получать из МойСклад все ранее выгруженные закзаы со статусом *delivering*, *awaiting_deliver* и *awaiting_pachaging* за 45 дней. Далее необходимо найти их среди заказов ОЗОН за последние 45 дней и проверить не изменился ли статус. Если статус обновился - обновить его и в МойСклад.
- [ ] Создать полноценный модуль регулярной обработки полученных из OZON заказов, и отправки их в открытую смену.
- [ ] Использовать файл *data/product-id_corr-table.json* для того, чтобы отредактировать товары на МойСклад, заменив КодТовара на артикул из ОЗОН. **Первоначально проверить, есть ли 100% соответствие с ШК ВБ!!!**

### Файлы-шаблоны для МойСклад
- **/data/retailDemand_create.json** - Шаблон json для создания смены
- **/data/retailShift_create.json** - Шаблон json для создания розничной продажи

### Скрытые файлы
- Схема файлов с апи ключами и секретными мета-данными, скрытых в .gitignore находится в папке **/scheme/**
- тильда в названии папок *~api-keys* и *~meta* обозначает, что рабочие версии этих папок (без тильды в названии) указаны в .gitignore
- папка *data* содержит резервную копию (шаблон) рабочих файлов данных на случай необходимости их восстановления после утраты

