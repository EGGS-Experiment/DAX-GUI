import matplotlib.pyplot as plt
import numpy as np
from qutip import *
from ipywidgets import interact, interactive, fixed, interact_manual
import ipywidgets as widgets
import matplotlib.colors as mcolors
import math
import os


def vcd_viewer(filename, resolution = 1000):
    global urukul
    f = open(filename, "r")

    rows = []

    for row in f:
        rows.append(row)

    device_list = []
    time_master = []
    sub_device_list = []


    #devices
    ttl = {
           "output": [],
           "time" : [],
          }


    urukul = {
              "freq" : [],
              "amp" : [],
              "phase" : [],
              "state" : [], #compare state and amp, if state[i] = 0, amp[i] = 0
              "att" : [],
              "freq_time" : [],
              "amp_time" : [],
              "phase_time" : [],
              "state_time" : [],
              "att_time" : [],
             }


    phaser = {} #To-do


    #timeline
    timescale_dict = {"ns": 1e-9, "us": 1e-6, "ms": 1e-3, "s": 1}

    for i in range(len(rows)): #inserts a space in VCD file where number and descriptor are attached
        try:
            float(rows[i][0])
            rows[i] = " ".join(rows[i])

        except:
            pass

    for i in range(len(rows)): #this part of the code goes through the entire VCD file, finds each device, the device's sub options, and each time at which something happens

        if "$timescale" in rows[i]:
            timescale = rows[i].split()[2]

        elif "$version" in rows[i]:
            version = rows[i].split()[1]

        elif "$scope" in rows[i]:
            j = 0
            while True:
                row = rows[i + j].split()
                if "$upscope" in rows[i + j]:
                    break
                if row[1] == "module":
                    device_list.append(row[2])
                    device = row[2]
                elif row[0] == "$var":
                    sub_device_list.append([device, row[3], row[4]])
                j += 1
        elif "$enddefinitions" in rows[i]:
            time_start = i

        elif "#" in rows[i][0]:
            time_master.append(float(rows[i].split("#")[1]))

    time_lin = np.linspace(time_master[0], time_master[-1], resolution) * timescale_dict[timescale]

    ttl_count = 0
    urukul_count = 0
    phaser_count = 0

    urukul_order = {}
    ttl_order = {}
    phaser_order = {}

    for i in range(len(device_list)):
        if "urukul" in device_list[i] and "ch" in device_list[i]:
            urukul_order[device_list[i]] = urukul_count
            urukul_count +=1
        
        elif "ttl" in device_list[i] and "urukul"  not in device_list[i]:
            ttl_order[device_list[i]] = ttl_count
            ttl_count +=1
            
        elif "phaser" in device_list[i] and "ch" in device_list[i]:
            phaser_order[device_list[i]] = phaser_count
            phaser_count +=1

    for i in urukul:
        urukul[i] = [[] for i in range(urukul_count)]

    for i in phaser:
        phaser[i] = [[] for i in range(phaser_count)]

    for i in ttl:
        ttl[i] = [[] for i in range(ttl_count)]

    current_time = 0

    timed_rows = rows[time_start+1:]

    device_dict = {}
    for i in range(len(sub_device_list)):
        device_dict[sub_device_list[i][1]] = [sub_device_list[i][0], sub_device_list[i][2]]


    for i in range(len(timed_rows)):

        if "#" in timed_rows[i][0]:
            current_time = float(timed_rows[i].split("#")[1])

        row = timed_rows[i].split()

        if len(row) > 1:
            attribute = row[1]

            device = device_dict[attribute][0]
            descriptor = device_dict[attribute][1]
            value = row[0]

            if "urukul" in device: 

                if "ch" in device:
                    if descriptor == "freq":
                        urukul["freq"][urukul_order[device]].append(float(value.split("r")[1]))
                        urukul["freq_time"][urukul_order[device]].append(current_time)

                    elif descriptor == "phase":
                        urukul["phase"][urukul_order[device]].append(float(value.split("r")[1]))
                        urukul["phase_time"][urukul_order[device]].append(current_time)

                    elif descriptor == "amp":
                        urukul["amp"][urukul_order[device]].append(float(value.split("r")[1]))
                        urukul["amp_time"][urukul_order[device]].append(current_time)

                elif "cpld" in device:
                    if "att" in descriptor:
                        device = device.split("_")[0] + "_ch" + descriptor.split("_")[1]

                        if device in urukul_order:
                            urukul["att"][urukul_order[device]].append(float(value.split("r")[1]))
                            urukul["att_time"][urukul_order[device]].append(current_time)

                elif "ttl" in device:
                    device = device.split("_")[1] + "_ch" + device.split("_")[2][-1]
                    if device in urukul_order:
                        urukul["state"][urukul_order[device]].append(float(value))
                        urukul["state_time"][urukul_order[device]].append(current_time)

    for i in range(len(urukul_order)):
        if urukul["amp_time"][i] != urukul["state_time"][i]:
            for j in range(len(urukul["state_time"][i])):
                if urukul["state_time"][i][j] in urukul["amp_time"][i]:
                    counter = 0

                    while True:
                        if urukul["amp_time"][i][counter] == urukul["state_time"][i][j]:
                            time = urukul["state_time"][i][j]
                            break
                        else:
                            counter+=1

                else:
                    for k in range(len(urukul["amp_time"][i])):
                        if urukul["state_time"][i][j] not in urukul["amp_time"][i]:
                            if urukul["state_time"][i][j] < urukul["amp_time"][i][k]:
                                urukul["amp_time"][i].insert(k - 1, urukul["state_time"][i][j])

                                insert = urukul["state"][i][j] * urukul["amp"][i][k - 1]
                                urukul["amp"][i].insert(k - 1, insert)
                                break
                            try:
                                if urukul["state_time"][i][j] < urukul["amp_time"][i][k + 1]:
                                    urukul["amp_time"][i].insert(k, urukul["state_time"][i][j])
                                    insert = urukul["state"][i][j] * urukul["amp"][i][k + 1]
                                    urukul["amp"][i].insert(k + 1, insert)
                                    break
                            except:
                                insert = urukul["state"][i][j] * urukul["amp"][i][k - 1]
                                urukul["amp"][i].append(insert)
                                urukul["amp_time"][i].append(urukul["state_time"][i][j])
                                break

    parts = ["freq", "amp", "phase", "att"]

    for part in parts:
        part_time = part + "_time"
        for i in range(len(urukul_order)):
            for j in range(len(time_master)):
                if time_master != urukul[part_time][i]:
                    if time_master[j] not in urukul[part_time][i]:
                        for k in range(len(urukul[part_time][i])):
                            if time_master[j] not in urukul[part_time][i]:
                                if time_master[j] < urukul[part_time][i][k]:
                                    urukul[part_time][i].insert(k - 1, time_master[j])
                                    urukul[part][i].insert(k - 1, urukul[part][i][k - 1])
                                    break
                                else:
                                    try:
                                        if time_master[j] < urukul[part_time][i][k + 1]:
                                            urukul[part_time][i].insert(k + 1, time_master[j])
                                            urukul[part][i].insert(k + 1, urukul[part][i][k + 1])
                                            break
                                    except:

                                        urukul[part_time][i].append(time_master[j])
                                        urukul[part][i].append(urukul[part][i][-1])
                                        break




    for part in parts:

        part_time = part + "_time"

        for i in range(len(urukul_order)):
            saved_t = [[]]
            current = 0
            saved_y = [[]]
            counter = 0
            for j in range(len(urukul[part][i])):
                if j == 0:
                    current = urukul[part][i][j]
                if urukul[part][i][j] != current:
                    current = urukul[part][i][j]
                    saved_y.append([urukul[part][i][j]])
                    saved_t.append([urukul[part_time][i][j]])
                    counter +=1
                else:
                    saved_y[counter].append(urukul[part][i][j])
                    saved_t[counter].append(urukul[part_time][i][j])

            urukul[part][i] = saved_y
            urukul[part_time][i] = saved_t



    for i in range(len(urukul_order)):
        counter = 0
        while True:
            
            lengths = [[] for _ in range(len(parts))]
            for j in range(len(parts)):
                part_time = parts[j] + "_time"
                for k in range(len(urukul[part_time][i])):
                    lengths[j].append(len(urukul[part_time][i][k]))
            arr = []
            if len(lengths[0]) == counter:
                break
            for j in range(len(lengths)):
                arr.append(lengths[j][counter])

            min_len = min(arr)

            for j in range(len(parts)):
                part_time = parts[j] + "_time"

                if len(urukul[part_time][i][counter]) != min_len:
                    temp = [urukul[part_time][i][counter][:min_len], urukul[part_time][i][counter][min_len:]]
                    urukul[part_time][i][counter] = temp[0]
                    urukul[part_time][i].insert(counter + 1, temp[1])

                    temp2 = [urukul[parts[j]][i][counter][:min_len], urukul[parts[j]][i][counter][min_len:]]
                    urukul[parts[j]][i][counter] = temp2[0]
                    urukul[parts[j]][i].insert(counter + 1, temp2[1])

            counter += 1

    t_arr = [[] for _ in range(len(urukul_order))]

    for i in range(len(t_arr)):
        t_arr[i] = [[] for _ in range(len(urukul["freq_time"][i]))]


    t_arr_res = [[] for _ in range(len(urukul_order))]

    for i in range(len(t_arr_res)):
        t_arr_res[i] = [[] for _ in range(len(urukul["freq_time"][i]))]



    for i in range(len(t_arr_res)):
        for j in range(len(t_arr_res[i])):
            if (j + 1) != len(t_arr_res[i]):
                t_arr_res[i][j] = urukul["freq_time"][i][j+1][0] - urukul["freq_time"][i][j][0] 
            else:
                t_arr_res[i][j] = (urukul["freq_time"][i][j][0] + urukul["freq_time"][i][j][0]*.1) - urukul["freq_time"][i][j][0]

    for i in range(len(t_arr_res)):
        total = sum(t_arr_res[i])
        for j in range(len(t_arr_res[i])):
            t_arr_res[i][j] = (t_arr_res[i][j] / total) * resolution

            if t_arr_res[i][j] < 100:
                t_arr_res[i][j] = 100

    for i in range(len(t_arr)):
        for j in range(len(t_arr[i])):
            if (j + 1) != len(t_arr[i]):
                t_arr[i][j] = np.linspace(urukul["freq_time"][i][j][0], urukul["freq_time"][i][j+1][0], math.ceil(t_arr_res[i][j]))
            else:
                t_arr[i][j] = np.linspace(urukul["freq_time"][i][j][0], urukul["freq_time"][i][j][0] + urukul["freq_time"][i][j][0]*.1, math.ceil(t_arr_res[i][j]))


    y_arr = [[] for _ in range(len(urukul_order))]

    params = [[] for _ in range(len(urukul_order))]

    for i in range(len(params)):
        params[i] = [[] for _ in range(len(parts))]

    for i in range(len(y_arr)):
        y_arr[i] = [[] for _ in range(len(urukul["freq"][i]))]

    for i in range(len(y_arr)):
        for j in range(len(y_arr[i])):
            y_arr[i][j] = urukul["amp"][i][j][0] * np.sin(t_arr[i][j] * urukul["freq"][i][j][0]*2*np.pi +  urukul["phase"][i][j][0])
            
    for i in range(len(params)):
        for j in range(len(params[i])):
            part = parts[j]
            for k in range(len(urukul[part][i])):
                params[i][j].append(urukul[part][i][k][0])
            
    device_output = []
    for i in urukul_order:
        device_output.append(i)
        
    for i in ttl_order:
        device_output.append(i)

    for i in phaser_order:
        device_output.append(i)

        
    return t_arr, y_arr, device_output, params
