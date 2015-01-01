# koshian.py (こしあんパイ)

## これはなに

[koshian](http://www.m-pression.com/ja/solutions/boards/koshian)をPCからArduinoのようにPythonから制御する
ライブラリです。現時点では Ubuntu14.04 でしか動きません。

## インストール

koshian,pyのインストールの前に [pygattlib](https://bitbucket.org/OscarAcena/pygattlib) を
インストールしてください。インストール方法はリンク先を参照のこと。しかるのちに、

> python ./setup.py install

## ハードウェア

konashi.jsアプリを使ってkoshianのファームをkonashi2.0にアップデートします。

## 例

### MACアドレス指定
```python
from koshian import *
mac = "00:00:00:00:00:00"
k= Koshian(mac)
```

MAC アドレスは下記のコマンドでスキャンできます。

> sudo hcitool lescan

もしhcitoolが見つからなければ、[blueZ](http://www.bluez.org/)をインストールしてください。


### 自動検出

```python
from koshian import *
k= Koshian()
k.pinMode(PIO5,OUTPUT)
k.digitalWrite(PIO5,HIGH)
```

自動検出にはsudoでスクリプトを実行する必要があります。

### 普通のコーディング

```python
from koshian import *
mac = "00:00:00:00:00:00"
k= Koshian(mac)
k.pinMode(PIO5,OUTPUT)
k.digitalWrite(PIO5,HIGH)
```

### Arduino風コーディング
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

### I2Cの例

I2Cはまだデバッグ中です。。

### UARTの例

UARTはまだデバッグ中です。。


## License

koshian.py is licensed under [MIT License](http://opensource.org/licenses/mit-license.php).
