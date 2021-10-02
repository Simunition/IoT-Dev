import random 

#Thermostat framework

class Thermostat:

    #Attributes for setting and maintaining data about the thermostat and values associated with a typical physical device
    #last humidity and last temp are used to know which direction to move in when psuedo naturally changing those values.

    def __init__(self, storage_ID, storage_name, address, humidity = 70, light_level = 1, set_temp = 70, actual_temp = 70):
        self.storage_ID = storage_ID
        self.storage_name = storage_name
        self.address = address
        self.humidity = humidity
        self.last_humidity = humidity
        self.light_level = light_level
        self.last_temp = actual_temp
        self.set_temp = set_temp
        self.actual_temp = actual_temp
    

    #Method to create a payload for publishing, the dictionary is formatted as a json for clean passing of messages

    def getData(self):
        data = {}
        data['storageID'] = self.storage_ID
        data['storageName'] = self.storage_name
        data['lightLevel'] = self.light_level
        data['temperature'] = self.actual_temp
        data['setTemperature'] = self.set_temp
        data['humidity'] = self.humidity
        data['address'] = self.address
        return data

    #This loop creates a wave around the set temperature of the thermostat. The thresholds are 2 degrees below and 1 degree above the set.
    #If the actual temperature is within this range of set temp, the loop iterates up until it hits the max, then back down until it hits the min.
    #If the set temperature is changes, then this loop will allow the temperature to iterate up until it hits the new max, or down until it hits the new min.
    #This simulates a real-world environment where if the temperature is set to 70 and the user changes it to 30, it will take somewhere
    #between 80 and 400 minutes to adjust to the new set temperature, and the exact time between that is generated at random.

    #Note: If you're using this script to connect an actual physical thermostat, these loops would be replaced with methods to collect the 
    #actual data from sensors on the device.

    def temp_loop(self):

        min = self.set_temp - 2
        max = self.set_temp + 1

        def increment(x):
            self.last_temp = self.actual_temp
            self.actual_temp += x

        if self.actual_temp >= self.last_temp:
            if self.actual_temp < max:
                increment(1)
            else:
                increment(-1)
        elif self.actual_temp < self.last_temp:
            if self.actual_temp > min:
                increment(-1)
            else:
                increment(1)

    #Humidity only allows for one above or one below the original set humidity, there's no expectation of receiving a message to change
    #set humidity because that is a product of the environment.

    def humidity_loop(self):

        def increment(x): 
            self.last_humidity = self.humidity
            self.humidity += x 

        if self.humidity == self.last_humidity:
            increment(random.randint(-1,1))
        elif self.humidity > self.last_humidity:
            increment(-1)
        elif self.humidity < self.last_humidity:
            increment(1)

