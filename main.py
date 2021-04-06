import requests
from bs4 import BeautifulSoup
from bs4 import Comment
import pandas as pd

url = 'https://fbref.com/es/comps/12/stats/Estadisticas-de-La-Liga'
page = requests.get(url)
soup = BeautifulSoup(page.text, 'html.parser')

comments = soup.find_all(string=lambda text: isinstance(text, Comment))

tables = []
for each in comments:
    if 'table' in each:
        try:
            tables.append(pd.read_html(each)[0])
        except:
            continue

df = tables[0]

df.columns = [col[1] for col in df.columns]

df.drop('Partidos',axis=1, inplace=True)
df.drop('xG',axis=1, inplace=True)
df.drop('npxG',axis=1, inplace=True)
df.drop('xA',axis=1, inplace=True)
df.drop('npxG+xA',axis=1, inplace=True)
df.drop('xG+xA',axis=1, inplace=True)

indexs_drop = df[df['RL']=='RL'].index

df.drop(index=indexs_drop, inplace=True)

df.to_csv('C:/Tmp/estadisticas_jugadores_lfp_20_21.csv', sep=';', index=False)