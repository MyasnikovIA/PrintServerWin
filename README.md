# PrintServereWin
Локальный сервис для windows(печать)
Работает на порту 51003


BarsPyService.exe - сервис для печати 

<table>
<tr> <td>\app\*.*</td><td> папка с плагином </td> </tr>
<tr> <td>\html\*.*</td><td>пример обращениия к сервису из JS </td> </tr>
<tr> <td>\host\*.*</td><td>исходний код сервиса</td> </tr>
<tr> <td>\host\dist\BarsPyService.exe</td><td>собранный сервис</td> </tr>
</table>
**управление:**
   \host\dist\Install.bat - регистрация программы в автозагрузке
    BarsPyServer.exe      - Запуск сервера в фоновом режиме  
**Сборка сервиса:**
<pre>
cd host
pyinstaller --onefile  --noconsole --noupx --icon="app.ico" --hidden-import win32timezone BarsPyServer.py
</pre> 

**Проверка работы сервиса:**
http://localhost:51003/

**Установка плагина в Firefox:**
<pre>
1) about:debugging#/runtime/this-firefox
2) Загрузить файл \app\manifest.json
</pre>
**Установка плагина в Chrome:**
<pre>
1) chrome://extensions/
2) Влючить "Режим разработчика"
3) Загрузить распакованное расширение из папки "\app\"
4) Перезагрузить страницу
</pre>

**Обратится к сервису из плагина (после установки плагина в браузере)**

<pre>
    BarsPy.send({"GetPrinterList":1},function(dat){console.log(dat);}) // получить список принтеров установленных в системе
    BarsPy.send({"Print":"< h1>Привет Мир-HelloWorld</h1>","widthPage":300,"heightPage":100,"PrinterName":"Microsoft XPS Document Writer"},function(dat){console.log(dat);})
    BarsPy.send({"Print":"< h1>Привет Мир-HelloWorld</h1>"+Date(Date.now()).toString()}) // отправека на печать без получения ответа 
	BarsPy.send({"PrintUrl":"http://127.0.0.1/sprint.png" },function(dat){console.log(dat);}) // Отправка на печать страницы по URL адресу
</pre>

**Обратится к сервису из JS**
<pre>

BarsPySend= function(messageObject,FunCallBack ){
    var host = "http://127.0.0.1:51003/";
    var cspBindRequestCall = new XMLHttpRequest();
    cspBindRequestCall.open('GET',host, true);
    if (typeof FunCallBack === 'function'){ 
         cspBindRequestCall.onreadystatechange = function() {
         if (this.readyState == 4 && this.status == 200) {
            if (typeof FunCallBack === 'function'){
		    try {
			   FunCallBack(JSON.parse(decodeURIComponent(this.responseText)));
			} catch (err) {
			    FunCallBack(decodeURIComponent(this.responseText));
			}
          }
         };
       };
    }
    cspBindRequestCall.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
    if (typeof messageObject == "object"){
        for (var prop in messageObject) {
           cspBindRequestCall.setRequestHeader("X-My-"+prop, encodeURI(messageObject[prop]));
        }
    } else{
        cspBindRequestCall.setRequestHeader("X-My-message", encodeURI(messageObject));
    }
    cspBindRequestCall.send();
    return cspBindRequestCall; 
}
BarsPySend({"GetPrinterList":1},function(dat){console.log(dat);}) // получить список принтеров установленных в системе
BarsPySend({"Print":"< h1>Привет Мир-HelloWorld</h1>","widthPage":300,"heightPage":100,"PrinterName":"Microsoft XPS Document Writer"},function(dat){console.log(dat);})
BarsPySend({"Print":"< h1>Привет Мир-HelloWorld</h1>"}) // отправека на печать без получения ответа
BarsPySend({"PrintUrl":"http://127.0.0.1/sprint.png" },function(dat){console.log(dat);}) // Отправка на печать страницы по URL адресу
</pre>

<h4>Python V3</h4>
**Для сблрки необходимо использовать сторонние пакеты:**
<pre>
pip install Flask
pip install Flask-cors
pip install imgkit
pip install pyinstaller
</pre> 

<h4>Python3.8 с установленными пакетами</h4>
распоковать в C:\Program Files\Python38
<pre> 
https://yadi.sk/d/nYL9MjYO_oMsBA
</pre> 
