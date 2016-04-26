#-*- encoding: utf-8 -*-

from autobahn.twisted.websocket import WebSocketServerProtocol, \
        WebSocketServerFactory
from twisted.web.client import getPage

import datetime

import urllib
import json
from BeautifulSoup import BeautifulSoup as Soup


class Worker(WebSocketServerProtocol):

    def getUrls(self):
        """
        Этот метод опрашивает наш сайт на Django для того чтобы получить список
        URL-ов для парсинга и время когда этот парсинг надо запустить
        """
        url = str('http://127.0.0.1:8000/geturls/')
        deferred = getPage(url, timeout=20,
                           headers={'Accept': 'application/json'})
        deferred.addCallback(self.makeTasks)
        deferred.addErrback(self.failInfo, url)
        return deferred

    def onConnect(self, *args, **kwargs):
        """
        Этот метод срабатывает в момент подключения клиента по WebSocket.
        Когда клиент подключается к нам по WebSocket, мы должны получить список
        заданий и начать парсинг
        """
        deferred = self.getUrls()
        return deferred

    def makeTasks(self, response):
        """
        После получения списка задач, мы должны эти самые задачи назначить
        для выполнения.

        :param response str: JSON строка, содержащая id задания, url для парсинга и timeshift (смещение во времени для запуска задания)
        """
        urls_list = json.loads(response)
        for url in urls_list:
            timeshift = url.get('timeshift', None)
            if not timeshift:
                timeshift = 0
            reactor.callLater(timeshift, self.getInfo, url)

    def failInfo(self, response, url):
        """
        В случае неудачи на каком-либо этапе, данный метод оповестит клиента
        об этом через WebSocket
        """
        dt = datetime.datetime.now().isoformat()
        ret = {'date': dt, 'url': url['url'], 'success': False}
        self.sendMessage(json.dumps(ret).encode('utf8'))

    def saveInfo(self, body, url):
        """
        В случае удачного получения документа по URL, мы должны узнать о нем
        необходимую информацию:
            - содержимое тэга Title
            - содержимое тэга H1 (если таковой имеется)
            - возможную кодировку документа

        После этого необходимо отправить полученые данные в приложение Django,
        которая занесет их в базу данных. В случае удачи - отпавляем эти же
        данные через WebSocket пользователю

        :param body str: содержимое страницы
        :param url dict: объект задания, содержащий сам URL, а так же id задания
        """
        dt = datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S")
        soup = Soup(body)
        title = soup.find('title')
        if title:
            title = title.text.encode('utf-8')
        h1 = soup.find('h1')
        if h1:
            h1 = h1.text.encode('utf-8')
        encoding = soup.originalEncoding
        ret = {'date': dt, 'url_id': url['id'], 'h1': h1, 'encoding': encoding,
               'title': title, 'success': True, 'url': url['url']}
        s_url = 'http://127.0.0.1:8000/saveinfo/?' + urllib.urlencode(ret)
        deferred = getPage(s_url, timeout=20)
        deferred.addCallback(self.sendResult, ret)
        deferred.addErrback(self.failInfo, url)

    def sendResult(self, response, ret):
        """
        Если удалось сохранить полученные данные в базу данных на стороне Django,
        можем выслать пользователю результат.

        :param response json: Ответ от приложения Django об успешности сохранения полученых данных
        :param ret dict: Данные для отправки пользователю
        """
        self.sendMessage(json.dumps(ret).encode('utf8'))

    def getInfo(self, url):
        """
        Этот метод закачивает требуемую страницу и передает ее обработчику

        :param url str: URL страницы которую будем обрабатывать
        """
        deferred = getPage(str(url['url']), timeout=20)
        deferred.addCallback(self.saveInfo, url)
        deferred.addErrback(self.failInfo, url)
        return deferred


if __name__ == '__main__':
    from twisted.internet import reactor
    import sys
    from twisted.python import log
    log.startLogging(sys.stdout)

    factory = WebSocketServerFactory(u"ws://127.0.0.1:9000")
    factory.protocol = Worker

    reactor.listenTCP(9000, factory)
    reactor.run()
