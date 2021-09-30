# OZON-MoySklad_server

## api-key json structure:
```json
{
    "api_ozon":
        {
        "client_id": "string",
        "api_key": "string",
        "url_domain": "string",
        "url_command": "string"
        },
    "api_moysklad":
        {
        "client_id": "string",
        "api_key": "string",
        "url_domain": "string",
        "url_command": "string"
        }

}
```
## Задачи

- [x] organization - мета-данные юрлица           *готово*
- [x] store - мета-данные склада                  *готово*
- [x] retailStore - мета-данные точки продаж      *готово*

- [ ] Открыть смену, получить ID смены и закрыть ее.
- [ ] retailShift - мета-данные смены для розничной продажи: открываю смену через API, получаю эти мета-данные 
- [ ] name - номер продажи, пока не ясно должна быть она порядковым числом или я могу задавать любое значение



