#!/usr/bin/python
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.



import argparse, logging, struct, binascii, sys, time, os


"""
	pyTISensorsDemo.py
	
	This script allows you to try out the different Texas Instruments Sensors.
	When you connect to a sensor the script will automatically load in the correct
	sensor software and communicate to the sensor via the GATTServer module.
	
	To talk to the TI sensors you need to have the TI bluetooth development dongle connected to your computer.
	
	

"""


import GATTServer

SensorUUIDList = {	'09596E0000E5C578': 'TIKeyFobSensor',
					'5B22AB0000296ABC': 'TITagSensor',
				}

class TISensor():
	def __init__(self, gattServer, connectSession, ledDevice = None):
		self._gattServer = gattServer
		self._connectSession = connectSession
		self._ledDevice = ledDevice
	
	def accelerometer(self):
		logging.warn("This sensor device does not support accelerometer")
		
	def battery(self):
		logging.warn("This sensor device does not support battery data")

	def gyroscope(self):
		logging.warn("This sensor device does not support gyroscope")

	def temperature(self):
		logging.warn("This sensor device does not support temperature")
		
	def humidity(self):
		logging.warn("This sensor device does not support humidity")
		
	def magnetometer(self):
		logging.warn("This sensor device does not support magnetometer")

	def barometer(self):
		logging.warn("This sensor device does not support barometer")


	def _writeLEDDevice(self, value):
		if self._ledDevice and os.path.exists(self._ledDevice):
			with open(self._ledDevice, 'w') as fp:
				fp.write(value)
		
		

class TIKeyFobSensor(TISensor):
	
	def accelerometer(self):
			
		self._connectSession.OnEventNotification = self._onNotification
		self.accelerometerValues = {'x': 0, 'y': 0, 'z': 0}
		
		# enable key press
		self._connectSession.writeRequestWord(0x48, 0x01)
		
		# enable Accel
		self._connectSession.writeRequestWord(0x34, 0x01)
		# enable x
		self._connectSession.writeRequestWord(0x3B, 0x01)
		# enable y
		self._connectSession.writeRequestWord(0x3F, 0x01)
		#enable z
		self._connectSession.writeRequestWord(0x43, 0x01)
		
		# now wait for data or the key press
		self._gattServer.waitForResponse()
		
		# finish - so close down
		self._connectSession.writeRequestWord(0x43, 0x00)
		self._connectSession.writeRequestWord(0x3F, 0x00)
		self._connectSession.writeRequestWord(0x3B, 0x00)
			
		self._connectSession.writeRequestWord(0x34, 0x00)
		
		self._connectSession.writeRequestWord(0x48, 0x00)


	def battery(self):
		value = self._connectSession.discoverByHandle(0x2F)
		print("Battery level %d%%" % value)
			
	def _onNotification(self, attribute, value):
		direction = {0x3A: 'x', 0x3E: 'y', 0x42: 'z'}
		if attribute in direction:
			self.accelerometerValues[direction[attribute]] = value
			print(self.accelerometerValues)
		elif attribute == 0x47:
			if value == 0x01:
				self._gattServer.responseFinished()
		else:
			print("Unkown attribute %04X =" % (attribute), value)

class TITagSensor(TISensor):
	
	def accelerometer(self):
			
		self._connectSession.OnEventNotification = self._onNotification
		self.accelerometerValues = {'x': 0, 'y': 0, 'z': 0}
		

		# enable accelerometer notification
		self._connectSession.writeRequestWord(0x2E, 0x01)
		# wake up the sensor
		self._connectSession.writeRequestByte(0x31, 0x01)

		# speed up the time period to fastest
		self._connectSession.writeRequestByte(0x34, 100)
				
		
		
		# now wait for data , key press or timeout
		self._gattServer.waitForResponse()
		
		# finish - so close down
		self._connectSession.writeRequestByte(0x31, 0x00)		
		self._connectSession.writeRequestWord(0x2E, 0x00)		

			


	def gyroscope(self):
		self._connectSession.OnEventNotification = self._onNotification
		self.gyroscopeValues = {'x': 0, 'y': 0, 'z': 0}
		

		# enable Gyroscope notification (all axis)
		self._connectSession.writeRequestByte(0x5B, 0x07)

		# enable Gyroscope sensor
		self._connectSession.writeRequestWord(0x58, 0x01)


		# now wait for data , key press or timeout
		self._gattServer.waitForResponse()
		
		# finish - so close down turn off gyroscope
		self._connectSession.writeRequestByte(0x5B, 0x00)		

		# disable gyroscope sensor
		self._connectSession.writeRequestWord(0x58, 0x00)


	def temperature(self):
		self._connectSession.OnEventNotification = self._onNotification
		self.tempValues = {'object': 0, 'ambient': 0}
		# enable temp notification
		self._connectSession.writeRequestWord(0x26, 0x01)

		# enable temp sensor
		self._connectSession.writeRequestByte(0x29, 0x01)


		# now wait for data , key press or timeout
		self._gattServer.waitForResponse()
		
		# finish - so put temp to sleep
		self._connectSession.writeRequestByte(0x29, 0x00)		

		# disable temp sensor notifications
		self._connectSession.writeRequestWord(0x26, 0x00)
		
	def humidity(self):
		self._connectSession.OnEventNotification = self._onNotification
		self.humidityValues = {'temperature': 0, 'humidity': 0}
		# enable humidity notification
		self._connectSession.writeRequestWord(0x39, 0x01)

		# enable humidity sensor
		self._connectSession.writeRequestByte(0x3c, 0x01)


		# now wait for data , key press or timeout
		self._gattServer.waitForResponse()
		
		# finish - so put humidity to sleep
		self._connectSession.writeRequestByte(0x3c, 0x00)		

		# disable humidity sensor notifications
		self._connectSession.writeRequestWord(0x39, 0x00)

	def magnetometer(self):
		self._connectSession.OnEventNotification = self._onNotification
		self.magnetometerValues = {'x': 0, 'y': 0, 'z': 0}

		# enable magnetometer notification
		self._connectSession.writeRequestWord(0x41, 0x01)
		# wake up the sensor
		self._connectSession.writeRequestByte(0x44, 0x01)

		# now wait for data , key press or timeout
		self._connectSession.writeRequestByte(0x47, 10)
				
		
		
		# now wait for data or the key press
		self._gattServer.waitForResponse()
		
		# finish - so close down
		self._connectSession.writeRequestByte(0x44, 0x00)		
		self._connectSession.writeRequestWord(0x41, 0x00)		


	def barometer(self):
		self._connectSession.OnEventNotification = self._onNotification
		self.barometerValues = {'temperature': 0, 'pressure': 0}
		# enable barometer notification
		self._connectSession.writeRequestWord(0x4C, 0x01)

		# enable barometer sensor
		self._connectSession.writeRequestByte(0x4F, 0x01)


		# now wait for data , key press or timeout
		self._gattServer.waitForResponse()
		
		# finish - so put barometer to sleep
		self._connectSession.writeRequestByte(0x4F, 0x00)		

		# disable barometer sensor notifications
		self._connectSession.writeRequestWord(0x4C, 0x00)

		

	def _onNotification(self, attribute, value):
		self._writeLEDDevice("255")
		
		if attribute == 0x2D:			# data from the accelerometer
			self.accelerometerValues['x'] = value[0]
			self.accelerometerValues['y'] = value[1]
			self.accelerometerValues['z'] = value[2]
			print(self.accelerometerValues)
			
		elif attribute == 0x57:			# data from the gyroscope
			values = struct.unpack('<HHH', value)
			self.gyroscopeValues['x'] = values[0]
			self.gyroscopeValues['y'] = values[1]	
			self.gyroscopeValues['z'] = values[2]	
			print(self.gyroscopeValues)
			
		elif attribute == 0x25:			# data from the external temperature
			values = struct.unpack('<HH', value)
			self.tempValues['object'] = values[0]
			self.tempValues['ambient'] = values[1]	
			print(self.tempValues)
					
		elif attribute == 0x38:			#data from the humidity sensor
			values = struct.unpack('<HH', value)
			self.humidityValues['temperature'] = values[0]
			self.humidityValues['humidity'] =values[1]
			print(self.humidityValues)
			
		elif attribute == 0x40:			#data from the magnetometer
			values = struct.unpack('<HHH', value)
			self.magnetometerValues['x'] = values[0]
			self.magnetometerValues['y'] = values[1]
			self.magnetometerValues['z'] = values[2]
			print(self.magnetometerValues)
			
		elif attribute == 0x4B:			#data from the barometer sensor
			values = struct.unpack('<HH', value)
			self.barometerValues['temperature'] = values[0]
			self.barometerValues['pressure'] = values[1]
			print(self.barometerValues)

		elif attribute == 0x5F:			#key pressed
			if value == 0x01:			# force  a close down, this will stop the reading of data and return back 
				self._gattServer.responseFinished()
		else:
			print("Attribue = %04X" % attribute)
			
		self._writeLEDDevice("0")
			
class Commands:
	
	"""
	Command processor, this class executes all of the user commands entered in.
	
	"""
	def __init__(self, args, gattServer):
		self._gattServer = gattServer
		self._args = args
		self._commands = { 'discover': self._commandDiscover,
							'accelerometer': self._commandAccelerometer,
							'battery': self._commandBattery,
							'gyroscope': self._commandGyroscope,
							'temperature': self._commandTemperature,
							'humidity': self._commandHumidity,
							'magnetometer': self._commandMagnetometer,
							'barometer': self._commandBarometer,
						}
	def execute(self, name):
		"""
		Execute the command 'name'
		"""
		result = False
		if name in self._commands:
			methodCall = self._commands[name]
			methodCall()
			result = True
		return result	


	def _commandDiscover(self):
		if not self._gattServer.start():
			logging.error("Cannot connect to the USB dongle")
			return False
			
		devices = self._gattServer.discover()
		if len(devices) > 0:
			print("Found %d device" % len(devices))
			for device in devices:
				print("Device: %s" % device.asString())
		
		return True
		
	def _sensorOpen(self, remoteAddress):
		if not self._gattServer.start():
			logging.error("Cannot connect to the USB dongle")
			return False
			
		# try to find if the device is connected already
		# setup a dummy connectSession
		
		connectSession = self._gattServer.addConnectSession(remoteAddress, 0)
		sensor = self._loadSensor(connectSession, 2, self._args.ledDevice)
		if sensor == None:
			# connect session failed so now remove it
			self._gattServer.removeConnectSession(connectSession)
			
			# now request a new connect session using the GATT server connect
			connectSession = self._gattServer.connect(remoteAddress)
			if connectSession:
				# find the correct sensor based on the UUID returned from the device
				sensor = self._loadSensor(connectSession, None, self._args.ledDevice)
				if sensor:
					return sensor
			else:
				logging.error("Cannot connect to device %s" % remoteAddress)			
			return None
		return sensor
		
	def _sensorClose(self):
		self._gattServer.disconnect()

				
	def _commandAccelerometer(self):
		sensor = self._sensorOpen(self._args.address)
		if sensor:
			sensor.accelerometer()				
			self._sensorClose()

	def _commandBattery(self):
		sensor = self._sensorOpen(self._args.address)
		if sensor:
			sensor.battery()		
			self._sensorClose()


	def _commandGyroscope(self):
		sensor = self._sensorOpen(self._args.address)
		if sensor:
			sensor.gyroscope()		
			self._sensorClose()

	def _commandTemperature(self):
		sensor = self._sensorOpen(self._args.address)
		if sensor:
			sensor.temperature()		
			self._sensorClose()

	def _commandHumidity(self):
		sensor = self._sensorOpen(self._args.address)
		if sensor:
			sensor.humidity()		
			self._sensorClose()

	def _commandMagnetometer(self):
		sensor = self._sensorOpen(self._args.address)
		if sensor:
			sensor.magnetometer()
			self._sensorClose()

	def _commandBarometer(self):
		sensor = self._sensorOpen(self._args.address)
		if sensor:
			sensor.barometer()
			self._sensorClose()


	def _commandTest(self):
		if not self._gattServer.start():
			logging.error("Cannot connect to the USB dongle")
			return False
		remoteAddress = self._args.address
		remoteDevice = self._gattServer.connect(remoteAddress)
		if remoteDevice:
			self._gattServer.test()
			self._gattServer.disconnect()
		else:
			logging.error("Cannot connect to device %s" % remoteAddress)
		
	def _loadSensor(self, connectSession, timeout = None, led_device = None):
		# find the type of remote device from UUID
		# i assume that all sensor tags support the handle 0x12 to read the uuid of the device.
		
		deviceUUID = ''
		data = connectSession.discoverByHandle(0x12, timeout)
		if data:
			deviceUUID = ''.join([("%02X" % v) for v in data])
		else:
			return None
		sensor = None
		if deviceUUID in SensorUUIDList:
			sensorName = SensorUUIDList[deviceUUID]
			logging.debug("Found sensor '%s'" % sensorName)
			sensor = getattr(sys.modules[__name__], sensorName)(self._gattServer, connectSession, led_device)
		else:
			print("Unknown device connected '%s'" % deviceUUID)
		return sensor
		
		
def main():

	commandList = [ "discover:\t\tList known devices within range",
					"accelerometer:\t\tReturn accelerometer information",
					"gyroscope:\t\tReturn gyroscope information",
					"temperature:\t\tReturns the object and ambient temperature",
					"humidity:\t\tReturns the temperature and humidity",
					"magnetometer:\t\tReturns the magnetic position",
					"barometer:\t\tReturns the temperature and pressure"
				]
	parser = argparse.ArgumentParser(description = "Talk Bluetooth to CC2540/1 Sensors")

	parser.add_argument('command', nargs='?', help="Possible commands are:\n %s" % "\n".join(commandList))
	parser.add_argument('options', nargs='*', help='options')

	parser.add_argument('--device', '-d', 
						dest='device', 
						default='/dev/ttyACM0', 
						help='Device to connect too'
					)

	parser.add_argument('--led', dest='ledDevice',
						default = None,
						help='LED device to flash when reading data. e.g. /sys/class/leds/ph21:blue:led2/brightness'
						)
						
	parser.add_argument('--timeout', '-t', 
						dest='timeout',
						type=int,
						default=10,
						help='Timeout in seconds before a GATT command will fail.'
					)

	parser.add_argument('--address', '-a', 
						dest='address', 
						default='', 
						help='Address of device to connect to usually returned by the discover command. If not set then a discovery will be made and the first device on the list will be used.'
					)


	parser.add_argument('-v', '--verbose', 
											dest="isVerbose",
											action="store_true", 
											help="Show more messages", 
											default=False)

					
					
	args = parser.parse_args()
		
	logLevel = logging.NOTSET
	if args.isVerbose:
		logLevel = logging.DEBUG
		logging.basicConfig(level = logLevel)
		logging.info("Set verbose mode on")

	
	
	gattServer = GATTServer.GATTServer()	
	gattServer.open(args.device, args.timeout)
	
	commands = Commands(args, gattServer)
	if args.command:
		commands.execute(args.command)
	else:
		print("Unknown command\n")
		print("Commands are:")
		print("\n".join(commandList))
	

	
# actual main call
if __name__ == "__main__":
    main()


