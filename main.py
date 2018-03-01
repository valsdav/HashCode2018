import os
import sys
from operator import attrgetter, itemgetter

def time_distance(A, B):
    return abs(A[0] - B[0]) + abs(A[1]-B[1])

def driver_ride_distance(driver, ride):
    deltaT = driver.get_current_time() + time_distance(driver.get_current_loc(), ride.start) -  ride.T0
    if deltaT < 0:
        return ride.G * 5 
    else:
        if deltaT > ride.G:
            return -1
        else:
            return ride.G - deltaT 


class Ride: 

    def __init__(self, id,  start, stop, T0, T1 ):
        self.id = id
        self.start = start
        self.stop = stop
        self.T0 = T0
        self.T1 = T1
        self.duration =  time_distance(start, stop)
        self.Tc = T1- self.duration
        #Tempo di arrivo del driver
        self.Tf = None
        # Massimo guadagno di tempo
        self.G = self.Tc - T0 


class Driver: 

    def __init__(self,i):
        self.id = i
        self.rides = []
        self.current_ride = Ride(0, (0,0),(0,0), 0, 0)

    def get_current_time(self):
        if (self.current_ride.Tf == None):
            return 0
        return self.current_ride.Tf

    def get_current_loc(self):
        return self.current_ride.stop

    def add_ride(self, ride):
        ride.Tf = self.get_Tf(ride)
        self.rides.append(ride)
        self.current_ride = ride

    def get_Tf(self, ride):
        time_arrival =  self.get_current_time() + time_distance(self.get_current_loc(), ride.start) 
        if (time_arrival > ride.T0):
            return time_arrival + ride.duration
        else:
            return ride.T0 + ride.duration

def get_available_drivers(drivers, t1, t2):
    drs =[]
    for driver in drivers:
        ct = driver.get_current_time()
        if  ct >= t1 and ct <= t2:
            drs.append(driver)
    return drs 

Next_ride_to_look = 10
 
def get_best_driver_ride(drivers, rides):
    #cut rides
    if (len(rides) > Next_ride_to_look*len(drivers)):
        limit = Next_ride_to_look*len(drivers)
    else:
        limit = len(rides)
    rides_sel = sorted(rides, key=attrgetter("T0") )[:limit]
    ranking = []
    di = 0
    for driver in drivers:
        ri = 0
        for ride in rides_sel:
            distance = driver_ride_distance(driver, ride)
            if distance != -1:
                ranking.append((di, ri, distance ))
            ri +=1
        di+=1
    results = []
    drivers_done = []
    rides_done = []
    #ordine crescente
    for r in sorted(ranking, key=itemgetter(2), reverse=True):
        if r[1] not in rides_done: 
            if r[0] not in drivers_done:
                results.append((drivers[r[0]], rides[r[1]], r[2]))
                drivers_done.append(r[0])
                rides_done.append(r[1])
    return results


def get_lost_time(pairs, t): 
    sum = 0
    for driver, ride, cost in pairs: 
        c = t -driver.get_Tf(ride)
        if c > 0 :
            sum+= c
    return sum


if __name__ == "__main__":

    Rides_todo = []
    Rides_done = []
    Drivers = []

    with open(sys.argv[1], "r") as file:
        lines = file.readlines()
    line0 = lines[0]
    d0 = line0.split(" ")
 
    for j in range(int(d0[2])):
        Drivers.append( Driver(j))

    i = 0
    for line in lines[1:]:
        pars = line.split(" ")
        rid = Ride( i, (int(pars[0]), int(pars[1])),  (int(pars[2]), int(pars[3])), int(pars[4]), int(pars[5]) )
        if rid.Tc > rid.T0:
            Rides_todo.append(rid)
        i+=1

    Ttotal = int(d0[5])
    DeltaT_step = 500
    Tw_start = 0
    Tw_stop = 0
    
    quality_factor = 0
    idle_drivers = None
    pairs = None
    i = 0 
    while(True):
        if Tw_stop > Ttotal:
            break
        Tw_stop += DeltaT_step
        _idle_drivers = get_available_drivers(Drivers, Tw_start, Tw_stop)
        _pairs = get_best_driver_ride(_idle_drivers, Rides_todo)
        _lost_time = get_lost_time(_pairs, Tw_stop)
        _gain = 0
        for p in _pairs:
            _gain+= p[2]
        _quality_factor = 0.5*_gain- _lost_time
        print("Tstart: {}| Tstop: {}| Rides_todo:  {}| Drivers: {} | QF: {} | loss: {}".format(
                Tw_start, Tw_stop, len(Rides_todo),  len(_idle_drivers), _quality_factor, _lost_time))
        
        if ( i==0  or _quality_factor >= quality_factor):
            idle_drivers = _idle_drivers
            pairs = _pairs
            quality_factor = _quality_factor
            print("Expand")
        else:
            #mi fermo
            min_Tf = -1
            for driver, ride, cost in pairs:
                driver.add_ride(ride)
                Rides_todo.remove(ride)
                Rides_done.append(ride)
                if min_Tf == -1 or ride.Tf < min_Tf:
                    min_Tf = ride.Tf
            print("###SAVE")    
            lost_time = 0
            idle_drivers = None
            pairs = None
            Tw_start = min_Tf
            Tw_stop = Tw_start
            i = 0
            if len(Rides_todo) == 0:
                break
            continue
            
        i += 1

    with open(sys.argv[1]+"_output", "w") as output:
        for i in range(len(Drivers)):
            rs = [str(r.id) for r in Drivers[i].rides]
            output.write("{} {}\n".format(len(rs), " ".join(rs)))



            
