# sys.stdout = sys.stderr = open(os.devnull, 'w')
from flask import Flask
from flask_cors import CORS, cross_origin
from json import dumps
from os import remove
from win32print import EnumPrinters, PRINTER_ENUM_LOCAL, PRINTER_ENUM_CONNECTIONS, GetDefaultPrinter
from win32ui import CreateDC
from PIL import Image
from PIL import ImageWin
from imgkit import from_url, from_string
from tempfile import mktemp
from flask import request
from urllib.parse import unquote
from traceback import format_exc
from win32con import HORZRES, VERTRES, MM_ISOTROPIC

widthPage = 300
heightPage = 100
printer_name = ""
portServer = 51003
version = '0.1'
app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'


@app.errorhandler(404)
def not_found(error):
    return "no service", 404


def parseHead():
    """
     Чтение входных пользовательских аргументов в заголовке запроса
    """
    requestMessage = {}
    for rec in request.headers:
        if "X-My-" in rec[0]:
            message = unquote(unquote(request.headers.get(rec[0])))
            key = rec[0][5:len(rec[0])]
            requestMessage[key] = message
    return requestMessage


def get_print_list():
    """
    функция получения списка принтеров установленных в системе
    :return:
    """
    requestMessage = {}
    printers = EnumPrinters(PRINTER_ENUM_LOCAL | PRINTER_ENUM_CONNECTIONS)
    requestMessage["Printers"] = [printer[2] for printer in printers]
    return requestMessage


def print_image(img, printer_name):
    """процедура печати картинки"""
    requestMessage = {}
    try:
        if printer_name == "":
            printer_name = GetDefaultPrinter()
    except Exception:
        requestMessage["Error"] = "GetDefaultPrinter:%s" % format_exc()
        return requestMessage
    hdc = CreateDC()
    hdc.CreatePrinterDC(printer_name)
    horzres = hdc.GetDeviceCaps(HORZRES)
    vertres = hdc.GetDeviceCaps(VERTRES)
    landscape = horzres > vertres
    if landscape:
        if img.size[1] > img.size[0]:
            img = img.rotate(90, expand=True)
    else:
        if img.size[1] < img.size[0]:
            img = img.rotate(90, expand=True)
    img_width = img.size[0]
    img_height = img.size[1]
    if landscape:
        # we want image width to match page width
        ratio = vertres / horzres
        max_width = img_width
        max_height = (int)(img_width * ratio)
    else:
        # we want image height to match page height
        ratio = horzres / vertres
        max_height = img_height
        max_width = (int)(max_height * ratio)
    # map image size to page size
    hdc.SetMapMode(MM_ISOTROPIC)
    hdc.SetViewportExt((horzres, vertres));
    hdc.SetWindowExt((max_width, max_height))
    # offset image so it is centered horizontally
    offset_x = (int)((max_width - img_width) / 2)
    offset_y = (int)((max_height - img_height) / 2)
    hdc.SetWindowOrg((-offset_x, -offset_y))
    hdc.StartDoc('Result')
    hdc.StartPage()
    dib = ImageWin.Dib(img)
    dib.draw(hdc.GetHandleOutput(), (0, 0, img_width, img_height))
    hdc.EndPage()
    hdc.EndDoc()
    hdc.DeleteDC()


def htmlurl_to_image(UrlPath="", printer_name="", widthPage=300, heightPage=100):
    """
    Функция вывода HTML на принтер
    :param UrlPath: - адрес запроса
    :param printer_name: - имя принтера
    :return:
    """
    requestMessage = {}
    try:
        filename = mktemp(".png")
        from_url(UrlPath, filename, options={'width': widthPage, 'height': heightPage})
    except Exception:
        requestMessage["Error"] = "create temp file %s %s" % (filename, format_exc())
        return requestMessage
    requestMessage = print_local_file(filename, printer_name)
    try:
        remove(filename)
    except  Exception:
        print("Remove file from temp :(%s)  %s" % (filename, format_exc()))
    return requestMessage


def html_to_image(StrPrintHtml="", printer_name="", widthPage=300, heightPage=100):
    """
    Функция вывода текста на принтер
    :param StrPrintHtml: - Текст HTML
    :param printer_name: - имя принтера
    :return:
    """
    requestMessage = {}
    try:
        filename = mktemp(".png")
        from_string(
            """<!DOCTYPE html><html><head><meta charset="utf-8"><title>Печать</title></head><body>%s</body></html>""" % StrPrintHtml,
            filename, options={'width': widthPage, 'height': heightPage})
    except Exception:
        requestMessage["Error"] = "create temp file %s %s" % (filename, format_exc())
        return requestMessage
    requestMessage = print_local_file(filename, printer_name)
    try:
        remove(filename)
    except  Exception:
        print("Remove file from temp :(%s)  %s" % (filename, format_exc()))
    return requestMessage


def print_local_file(filename, printer_name=""):
    """
    печать локального файла на принтер
    """
    requestMessage = {}
    try:
        img = Image.open(filename, 'r')
    except Exception:
        requestMessage["Error"] = "Open file from temp :(%s)  %s" % (filename, format_exc())
        return requestMessage
    try:
        print_image(img, printer_name)
    except Exception:
        requestMessage["Error"] = "Print image : %s" % format_exc()
        return requestMessage
    return requestMessage


@app.route("/")
@cross_origin()
def requestFun():
    """
    Функция обработки входящих команд с сервера
    :return:
    """
    global printer_name
    global widthPage
    global heightPage
    if request.host[:9] != "127.0.0.1":
        if request.host[:9] != "localhost":
            return "no service", 404
    requestMessage = parseHead()
    if "WidthPage" in requestMessage:
        widthPage = requestMessage.get("WidthPage")
    if "HeightPage" in requestMessage:
        heightPage = requestMessage.get("HeightPage")
    if "PrinterName" in requestMessage:
        printer_name = requestMessage.get("PrinterName")
    if "Print" in requestMessage:
        res = html_to_image(requestMessage["Print"], printer_name, widthPage, heightPage)
        return dumps(res), 200
    if "Printurl" in requestMessage:
        res = htmlurl_to_image(requestMessage["Printurl"], printer_name)
        return dumps(res), 200
    if "Getprinterlist" in requestMessage:
        return dumps(get_print_list()), 200
    if "Message" in requestMessage:
        if '[GetPrinterList]' in requestMessage["Message"]:
            return dumps(get_print_list()), 200
    if "Version" in requestMessage:
        requestMessage["Version"] = version
    return dumps(requestMessage), 200


if __name__ == '__main__':
    _svc_description_ = """
    Сервис предназначен для доступа к локальным ресурсам рабочей станции (Принтеры , сканеры , и.т.д),
    через крос-доменные запросов на хоси 127.0.0.1 (localhost)
    URL:  http://127.0.0.1:%s/
    Пример обращение к сервису через JS:
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
    BarsPySend({"Print":"<h1>Привет Мир-HelloWorld</h1>","widthPage":300,"heightPage":100,"PrinterName":"Brother QL-810W"},function(dat){console.log(dat);})
    BarsPySend({"Print":"<h1>Привет Мир-HelloWorld</h1>"+Date(Date.now()).toString()}) // отправека на печать без получения ответа
    BarsPySend({"PrintUrl":"http://127.0.0.1/sprint.png" },function(dat){console.log(dat);}) // Печать сайта по URL адресу
        """ % portServer
    print(_svc_description_)
    app.run(host='0.0.0.0', port=51003)
