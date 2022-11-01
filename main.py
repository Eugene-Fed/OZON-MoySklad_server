# -*- coding: UTF-8 -*-

import moysklad_import_ids as ms_import
import moysklad_retail_shifts as ms_retail
import ozon_import
import moysklad_export

FIRST_START = False         # флаг, от которого зависит, будет ли запускаться скрипт для импорта айдишников с МойСклад

if __name__ == "__main__":
    # TODO: переписать все скрипты в готовые для использования модули и прописать их запуск в main.py
    if FIRST_START:
        ms_import.import_ids()
    ms_retail.create_retail_shift()
    ozon_import.import_orders()
    moysklad_export.export_orders()
    wait = input("PRESS ENTER TO CONTINUE.")
