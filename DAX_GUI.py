import sys
import io
import contextlib
import os
import subprocess
import vcd_grapher
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import datetime


from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.setWindowTitle("DAX Simulations")

        self.width = 1920
        self.height = 1080
        self.resize(self.width, self.height)
        
    def initUI(self):
        main = QGridLayout()
        self.output = QTextEdit(self)
        self.output.setFixedHeight(100)
        self.output.setReadOnly(True) 
        self.output.setPlaceholderText("Output window (will display info)")

        
        main.addWidget(self.output, 2, 0)
        
        self.vcd = QTextEdit(self)
        self.vcd.setReadOnly(True)
        self.vcd.setPlaceholderText("Imported VCD files will be shown here")
        
        
        sub_layout = QGridLayout()
        
        dax_layout = QVBoxLayout()
        dax_buttons = QHBoxLayout()
        
        qutip_layout = QVBoxLayout()
        qutip_buttons = QHBoxLayout()
        
        graph_layout = QVBoxLayout()
        graph_buttons = QHBoxLayout()
        
        sub_layout.addLayout(dax_layout, 0, 0, 2, 1)
        sub_layout.addLayout(qutip_layout, 0, 1, 2, 1)
        sub_layout.addLayout(graph_layout, 0, 2, 2, 1)


        main.addLayout(sub_layout, 0, 0, 1, 3)
        
        self.dax_script = QTextEdit(self)
        
        self.dax_script.setSizePolicy(
            self.dax_script.sizePolicy().horizontalPolicy(),
            self.dax_script.sizePolicy().verticalPolicy().Expanding
        )
        
        self.dax_label = QLabel("ARTIQ (DAX) Script")
        dax_layout.addWidget(self.dax_label)
        
        dax_layout.addWidget(self.dax_script)
        
        self.dax_submit = QPushButton("Submit", self)
        self.dax_submit.clicked.connect(self.submit)
        self.dax_submit.setFixedWidth(120)
        
        self.dax_save = QPushButton("Save", self)
        self.dax_save.clicked.connect(self.save)
        self.dax_save.setFixedWidth(120)
        
        self.dax_load = QPushButton("Load", self)
        self.dax_load.clicked.connect(self.load)
        self.dax_load.setFixedWidth(120)
        
        dax_buttons.addWidget(self.dax_submit)
        dax_buttons.addWidget(self.dax_save)
        dax_buttons.addWidget(self.dax_load)
        
        
        self.qutip_script = QTextEdit(self)
        
        self.qutip_script.setSizePolicy(
            self.qutip_script.sizePolicy().horizontalPolicy(),
            self.qutip_script.sizePolicy().verticalPolicy().Expanding
        )
        self.qutip_label = QLabel("Qutip/Python Script")
        qutip_layout.addWidget(self.qutip_label)
        
        qutip_layout.addWidget(self.qutip_script)
        
        self.qutip_submit = QPushButton("  Submit  ", self)
        self.qutip_submit.clicked.connect(self.submit)
        self.qutip_submit.setFixedWidth(120)
        
        self.qutip_save = QPushButton("  Save  ", self)
        self.qutip_save.clicked.connect(self.save)
        self.qutip_save.setFixedWidth(120)
        
        self.qutip_load = QPushButton("  Load  ", self)
        self.qutip_load.clicked.connect(self.load)
        self.qutip_load.setFixedWidth(120)
        
        
        qutip_buttons.addWidget(self.qutip_submit)
        qutip_buttons.addWidget(self.qutip_save)
        qutip_buttons.addWidget(self.qutip_load)
        

        dax_layout.addLayout(dax_buttons, 1)
        qutip_layout.addLayout(qutip_buttons, 1)
        
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        self.ax = self.figure.add_subplot(111)
        try:
            self.line, = self.ax.plot(self.t, self.y)
        except:
            print('skip')
        
        
        tabs = QTabWidget()
        tabs.setTabPosition(QTabWidget.TabPosition.South)
        tabs.addTab(self.canvas, "Graph")
        tabs.addTab(self.vcd, "VCD")
        
#         device_tabs = QTabWidget()
#         tabs.setTabPosition(QTabWidget.TabPosition.West)
        
        
        self.graph_label = QLabel("Graphs")
        graph_layout.addWidget(self.graph_label)
        
        graph_layout.addWidget(tabs)
        
        self.graph_submit = QPushButton(" Submit ", self)
        self.graph_submit.clicked.connect(self.submit)
        self.graph_submit.setFixedWidth(120)
        
        self.graph_save = QPushButton(" Save ", self)
        self.graph_save.clicked.connect(self.save)
        self.graph_save.setFixedWidth(120)
        
        self.graph_load = QPushButton(" Load ", self)
        self.graph_load.clicked.connect(self.load)
        self.graph_load.setFixedWidth(120)
        
        graph_buttons.addWidget(self.graph_submit)
        graph_buttons.addWidget(self.graph_save)
        graph_buttons.addWidget(self.graph_load)
         
        graph_layout.addLayout(graph_buttons, 1)

        self.canvas.draw()
        self.setLayout(main)


    def output_window(self, text):
        now = datetime.datetime.now()
        formatted_time = now.strftime("%H:%M:%S")
        self.output.append("[" + formatted_time + "]: " + text)
        self.output.append("")
        
    def submit(self):
        button = self.sender()
        name = button.text()
        
        if name == "Submit":
            text = self.dax_script.toPlainText()
            with open("tmp.py", "w") as file:
                file.write(text)
            try:
                result = subprocess.run(["artiq_run", "tmp.py"], capture_output=True, text=True)
                output = result.stdout
                self.output_window(output)
                
            except Exception as e:
                self.output_window(f"Error: {e}")
                
                
        elif name == "  Submit  ":
            text = self.qutip_script.toPlainText()
            
            with open("tmp.py", "w") as file:
                file.write(text)
            try:
                result = subprocess.run(["python", "tmp.py"], capture_output=True, text=True)
                output = result.stdout
                self.output_window(output)
                
            except:
                try:
                    result = subprocess.run(["python3", "tmp.py"], capture_output=True, text=True)
                    output = result.stdout
                    self.output_window(output)
                except  Exception as e:
                    self.output_window(f"Error: {e}")
            
    def save(self):
        button = self.sender()
        return
    
    def load(self):
        button = self.sender()
        file_path, _ = QFileDialog.getOpenFileName(self, "Open File", "", "All Files (*);;Text Files (*.txt)")
        name = button.text()
        if file_path:
            self.output_window(f"Selected file: {file_path}")
            out = io.StringIO()
            
            with contextlib.redirect_stdout(out):
                with contextlib.redirect_stderr(out):
                    try:
                        with open(file_path, "r") as file:
                            # Read and print each line of the file
                            for line in file:
                                print(line, end="")
                    except Exception as e:
                        print(f"Error: {e}")
            if name == "Load":
                if file_path.split(".")[1] == "py":
                    self.dax_script.setPlainText(out.getvalue())
                else:
                    self.output_window("Error: Please select a .py file.")
            elif name == "  Load  ":
                self.qutip_script.setPlainText(out.getvalue())
                
            else:
                self.t, self.y, self.device = vcd_grapher.vcd_viewer(file_path)
                for n in range(len(self.t)):
                    self.line = self.ax.plot(self.t[n], self.y[n])
                self.ax.set_title(self.device)
                self.ax.set_xlabel("Time (s)")
                self.ax.set_ylabel("Relative Amplitude")
                self.canvas.draw()
                self.vcd.setPlainText(out.getvalue())
    
    
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
