#import Tkinter
from serial import *
import ttk, user, sys, time, datetime, thread


from helpers import *
from Aerial import *
from UIelements import *

try:
    # for Python2
    import Tkinter as Tk
except:
    # for Python3
    import tkinter as Tk

####################### Setup ########################################

# team information
TEAM_NUM = 1138
baud_rate = 9600
file_name = "data_log/CANSAT2018_TLM_1138_RSX_Cansat_" + str(datetime.datetime.now())[0: 19] + ".csv"

# Vars
force_status_var = 0
last_com_time = 'N/A'

var_dict = {1:'data_altitude',2:'data_pressure',3:'data_temp',4:'data_voltage',5:'data_GPStime',\
6:'data_GPSlat',7:'data_GPSlong',8:'data_GPSalt',9:'data_GPSsat',10:'data_tiltx',11:'data_tilty',12:'data_tiltz'\
,13:'data_state'}
flight_status_dict = {1:'Waiting', 2:'Ascending', 3:'HS-Deploy', 4:'HS-Descent', 5:'Release',\
    6:'Descent', 7:'Landed', 8:'Unknown'}

########################### Main Function ######################################

if __name__ == "__main__":
    # wirte header to log file
    f = open(file_name, 'w')
    f.write("TEAM_ID,MISSION_TIME,PACKET_CNT,ALTITUDE,PRESSURE,TEMP,VOLTAGE,GPSTIME,GPSLAT,GPSLONG,GPSALT,GPSSAT,TILTX,TILTY,TILTZ,SOFTWARE_STATE\n")
    f.close()

    # new: initialize cansat
    cansat = Cansat()
    tel = Telemetry(cansat, file_name)

    # initialize the main gui
    root = MainGUI(None, cansat, tel)
    root.title('CANSAT - 2018    Team: ' + str(TEAM_NUM))


    # Text Variables
    text_var = TextVar(root, cansat)
    root.menu.set_text_var(text_var)

    # initialize UI elements
    panel = Panel(root, cansat)

    # Top info bar
    top_info_frame = TopInfoFrame(root, text_var, TEAM_NUM)

    # Left info bar (team, time, flight status)
    left_info_frame = LeftInfoFrame(panel, text_var)

    # Force Button
    force_frame = ForceFrame(panel, text_var, force_status_var, tel)

    # Main chart area
    chart = Chart(root, cansat)

    # Scroll Telemetry
    telemetry_box = TelemetryBox(root)

    # Bottom status bar
    status = StatusBar(root)
    status.pack(side='bottom', fill='x')


     # call loops
    root.after(0, chart.plot_altitude)
    root.after(0, chart.plot_temperature)
    root.after(0, chart.plot_voltage)

    root.after(1000, update_mission_time, text_var, root)
    root.after(1000, update_flight_status, tel, text_var, root, cansat)
    root.after(1000, panel.update_panel, root, cansat, text_var)
    root.after(1000, tel.serial_update_write, root, telemetry_box)
    root.after(1000, conclude, chart)

    root.mainloop()
