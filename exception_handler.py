# -*- coding: UTF-8 -*-
import sys


def unexpected(e: Exception, er_type="Unexpected error"):
    print(f"\n{er_type}:\n", e)
    wait = input("PRESS ENTER TO EXIT")
    sys.exit(1)

