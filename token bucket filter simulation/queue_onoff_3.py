# -*- coding: utf-8 -*-
"""
Created on Thu Dec 19 16:09:03 2019

@author: dell
"""

import argparse
import numpy as np
import simpy


class Packet(object):
    """
    Parameters:
    - ctime: packet creation time
    - size: packet size in bytes
    """
    def __init__(self, ctime, size):
        self.ctime = ctime
        self.size = size


class OnoffPacketGenerator(object):
    """Generate fixed-size packets back to back based on on-off status.

    Parameters:
    - env: simpy.Environment
    - pkt_size: packet size in bytes
    - pkt_ia_time: packet interarrival time in m second
    - on_period: ON period in m second
    - off_period: OFF period in m second
    """
    def __init__(self, env, pkt_size, pkt_ia_time, on_period, off_period,
                 trace=False):
        self.env = env
        self.pkt_size = pkt_size
        self.pkt_ia_time = pkt_ia_time
        self.on_period = on_period
        self.off_period = off_period
        self.trace = trace
        self.out = None
        self.on = True
        self.gen_permission = simpy.Resource(env, capacity=1)
        self.action = env.process(self.run())  # start the run process when an instance is created

    def run(self):
        env.process(self.update_status())
        while True:
            with self.gen_permission.request() as req:
                yield req
                p = Packet(self.env.now, self.pkt_size)
                self.out.put(p)
                if self.trace:
                    print("t={0:.4E} [ms]: packet generated with size={1:.4E} [B]".format(self.env.now, self.pkt_size))
            yield self.env.timeout(self.pkt_ia_time)

    def update_status(self):
        while True:
            now = self.env.now
            if self.on:
                if self.trace:
                    print("t={:.4E} [s]: OFF->ON".format(now))
                yield env.timeout(self.on_period)
            else:
                if self.trace:
                    print("t={:.4E} [s]: ON->OFF".format(now))
                req = self.gen_permission.request()
                yield env.timeout(self.off_period)
                self.gen_permission.release(req)
            self.on = not self.on  # toggle the status


class FifoQueue(object):
    """Receive, process, and send out packets.

    Parameters:
    - env : simpy.Environment
    """
    def __init__(self, env, trace=False):
        self.trace = trace
        self.store = simpy.Store(env)
        self.env = env
        self.out = None
        self.action = env.process(self.run())
        self.current=env.now
       
    def run(self):
        tokengenerate=5*10**3
        capacity_size=5*10**3
        token_number=capacity_size
        #transmissionrate=10*10**3
        
        while True:
            msg = (yield self.store.get())
            
        if msg.size<=capacity_size:
            now=env.now
            passtime=now-self.current
            
     #  from the time zero to start, assume the bucket is full when simulation start 
            new_generatetoken=tokengenerate*passtime
            # the generator is always generate new tokens
            token_number=new_generatetoken+token_number
              
            if token_number>capacity_size:
                 token_number=capacity_size
             # the TBF can only let the capacity size burst though     
        
            if token_number<msg.size:
                yield self.env.timeout((msg.size-token_number)/tokengenerate)
                token_number=0
                
                 #delay=msg.size/transmissionrate
                 #yield self.env.timeout(delay)
            # if the packetsize is smaller than the number of token, it will pass immiedatily
            else:
                token_number= token_number-msg.size
                self.current=env.now
            # if packet is larger than token number, it should wait and will shaping
           
                
            self.out.put(msg)

    def put(self, pkt):
        self.store.put(pkt)


class PacketSink(object):
    """Receives packets and display delay information.

    Parameters:
    - env : simpy.Environment
    - trace: Boolean

    """
    def __init__(self, env, trace=False):
        self.store = simpy.Store(env)
        self.env = env
        self.trace = trace
        self.wait_times = []
        self.action = env.process(self.run())

    def run(self):
        while True:
            msg = (yield self.store.get())
            now = self.env.now
            msg.delay=now-msg.ctime
            #self.wait_times.append(now - msg.ctime)
            self.wait_times.append(msg)
            if self.trace:
                print("t={0:.4E} [s]: packet arrived with size={1:.4E} [B]".format(now, msg.size))
            
                
    def put(self, pkt):
        self.store.put(pkt)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-S",
        "--pkt_size",
        help="packet size [byte]; default is 100",
        default=1000,
        type=int)
    parser.add_argument(
        "-A",
        "--pkt_ia_time",
        help="packet interarrival time [m second]; default is 10*10**(-3)",
        default=10*10**(-3),
        type=float)
    parser.add_argument(
        "--on_period",
        help="on period [m second]; default is 1.0",
        default=1,
        type=float)
    parser.add_argument(
        "--off_period",
        help="off period [m second]; default is 1.0",
        default=1,
        type=float)
    parser.add_argument(
        "-T",
        "--sim_time",
        help="time to end the simulation [second]; default is 2s",
        default=2,
        type=float)
    parser.add_argument(
        "-R",
        "--random_seed",
        help="seed for random number generation; default is 1234",
        default=1234,
        type=int)
    parser.add_argument('--trace', dest='trace', action='store_true')
    parser.add_argument('--no-trace', dest='trace', action='store_false')
    parser.set_defaults(trace=True)
    args = parser.parse_args()

    # set variables using command-line arguments
    pkt_size = args.pkt_size
    pkt_ia_time = args.pkt_ia_time
    on_period = args.on_period
    off_period = args.off_period
    sim_time = args.sim_time
    random_seed = args.random_seed
    trace = args.trace

    env = simpy.Environment()
    pg = OnoffPacketGenerator(env, pkt_size, pkt_ia_time, on_period, off_period,
                              trace)
    fifo = FifoQueue(env, trace)  # TODO: implemente FifoQueue class
    ps = PacketSink(env, trace)
    pg.out = fifo
    fifo.out = ps
    env.run(until=sim_time)
    
    #ps.wait_times=sorted(ps.wait_times,key=lambda Packet:Packet.ctime)

    #print("Average waiting time = {:.4E} [s]\n".format(np.mean(ps.wait_times)))
    List_msg=[]
    for i in range(len(ps.wait_times)-1):
        msg_current=ps.wait_times[i+1]
        msg_previous=ps.wait_times[i]
        
        if i==0:
            turedelay=msg_previous.ctime-0
        else:
            turedelay=msg_current.delay-msg_previous.delay
            
        if turedelay<0:
            turedelay=0
        packet=Packet(msg_previous.ctime,msg_previous.size)
        packet.delay=turedelay
        List_msg.append(packet) 
    
        
    for msg in List_msg:
        print(msg.ctime,msg.delay)
        print("average waiting time:")
        print("{:,4E} = {:.4E}\n".format(pkt_size,np.mean([msg.delay for msg in List_msg])))
           
       #print("Average waiting time = {:.4E} [s]\n".format(ps.wait_times[i+1]-ps.wait_times[i]))
        