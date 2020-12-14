"""
 * Copyright 2020, Departamento de sistemas y Computación
 * Universidad de Los Andes
 *
 *
 * Desarrolado para el curso ISIS1225 - Estructuras de Datos y Algoritmos
 *
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 * Contribución de:
 *
 * Dario Correal
 *
 """
import config
from functools import partial
from DISClib.ADT.graph import gr
from DISClib.ADT import map as m
from DISClib.ADT import orderedmap as om
from DISClib.ADT import list as lt
from DISClib.ADT import graph as gr
from DISClib.DataStructures import listiterator as it
from DISClib.Algorithms.Graphs import scc
from DISClib.Algorithms.Graphs import dijsktra as djk
from DISClib.Utils import error as error
from DISClib.Algorithms.Sorting import mergesort
import datetime
assert config

"""
En este archivo definimos los TADs que vamos a usar y las operaciones
de creacion y consulta sobre las estructuras de datos.
"""

# ==============================
# Funciones Helper
# ==============================


def travel_lst(lista, parameter=None):
    iter = it.newIterator(lista)
    while it.hasNext(iter):
        node = it.next(iter)
        if parameter:
            yield node[parameter]
        else:
            yield node


def travel_map(Map, tree=False):
    lst = om.keySet(Map) if tree else m.keySet(Map)
    iter = it.newIterator(lst)
    while it.hasNext(iter):
        key = it.next(iter)
        value = om.get(Map, key) if tree else m.get(Map, key)
        yield key, (None if value is None else value["value"])


def getDateTimeTaxiTrip(taxitrip):
    """

    Recibe la informacion de un servicio de taxi leido del archivo de datos (parametro).

    Retorna de forma separada la fecha (date) y el tiempo (time) del dato 'trip_start_timestamp'

    Los datos date se pueden comparar con <, >, <=, >=, ==, !=

    Los datos time se pueden comparar con <, >, <=, >=, ==, !=

    """
    tripstartdate = taxitrip['trip_start_timestamp']

    return datetime.datetime.strptime(
        tripstartdate, '%Y-%m-%dT%H:%M:%S.%f')


# ==============================
# Funciones de Comparacion
# ==============================

def compfun(key: str = None, just=None):
    if key is None:
        def fc(x, y): return 0 if x == y else (
            1 if x > y else -1)
    elif just is None:
        def fc(x, y): return 0 if x[key] == y[key] else (
            1 if x[key] > y[key] else -1)
    elif just in ["x", "first", "1", 1]:
        def fc(x, y): return 0 if x[key] == y else (
            1 if x[key] > y else -1)
    elif just in ["y", "second", "2", 2]:
        def fc(x, y): return 0 if x == y[key] else (
            1 if x > y[key] else -1)
    return fc


# -----------------------------------------------------
#                       API
# -----------------------------------------------------


def init():
    analyzer = {}
    analyzer["taxis"] = m.newMap(
        maptype="CHAINING", comparefunction=compfun("key", "y"))
    analyzer["graph"] = gr.newGraph(
        datastructure="ADJ_LIST", directed=True, comparefunction=compfun("key", "y"))
    return analyzer


def try_convert(obj, type=float, default=0):
    try:
        return type(obj)
    except:
        # Si el usuario desea que el default sea el mismo obj debe indicarlo por parámetro default.
        return default


def addtaxi(analyzer, row):
    got = m.get(analyzer["taxis"], row["taxi_id"])
    if got is None:
        value = {"company": row["company"] if row["company"] else "Independent Owner",
                 "miles": try_convert(row["trip_miles"], float, 0),
                 "money": try_convert(row["trip_total"], float, 0),
                 "dates": [getDateTimeTaxiTrip(row)]
                 }
        m.put(analyzer["taxis"], row["taxi_id"], value)
    else:
        value = {"company": row["company"] if row["company"] else "Independent Owner",
                 "miles": try_convert(row["trip_miles"], float, 0) + got["value"]["miles"],
                 "money": try_convert(row["trip_total"], float, 0) + got["value"]["money"],
                 "dates": [getDateTimeTaxiTrip(row)] + got["value"]["dates"]
                 }
        m.put(analyzer["taxis"], row["taxi_id"], value)

# Funciones para agregar informacion al grafo


def addCommunityArea(analyzer, row):
    # Se modificó la Estructura de Datos "adjlist" con el fin de que cuando encontrara un nuevo
    # vértice al momento de agregar un arco, también añadiera el vértice al grafo.
    # Esto con el fin de disminuir considerablemente la complejidad del algoritmo.
    begin = try_convert(try_convert(row["pickup_community_area"]), int)
    end = try_convert(try_convert(row["dropoff_community_area"]), int)
    cost = try_convert(row["trip_seconds"])

    # Si los dos son diferentes a 0 (es decir, si la casilla no está vacía)
    if all([begin, end]):
        gr.addEdge(analyzer["graph"],
                   begin,
                   end,
                   cost)

# ==============================
# Funciones de consulta
# ==============================


def reqApart1(analyzer):
    companies = {}
    # Diccionario que almacena las compañías
    # O(analyzer["taxis"]["size"])
    for key, value in travel_map(analyzer["taxis"]):
        if value["company"] in companies:
            companies[value["company"]]["taxnum"] += 1
            companies[value["company"]]["servnum"] += len(value["dates"])
        else:
            companies[value["company"]] = {
                "taxnum": 1, "servnum": len(value["dates"])}
    return companies


def reqApart2(companies, M, N):
    topM = lt.newList(datastructure="ARRAY_LIST")
    topN = lt.newList(datastructure="ARRAY_LIST")
    # O(len(companies)*(max(M,N)))
    keepM, keepN = topM['size'] < M, topN['size'] < N
    while keepM or keepN:
        bestM = 0
        bestN = 0
        for i in companies:
            if keepM:
                taxnum = companies[i]["taxnum"]
                if taxnum > bestM and i not in topM['elements']:
                    bestM = taxnum
                    compM = i
            if keepN:
                servnum = companies[i]["servnum"]
                if servnum > bestN and i not in topN['elements']:
                    bestN = servnum
                    compN = i
        if keepM:
            lt.addLast(topM, compM)
        if keepN:
            lt.addLast(topN, compN)

        keepM, keepN = topM['size'] < M, topN['size'] < N

    return topM, topN

def puntos (companies):
   #funcion que calcula puntos y ordena en mmayor a menor los puntos
    pass

def  reqBpart1 (companies, N, fecha):
    Puntos = puntos(companies)
    final = lt.newList(datastructure="ARRAY_LIST")
    i=0
    while final["size"] >= N:
        if (companies[i]["fecha"]) == fecha:
            final.addLast(companies[i]["taxi_id"])
            i+=1
    return final

    
def reqBpart2 (companies,M,fecha1,fecha2):
    Puntos = puntos(companies)
    final2 = lt.newList(datastructure="ARRAY_LIST")
    i=0
    while final["size"] >= N:
        if (companies[i]["fecha"]) >= fecha1 and <= fecha2:
            final.addLast(companies[i]["taxi_id"])
            i+=1
    return final2