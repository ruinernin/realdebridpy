"""Stupidly basic real-debrid interface.

foxyglacier is probably better: https://github.com/ruinernin/foxyglacier

But I haven't looked at it in a while and wanted something quick and easy that
was real-debrid specific.

This module has the most basic API calls needed and a really simple interactive
UI when called as a script.

INSTALL:
 It needs requests, you probably have it, if not don't make a mess of your
 system python, use pipenv or something.

USAGE:
 Start it with: `$ python realdebrid.py YOUR_API_KEY`
 Paste magnet links in, get HTTP(S) links out. Simples.

"""
import sys

import requests

BASE_URI = 'https://api.real-debrid.com/rest/1.0'
API_KEY = 'DEADBEEF'


def auth_header(api_key : str = None) -> dict:
    if api_key is None:
        api_key = API_KEY
    return {'Authorization': f'Bearer {api_key}'}


def instantAvailability(t_hash: str) -> dict:
    uri = f'{BASE_URI}/torrents/instantAvailability/{t_hash}'
    req = requests.get(uri, headers=auth_header())
    return req.json()[t_hash]['rd']


def addMagnet(t_hash: str) -> str:
    uri = f'{BASE_URI}/torrents/addMagnet'
    req = requests.post(uri, headers=auth_header(),
                        data=(('magnet', f'magnet:?xt=urn:btih:{t_hash}'),))
    return req.json()['id']


def selectFiles(_id: str, file_ids: [str]):
    uri = f'{BASE_URI}/torrents/selectFiles/{_id}'
    req = requests.post(uri, headers=auth_header(),
                        data=(('files', ','.join(file_ids)),))


def delete(_id: str):
    uri = f'{BASE_URI}/torrents/delete/{_id}'
    req = requests.delete(uri, headers=auth_header())


def unrestrict(link: str) -> str:
    uri = f'{BASE_URI}/unrestrict/link'
    req = requests.post(uri, headers=auth_header(),
                        data=(('link', link),))
    return req.json()['download']


def links(_id: str) -> [str]:
    uri = f'{BASE_URI}/torrents/info/{_id}'
    req = requests.get(uri, headers=auth_header())
    return req.json()['links']


def main():
    # Yeah global's suck but so does OOP and the only global here is the API
    # key and supporting multiple accounts or keys here is pointless.
    global API_KEY
    API_KEY = sys.argv[1]
    while True:
        mag = input('Paste a magnet: ').strip()
        print()
        if mag[:20] == 'magnet:?xt=urn:btih:':
            hsh = mag[20:20+40]
            tid = addMagnet(hsh)
            selectFiles(tid, ['all',])
            rd_links = links(tid)
            if not rd_links:
                y_n_prompt = input('No links found, remove torrent (Y/n)?: ')
                if y_n_prompt.strip().lower().startswith('n'):
                    print()
                    continue
            for link in rd_links:
                print(unrestrict(link))
            delete(tid)
            print()


if __name__ == '__main__':
    main()
