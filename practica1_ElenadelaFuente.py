#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: elenadelafuente
"""
from multiprocessing import Process, Manager
from multiprocessing import BoundedSemaphore, Semaphore, Lock
from multiprocessing import current_process
from multiprocessing import Value, Array
from time import sleep
from random import random

N = 5 # Cantidad de veces que produce cada produtor
K = 3 #Capacidad que tiene cada buffer de cada productor
NPROD = 3 # Numero de productores 

storage = Array('i', NPROD*[-2]) #Almacen inicial 
index = Value('i', 0)

non_empty = Semaphore(0)
empty = Lock()
manager = Manager()
almacen = manager.list() 
mutex = Lock()


def delay():
    sleep(random()/3)
    
   
#Funciones auxiliares 

def min_pos(lista):
    # buscar el min positivo 
    #lista = list(array)
    l = []
    for i in range(len(lista)):
        if lista[i]>=0:
            l.append(lista[i])
    return min(l)
            
def lis_acaba(lista):
    """
    Parameters
    ----------
    lista : La lista  donde los productores meten numeros 

    Returns
    -------
    t : Si todos los elmentos de la lista son igual a -1 devuelve TRUE, 
        en caso contrario Flase
    """
    t = True
    for i in lista :
        if i == -1:
            t = t
        else:
            t = False
    return t

def lis_acaba2(lista):
    """
    Parameters
    ----------
    lista : La lista  donde los productores meten numeros 

    Returns
    -------
    t : Si hay almenos un elemento igual a -1 devuelve TRUE,
       en caso contrario devuelve FALSE 
    """
    for i in lista:
        if i == -1:
            return True 
    return False

def add_data(storage, mutex, value):
    # Dado un valor, lo añade al storage en función de si el semaforo mutex lo permite o no 
    mutex.acquire()
    try:
        j = storage.index(-2) #Buscamos el primer hueco vacio en el array 
        storage[j] = value #Añadimos el valor que ha producido un productor al array 
        delay()
    finally:
        mutex.release()
        
def producer(storage, index, empty, non_empty, mutex):
    for v in range(N):
        delay()
        empty.acquire()
        value = max(storage) + random(0,10)
        add_data(storage, mutex,value)
        non_empty.release()
        print (f"producer {current_process().name} almacenado {v}",storage[:])

def mover(storage):
    n = len(storage)
    storage1 = list(storage)
    for i in range(n-1):
        storage[i] = storage1[i+1]
    storage[n-1] = -2
    return storage

def get_data(storage, almacen, mutex):
    mutex.acquiere()
    try:
        value = storage[0]
        almacen.append(value)
        storage = mover(storage)        
    finally:
        mutex.release()
    return 

def consumer(storage, index, empty, non_empty, mutex):
    for v in range(N):
        non_empty.acquire()
        print (f"consumer {current_process().name} desalmacenando",storage[:])
        dato = get_data(storage, index, mutex)
        empty.release()
        print (f"consumer {current_process().name} consumiendo {dato}",storage[:])
        delay()

def main():
    print ("almacen inicial", storage[:])
    prodlst = [Process(target=producer, name=f'prod_{i}', args=(storage, index, empty, non_empty, mutex))
                for i in range(NPROD)]

    conslst = [Process(target=consumer,name= f'cons',
                      args=(storage, index, empty, non_empty, mutex))]

    for p in prodlst + conslst:
        p.start()

    for p in prodlst + conslst:
        p.join()


if __name__ == '__main__':
    main()
    
    