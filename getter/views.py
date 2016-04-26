from django.shortcuts import render
from models import URLs, URLInfo
from django.http import JsonResponse
import datetime


def home(request):
    return render(request, 'index.html')


def getTaskList(request):
    urls = list(URLs.objects.values())
    for url in urls:
        timeshift = url.get('timeshift', None)
        if timeshift:
            url['timeshift'] = datetime.timedelta(
                hours=timeshift.hour,
                minutes=timeshift.minute,
                seconds=timeshift.second).total_seconds()
        else:
            url['timeshift'] = 0
    return JsonResponse(urls, safe=False)


def saveTask(request):
    url_id = request.GET.get('url_id', None)
    if url_id:
        url = URLs.objects.get(id=url_id)
        title = request.GET.get('title', None)
        charset = request.GET.get('encoding', None)
        h1 = request.GET.get('h1', None)
        parsed_date = datetime.datetime.strptime(
            request.GET.get('date', None), "%d.%m.%Y %H:%M:%S")
        status = request.GET.get('status', False)
        url_info = URLInfo(url=url, title=title, charset=charset, h1=h1,
                           parsed_date=parsed_date, status=status)
        url_info.save()
        return JsonResponse({'success': True})
