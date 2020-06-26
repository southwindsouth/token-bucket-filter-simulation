@echo off 
for /L %S in (1000, 500, 10000) do python queue_onoff_traffic1.py  -S %S --no-trace>>averagewaitingtime1(packet_size_change).out
for /L %T in (0.002, 0.002, 0.01) do python queue_onoff_traffic2.py  -T %T --no-trace>>averagewaitingtime2(simulation_time_change).out
for /L %X in (1000, 500, 10000) do python queue_onoff_traffic3.py  -X %X --no-trace>>averagewaitingtime3(token_bucket_size_change).out