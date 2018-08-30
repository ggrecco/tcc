from app import celery
from app.portscan import portScan


@celery.task(name='tcc.scaneando')
def scaneando(url, user):
    portScan(url, user)
    return 'Done!'
