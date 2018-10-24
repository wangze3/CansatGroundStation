import ttk, user, sys, time, datetime, thread
from Aerial import *

var_dict = {1:'data_altitude',2:'data_pressure',3:'data_temp',4:'data_voltage',5:'data_GPStime',\
6:'data_GPSlat',7:'data_GPSlong',8:'data_GPSalt',9:'data_GPSsat',10:'data_tiltx',11:'data_tilty',12:'data_tiltz'\
,13:'data_state'}

flight_status_dict = {0:'Looking for Probe...',1:'Waiting', 2:'Ascending', 3:'HS-Deploy', 4:'HS-Descent', 5:'Release',\
    6:'Descent', 7:'Landed', 8:'Unknown'}


def update_mission_time(text_var, root):
	current_time = str(datetime.datetime.now())[0: 19]
	text_var.mission_time.set("Mission Time: %s EST" % current_time)
	root.after(1000, update_mission_time, text_var, root)

def update_flight_status(tel, text_var, root, cansat):
	if tel.ser_connected == True:
		text_var.flight_status.set("Flight Status: " + flight_status_dict[cansat.flight_status])
	elif tel.ser_connected == False:
		text_var.flight_status.set("Flight Status: Not Connected")
	else:
		text_var.flight_status.set("Flight Status: Unknown")

	# print tel.ser_connected
	root.after(500, update_flight_status, tel, text_var, root, cansat)

def conclude(chart):
    chart.frame.focus_set()

# in case of processor reset packet_cnt needs to be cts
# can just use a script to go through and fix any discontinuities
def check_packet_cnt():
	pass
