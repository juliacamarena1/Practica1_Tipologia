from unittest.mock import inplace

import numpy as np
import requests
from bs4 import BeautifulSoup
from bs4 import Comment
import pandas as pd

# Función para obtener la tabla de los datos de cada llamda que hacemos mediante BeautifulSoup
def get_dataframe_data_from_soup(soup):

    comments = soup.find_all(string=lambda text: isinstance(text, Comment))
    tables = []
    for each in comments:
        if 'table' in each:
            try:
                tables.append(pd.read_html(each)[0])
            except:
                continue

    df = tables[0]
    return df


# Función para eliminar los datos genéricos por cada fila de cada llamada
def drop_generic_columns(df):

    df.drop('Jugador', axis=1, inplace=True)
    df.drop('País', axis=1, inplace=True)
    df.drop('Posc', axis=1, inplace=True)
    df.drop('Equipo', axis=1, inplace=True)
    df.drop('Edad', axis=1, inplace=True)
    df.drop('Nacimiento', axis=1, inplace=True)
    df.drop('90 s', axis=1, inplace=True)
    df.drop('Partidos', axis=1, inplace=True)

    return df


# Función para eliminar las cabeceras que se van poniendo cada X filas en cada llamada
def drop_rows_heeaders(df):

    indexs_drop = df[df['RL'] == 'RL'].index
    df.drop(index=indexs_drop, inplace=True)

    return df


# Función para eliminar las columnas de las estadísticas básicas que no nos interesan
def drop_columns_basic_stats(df_stats_base):

    # Nos quedamos con los valores de ambas columnas para renombrarlas después
    col_gls = df_stats_base['Por 90 Minutos']['Gls.']
    col_gls_90 = df_stats_base['Por 90 Minutos']['Gls.']

    df_stats_base.columns = [col[1] for col in df_stats_base.columns]

    df_stats_base.drop('Gls.', axis=1, inplace=True)
    df_stats_base.drop('xG', axis=1, inplace=True)
    df_stats_base.drop('npxG', axis=1, inplace=True)
    df_stats_base.drop('xA', axis=1, inplace=True)
    df_stats_base.drop('npxG+xA', axis=1, inplace=True)
    df_stats_base.drop('xG+xA', axis=1, inplace=True)
    df_stats_base.drop('Partidos', axis=1, inplace=True)

    df_stats_base['Gls.'] = col_gls
    df_stats_base['Gls/90'] = col_gls_90

    return df_stats_base


# Función para eliminar las columnas de las estadísticas de disparos que no nos interesan
def drop_columns_shoot_stats(df_stats_shoot):

    df_stats_shoot.columns = [col[1] for col in df_stats_shoot.columns]

    df_stats_shoot = drop_generic_columns(df_stats_shoot)
    df_stats_shoot.drop('Gls.', axis=1, inplace=True)
    df_stats_shoot.drop('TP', axis=1, inplace=True)
    df_stats_shoot.drop('TPint', axis=1, inplace=True)
    df_stats_shoot.drop('xG', axis=1, inplace=True)
    df_stats_shoot.drop('npxG', axis=1, inplace=True)
    df_stats_shoot.drop('npxG/Sh', axis=1, inplace=True)
    df_stats_shoot.drop('G-xG', axis=1, inplace=True)
    df_stats_shoot.drop('np:G-xG', axis=1, inplace=True)

    return df_stats_shoot


def drop_columns_misc_stats(df_stats_misc):

    df_stats_misc.drop('RL', axis=1, inplace=True)
    df_stats_misc.drop('TA', axis=1, inplace=True)
    df_stats_misc.drop('TR', axis=1, inplace=True)
    df_stats_misc.drop('Pcz', axis=1, inplace=True)
    df_stats_misc.drop('TklG', axis=1, inplace=True)
    df_stats_misc.drop('Penal ejecutado', axis=1, inplace=True)

    return df_stats_misc

def modify_country_age(df_stats_base):


    df_stats_base['País'] = df_stats_base['País'].str[3:]

    df_stats_base['Edad'] = df_stats_base['Edad'].str[:2]

    return df_stats_base


def get_stats_base():

    # Realizamos la llamada a las estadisticas básicas
    url_stats_base = 'https://fbref.com/es/comps/12/stats/Estadisticas-de-La-Liga'
    soup_stats_base = BeautifulSoup(requests.get(url_stats_base).text, 'html.parser')

    # Recuperamos la tabla con los datos que nos interesa
    df_stats_base = get_dataframe_data_from_soup(soup_stats_base)

    # Borramos las columnas que opinamos que no son de utilidad
    df_stats_base = drop_columns_basic_stats(df_stats_base)

    # Modificamos el formato en el que está el país y la edad
    df_stats_base = modify_country_age(df_stats_base)

    # Eliminamos las cabeceras que aparecen cada X filas
    df_stats_base = drop_rows_heeaders(df_stats_base)



    return df_stats_base


def get_stats_shoot():

    # Realizamos la llamada a las estadisticas de disparos
    url_stats_shoot = 'https://fbref.com/es/comps/12/shooting/Estadisticas-de-La-Liga'
    soup_stats_shoot = BeautifulSoup(requests.get(url_stats_shoot).text, 'html.parser')

    # Recuperamos la tabla con los datos que nos interesa
    df_stats_shoot = get_dataframe_data_from_soup(soup_stats_shoot)

    # Borramos las columnas que opinamos que no son de utilidad
    df_stats_shoot = drop_columns_shoot_stats(df_stats_shoot)

    # Eliminamos las cabeceras que aparecen cada X filas
    df_stats_shoot = drop_rows_heeaders(df_stats_shoot)
    df_stats_shoot.drop('RL', axis=1, inplace=True)

    df_stats_shoot['Dist'].replace(np.nan,'0',inplace=True)

    # Transformamos la distancia del chute de yardas a metros
    df_stats_shoot['Dist'] = (pd.to_numeric(df_stats_shoot['Dist'])/1.0936).map('{:,.2f}'.format)

    return df_stats_shoot


def get_stats_misc():

    # Realizamos la llamada a las estadisticas diversas
    url_stats_misc = 'https://fbref.com/es/comps/12/misc/Estadisticas-de-La-Liga'
    soup_stats_misc = BeautifulSoup(requests.get(url_stats_misc).text, 'html.parser')

    # Recuperamos la tabla con los datos que nos interesa
    df_stats_misc = get_dataframe_data_from_soup(soup_stats_misc)

    df_stats_misc.columns = [col[1] for col in df_stats_misc.columns]

    df_stats_misc = drop_generic_columns(df_stats_misc)

    df_stats_misc = drop_rows_heeaders(df_stats_misc)

    df_stats_misc = drop_columns_misc_stats(df_stats_misc)

    return df_stats_misc


def save_dataset(df_final):

    # Guardamos el dataframe con todos los datos
    df_final.to_csv('estadisticas_jugadores_lfp_20_21.csv', sep=';', index=False)



df_stats_base = get_stats_base()
df_stats_shoot = get_stats_shoot()
df_stats_misc = get_stats_misc()

# Hacemos una concatenación de los dos tipos de estadisticas, ambas están ordenadas por nombre, por tanto simplemente concatenando es suficiente
df_merge = pd.concat([df_stats_base, df_stats_shoot], axis=1)

# Hacemos una concatenación del dataframe concatenado más el dataframe de estadísticas varias
df_final = pd.concat([df_merge, df_stats_misc], axis=1)

save_dataset(df_final)

