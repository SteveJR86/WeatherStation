#!/usr/bin/python
# Library Import
import MySQLdb
import time
import threading
import sense_hat

# SenseHat Setup
sense = sense_hat.SenseHat()
sense.clear()
sense.set_rotation(270)

# Initial Variables
p = int(sense.get_pressure())
t = round(sense.get_temperature(), 1)
h = int(sense.get_humidity())
pressure = [p, p, p, p, p, p, p, p];
temperature = [t, t, t, t, t, t, t, t];
humidity = [h, h, h, h, h, h, h, h];
del p, t, h
white = (255, 255, 255)
red = (255, 0, 0)
yellow = (255, 255, 0)
green = (0, 255, 0)

# Graph Function
def display_graph(item, values):
	sense.show_letter(item)
	time.sleep(2)
	sense.clear()
	if item == "P":
		sense.show_message(str(values[7]) + "mBar")
	elif item == "T":
		sense.show_message(str(values[7]) + "C")
	elif item == "H":
		sense.show_message(str(values[7]) + "%")
	baseline = 4
	modifier = 0
	y = 1
	display = []
	colour = []
	xold = values[0]
	for x in values[1:]:
		if x > xold:
			display.append(-1)
		elif x < xold:
			display.append(1)
		else:
			display.append(0)
		if item == "P":
			if x == xold:
				colour.append(white)
			elif abs(x - xold) > 5:
				colour.append(red)
			elif abs(x - xold) < 2:
				colour.append(green)
			else:
				colour.append(yellow)
		else:
			colour.append(white)
		xold = x
	for x in display:
		baseline += x
		if baseline > 7:
			modifier -= 1
		elif baseline < 0:
			modifier += 1
	baseline = 4 + modifier
	sense.set_pixel(0, baseline, 255, 255, 255)
	for x in display:
		baseline += x
		sense.set_pixel(y, baseline, colour[y-1])
		y += 1
	time.sleep(2)
	sense.clear()		

# Display Thread
def display_data():

	while True:
		if (sense.get_accelerometer_raw()['x'] > 1 or sense.get_accelerometer_raw()['y'] > 1 or sense.get_accelerometer_raw()['z'] > 1):
			display_graph("P", pressure)
			display_graph("T", temperature)
			display_graph("H", humidity)


# Collect Data Thread
def collect_data():
	while True:
		del pressure[0];
		pressure.append(int(sense.get_pressure()))
		del temperature[0];
		temperature.append(round(sense.get_temperature(), 1))
		del humidity[0];
		humidity.append(int(sense.get_humidity()))
		db = MySQLdb.connect("localhost","logger","HdSoAw1","datalogger")
		cursor = db.cursor()
		sql = "INSERT INTO data(pressure, temperature, humidity) VALUES ('%d', '%f', '%d')" % (pressure[7], temperature[7], humidity[7])
		try:
			cursor.execute(sql)
			db.commit()
		except:
			db.rollback()
		db.close() 
		time.sleep(3600)

# Start all the Threads
display = threading.Thread(target=display_data)
display.daemon = True
display.start()
collect = threading.Thread(target=collect_data)
collect.daemon = True
collect.start()
while True:
	time.sleep(0.1)
