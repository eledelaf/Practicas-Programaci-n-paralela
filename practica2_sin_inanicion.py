#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: elenadelafuente
Solución evitando la inanición 
"""
from multiprocessing import Process
from multiprocessing import Condition, Lock
from multiprocessing import Value
from multiprocessing import current_process
import time, random

SOUTH = 1
NORTH = 0

NCARS = 100
NPED = 10
TIME_CARS_NORTH = 0.5  # a new car enters each 0.5s
TIME_CARS_SOUTH = 0.5  # a new car enters each 0.5s
TIME_PED = 5 # a new pedestrian enters each 5s
TIME_IN_BRIDGE_CARS = (1, 0.5) # normal 1s, 0.5s
TIME_IN_BRIDGE_PEDESTRIAN = (30, 10) # normal 30s, 10s
"""
Tengo que haceruna lista de los elementos que estan esperando
Voy a hacer turnos, en cada turno pasan maximo 5 coches o peatones
Si no hay nadie esperando paso al turno siguiente
"""

class Monitor():
    def __init__(self):
        self.patata = Value('i',0) #Contador
        
        self.np = Value('i',0) # Cuantas personas hay en el tunel
        self.ncn = Value('i',0) # Cuantos coches hay en el tunel dirección norte
        self.ncs = Value('i',0) # Cuantos coches hay en el tunel dirección sur
        
        self.p_waiting = Value('i',0) # Cantidad de peatones esperando 
        self.ncn_waiting = Value('i',0) # Cantidad de coches dirección norte esperando
        self.ncs_waiting = Value('i',0) # Cantidad de coches dirección sur esperando 
        
        self.turn = Value('i',0) # Toma valor 0 para peatones 1 para coches norte y 2 para coches sur
        
        self.mutex = Lock()
        
        self.cs = Condition(self.mutex)
        self.cn = Condition(self.mutex)
        self.p = Condition(self.mutex)
        
    def con_p(self):
        c1 = self.ncn.value == 0
        c2 = self.ncs.value == 0
        c3 = self.turn.value == 0
        
        """
        c4 = self.turn.value == 2
        c5 = self.ncs_waiting ==0
        """
        return c1 and c2 and c3
    
    def want_enter_p(self):
        self.patata.value += 1
        self.mutex.acquire()
        self.p_waiting.value += 1 # Sumo un peaton a los que estan esperando
        self.p.wait_for(self.con_p) # Espero a que no haya coches y que sea el turno de los peatones
        self.p_waiting.value -= 1
        self.np.value += 1
        self.mutex.release()
        
    def leaves_p(self):
        self.mutex.acquire()
        self.np.value -= 1
        if self.np.value == 0:
            self.cn.notify()
            self.cs.notity()
            self.turn.value = 1
        self.release()
        
    def con_cn(self):
        c1 = self.ncs == 0 #Num de coches direccion suren el tunel = 0 
        c2 = self.np == 0 #Num de peatones en el tunel = 0
        c3 = self.turn ==1 #Turno de los coches direccion norte
        """
        #Para tener en cuenta el caso en el que no haya gente esperando en el turno anterior
        c4 = self.turn == 0 #Si es el turno de los peatones pero no hay nadie esperando 
        c5 = self.p_waiting == 0
        """
        return c1 and c2 and c3
    
    def con_cs(self):
        c1 = self.ncs == 0
        c2 = self.np == 0
        c3 = self.turn ==1
        """
        c4 = self.turn == 0 
        c5 = self.p_waiting == 0
        """
        return c1 and c2 and c3
    
    def want_enter_c(self,direction):
        self.mutex.acquire()
        self.patata.value += 1
        if direction == NORTH:
            self.ncn_waiting.value += 1
            self.cn.wait_for(con_cn)
            self.cn_waiting.vale -= 1
            self
            
            
    
        
        
        
def main():
    monitor = Monitor()
        