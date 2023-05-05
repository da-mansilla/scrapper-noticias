import requests
from bs4 import BeautifulSoup
from collections import Counter
import nltk
from nltk import SnowballStemmer

# Link hacia la pagina a escanear
LINK = "https://www.infobae.com/economia/"

# Obtener contenido de la página
r = requests.get(LINK)

# Array para contener las urls de las noticias
noticas_urls = []
if r.status_code == 200:
    soup = BeautifulSoup(r.text, 'html.parser')
    noticias_a = soup.find_all('a', {'class': 'headline-link'})
    for noticia in noticias_a:
        url = noticia['href']
        noticas_urls.append(url)

# Obtener las noticias de Economia
noticias_economia = list(filter(lambda n: "/economia/" in n,noticas_urls))

# Agregar prefijo para tener url completa
urls_completas = list(map(lambda n: "https://infobae.com"+n,noticias_economia))

# Obtener primeras 10 URLS
primeras_10_noticias = urls_completas[:10]

# Obtener el Titulo, Resumen, Imagenes y Cuerpo de cada noticia
noticias = []
for noticia in primeras_10_noticias:
    print(f"Escaneando noticia: {noticia}\n")
    response = requests.get(noticia)
    if response.status_code == 200:

        # Obtener Titulo
        soup = BeautifulSoup(response.text, 'html.parser')
        titulo_noticia = soup.find_all('h1', {'class': 'd23-article-headline left'})
        if not titulo_noticia:
            titulo_noticia = soup.find_all('h1', {'class': 'd23-article-headline-live-blogging'})
        titulo = titulo_noticia[0].text

        # Obtener Resumen
        resumen_noticia = soup.find_all('h2', {'class': 'd23-article-subheadline left'})
        if not resumen_noticia:
            resumen_noticia = soup.find_all('h2', {'class': 'd23-article-subheadline-live-blogging'})
        resumen = resumen_noticia[0].text

        # Obtener Imagenes
        imagenes = []
        imagenes_noticia = soup.find_all('img')
        # Obtener Imagenes de Cloudfront
        imagenes_filtradas = list(filter(lambda imagen: "cloudfront" in imagen.get('src'),imagenes_noticia))
        for imagen in imagenes_filtradas:
            imagenes.append(imagen.get('src'))

        # Obtener Cuerpo de la noticia
        cuerpo = ""
        cuerpo_noticia = soup.find_all('div',{'class':'d23-body-article'})
        if not cuerpo_noticia:
            cuerpo_noticia = soup.find_all('div',{'class':'d23-nd-body-blogging'})
        parrafos_noticia = cuerpo_noticia[0].find_all('p',{'class':'paragraph'})
        if not parrafos_noticia:
            parrafos_noticia = cuerpo_noticia[0].find_all('p',{'class':'d23-paragraph'})
        for parrafo in parrafos_noticia:
            cuerpo += parrafo.text

        # Guardar información en un array de documentos
        noticias.append({
                "titulo":titulo,
                "resumen":resumen,
                "imagenes":imagenes,
                "cuerpo":cuerpo
        })

# Realizar analisis de las noticias obtenidas

# Leer archivo con stop-words
with open('stop-words.txt', 'r') as exclusiones:
    palabras_excluidas = exclusiones.read().splitlines()

# Almacenar informacion de las noticias en una unica variable
texto_noticias = ""
for noticia in noticias:
    texto_noticias += noticia["titulo"].lower()
    texto_noticias += noticia["resumen"].lower()
    texto_noticias += noticia["cuerpo"].lower()

# Tokenizar texto
palabras_texto = nltk.word_tokenize(texto_noticias)

# Eliminar stop stop-words
palabras_filtradas = list(filter(lambda palabra: palabra not in palabras_excluidas,palabras_texto))

# Eliminar palabras que solo son numeros
palabras_filtradas = list(filter(lambda palabra: not palabra.isnumeric() ,palabras_filtradas))

# Obtener las 100 palabras mas frecuentes
contador = Counter(palabras_filtradas)
top_100_palabras = contador.most_common(100)

# Agregar palabras mas comunes a un array
palabras_mas_comunes = []
for palabra in top_100_palabras:
    palabras_mas_comunes.append(palabra[0])

# Obtener las palabras pasadas por el proceso de steamming
steamming_snowball = SnowballStemmer("spanish")
palabras_comunes_steamming = []
for palabra in palabras_mas_comunes:
    palabras_comunes_steamming.append(steamming_snowball.stem(palabra))

# Imprimir palabras
print("Top 100 palabras más comunes encontradas en Sección Economia de Infobae")
print(f" {'Palabra': <20} {'Stemming Porter': <20}")
for i,palabra in enumerate(palabras_mas_comunes):
    print(f" {palabras_mas_comunes[i]: <20} {palabras_comunes_steamming[i]: <20}")

