# deezer-playlist-generator
![Python package](https://github.com/ElinaValieva/deezer-playlist-generator/workflows/Python%20package/badge.svg)
![Python](https://img.shields.io/pypi/pyversions/deezer-playlist-generator.svg?style=flat-square)
![](https://img.shields.io/pypi/l/deezer-playlist-generator.svg?style=flat-square)
![Version](https://img.shields.io/pypi/v/deezer-playlist-generator.svg?logo=python&amp;logoColor=fff&amp;style=flat-square)

> Library for working with Deezer API for creating a playlist by your preferences in **Deezer**

&nbsp;

## Installation :hammer:
The package is published on [PyPI](https://pypi.org/project/deezer-playlist-generator/#description) and can be installed by running:
```
pip install deezer-playlist-generator
```
&nbsp;

## Usage :musical_note:
Easily query the Deezer API from you Python code. The data returned by the Deezer API is mapped to python resources:
```python
>>> client = DeezerApi()
>>> client.get_artist(27).name
> 'Daft Punk'
>>> client.get_track(3135556).title
'Harder, Better, Faster, Stronger'
>>> client.get_album(302127).title
> 'Discovery'
>>> client.client.get_playlist(908622995).title
> 'Bain moussant'
```
&nbsp;

## Deezer Client :triangular_flag_on_post:
#### Supported [permissions](https://developers.deezer.com/api/permissions)
 ```python 
 Access.BASIC = basic_access
 Access.MANAGE = manage_library
 Access.DELETE = detele_library
 ```
**Basic Client** - client with `basic_access`, which supports access users basic information
```python
client = DeezerApi()
```
**Client with a token** - the client allows for request an access token which is necessary to take action requiring the permissions you asked.
```python
client = DeezerApi(token=<TOKEN>, expired=3600, access=Access.MANAGE)
```
**Client with code auth** - client with next token generation
```python
client = DeezerApi(app_id=<APP_ID>, secret=<SECRET>, code=<CODE>, access=Access.MANAGE)
```
**Client** - client with all parameters, without a manual work for code and token generation
```python
client = DeezerApi(app_id=<APP_ID>, secret=<SECRET>, redirect_url=<REDIRECTED_URL>, access=Access.DELETE)
```
&nbsp;

## Player :arrow_forward:
For reproducing a playlist by your preferences in Deezer:  
```python
from deezer_api import DeezerApi, Access, DeezerPlayer

client = DeezerApi(app_id=<APP_ID>, secret=<SECRET>, redirect_url=<REDIRECTED_URL>, access=Access.MANAGE)  
tracks = cp.generate_tracks()  
DeezerPlayer(tracks).start()
```

![](https://github.com/ElinaValieva/deezer-playlist-generator/blob/master/images/markdown.png)