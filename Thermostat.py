
##Thermostat framework

class Thermostat:

    def __init__(self, name, last_temp = 69, set_temp = 70, actual_temp = 70):
        self.name = name
        self.last_temp = last_temp
        self.set_temp = set_temp
        self.actual_temp = actual_temp
        self.max = set_temp + 1
        self.min = set_temp - 2
    
    def increment_temp(self, x):
        self.actual_temp += x

    def change_set_temp(self, x):
        self.set_temp = x
        self.max = self.set_temp + 1
        self.min = self.set_temp - 2

    def getData(self):
        data = {}
        data['Thermostat Name'] = self.name
        data['Set Temperature'] = self.set_temp
        data['Actual Temperature'] = self.actual_temp
        data2 = {}
        data2['desired'] = data
        data3 = {}
        data3['state'] = data2
        return data3

    def temp_loop(self):

        def increment(x):
            self.last_temp = self.actual_temp
            self.increment_temp(x)

        if self.actual_temp > self.last_temp:
            if self.actual_temp < self.max:
                increment(1)
            else:
                increment(-1)
        elif self.actual_temp < self.last_temp:
            if self.actual_temp > self.min:
                increment(-1)
            else:
                increment(1)
        
            



