#!/bin/bash
cd /home/ec2-user/css/kernel/kernel-of-truth/poc/99a-sim
nice -n 10 ./venv/bin/python -u gate_cal_battery.py 3000 0.1 96 > results/gatecal_r9a/log_0.1_96.txt 2>&1 &
nice -n 10 ./venv/bin/python -u gate_cal_battery.py 3000 0.8 96 > results/gatecal_r9a/log_0.8_96.txt 2>&1 &
wait
nice -n 10 ./venv/bin/python -u gate_cal_battery.py 3000 0.1 160 > results/gatecal_r9a/log_0.1_160.txt 2>&1 &
nice -n 10 ./venv/bin/python -u gate_cal_battery.py 3000 0.8 160 > results/gatecal_r9a/log_0.8_160.txt 2>&1 &
wait
echo "BATTERY_COMPLETE" > results/gatecal_r9a/DONE.txt
