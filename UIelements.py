from serial import *
from subprocess import check_output
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure
from tkFileDialog import asksaveasfile
import csv
import datetime
import time

from helpers import *
try:
    # for Python2
    import Tkinter as Tk
except:
    # for Python3
    import tkinter as Tk

baud_rate = 9600

class MainGUI(Tk.Tk):
    def __init__(self,parent, cansat, tel):
        Tk.Tk.__init__(self,parent)
        self.parent = parent
        self.geometry("1300x900+100+50")
        self.menu = MenuBar(self, cansat, tel)
        self.config(menu=self.menu)


class MenuBar(Tk.Menu):
    """
    """
    def __init__(self, parent, cansat, tel):
        Tk.Menu.__init__(self, parent)
        self.parent = parent
        self.tel = tel
        self.initialize()
        self.cansat = cansat

    def initialize(self):
        # File menu
        self.file_menu = Tk.Menu(self, tearoff=0)
        self.file_menu.add_command(label="Start", command=self.start_operation)
        self.file_menu.add_command(label="Pause", command=self.pause_operation)
        self.file_menu.add_command(label="Stop", command=self.stop_operation)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit", underline=1, command=self.quit)
        self.add_cascade(label="File", underline=0, menu=self.file_menu)

        # Connection menu
        port_menu = Tk.Menu(self, tearoff=0)
        found_port = False
        for port in check_output(["ls", "/dev"]).split("\n"):
            if port.find("USB") != -1:
                found_port = True
                usb_port = str(port)
                print(usb_port)
                port_menu.add_command(label=port, command=lambda usb_port=usb_port: self.open_ser(usb_port, self.tel))

                port_menu.add_command(label="Disconnect", command=lambda usb_port=usb_port: self.disconnect(usb_port, self.tel))

        if not found_port:
            port_menu.add_command(label="No COM Device Found")

        self.add_cascade(label="Connection", underline=0, menu=port_menu)

        # Help menu
        help_menu = Tk.Menu(self, tearoff=0)
        help_menu.add_command(label="About", command=self.info)
        self.add_cascade(label="Help", menu=help_menu)

    def save_data(self):
        pass


    def start_operation(self):
        pass

    def pause_operation(self):
        pass

    def stop_operation(self):
        pass

    def quit(self):
        sys.exit(0)

    def open_ser(self, usb_port, tel):
        print "trying to connect..."
        address = "/dev/" + usb_port
        try:
            tel.ser = Serial(address, baud_rate, timeout=0, write_timeout=0)
            print "attempt to connected to %s" % usb_port
            tel.ser_connected = True
            print("Connected to " + usb_port)
            #flight_status.set("Flight Status: Ready")
        except Exception as e:
            print("Error:connection cannot be established")
            print(e)

    def set_text_var(self, text_var):
        self.text_var = text_var

    def disconnect(self, usb_port, tel):
        tel.ser.close()
        tel.ser_connected = False
        print("Ended connection")
        self.text_var.flight_status.set("Flight Status: Standby")
        # tel.f.close()


class StatusBar(Tk.Frame):
    """
    """
    def __init__(self, parent):
        Tk.Frame.__init__(self, parent)
        self.label = Tk.Label(self, relief='sunken', anchor='w')
        self.label.pack(fill='x')
        self.set("CANSAT-2018 with RSX")

    def set(self, format, *args):
        self.label.config(text=format % args)
        self.label.update_idletasks()

    def clear(self):
        self.label.set("")


class Chart(object):
    """ Chart class for data plots
    """

    def __init__(self, parent, cansat):
        self.cansat = cansat
        self.frame = Tk.Frame(parent)
        self.frame2 = Tk.Frame(parent)
        self.chart1_frame = Tk.Frame(self.frame)
        self.chart2_frame = Tk.Frame(self.frame)
        self.chart4_frame = Tk.Frame(self.frame)
        self.pack_frame()

    def pack_frame(self):
        self.frame.pack(side='top', expand = 1, fill='x')
        self.frame.focus_set()

        self.chart1_frame.pack(side = "left", expand = 1, fill = 'both')
        self.chart2_frame.pack(side = "left", expand = 1, fill = 'both')
        self.chart4_frame.pack(side = "left", expand = 1, fill = 'both')

        self.frame2.pack(expand = 1, fill='x')


    def plot_altitude(self):
        global fig_altitude, dataPlot_altitude, a_altitude

        fig_altitude = Figure(figsize=(4, 4), dpi = (self.frame.winfo_width() - 50) / 16)
        dataPlot_altitude = FigureCanvasTkAgg(fig_altitude, master = self.chart1_frame)
        a_altitude = fig_altitude.add_subplot(111)

        dataPlot_altitude.show()
        dataPlot_altitude.get_tk_widget().pack()

        def plot_cts():
            global a_altitude
            x_axis1 = range(0, len(self.cansat.altitude))
            x_axis2 = range(0, len(self.cansat.gpsalt))

            a_altitude.clear()
            a_altitude.plot(x_axis1, self.cansat.altitude, "r", label = "BMP180")
            a_altitude.plot(x_axis2, self.cansat.gpsalt, "b", label = "GPS")


            a_altitude.set_title("Altitude (m)")
            legend = a_altitude.legend(loc='upper left', shadow=True)

            dataPlot_altitude.show()
            dataPlot_altitude.get_tk_widget().pack()

            self.chart1_frame.after(1000, plot_cts)

        plot_cts()


    def plot_temperature(self):
        global fig_temp, dataPlot_temp, a_temp

        fig_temp = Figure(figsize=(4, 4), dpi = (self.frame.winfo_width() - 50) / 16)
        dataPlot_temp = FigureCanvasTkAgg(fig_temp, master = self.chart2_frame)
        a_temp = fig_temp.add_subplot(111)

        dataPlot_temp.show()
        dataPlot_temp.get_tk_widget().pack()

        def plot_cts():
            global a_temp
            x_axis = range(0, len(self.cansat.temp))

            a_temp.clear()
            a_temp.plot(x_axis, self.cansat.temp, "r", label = "deg C")

            a_temp.set_title("Temperature (C)")
            a_temp.set_ylim([0, 60])

            dataPlot_temp.show()
            dataPlot_temp.get_tk_widget().pack()

            self.chart2_frame.after(1000, plot_cts)

        plot_cts()

    def plot_voltage(self):
        global fig_voltage, dataPlot_voltage, a_voltage

        fig_voltage = Figure(figsize=(4, 4), dpi = (self.frame.winfo_width() - 50) / 16)
        dataPlot_voltage = FigureCanvasTkAgg(fig_voltage, master =self.chart4_frame)

        a_voltage = fig_voltage.add_subplot(111)
        dataPlot_voltage.show()
        dataPlot_voltage.get_tk_widget().pack()

        def plot_cts():
            global a_voltage
            a_voltage.clear()
            voltage = self.cansat.voltage[len(self.cansat.voltage) - 1]
            if voltage > 7.3:
                a_voltage.bar(0, voltage, 1, color = 'g')
            elif voltage > 5:
                a_voltage.bar(0, voltage, 1, color = 'y')
            else:
                a_voltage.bar(0, voltage, 1, color = 'r')

            a_voltage.set_title("Voltage (V)")
            a_voltage.set_ylim([0, 10])
            a_voltage.get_xaxis().set_visible(False)

            dataPlot_voltage.show()
            dataPlot_voltage.get_tk_widget().pack()

            self.chart4_frame.after(1000, plot_cts)

        plot_cts()




class Panel(Tk.Frame):
    """ Panel for showing current data
    """
    def __init__(self, parent, cansat):
        Tk.Frame.__init__(self, parent)
        self.pack(side = "left", expand = 1, padx = 20, fill = 'y')
        self.cansat = cansat

    def update_panel(self, root, target, text_var):
        text_var.pack_cnt.set("Packet Cnt: %d" % target.packet_cnt)
        text_var.pressure_var.set("Atm Pressure %.1f kPa" % target.pressure[-1])
	text_var.gps_time.set("GPS Time: %s" % target.gpstime)
        text_var.gps_lat.set("GPS Latitude: %.4f" % target.gpslat[-1])
        text_var.gps_long.set("GPS Longitude: %.4f" % target.gpslong[-1])
        text_var.gps_num.set("GPS # Sat: %d" % target.gpssat[-1])
	text_var.tilt_x.set("Tilt X: %d deg" % target.tiltx[-1])
	text_var.tilt_y.set("Tilt Y: %d deg" % target.tilty[-1])
	text_var.tilt_z.set("Tilt Z: %d deg" % target.tiltz[-1])
        root.after(1000, self.update_panel, root, target, text_var)


class TextVar(object):
    """ TextVar object to group text labels
    """
    def __init__(self, root, cansat):
        self.mission_time = Tk.StringVar()
        self.bg_time = Tk.StringVar()

        self.force_status = Tk.StringVar()
        self.flight_status = Tk.StringVar()
        self.pack_cnt = Tk.StringVar()

        self.pressure_var = Tk.StringVar()
	self.gps_time = Tk.StringVar()
        self.gps_lat = Tk.StringVar()
        self.gps_long = Tk.StringVar()
        self.gps_num = Tk.StringVar()
	self.tilt_x = Tk.StringVar()
	self.tilt_y = Tk.StringVar()
	self.tilt_z = Tk.StringVar()

        self.cansat = cansat
        self.set_text(root)


    def set_text(self, root):
        self.force_status.set("None Selected")
        self.flight_status.set("Flight Status: Not Connected")


class TopInfoFrame(Tk.Frame):
    """
    """
    def __init__(self, parent, text_var, TEAM_NUM):
        self.top_info_frame = Tk.Frame(parent, bg='black')
        self.label_top1 = Tk.Label(self.top_info_frame, text = "TEAM #"+str(TEAM_NUM), fg='white', bg='black')
        self.label_top2 = Tk.Label(self.top_info_frame, textvariable = text_var.mission_time, fg='white', bg='black')
        self.label_top3 = Tk.Label(self.top_info_frame, textvariable = text_var.flight_status, fg='white', bg='black')
        self.pack_frame()

    def pack_frame(self):
        self.top_info_frame.pack(side = "top", expand = 1, fill = 'x')
        self.label_top1.pack(side='left', expand = 1, fill = 'x')
        self.label_top2.pack(side='left', expand = 1, fill = 'x')
        self.label_top3.pack(side='left', expand = 1, fill = 'x')



class LeftInfoFrame(Tk.Frame):
    """
    """
    def __init__(self, parent, text_var):
        self.info_frame = Tk.Frame(parent)
        self.label_info1 = Tk.Label(self.info_frame, textvariable = text_var.pack_cnt)
        self.label_info2 = Tk.Label(self.info_frame, textvariable = text_var.pressure_var)
        self.label_info3 = Tk.Label(self.info_frame, textvariable = text_var.gps_time)
        self.label_info4 = Tk.Label(self.info_frame, textvariable = text_var.gps_lat)
        self.label_info5 = Tk.Label(self.info_frame, textvariable = text_var.gps_long)
        self.label_info6 = Tk.Label(self.info_frame, textvariable = text_var.gps_num)
	self.label_info7 = Tk.Label(self.info_frame, textvariable = text_var.tilt_x)
	self.label_info8 = Tk.Label(self.info_frame, textvariable = text_var.tilt_y)
	self.label_info9 = Tk.Label(self.info_frame, textvariable = text_var.tilt_z)
        self.label_info10 = Tk.Label(self.info_frame, textvariable= text_var.bg_time)
        self.pack_frame()

    def pack_frame(self):
        self.info_frame.pack(side = "top",expand = 1,  fill = 'both')
        self.label_info1.grid(column = 0, row = 0,sticky = 'w')
        self.label_info2.grid(column = 0, row = 1,sticky = 'w')
        self.label_info3.grid(column = 0, row = 2, sticky = 'w')
        self.label_info4.grid(column = 0, row = 3, sticky = 'w')
        self.label_info5.grid(column = 0, row = 4,sticky = 'w')
        self.label_info6.grid(column = 0, row = 5,sticky = 'w')
	self.label_info7.grid(column = 0, row = 6,sticky = 'w')
	self.label_info8.grid(column = 0, row = 7,sticky = 'w')
	self.label_info9.grid(column = 0, row = 8,sticky = 'w')
        self.label_info10.grid(column = 0, row = 9, sticky='w')

class ForceFrame(Tk.Frame):
    """
    """
    def __init__(self, parent, text_var, force_status_var, telemetry):
        self.force_status_var = force_status_var
        self.tel = telemetry

        self.status_button_frame = Tk.Frame(parent, bg = 'red')
        self.force_status = text_var.force_status
        self.force_status.set("None Selected")

        self.label_force = Tk.Label(self.status_button_frame, text = "FORCE ACTIONS",bg = 'red')
        self.button_none = Tk.Button(self.status_button_frame,text=u"0:Reset",command = lambda x=0: self.force_status_callback(x))
        self.button_wait = Tk.Button(self.status_button_frame,text=u"1:Waiting",command = lambda x=1: self.force_status_callback(x))
        self.button_ascend = Tk.Button(self.status_button_frame,text=u"2:Ascend",command = lambda x=2: self.force_status_callback(x))
        self.button_hsdeploy = Tk.Button(self.status_button_frame,text=u"3:Stabilizing",command = lambda x=3: self.force_status_callback(x))
	self.button_hsdescent = Tk.Button(self.status_button_frame,text=u"4:Release",command = lambda x=4: self.force_status_callback(x))
	self.button_release = Tk.Button(self.status_button_frame,text=u"5:Descent",command = lambda x=5: self.force_status_callback(x))
	self.button_descent = Tk.Button(self.status_button_frame,text=u"6:Land",command = lambda x=6: self.force_status_callback(x))
        self.button_land = Tk.Button(self.status_button_frame,text=u"7:None",command = lambda x=7: self.force_status_callback(x))

        self.label_force_status = Tk.Label(self.status_button_frame, textvariable=self.force_status, pady=12, bg = 'red')
        self.button_act = Tk.Button(self.status_button_frame, text = "Execute",command = self.execute_button_callback)

        self.pack_frame()

    def pack_frame(self):
        self.status_button_frame.pack(side = "top", expand = 1, fill = 'both')
        self.label_force.pack(side = 'top', fill = 'both')
        self.button_none.pack(side = 'top')
        self.button_wait.pack(side = 'top')
        self.button_ascend.pack(side = 'top')
        self.button_hsdeploy.pack(side = 'top')
	self.button_hsdescent.pack(side = 'top')
	self.button_release.pack(side = 'top')
	self.button_descent.pack(side = 'top')
        self.button_land.pack(side = 'top')
        self.label_force_status.pack(side = 'top',fill = 'x')
        self.button_act.pack(side = 'top')


# TODO status and force_status variables
    def force_status_callback(self, status):
        # print status
	if status == 0:
            self.force_status.set("Reset Selected")
            self.force_status_var = 0	            
	elif status == 1:
            self.force_status.set("Wait Selected")
            self.force_status_var = 1
        elif status == 2:
            self.force_status.set("Ascending Selected")
            self.force_status_var = 2
        elif status == 3:
            self.force_status.set("Stabilizing Selected")
            self.force_status_var = 3
        elif status == 4:
            self.force_status.set("Release Selected")
            self.force_status_var = 4
        elif status == 5:
            self.force_status.set("Descent Selected")
            self.force_status_var = 5
        elif status == 6:
            self.force_status.set("Landed Selected")
            self.force_status_var = 6
        else:
            self.force_status.set("None Selected")
            self.force_status_var = 7

    def execute_button_callback(self):
        if self.tel.ser_connected == 1:
            print "Force Status:", self.force_status.get()
            if self.force_status_var == 0 or self.force_status_var == 1 or self.force_status_var == 2 or self.force_status_var == 3 or self.force_status_var == 4 or self.force_status_var == 5 \
		 or self.force_status_var == 6 or self.force_status_var == 7:
                print 'sending force command...'
                try:
                    msg = ("f0%d\n" % self.force_status_var).encode('utf-8')
                    # self.tel.ser.write(msg.encode())

                    self.tel.ser.write(msg)
		    time.sleep(.100)
                    print "sent..." + msg
		    self.force_status.set(["Send" + msg])
                except Exception as e:
                    print "Error: Could not write to serial"
                    # ????
                    self.force_status.set("Error: Could not write to serial. %s" % e)
                print 'force command sent with %d' % self.force_status_var
            else:
                print 'Nothing was executed'



class TelemetryBox(Tk.Frame):
    """
    """
    def __init__(self, parent):
        self.stream_frame = Tk.Frame(parent, bg = "white")
        self.scrollbar = Tk.Scrollbar(self.stream_frame)
        self.listbox = Tk.Listbox(self.stream_frame, width = 600,height = 20, yscrollcommand=self.scrollbar.set)

        self.pack_frame()

    def pack_frame(self):
        self.stream_frame.pack(side = "top", pady = 0, fill = 'both', expand = True)
        self.scrollbar.pack(side = 'right', fill = 'y')
        self.listbox.pack(side ='left', fill = 'both')
        self.scrollbar.config(command=self.listbox.yview)
