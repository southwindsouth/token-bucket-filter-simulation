#!/usr/bin/env python
# -*- coding: utf-8 -*-
##
# @file     queue_onoff_traffic.py
# @author   Kyeong Soo (Joseph) Kim <kyeongsoo.kim@gmail.com>
# @date     2018-11-23
#
# @brief    Simulate a queueing system with an on-off packet generator.
#


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
    - pkt_ia_time: packet interarrival time in second
    - on_period: ON period in second
    - off_period: OFF period in second
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
                    print("t={0:.4E} [s]: packet generated with size={1:.4E} [B]".format(self.env.now, self.pkt_size))
            yield self.env.timeout(self.pkt_ia_time)
    
    #renew the toggle status
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

#fifo first in first out 
class FifoQueue(object):
    """Receive, process, and send out packets.

    Parameters:
    - env : simpy.Environment
    """
    def __init__(self, env,token_grate,bucket_size, trace=False):

        self.trace = trace
        self.store = simpy.Store(env)
        self.env = env
        self.out = None
        self.action = env.process(self.run(token_grate,bucket_size))
        self.wait_times = []
        self.lastTime=0
        self.bucket_size=bucket_size
        self.token_grate=token_grate




    def run(self,token_grate,bucket_size):


        token_grate=token_grate
        bucket_size=bucket_size
        bucket_fixed=bucket_size 
        lasttime = 0
        
        while True:
            msg = (yield self.store.get())

            # TODO: Implement packet processing here.
            # Calculate the generated token size based on the time difference between the two packets
            delay_global=(self.env.now-lasttime)
            bucket_size=bucket_size+delay_global*token_grate
            # If the token size exceeds the set maximum, modify it to a fixed size
            if(bucket_size>bucket_fixed):
                bucket_size=bucket_fixed
            # When the packet is larger than the token size, wait for the token to grow to match the packet size
            if(msg.size>bucket_size):   
                delay_add=(msg.size-bucket_size)/token_grate
                yield self.env.timeout(delay_add)
                self.out.put(msg) 
                bucket_size=0
            # If the packet is smaller than the token size, the token size is reduced by one packet size   
            if(msg.size<= bucket_size):
                bucket_size=bucket_size-msg.size
                self.out.put(msg)
            # Update the time when the last packet was sent
            lasttime=self.env.now    
           

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

        self.delay_msg_all=0

    def run(self):
        i=0
        # msg_lasttime=0
        # delay_msg_all=0
        while True:
            msg = (yield self.store.get())





            now = self.env.now
            delay_sink=now - msg.ctime
            self.wait_times.append(now - msg.ctime)
            if self.trace:
                print("t={0:.4E} [s]: packet arrived at PacketSink with delay={1:.4E} [B]".format(now, delay_sink))
              
                
            # msg_current_time=self.wait_times[i+1]
            # msg_previous_time=self.wait_times[i] 
            # if(i==0):
            #    delay_msg=msg_current_time-0
            # else:
            #    delay_msg=msg_current_time-msg_previous_time
            # self.delay_msg_all=delay_msg+self.delay_msg_all
            # i=i+1

    def put(self, pkt):
        self.store.put(pkt)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-S",
        "--pkt_size",
        help="packet size [byte]; default is 1000",
        default=1000,
        type=int)
    
    parser.add_argument(
        "-V",
        "--token_grate",
        help="token_generator_rate [byte/second]; default is 5000000",
        default=5000000,
        type=int)

    parser.add_argument(
        "-X",
        "--bucket_size",
        help="token_bucket_size size [byte]; default is 5000",
        default=5000,
        type=int)

    parser.add_argument(
        "-A",
        "--pkt_ia_time",
        help="packet interarrival time [second]; default is 0.00001",
        default=0.0001,
        type=float)

    parser.add_argument(
        "--on_period",
        help="on period [second]; default is 0.0001",
        default=0.001,
        type=float)

    parser.add_argument(
        "--off_period",
        help="off period [second]; default is 0.0001",
        default=0.001,
        type=float)

    parser.add_argument(
        "-T",
        "--sim_time",
        help="time to end the simulation [second]; default is 10",
        default=0.002,
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
    token_grate = args.token_grate
    bucket_size = args.bucket_size
    pkt_ia_time = args.pkt_ia_time
    on_period = args.on_period
    off_period = args.off_period
    sim_time = args.sim_time
    random_seed = args.random_seed
    trace = args.trace


    env = simpy.Environment()
    pg = OnoffPacketGenerator(env,pkt_size, pkt_ia_time, on_period, off_period,
                              trace)
    fifo = FifoQueue(env,token_grate,bucket_size,trace)  # TODO: implemente FifoQueue class
    ps = PacketSink(env, trace)
    pg.out = fifo
    fifo.out = ps
    env.run(until=sim_time)

    # print("Average waiting time = {:.4E} [s]\n".format(np.mean(ps.wait_times)))
    
    
    print("{0:.4E}\t{1:.4E}".format(pkt_size,np.mean(ps.wait_times)))
    # print("{0:.4E}\t{1:.4E}".format(sim_time,np.mean(ps.wait_times)))
    # print("{0:.4E}\t{1:.4E}".format(bucket_size,np.mean(ps.wait_times)))


    # delay_between_packet_average=ps.delay_msg_all/(bucket_size/1000)
    # print("{0:.4E}\t".format(delay_between_packet_average))