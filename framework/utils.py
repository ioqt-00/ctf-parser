#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# _authors_: ioqt

import logging
from pathlib import PosixPath

def not_implemented():
    logging.error("Not implemented")
    return {"msg": "Not implemented"}

class UrlPath(PosixPath):
    def joinpath(self, *args, **kwargs) -> str:
        res = super().joinpath(*args, **kwargs)
        res = str(res)
        res = res.replace("http:/", "http://")
        res = res.replace("https:/", "https://")

        return res
