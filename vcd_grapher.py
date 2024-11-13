import matplotlib.pyplot as plt
import numpy as np
from qutip import *
from ipywidgets import interact, interactive, fixed, interact_manual
import ipywidgets as widgets
import matplotlib.colors as mcolors
import os

def vcd_viewer(filename, resolution = 1000):
    global device_list, temp_counter, device_dict, freq, time_list, sub_device_list, device_timeline, plot, plot_phase, plot_amp, temp, amp, phase, temp_vars
    f = open(filename, "r")

    rows = []
    for row in f:
        rows.append(row)

    device_list = []
    time_list = []
    sub_device_list = []

    timescale_dict = {"ns": 1e-9, "us": 1e-6, "ms": 1e-3, "s": 1}
    for i in range(len(rows)):
        j = i
        if "$timescale" in rows[i]:
            timescale = rows[i].split()[2]
        if "$scope" in rows[i]:
            while True:
                row = rows[j].split()
                if row[1] == "module":
                    device_list.append(row[2])
                    device = row[2]
                if row[0] == "$var":
                    sub_device_list.append([device, row[3], row[4]])
                elif "$upscope" in rows[j]:
                    break
                j+=1
        if "#" in rows[i][0]:
            row = rows[j].split()
            if row[0].split("#")[1] =="":
                time_list.append(row[0][-1])
            else:
                time_list.append(row[0].split("#")[1])


    device_timeline = [[] for i in range(len(device_list))]

    device_dict = {}
    sub_device_dict = {}
    sub_device_def = {}

    for i in range(len(sub_device_list)):
        device = sub_device_list[i][0]
        if sub_device_list[i][0] not in device_dict:
            device_dict[device] = []

        device_dict[device].append([sub_device_list[i][1], sub_device_list[i][2]])
        sub_device_dict[sub_device_list[i][1]] = len(device_dict[device])-1
        sub_device_def[sub_device_list[i][1]] = sub_device_list[i][2]

    device_nums = {}

    for i in range(len(device_list)):
        device_nums[device_list[i]]=i

    for i in range(len(device_timeline)):
        device_timeline[i] = [[0 for k in range(len(time_list))] for j in range(len(device_dict[device_list[i]]))]

    time_dict = {}
    for i in range(len(time_list)):
        time_dict[time_list[i]]=i

    for i in range(len(rows)):
        cont = 0
        row = rows[i]
        if row[0] == "#":
            time = row.split("#")[1].replace("\n", "")
            if row.split("#")[1] == "":
                time = row.split("#")[2].replace("\n", "")
        if row[0] == "1" or row[0] == "0":
            value = int(row[0])
            cont = 1
        if row[0] == "r":
            value = float(row.replace("\n", "").split("r")[1].split()[0])
            row = rows[i].split()
            cont = 1
        if cont == 1: 
            for j in device_dict:
                for k in range(len(device_dict[j])):
                    if row[1] in device_dict[j][k]:
                        device = j
                        time_val = time_dict[time]
                        for l in range(time_val,len(time_list)):
                            device_timeline[device_nums[device]][sub_device_dict[row[1]]][l] = value


    urukul_control = []
    
    for i in range(len(device_list)):
        
        
        if "ttl" in device_list[i] and "urukul" not in device_list[i]:
            y = np.array(device_timeline[i][0])
            x = np.array(time_list)
            plt.step(x, y, "-", where="post", label = device_list[i])
            plt.legend()
            return x, y, device_list[i]
                        

        elif "urukul" in device_list[i] and "ch" in device_list[i]:
            for j in range(len(time_list)):
                temp_time = []
                plot = []
                freq = []
                amp = []
                phase = []
                for k in range(len(time_list)):
                    if k == 0:
                        prev_val_freq = device_timeline[i][1][k]     
                        prev_val_amp = device_timeline[i][4][k]  
                        prev_val_phase = device_timeline[i][2][k]
                        temp_time.append(time_list[k])
                    else:
                        if device_timeline[i][1][k] == prev_val_freq:
                            temp_time.append(time_list[k])
                            prev_val_freq = device_timeline[i][1][k]
                            if k == len(time_list)-1:
                                plot.append(temp_time)
                                freq.append(device_timeline[i][1][k])
                        else:
                            plot.append(temp_time)
                            freq.append(prev_val_freq)
                            temp_time = []
                            prev_val_freq = device_timeline[i][1][k]     
                            prev_val_amp = device_timeline[i][4][k]  
                            prev_val_phase = device_timeline[i][2][k]
                            temp_time.append(time_list[k])

                plot_amp = []
                amp = []
                temp_time_amp = []
                for k in range(len(time_list)):
                    if k == 0:
                        prev_val_amp = device_timeline[i][4][k]  
                        temp_time_amp.append(time_list[k])
                    else:
                        if device_timeline[i][4][k] == prev_val_amp:
                            temp_time_amp.append(time_list[k])
                            prev_val_amp = device_timeline[i][4][k]
                            if k == len(time_list)-1:
                                plot_amp.append(temp_time_amp)
                                amp.append(device_timeline[i][4][k])
                        else:
                            plot_amp.append(temp_time_amp)
                            amp.append(prev_val_amp)
                            temp_time_amp = []
                            prev_val_amp = device_timeline[i][4][k]  
                            temp_time_amp.append(time_list[k])

                plot_phase = []
                phase = []
                temp_time_phase = []
                for k in range(len(time_list)):
                    if k == 0:
                        prev_val_phase = device_timeline[i][2][k]  
                        temp_time_phase.append(time_list[k])
                    else:
                        if device_timeline[i][2][k] == prev_val_phase:
                            temp_time_phase.append(time_list[k])
                            prev_val_phase = device_timeline[i][2][k]
                            if k == len(time_list)-1:
                                plot_phase.append(temp_time_phase)
                                phase.append(device_timeline[i][2][k])
                        else:
                            plot_phase.append(temp_time_phase)
                            phase.append(prev_val_phase)
                            temp_time_phase = []
                            prev_val_phase = device_timeline[i][2][k]  
                            temp_time_phase.append(time_list[k])

                            
    #Graphing
            
            if len(plot) == len(plot_amp) == len(plot_phase):
                t_arr = []
                y_arr = []
                for z in range(len(plot)):
                    t = np.linspace()
                    y = amp[z]*np.sin(t*freq[z]*2*np.pi + phase[z])
                    t_arr.append(t)
                    y_arr.append(y)
                    plt.xlabel("Seconds (s)")
                    plt.ylabel("Relative Amplitude")
                return t_arr, y_arr, device_list[i]
            elif len(plot) == len(plot_amp):
                t_arr = []
                y_arr = []
                if len(plot_phase) == 1:
                    for z in range(len(plot)):
                        t = np.linspace(float(plot[z][0])*timescale_dict[timescale], float(plot[z][-1])*timescale_dict[timescale], resolution)
                        
                        tf = float(plot[z][-1])*timescale_dict[timescale]
                        ti = float(plot[z][0])*timescale_dict[timescale]
                        
                        t_end = tf - ti 
                        t_graph = np.linspace(0, t_end, resolution)
                        
                        y = amp[z]*np.sin(t_graph*freq[z]*2*np.pi + phase[0])

                        if device_list[i]!="core":
                            t_arr.append(t)
                            y_arr.append(y)

                return t_arr, y_arr, device_list[i]

            elif len(plot_phase) == 1 and len(plot_amp) == 1:
                t_arr = []
                y_arr = []
                for z in range(len(plot)):
                        t = np.linspace(float(plot[z][0])*timescale_dict[timescale], float(plot[z][-1])*timescale_dict[timescale], resolution)
                        tf = float(plot[z][-1])*timescale_dict[timescale]
                        ti = float(plot[z][0])*timescale_dict[timescale]
                        
                        t_end = tf - ti 
                        t_graph = np.linspace(0, t_end, resolution)
                        y = amp[0]*np.sin(t_graph*freq[z]*2*np.pi + phase[0])

                        if device_list[i]!="core":
                            t_arr.append(t)
                            y_arr.append(y)
                            plot(freq[z])

                return t_arr, y_arr, device_list[i]
                            
            else:
                t_arr = []
                y_arr = []
                if len(plot) > 1:
                    
                    temp = [[] for j in range(len(plot))]
                    temp_vars = [[] for j in range(len(plot))]

                    for x in range(len(plot)):
                        for w in range(len(plot_amp)):
                            if set(plot[x]).issubset(set(plot_amp[w])):
                                for v in range(len(plot_phase)):
                                    if set(plot[x]).issubset(set(plot_phase[v])): 
                                        temp[x] = plot[x]
                                        temp_vars[x] = [freq[x],  amp[w], phase[v]]
                
                                        
                
                elif len(plot_amp) > 1:
                    temp = [[] for j in range(len(plot_amp))]
                    temp_vars = [[] for j in range(len(plot_amp))]

                    for x in range(len(plot_amp)):
                        for w in range(len(plot)):
                            if set(plot_amp[x]).issubset(set(plot[w])):
                                for v in range(len(plot_phase)):
                                    if set(plot_amp[x]).issubset(set(plot_phase[v])):
                                        temp_vars[x] = [freq[w], amp[x], phase[v]]
                                        temp[x] = plot_amp[x]
                                        

                elif len(plot_phase) > 1:
                    temp = [[] for j in range(len(plot_phase))]
                    temp_vars = [[] for j in range(len(plot_phase))]
                    for x in range(len(plot_phase)):
                        for w in range(len(plot)):
                            if set(plot_phase[x]).issubset(set(plot_amp[w])):
                                for v in range(len(plot_amp)):
                                    if set(plot_phase[x]).issubset(set(plot[v])): 
                                        temp[x] = plot_phase[x]
                                        temp_vars[x] = [freq[w],  amp[v], phase[x]]
                                        
                                        
                if len(temp) == len(temp_vars):
                    for x in range(len(temp)):
                        for y in range(len(temp[x])):
                        
                            temp[x][y] = float(temp[x][y])
                            temp_vars[x][y] = float(temp_vars[x][y])
                            
                        t = np.linspace(temp[x][0]*timescale_dict[timescale], temp[x][-1]*timescale_dict[timescale], resolution)
                        tf = temp[x][-1]*timescale_dict[timescale]
                        ti = temp[x][0]*timescale_dict[timescale]
                        
                        t_end = tf - ti 
                        t_graph = np.linspace(0, t_end, resolution)
                        y = temp_vars[x][1]*np.sin(t_graph*temp_vars[x][0]*2*np.pi + temp_vars[x][2])
                        
                        t_arr.append(t)
                        y_arr.append(y)
                        
                        
                return t_arr, y_arr, device_list[i]
                        
def graph_viewer(filename):
    '''
    Callable functions from ChatGPT, only compatiable with Jupyter Notebook
    '''

    t, y, device = vcd_viewer(filename, 1000)

    def f(Resolution = 1000, Save_Image = False, X_Axis_Scale = 8, Y_Axis_Scale = 6):
        t, y, device = vcd_viewer(filename, Resolution)
        graph_arr = []
        try:
            fig, ax = plt.subplots(figsize=(X_Axis_Scale, Y_Axis_Scale))
            for i in range(len(t)):
                ax.plot(t[i], y[i], color = ans["color"])
            ax.set_title(ans["title"])
            ax.set(xlabel=ans["xlabel"], ylabel=ans["ylabel"])
            ax.legend(ans["legend"])

        except:
            print("Not available")
            
        if Save_Image:
            name = device
            cont = 0
            tmp = 1
            while cont == 0:
                name = device.split()[0] + " (" + str(tmp) + ")"
                if os.path.isfile(name):
                    cont = 1
                else:
                    tmp += 1
            plt.savefig(name)
            Save_Image = False
    
    options = {
        "title":"Title of Graph: \n",
        "xlabel":"x Label: \n",
        "ylabel":"y Label: \n",
        "color":"Color of Plot: \n",
        "legend":"Legend: \n",
    }

    ans = {}
    def title(Title):
        ans['title']=Title
    def xlab(X_Label):
        ans['xlabel']=X_Label
    def ylab(Y_Label):
        ans['ylabel']=Y_Label
    def color(Color):
        if Color.lower() not in mcolors.CSS4_COLORS:
            print(Color + " is not a color option, please enter a different color.")
        else:
            print("")
            ans['color']=Color
    def legend(Legend):
        ans['legend']=Legend


    interact(title, Title=device)
    interact(xlab, X_Label='Time (s)')
    interact(ylab, Y_Label='Relative Amplitude')
    interact(color, Color='blue')
    interact(legend, Legend = "")

    

    w = interactive(f, Save_Image = False, Resolution=(0,1000), X_Axis_Scale=(1,100), Y_Axis_Scale=(1, 30), zoom = (1.0, t[-1][-1]), position = (0.0, t[-1][-1]))
    display(w)
