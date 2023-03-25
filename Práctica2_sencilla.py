#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: elenadelafuente

Solution simple to the tunel 
"""
patata=1

import time
import random
from multiprocessing import Lock, Condition, Process
from multiprocessing import Value
 
SOUTH = 1
NORTH = 0

NP = 10 # Numero de peatones
NCARS = 100

TIME_CARS_NORTH = 0.5  # a new car enters each 0.5s
TIME_CARS_SOUTH = 0.5
TIME_PED = 5 

time_in_sc_c = (1,0.5) # Tiempo que tarda cada coche en pasar
time_in_sc_p = (30,10) #Tiempo que tarda en pasar cada peaton

class Monitor():
    def __init__(self):
        self.np = Value('i',0) # Numero de peatones en el puente
        self.ncn = Value('i',0) # Numero de coches hacia el norte en el puente
        self.ncs = Value('i',0) # Numero de coches hacia el sur en el puente
        
        self.mutex = Lock()
        
        self.no_cars_n = Condition(self.mutex)
        self.no_cars_s = Condition(self.mutex)
        self.no_p = Condition(self.mutex)
        # self.nobody = Condition(self.mutex)

    # Ver si hay alguien en el puente     
    def are_no_p(self):
        t = self.np.value == 0 #Esto es verdad cuando no hay peatones
        return t
    
    def are_no_cn(self):
        t = self.ncn.value == 0 
        return t
    
    def are_no_cs(self):
        t = self.ncs.value == 0
        return t
    
    # Pedir entrada y salida peaton   
    def want_enter_p(self):
       self.mutex.acquire()
       self.no_cars_n.wait_for(self.are_no_cn) and \
           self.no_cars_s.wait_for(self.are_no_cs) #Ns si esto va a funcionar pero es cerciorarse de que no hay coches en el tunel
       self.np.value += 1 # Sumo uno al numero de peatones en el tunel 
       self.mutex.release()
     
    def leaves_p(self):
       self.mutex.acquiere()
       self.np.value -= 1
       if self.np.value == 0:
           self.no_cars_n.notify()
           self.no_cars_s.notify_all()
       self.mutex.release()
       
     
     #Pedir entrada salida coches norte
    def wants_enter_car_n(self):
         self.mutex.acquiere()
         self.no_p.wait_for(self.are_no_p) and \
             self.no_cars_s.wait_for(self.are_no_cs)
         self.ncn.value +=1
         self.mutex.release()
         
    def leaves_car_n(self):
         self.mutex.acquiere()
         self.ncn.value -=1
         if self.ncn.value == 0:
             self.no_cars_s.notify()
             self.no_p.notify_all()
         self.mutex.release()
         
         
     #Pedir entrada salida coches sur
    def wants_enter_car_s(self):
         self.mutex.acquiere()
         self.no_p.wait_for(self.are_no_p) and \
             self.no_cars_n.wait_for(self.are_no_cn)
         self.ncs.value +=1
         self.mutex.release()
         
    def leaves_car_s(self):
          self.mutex.acquiere()
          self.ncn.value -=1
          if self.ncs.value == 0:
              self.no_p.notify()
              self.no_cars_n.notify_all()
          self.mutex.release()


         
#El tiempo que estan en la sc
    
def delay_car(): #Lo que tarde un coche será lo mismo sin pensar en su dirección 
    time.sleep(random.random()/5)
 
def delay_pedestrian() -> None:
    time.sleep(random.random())
    
    # Ejecutar los procesos 
def car_n(cid, monitor):
    print(f"car {cid} heading NORTH wants to enter. {monitor}")
    monitor.wants_enter_car_n
    print(f"car {cid} heading NORTH enters the bridge. {monitor}")
    delay_car()
    print(f"car {cid} heading NORTH leaving the bridge. {monitor}")
    monitor.leaves_car_n
    print(f"car {cid} heading NORTH out of the bridge. {monitor}")
    
def car_s(cid, monitor):
    print(f"car {cid} heading SOUTH wants to enter. {monitor}")
    monitor.wants_enter_car_s
    print(f"car {cid} heading SOUTH enters the bridge. {monitor}")
    delay_car()
    print(f"car {cid} heading SOUTH leaving the bridge. {monitor}")
    monitor.leaves_car_s
    print(f"car {cid} heading SOUTH out of the bridge. {monitor}")
        
def pedestrian(pid, monitor):
    print(f"pedestrian {pid} wants to enter. {monitor}")
    monitor.want_enter_p()
    print(f"pedestrian {pid} enters the bridge. {monitor}")
    delay_pedestrian()
    print(f"pedestrian {pid} leaving the bridge. {monitor}")
    monitor.leaves_p()
    print(f"pedestrian {pid} out of the bridge. {monitor}")

#Generamos los procesos
    
def gen_cars_n(time_cars, monitor):
    cid = 0
    plst = []
    for _ in range(NCARS):
        cid += 1
        p = Process(target=car_n, args=(cid,monitor))
        p.start()
        plst.append(p)
        time.sleep(random.expovariate(1/time_cars))
    for p in plst:
        p.join()

def gen_cars_s(time_cars, monitor):
    cid = 0
    plst = []
    for _ in range(NCARS):
        cid += 1
        p = Process(target=car_s, args=(cid,monitor))
        p.start()
        plst.append(p)
        time.sleep(random.expovariate(1/time_cars))
    for p in plst:
        p.join()
    
def gen_pedestrian(monitor) -> None: 
    pid = 0
    plst = []
    for _ in range(NP):
        pid += 1
        p = Process(target=pedestrian, args=(pid, monitor))
        p.start()
        plst.append(p)
        time.sleep(random.expovariate(1/5))
    for p in plst:
        p.join()
          
    
def main():
    monitor = Monitor()
    gcars_north = Process(target=gen_cars_n, args=(TIME_CARS_NORTH, monitor))
    gcars_south = Process(target=gen_cars_s, args=(TIME_CARS_SOUTH, monitor))
    gped = Process(target=gen_pedestrian, args=(monitor,))
    
    gcars_north.start()
    gcars_south.start()
    gped.start()
    
    gcars_north.join()
    gcars_south.join()
    gped.join()     

if __name__ == '__main__':
    main()

       
       
       
       
       
       
       
       
        