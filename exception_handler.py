# -*- coding: UTF-8 -*-
import sys


def unexpected(e: Exception):
    print("\nUnexpected error:\n", e)
    wait = input("PRESS ENTER TO EXIT")
    sys.exit(1)

