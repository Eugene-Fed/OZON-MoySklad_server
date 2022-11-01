#!/bin/sh

echo "Открытие-закрытие смены"
python ./moysklad_retail_shifts.py
sleep 20

echo "Импорт из ОЗОН"
python ./ozon_import.py
sleep 20

echo "Экспорт в МойСклад"
python ./moysklad_export.py
