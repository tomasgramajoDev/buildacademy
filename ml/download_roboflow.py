"""Download the public pilot through Roboflow's API, without the export dialog.
The user's existing key is entered privately; it is never stored or printed.
"""
import getpass
import time
import zipfile
from pathlib import Path
from urllib.parse import urlsplit, urljoin
import requests

ENDPOINT='https://api.roboflow.com/bis497/motherboard-part-locater/5/yolov8'
TARGET=Path(__file__).resolve().parents[1]/'datasets'/'bis497-v5-yolov8.zip'

class DownloadError(Exception): pass

def allowed_url(url):
    p=urlsplit(url);host=p.hostname or ''
    return p.scheme=='https' and not p.username and not p.password and (host=='roboflow.com' or host.endswith('.roboflow.com') or host=='roboflow.io' or host.endswith('.roboflow.io') or host=='storage.googleapis.com')

def export_link(key,session=requests,wait=time.sleep):
    for attempt in range(36):
        with session.get(ENDPOINT,headers={'Authorization':'Bearer '+key},timeout=(15,30),allow_redirects=False) as response:
            if response.status_code in (401,403):raise DownloadError('Roboflow rechazo la clave o el acceso al dataset. Revisa tu Private API Key.')
            if response.status_code!=200:raise DownloadError(f'Roboflow respondio HTTP {response.status_code}. No se descargo el dataset.')
            data=response.json()
        link=data.get('export',{}).get('link')
        if link:
            if not allowed_url(link):raise DownloadError('El enlace tiene un destino no reconocido; requiere revision.')
            return link
        if data.get('ready') is not False:raise DownloadError('Roboflow no devolvio un enlace de descarga.')
        print(f'Roboflow esta preparando el ZIP ({attempt+1}/36)...',flush=True);wait(5)
    raise DownloadError('Roboflow tampoco termino la exportacion por API en 3 minutos. No sigas esperando esa ventana.')

def download(link,target=TARGET,session=requests):
    target=Path(target);part=target.with_suffix('.zip.part')
    if target.exists() or part.exists():raise DownloadError('Ya existe el ZIP o una descarga parcial. Conservados sin sobrescribir; pedime que los revise.')
    target.parent.mkdir(parents=True,exist_ok=True)
    for _ in range(6):
        if not allowed_url(link):raise DownloadError('Redireccion no reconocida; descarga detenida.')
        with session.get(link,stream=True,timeout=(15,60),allow_redirects=False) as response:
            if response.status_code in (301,302,303,307,308):
                link=urljoin(link,response.headers.get('Location',''));continue
            if response.status_code!=200:raise DownloadError(f'El archivo respondio HTTP {response.status_code}.')
            total=0
            with part.open('xb') as f:
                for chunk in response.iter_content(1024*1024):
                    total+=len(chunk)
                    if total>2_000_000_000:raise DownloadError('Archivo mayor a 2 GB; descarga detenida.')
                    f.write(chunk)
                    print(f'\rDescargados {total/1048576:.1f} MB',end='',flush=True)
            print()
            if not zipfile.is_zipfile(part):raise DownloadError('La respuesta no es un ZIP valido. No se importo.')
            with zipfile.ZipFile(part) as archive:
                if archive.testzip() is not None:raise DownloadError('ZIP incompleto o danado. No se importo.')
            part.rename(target);return target
    raise DownloadError('Demasiadas redirecciones de descarga.')

def main():
    print('BuildAcademy - descarga directa por API de Roboflow')
    print('Copia tu Private API Key existente desde Roboflow > Settings > API Keys.')
    print('Pegala aqui. No se vera al escribir, no se guarda y solo se envia a api.roboflow.com.')
    key=getpass.getpass('Private API Key: ').strip()
    if not key:raise DownloadError('No se ingreso una clave.')
    link=export_link(key);key=None
    result=download(link)
    print('ZIP descargado:',result)
    print('Avisame para validar sus etiquetas y comenzar el entrenamiento.')

if __name__=='__main__':
    try:main()
    except (KeyboardInterrupt,EOFError):print('\nCancelado.')
    except DownloadError as error:print('No se completo:',error)
    except Exception as error:print('No se completo por un error de red o archivo:',type(error).__name__,'(detalle omitido para proteger la clave).')
