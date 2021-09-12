# OZON-MoySklad_server
# api-key json structure:
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

нужно получить у апи мой_склад такие hrefs

organization - мета-данные юрлица
store - мета-данные склада
retailStore - мета-данные точки продаж
retailShift - мета-данные смены для розничной продажи: открываю смену через API, получаю эти мета-данные
name - номер продажи, пока не ясно должна быть она порядковым числом или я могу задавать любое значение