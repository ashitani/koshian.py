# koshian.py (Koshian-Pie)

## これはなに(What's This)

[koshian](http://www.m-pression.com/ja/solutions/boards/koshian)をPCからArduinoのようにPythonから制御する
ライブラリです。現時点では Ubuntu14.04 でしか動きません。

Python library to control [koshian](http://www.m-pression.com/ja/solutions/boards/koshian) like Arduino from PC.
At this time, only Ubuntu 14.04 is supported.


## インストール(Install)

koshian,pyのインストールの前に [pygattlib](https://bitbucket.org/OscarAcena/pygattlib) を
インストールしてください。インストール方法はリンク先を参照のこと。しかるのちに、

> python ./setup.py install

Before installing koshian,py, [pygattlib](https://bitbucket.org/OscarAcena/pygattlib) should be instelled. See the instruction on the Link. After that,

> python ./setup.py install

## ハードウェア（Hardware Setting）

konashi.jsアプリを使ってkoshianのファームをkonashi2.0にアップデートします。

Update koshian firmware to konashi2.0 by konashi.js application.


## 例（Example）

### MACアドレス指定（Connection by assigning MAC address）
```python
from koshian import *
mac = "00:00:00:00:00:00"
k= Koshian(mac)
```

MAC アドレスは下記のコマンドでスキャンできます。

> sudo hcitool lescan

もしhcitoolが見つからなければ、[blueZ](http://www.bluez.org/)をインストールしてください。

MAC address can be scanned by this command (only Linux).

> sudo hcitool lescan

If your linux system doesn't have hcitool, install [blueZ](http://www.bluez.org/).

### 自動検出（Automatic Find）
```python
from koshian import *
k= Koshian()
k.pinMode(PIO5,OUTPUT)
k.digitalWrite(PIO5,HIGH)
```

自動検出にはsudoでスクリプトを実行する必要があります。

You should "sudo" to find devices.

### 普通のコーディング（Normal Cording)
```python
from koshian import *
mac = "00:00:00:00:00:00"
k= Koshian(mac)
k.pinMode(PIO5,OUTPUT)
k.digitalWrite(PIO5,HIGH)
```

### Arduino風コーディング（Arduino Style Coding）
```python
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
```

### サーボの例（Servo example)
```python
from koshian import *

k= Koshian()
s= Servo(k)
s.attach(PIO2)
s.write(30)
```

### I2Cの例 （I2C example)

now under debugging..

### UARTの例 （UART example)

now under debugging..


## License

koshian.py is licensed under [MIT License](http://opensource.org/licenses/mit-license.php).
