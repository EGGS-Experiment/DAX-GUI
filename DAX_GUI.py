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
import random

from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *

class MainWindow(QMainWindow):  # Inherit QMainWindow for dock widgets
    def __init__(self):
        super().__init__()
        self.initUI()
        self.setWindowTitle("DAX Simulations")

        self.width = 1920
        self.height = 1080
        self.resize(self.width, self.height)

    def initUI(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QGridLayout(central_widget)
        self.output = QTextEdit(self)
        self.output.setFixedHeight(100)
        self.output.setReadOnly(True)
        self.output.setPlaceholderText("Output window (will display info)")

        main_layout.addWidget(self.output, 2, 0)
                
        
        self.vcd = QTextEdit(self)
        self.vcd.setReadOnly(True)
        self.vcd.setPlaceholderText("Imported VCD files will be shown here")

        self.sub_layout = QGridLayout()

        dax_layout = QVBoxLayout()
        dax_buttons = QHBoxLayout()

        qutip_layout = QVBoxLayout()
        qutip_buttons = QHBoxLayout()

        self.sub_layout.addLayout(dax_layout, 0, 0, 2, 1)
        self.sub_layout.addLayout(qutip_layout, 0, 1, 2, 1)

        main_layout.addLayout(self.sub_layout, 0, 0, 1, 3)

        # DAX Script Section
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
        dax_layout.addLayout(dax_buttons)

        # Qutip Script Section
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
        qutip_layout.addLayout(qutip_buttons)

        # Add Graph Dock
        graph_dock = self.create_dock("Graphs")
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, graph_dock)
    
        
    def create_dock(self, title):
        dock = QDockWidget(title, self)
        dock.setFloating(False)

        if title == "Graphs":
            graph_widget = QWidget()
            graph_layout = QVBoxLayout(graph_widget)
            self.figure_sim = Figure()
            self.canvas_sim = FigureCanvas(self.figure_sim)
            self.ax_sim = self.figure_sim.add_subplot(111)
            self.tabbed = QWidget()
        
            self.tabs = QTabWidget()
            self.tabs.setTabPosition(QTabWidget.TabPosition.South)
            self.tabs.addTab(self.tabbed, "Graph")
            self.tabs.addTab(self.vcd, "VCD")
            self.tabs.addTab(self.canvas_sim, "Qutip Sims")

            self.tabbed_layout = QVBoxLayout()
            self.sub_graph_widget = QTabWidget()

            self.tabbed_layout.addWidget(self.sub_graph_widget)
            self.tabbed.setLayout(self.tabbed_layout)

            graph_layout.addWidget(self.tabs)

            # Graph buttons
            graph_buttons = QHBoxLayout()
            graph_submit = QPushButton("   Submit   ", self)
            graph_submit.clicked.connect(self.submit)
            graph_submit.setFixedWidth(120)
            
            graph_save = QPushButton("   Save   ", self)
            graph_save.clicked.connect(self.save)
            graph_save.setFixedWidth(120)
            
            graph_load = QPushButton("   Load   ", self)
            graph_load.clicked.connect(self.load)
            graph_load.setFixedWidth(120)

            graph_buttons.addWidget(graph_submit)
            graph_buttons.addWidget(graph_save)
            graph_buttons.addWidget(graph_load)
            graph_layout.addLayout(graph_buttons)

            dock.setWidget(graph_widget)
            
        elif title == "ARTIQ (DAX) Script":
            pass
        
        elif title == "Qutip/Python Script":
            pass

        return dock

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
                except Exception as e:
                    self.output_window(f"Error: {e}")

    def save(self):
        # Save logic here
        pass
    
    def add_tab(self):
        for i in range(len(self.figure)):
            new_tab = QWidget()
            new_tab_layout = QVBoxLayout()
            new_tab_layout.addWidget(self.canvas[i])
            self.canvas[i].draw()
            new_tab.setLayout(new_tab_layout)
            self.sub_graph_widget.addTab(new_tab, self.device[i])
            self.output_window(f"Plotting: {self.device[i]}")
            out = io.StringIO()
            
            r = random.uniform(0.0, 1.0)
            g = random.uniform(0.0, 1.0)
            b = random.uniform(0.0, 1.0)
            for m in range(len(self.t[i])):
                self.line[i] = self.ax[i].plot(self.t[i][m], self.y[i][m], color = (r, g, b))

            self.ax[i].set_title(self.device[i])
            self.ax[i].set_xlabel("Time (s)")
            self.ax[i].set_ylabel("Relative Amplitude")
            self.canvas[i].draw()
            
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
                if file_path.split(".")[1] == "vcd":
                    self.t, self.y, self.device = vcd_grapher.vcd_viewer(file_path)
                    
                    
                    self.num_of_tabs = len(self.device)
                    self.figure = [Figure() for _ in range(self.num_of_tabs)]
                    self.canvas = [0 for _ in range(self.num_of_tabs)]

                    for n in range(len(self.canvas)):
                        self.canvas[n] = FigureCanvas(self.figure[n])

                    self.ax = [0 for _ in range(self.num_of_tabs)]

                    for n in range(len(self.ax)):
                        self.ax[n] = self.figure[n].add_subplot(111)



                    self.line = [0 for _ in range(self.num_of_tabs)]
                    self.add_tab()

                    self.vcd.setPlainText(out.getvalue())
                elif file_path.split(".")[1] == "py":
                    print("wait")

    def output_window(self, text):
        now = datetime.datetime.now()
        formatted_time = now.strftime("%H:%M:%S")
        self.output.append(f"[{formatted_time}]: {text}\n")
        

    def output_window(self, text):
        now = datetime.datetime.now()
        formatted_time = now.strftime("%H:%M:%S")
        self.output.append(f"[{formatted_time}]: {text}\n")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
