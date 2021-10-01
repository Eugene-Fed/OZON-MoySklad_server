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
- delivered
- cancelled
- delivering
- awaiting_deliver
- awaiting_packaging

### Задачи
- [x] Открыть смену и получить ее ID и имя (порядковый номер)
- [x] Закрыть все открытые смены - смены НЕВОЗМОЖНО закрыть через API или Интерфейс. Их можно только создать и удалить полностью. Возможно смены закрываются автоматически в какое-то время суток или по истечении определенного времени. В документации к API это не расписано, поэтому остается только ждать и проверить что будет с оставшимися сменами завтра (одну из смен 00003 я удалил из веб-интерфейса).
- [x] Получить от ОЗОН список всех заказов
- [ ] Создать временный скрипт, который отправит все заказы в смену 00001 на МойСклад
- [ ] Создать управляющий скрипт, который будет вызывать функцию открытия и закрытия смены
- [ ] Создать модуль обработки полученных из OZON заказов, и отправки их в открытую смену

### Скрытые файлы
- Схема файлов с апи ключами и секретными мета-данными, скрытых в .gitignore находится в папке **/scheme/**
- тильда в названии папок *~api-keys* и *~meta* обозначает, что рабочие версии этих папок указаны в .gitignore
- папка *data* содержит резервную копию (шаблон) рабочих файлов данных на случай необходимости их восстановления после утраты

