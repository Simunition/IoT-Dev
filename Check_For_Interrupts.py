import requests 

##Check for MQTT messages
def check_for_interrupt(thermostat):
    if (thermostat.set_temp) == 70:
        thermostat.change_set_temp(50)
        print("new set temp 50")
    #if interrupt && interrupt = temp request
        #publish temps
    #elif interrupt && interrupt = set request
        #set temp
        #publish temps 
    return None