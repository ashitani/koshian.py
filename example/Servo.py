#!/usr/bin/env python
# -*- coding:utf-8 -*-

import sys
sys.path.append('../')

from koshian import *

class myKoshian(Koshian):
    def setup(self):    
        self.s=Servo(self)
        self.s.attach(PIO2)
    def loop(self):
        self.s.write(30)
        delay(1000)
        self.s.write(90)
        delay(1000)

k= myKoshian()
k.run()
