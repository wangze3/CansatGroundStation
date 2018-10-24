from random import randint, uniform
import math
import datetime
import helpers
import csv


class Cansat(object):
    """ Cansat class to encapsulate shared variables and functions
    """
    def __init__(self):
        self.packet_cnt = 0
        self.altitude = [0.0]
        self.mission_time = str(datetime.datetime.now())[14:19]
        self.bg_time = 0    # background time
        self.pressure = [0.0] 
        self.temp = [0.0]
        self.voltage = [0.0]
        self.gpstime = "None"
        self.gpslat = [0.0]
	self.gpslong = [0.0]
	self.gpsalt = [0.0]
	self.gpssat = [0.0]
	self.tiltx = [0.0]
	self.tilty = [0.0]
	self.tiltz = [0.0]
        self.flight_status = 0
        self.identifier = "NO CONNECT."

        # for packet count fallback
        self.packet_cnt_store = 0


class Telemetry(object):
    """
    """
    def __init__(self, cansat, file_name):
        self.ser = None
        self.ser_connected = False
        self.cansat = cansat
        self.csv_test = False
        self.file_name = file_name
        self.f = open(self.file_name, 'r')
        self.reader = csv.reader(self.f)


    def conv_insert(self, data_var, data):
	try: 
	    temp = float(data)
	except:
	    temp = data_var[-1]

	data_var.append(temp)

    def serial_update_write(self, root, telemetry_box):
#        print "connection: " + str(self.ser_connected)

        # for testing plots without serial connection only, delete this later
        if self.csv_test:
            altitude = randint(1, 400)
            pressure = randint(101, 120) 
            temp = randint(22, 32) 
            voltage = uniform(0, 8) 
	    gps_time = "None"
            gps_lat = randint(0, 100) 
            gps_long = randint(0, 100) 
            gps_alt = randint(0, 1000) 
            gps_sat = randint(0, 10) 
	    tiltx = randint(-180,180)
	    tilty = randint(-180,180)
	    tiltz = randint(-180,180)
            state = randint(1,8) 


            self.cansat.packet_cnt += 1
            self.cansat.mission_time = str(datetime.datetime.now())[14:19]
            self.cansat.altitude.append(altitude)
            self.cansat.pressure.append(pressure)
            self.cansat.temp.append(temp)
            self.cansat.voltage.append(voltage)
            self.cansat.gpstime = gps_time
	    self.cansat.gpslat.append(gps_lat)
	    self.cansat.gpslong.append(gps_long)
	    self.cansat.gpsalt.append(gps_alt)
	    self.cansat.gpssat.append(gps_sat)
	    self.cansat.tiltx.append(tiltx)
	    self.cansat.tilty.append(tilty)
	    self.cansat.tiltz.append(tiltz)
            self.cansat.flight_status = state

        elif self.ser_connected:
            """ message format

            """

            data = self.ser.readline()
            data_list = data.split(",")
            
            print data_list

            if len(data_list) == 13:
                self.cansat.identifier = "Received"


		self.cansat.packet_cnt += 1
            	self.cansat.mission_time = str(datetime.datetime.now())[11:19]
            	self.cansat.gpstime = data_list[4] if data_list[4] != "" else self.cansat.gpstime
		self.conv_insert(self.cansat.altitude,data_list[0])
		self.conv_insert(self.cansat.pressure,data_list[1])
		self.conv_insert(self.cansat.temp,data_list[2])
		self.conv_insert(self.cansat.voltage,data_list[3])
		self.conv_insert(self.cansat.gpslat,data_list[5])
		self.conv_insert(self.cansat.gpslong,data_list[6])
		self.conv_insert(self.cansat.gpsalt,data_list[7])
		self.conv_insert(self.cansat.gpssat,data_list[8])
		self.conv_insert(self.cansat.tiltx,data_list[9])
		self.conv_insert(self.cansat.tilty,data_list[10])
		self.conv_insert(self.cansat.tiltz,data_list[11])

		try:
			temp = int(data_list[12])
		except:
			temp = self.cansat.flight_status
            	self.cansat.flight_status = temp

		mtime = str(self.cansat.mission_time)
		cnt = str(self.cansat.packet_cnt)
		altitude = str(self.cansat.altitude[-1])
		pressure = str(self.cansat.pressure[-1])
		temp = str(self.cansat.temp[-1])
		voltage = str(self.cansat.voltage[-1])
		gps_time = self.cansat.gpstime
		gps_lat = str(self.cansat.gpslat[-1])
		gps_long = str(self.cansat.gpslong[-1])
		gps_alt = str(self.cansat.gpsalt[-1])
		gps_sat = str(self.cansat.gpssat[-1])
		tiltx = str(self.cansat.tiltx[-1])
		tilty = str(self.cansat.tilty[-1])
		tiltz = str(self.cansat.tiltz[-1])
		state = str(self.cansat.flight_status)
		
		text = ",".join(["1138",mtime,cnt,altitude,pressure,temp,voltage,gps_time,gps_lat,gps_long,gps_alt,gps_sat,tiltx,tilty,tiltz,state])
		telemetry_box.listbox.insert(0, text)

		f = open(self.file_name, "aw")
		f.write(text + "\n")
		f.close()
	else:
		self.cansat.identifier = "INVALID DATA"

        root.after(200, self.serial_update_write, root, telemetry_box)

