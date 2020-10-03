#Imports
import os
import sys
import random
from math import log, sqrt
from collections import deque
from dotenv import load_dotenv
import numpy as np
from util.results import Result
load_dotenv()

max_nrt_miat = int(str(os.getenv('MAX_NRT_MIAT')))
nrt_miat_increments = int(str(os.getenv('NRT_MIAT_INCREMENTS')))

class Node:
    def __init__(self, mtype, arrival, time):
        self.type = mtype
        self.arrival = arrival
        self.time = time

class Simulation:
    def __init__(self):
        self.mc =  0
        self.rtcl = 3
        self.nrtcl = 5 
        self.scl = 4
        self.server = 2
        self.current = Node(2,0,4)
        self.rt_queue = deque([])
        self.nrt_queue = deque([])
        self.preempt = -1
        self.rt_iat = self.nrt_iat = self.rt_st = self.nrt_st = 0
        # Results
        self.m = 0
        self.b = 0
        self.nrt = 0
        self.nnrt = 0
        self.rt_times = []
        self.nrt_times = []
        self.rt_mean = []
        self.nrt_mean = []
        self.rt_percentile = []
        self.nrt_percentile = []
        self.results = Result()

    def get_inputs(self):
        # Get inputs
        print("\nEnter following details: ")
        self.rt_iat = float(input("Enter mean inter-arrival time of RT messages: "))
        self.nrt_iat = float(input("Enter mean inter-arrival time of nonRT messages: "))
        self.rt_st = float(input("Enter mean service time of RT message: "))
        self.nrt_st = float(input("Enter mean service time of non RT message: "))
        self.m = int(input("Enter number of batches: "))
        self.b = int(input("Enter batch size: "))
    
    def calculate_time(self, t):
        # Calculate psuedo-random time
        time = (-1*t)*log(random.random())
        time = round(time, 4)
        return time

    def rt_arrival(self):
        # Arrival of RT Event
        self.mc = self.rtcl
        self.rt_queue.append(Node(1, self.mc, self.calculate_time(self.rt_st)))        
        self.rtcl = round(self.mc + self.calculate_time(self.rt_iat), 4)

        if len(self.rt_queue) > 0 and self.server == 0: # RT Queue not empty and server idle
            self.current = self.rt_queue.popleft()
            self.scl = round(self.mc + self.current.time, 4)
            self.server = 1
        elif len(self.rt_queue) > 0 and self.server == 2: # RT Queue not empty and server executing nRT job
            remaining = self.scl - self.mc
            self.current.time = round(remaining, 4) 
            
            if remaining != 0: # Preempt the current nRT job
                self.preempt = self.current.time
                self.nrt_queue.appendleft(self.current)
            
            self.current = self.rt_queue.popleft()    
            self.scl = round(self.mc + self.current.time, 4)
            self.server = 1
    
    def nrt_arrival(self):
        # Arrival of nRT Event
        self.mc = self.nrtcl
        self.nrt_queue.append(Node(2, self.mc, self.calculate_time(self.nrt_st)))
        self.nrtcl = round(self.mc + self.calculate_time(self.nrt_iat), 4)
        
        if len(self.nrt_queue) > 0 and self.server == 0: # Schedule the job is server idle
            self.current = self.nrt_queue.popleft()
            self.scl = round(self.mc + self.current.time, 4)
            self.server = 2
    
    def service_complete(self):
        # Job completion event
        self.mc = self.scl
        if self.current.type == 1 and self.nrt != self.b: # Calculate total time for job
            self.nrt += 1
            self.rt_times.append(self.mc - self.current.arrival)
        elif self.current.type == 2 and self.nnrt != self.b:
            self.nnrt += 1
            self.nrt_times.append(self.mc - self.current.arrival)

        if len(self.rt_queue) > 0: # RT Queue is not empty
            self.current = self.rt_queue.popleft()
            self.scl = round(self.mc + self.current.time, 4)
            self.server = 1
        elif len(self.nrt_queue) > 0 and self.preempt != -1: # Schedule preempted event 
            self.current = self.nrt_queue.popleft()
            self.scl = round(self.mc + self.current.time, 4)
            self.server = 2
            self.preempt = -1
        elif len(self.nrt_queue) > 0: # nRT queue is not empty
            self.current = self.nrt_queue.popleft()
            self.scl = round(self.mc + self.current.time, 4)
            self.server = 2
        else:
            self.current = None
            self.server = 0
    
    def print_status(self):
        # Print current system status
        if self.server == 0:
            data = "{}| {}| {}| {}| {}| {}| {}|".format(str(self.mc).ljust(10), str(self.rtcl).ljust(10),str(self.nrtcl).ljust(10),
            str(len(self.rt_queue)).ljust(10), str(len(self.nrt_queue)).ljust(10), '-'.ljust(10), str(self.server).ljust(15))
        else:    
            data = "{}| {}| {}| {}| {}| {}| {}|".format(str(self.mc).ljust(10), str(self.rtcl).ljust(10),str(self.nrtcl).ljust(10),
            str(len(self.rt_queue)).ljust(10), str(len(self.nrt_queue)).ljust(10), str(self.scl).ljust(10), str(self.server).ljust(15))

        if(self.preempt != -1):
            data += " s={}".format(str(self.preempt))
        print("".ljust(102,'-'))
        print(data)

    def calculate_ci(self):
        # Pop batch 0
        self.rt_mean.pop(0)
        self.nrt_mean.pop(0)
        self.rt_percentile.pop(0)
        self.nrt_percentile.pop(0)
        
        # Response time for RT
        rt_mean = np.mean(self.rt_mean)
        rt_std = np.std(self.rt_mean)
        rtci_lb = rt_mean - (2.0086*(rt_std/sqrt(len(self.rt_mean))))
        rtci_ub = rt_mean + (2.0086*(rt_std/sqrt(len(self.rt_mean))))
        # Percentile for RT
        rt_percentile_mean = np.mean(self.rt_percentile)
        rt_percentile_std = np.std(self.rt_percentile)
        rtci_lb2 = rt_percentile_mean - (2.0086*(rt_percentile_std/sqrt(len(self.rt_mean))))
        rtci_ub2 = rt_percentile_mean + (2.0086*(rt_percentile_std/sqrt(len(self.rt_mean))))

        # Response time for nRT
        nrt_mean = np.mean(self.nrt_mean)
        nrt_std = np.std(self.nrt_mean)
        nrtci_lb = nrt_mean - (2.0086*(nrt_std/sqrt(len(self.nrt_mean))))
        nrtci_ub = nrt_mean + (2.0086*(nrt_std/sqrt(len(self.nrt_mean))))
        # Percentile for nRT
        nrt_percentile_mean = np.mean(self.nrt_percentile)
        nrt_percentile_std = np.std(self.nrt_percentile)
        nrtci_lb2 = nrt_percentile_mean - (2.0086*(nrt_percentile_std/sqrt(len(self.rt_mean))))
        nrtci_ub2 = nrt_percentile_mean + (2.0086*(nrt_percentile_std/sqrt(len(self.rt_mean))))

        # Calculate results for plotting graph
        self.results.nrt_miat.append(self.nrt_iat)

        self.results.rt_mean.append(round(rt_mean, 4))
        self.results.rt_percentile.append(round(rt_percentile_mean,4))
        self.results.rtci.append((round(rtci_lb, 4), round(rtci_ub, 4)))
        self.results.percentile_rtci.append((round(rtci_lb2, 4), round(rtci_ub2, 4)))

        self.results.nrt_mean.append(round(nrt_mean, 4))
        self.results.nrt_percentile.append(round(nrt_percentile_mean,4))
        self.results.nrtci.append((round(nrtci_lb,4), round(nrtci_ub,4)))
        self.results.percentile_nrtci.append((round(nrtci_lb2, 4), round(nrtci_ub2, 4)))

        # Print batch results
        print("\n\nMean Inter-arrival time of nRT message: {}".format(self.nrt_iat))
        print("Mean of RT response time: {:0.4f}".format(rt_mean))
        print("95th percentile of RT response time: {:0.4f}".format(rt_percentile_mean))
        print("Mean of nRT response time: {:0.4f}".format(nrt_mean))
        print("95th percentile of nRT response time: {:0.4f}".format(nrt_percentile_mean))
        print("RT Mean Confidence Interval: {:0.4f} - {:0.4f}".format(rtci_lb, rtci_ub))
        print("nRT Mean Confidence Interval: {:0.4f} - {:0.4f}".format(nrtci_lb, nrtci_ub))
        print("RT Percentile Confidence Interval: {:0.4f} - {:0.4f}".format(rtci_lb2, rtci_ub2))
        print("nRT Percentile Confidence Interval: {:0.4f} - {:0.4f}".format(nrtci_lb2, nrtci_ub2))

    def process(self):
        # Run the simulation
        while(True):
            if self.nrt == self.b and self.nnrt == self.b: # Batch complete
                rt_mean = np.mean(self.rt_times)
                nrt_mean = np.mean(self.nrt_times)
                rt_percentile = np.percentile(self.rt_times, 95)
                nrt_percentile = np.percentile(self.nrt_times, 95)
                self.rt_mean.append(round(rt_mean,4))
                self.nrt_mean.append(round(nrt_mean,4))
                self.rt_percentile.append(round(rt_percentile,4))
                self.nrt_percentile.append(round(nrt_percentile,4))
                # Reset the RT and nRT buffers
                self.rt_times = [] 
                self.nrt_times = []
                self.nrt = self.nnrt = 0
                self.m -= 1
                if self.m == 0:
                    break
            
            clocks = []
            # Find which event occurs next
            if self.server == 0:
                clocks = [self.rtcl, self.nrtcl]
            else:
                clocks = [self.rtcl, self.nrtcl, self.scl]
            
            if self.rtcl == min(clocks):
                self.rt_arrival()
            elif self.nrtcl == min(clocks):
                self.nrt_arrival()
            else:
                self.service_complete()
        # Calculate confidence interval
        self.calculate_ci()

    def reset(self, no_batches):
        # Reset for new batch
        self.mc = 0
        self.rtcl = 3
        self.nrtcl = 5 
        self.scl = 4
        self.server = 2
        self.current = Node(2,0,4)
        self.rt_queue = deque([])
        self.nrt_queue = deque([])
        self.preempt = -1
        self.nrt = 0
        self.nnrt = 0
        self.rt_times = []
        self.nrt_times = []
        self.rt_mean = []
        self.nrt_mean = []
        self.rt_percentile = []
        self.nrt_percentile = []
        self.m = no_batches

    def run(self):
        # Start Simulation
        self.get_inputs()
        no_batches = self.m

        while(self.nrt_iat <= max_nrt_miat):
            self.reset(no_batches)
            self.process()
            self.nrt_iat += nrt_miat_increments
        self.results.display()


if __name__=='__main__':
    sim = Simulation()
    sim.run()
    
        