#!/usr/bin/env python
# -*- coding:utf-8 -*-

import sys
sys.path.append('../')

from koshian import *

k= Koshian()
s=Servo(k)
s.attach(PIO1)
s.write(90)
