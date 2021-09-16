
##Thermostat framework

class Thermostat:

    def __init__(self, last_temp = 69, set_temp = 70, actual_temp = 70):
        self.last_temp = last_temp
        self.set_temp = set_temp
        self.actual_temp = actual_temp
        self.max = set_temp + 1
        self.min = set_temp - 2
    
    def increment_temp(self, x):
        self.actual_temp += x

    def temp_loop(self, thermostat):

        def increment(x):
            thermostat.last_temp = thermostat.actual_temp
            thermostat.increment_temp(x)
            print("set temp: ", thermostat.set_temp)
            print("actual temp: ", thermostat.actual_temp)
            print("last temp:", thermostat.last_temp)

        if thermostat.actual_temp > thermostat.last_temp:
            if thermostat.actual_temp < thermostat.max:
                increment(1)
            else:
                increment(-1)
        elif thermostat.actual_temp < thermostat.last_temp:
            if thermostat.actual_temp > thermostat.min:
                increment(-1)
            else:
                increment(1)
            



