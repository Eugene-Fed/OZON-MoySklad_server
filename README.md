## OZON-MoySklad_server

### Задачи
- [x] organization - мета-данные юрлица
- [x] store - мета-данные склада
- [x] retailStore - мета-данные точки продаж

- [ ] Открыть смену, получить ID смены и закрыть ее.
- [ ] retailShift - мета-данные смены для розничной продажи: открываю смену через API, получаю эти мета-данные 
- [ ] name - номер продажи, пока не ясно должна быть она порядковым числом или я могу задавать любое значение

### Скрытые файлы
Схема файлов с апи ключами и секретными мета-данными, скрытых в .gitignore находится в папке **/scheme/**

### api-key json structure:
```json
{
    "api_ozon":
        {
        "client_id": "145728",
        "api_key": "575bd492-325e-4507-9540-e9dc3f7c0c59",
        "url_domain": "https://api-seller.ozon.ru",
        "url_command": "/v2/posting/fbo/list"
        },
    "api_moysklad":
        {
        "api_key": "796da551e22d09c334f4106c5efb367d42ece8dc",
        "url_domain": "https://online.moysklad.ru",
        "url_api": "/api/remap/1.2/entity/",
        "account":
            {
            "id": "b0953a15-44e6-11eb-0a80-06920000941e",
            "url_command": "employee"
            },
        "organisation":
            {
            "id": "b0be614f-44e6-11eb-0a80-011800173209",
            "url_command": "organization"
            },
        "store":
            {
            "id": "537a0534-09c1-11ec-0a80-031000010c06",
            "url_command": "store"
            },
        "retailStore":
            {
            "id": "b0c8e663-44e6-11eb-0a80-011800173221",
            "url_command": "retailstore"
            }
        }

}
```