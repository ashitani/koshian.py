#!/usr/bin/env python
# -*- coding:utf-8 -*-

import sys
sys.path.append('../')

from koshian import *

class myKoshian(Koshian):
    def setup(self):    
        self.pinMode(PIO5, OUTPUT)

    def loop(self):
        self.digitalWrite(PIO5, HIGH)
        delay(1000)
        self.digitalWrite(PIO5, LOW)
        delay(1000)

k= myKoshian()
k.run()
