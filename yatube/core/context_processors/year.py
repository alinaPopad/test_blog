import datetime


def year(request):
    """Добавляет переменную с текущим годом."""
    abc = datetime.datetime.now()
    cba = int(abc.strftime('%Y'))
    return {'year': cba, }
