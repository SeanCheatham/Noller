
# Imports
import MySQLdb as mysql
import sys
import math
import random
import Queue
import threading
from datetime import datetime

# Config Variables
PERSONALSPACE = 0.5
GRAVITY = 1e-7
CENTER_REPULSION = 5e-4
PARTICLE_REPULSION = 5e-5
EXECUTIONTIME = 1740
CYCLE = 1

# Helper Functions
def populateData():
    global things, cur

    cur.execute("SELECT * FROM things")
    dbThings = cur.fetchall()
    for dbThing in dbThings:
        things[dbThing['id']] = {'pos': dbThing['pos'], 'force': dbThing['force'], 'mass': dbThing['mass']}

    cur.execute("SELECT * FROM relations")
    dbRelations = cur.fetchall()
    for dbRelation in dbRelations:
        relations.append({'parent': dbRelation['parent'], 'child': dbRelation['child'], 'value': dbThing['value']})


#Calculation Function
def calculate(indices):
    global things, relations
    # Calculate force, acceleration, velocity, and position for each thing
    for idx in indices:
        direction = 1 if things[idx] > 0 else -1
        scalar = direction * CENTER_REPULSION *

        # Force
        #Repulsive Force from center
        # f = ma, but consider "CENTER_REPULSION" to be "mass" since this is a fake force. a = 1/r^2 * direction

        direction = math.atan2(thing.posY, thing.posX)
        #distance = math.pow(thing.posX,2) + math.pow(thing.posY,2)
        #distance = distance if distance > 0 else 0.00001
        #fScalar = CENTER_REPULSION * (1/math.pow(distance,2))
        cfScalar = CENTER_REPULSION
        thing.forceX += cfScalar * math.cos(direction)
        thing.forceY += cfScalar * math.sin(direction)

        for thing2 in things:
            if thing2 == thing or thing2 in thing.relations: continue
            deltaX = thing.posX - thing2.posX
            deltaY = thing.posY - thing2.posY
            direction = math.atan2(deltaY, deltaX)
            distance = math.pow(deltaX,2) + math.pow(deltaY,2)
            distance = max(distance, 0.001)
            rfScalar = PARTICLE_REPULSION * (1/math.pow(distance,2))
            thing.forceX += rfScalar * math.cos(direction)
            thing.forceY += rfScalar * math.sin(direction)


        # Attractive force for each related thing
        #print len(thing.relations)
        for relatedThing in thing.relations:
            deltaX = thing.posX - relatedThing.child.posX
            deltaY = thing.posY - relatedThing.child.posY
            direction = math.atan2(deltaY, deltaX)
            distance = math.pow(deltaX,2) + math.pow(deltaY,2)
            #fScalar = GRAVITY * (thing.m if thing.m > 0 else 0.1) * relatedThing.child.m * math.pow(distance,2)
            afScalar = GRAVITY * (1/relatedThing.value) * math.pow(distance,2)
            #print thing.id,relatedThing.child.id,fScalar
            # f = ma = G(m1)(m2)(radius)^2 * direction
            thing.forceX -= afScalar * math.cos(direction)
            thing.forceY -= afScalar * math.sin(direction)

        # Acceleration
        thing.accX = thing.forceX #/ (thing.m if thing.m > 0 else 0.1)
        thing.accY = thing.forceY #/ (thing.m if thing.m > 0 else 0.1)

        # Velocity
        thing.velX = thing.accX * dt
        thing.velY = thing.accY * dt

        # Position
        thing.posX += thing.velX
        thing.posY += thing.velY

        #print thing.forceX,thing.forceY,thing.accX,thing.accY,thing.velX,thing.velY,thing.posX,thing.posY


def threadedCalculator(dt):
    random.shuffle(things)
    threads = []
    t1 = threading.Thread(name='t1', target=calculate, args=(dt,0,len(things)/4-1))
    threads.append(t1)
    t1.start()

    t2 = threading.Thread(name='t2', target=calculate, args=(dt,len(things)/4,len(things)/2-1))
    threads.append(t2)
    t2.start()

    t3 = threading.Thread(name='t3', target=calculate, args=(dt,len(things)/2,len(things)/4*3-1))
    threads.append(t3)
    t3.start()

    t4 = threading.Thread(name='t4', target=calculate, args=(dt,len(things)/4*3,len(things)-1))
    threads.append(t4)
    t4.start()

    t1.join()
    t2.join()
    t3.join()
    t4.join()


#Update Database
def updateDB():
    global cur, things
    print "Updating DB at ",datetime.now()
    i = 0
    for thing in things:
        cur.execute("""
            UPDATE things2
            SET posX = %s, posY = %s, mass = %s
            WHERE id = %s
        """,(str(thing.posX), str(thing.posY), str(thing.m) if thing.m > 0.1 else None, str(thing.id)))
        if(i%10 == 0): con.commit()
        i += 1
    con.commit()
    print "Finished Updating DB"

def refreshData():
    global things
    print "Refreshing data at ",datetime.now()
    things = {}
    populateData()

def exitCruncher():
    global cur, con
    print "Exiting at ",datetime.now()
    cur.close()
    con.close()
    sys.exit(0)

def dbConnect():
    global con, cur
    try:
        con = mysql.connect('', 'nollej', 'SU2orange!', 'nollej')
        cur = con.cursor(mysql.cursors.DictCursor)
    except mysql.Error, e:
        print "Error %d: %s" % (e.args[0], e.args[1])
        sys.exit(1)
# Main
print "Initializing Cruncher at ",datetime.now()
con = None
cur = None
things = {}
relations = []
dbConnect()
refreshData()

print "Starting calculator at ",datetime.now()
while ( True ):
    zeroVals()
    threadedCalculator(1)
    if(CYCLE%800 == 0):
        print "Halting calculator at ",datetime.now()
        updateDB()
        #refreshData()
        print "Starting calculator at ",datetime.now()
    CYCLE += 1

'''
Pseudo-Code for new algorithm


things = []
relations = []
LOAD-DATA:
    data = DB -> SELECT * FROM things
    for row in data:
        things[row.id] = {row}
    data = DB -> SELECT * FROM relations
    for row in data:
        relations[row.id] = {row}
CALCULATE:
    for t in things:
        t.force += Center_Force
        for t2 in things:
            if t == t2 or t2: continue/skip
            t.force -= Repulsive_Force
    for r in relations:
        things[r.parent].force += Attractive_Force(things[r.child])
'''
