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


import sys
import config
from App import controller
from DISClib.ADT import stack
from DISClib.ADT import orderedmap as om
from DISClib.ADT import graph as gr
from DISClib.ADT import map as m
import timeit

assert config

"""
La vista se encarga de la interacción con el usuario.
Presenta el menu de opciones  y  por cada seleccion
hace la solicitud al controlador para ejecutar la
operación seleccionada.
"""

# ___________________________________________________
#  Variables
# ___________________________________________________


# ___________________________________________________
#  Menu principal
# ___________________________________________________

"""
Menu principal
"""

recursionLimit = 20000
sys.setrecursionlimit(recursionLimit)


class InputError(Exception):
    pass


filenames = ("taxi-trips-wrvz-psew-subset-small.csv",
             "taxi-trips-wrvz-psew-subset-medium.csv",
             "taxi-trips-wrvz-psew-subset-large.csv")

num = 0


def show_menu():
    menu_op = ["Inicializar Analizador",
               "Cargar Datos",
               "Parte A",
               "Parte B",
               "Parte C",
               "Salir"]
    print("*"*30)
    for c, op in enumerate(menu_op):
        print(f"{c+1}) {op}")
    print("*"*30)


def menu():
    show_menu()
    return int(input("Ingresa la opcion:\n>"))


def argbytype(txt: str, tp: type = str):
    try:
        ret = tp(input(txt))
    except TypeError as tE:
        if tE.args[0].endswith("callable"):
            raise tE
        else:
            raise InputError(f"Wrong input, type:'{tp}' expected.")
    return ret


def solver(opt: int,):
    global num, filenames
    if opt == 1:
        globals().update({"analyzer": controller.init()})
    elif opt == 2:
        controller.load(filenames[num], analyzer)
    elif opt == 3:
        controller.reqA(analyzer)
    elif opt == 4:
        controller.reqB(analyzer)
    elif opt == 5:
        controller.reqC(analyzer)
    else:
        print("Hasta pronto!")
        return "finish"


def main():
    while (op := menu()) != 0:
        if solver(op) == "finish":
            break


if __name__ == "__main__":
    main()
