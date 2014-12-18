
# Imports
import MySQLdb as mysql
import sys
import math
import random
import Queue
import threading
from datetime import datetime

class Thing:
    def __init__(self, i, x, y, mass, rIds):
        self.id = i
        if (x == None or y == None):
            '''random.seed()
            r = 1
            rand = random.random() - 0.5
            self.posX = r * math.cos(2 * math.pi * rand)
            self.posY = r * math.sin(2 * math.pi * rand)'''
            #self.posX = random.random() * 20 - 10
            #self.posY = random.random() * 20 - 10
            t = 2*math.pi*random.random()
            u = random.random()+random.random()
            r = 2-u if u>1 else u
            self.posX = r * math.cos(t) * 10
            self.posY = r * math.sin(t) * 10
        else:
            self.posX = x
            self.posY = y
        self.velX = 0.0
        self.velY = 0.0
        self.accX = 0.0
        self.accY = 0.0
        self.forceX = 0.0
        self.forceY = 0.0
        self.m = mass if mass > 0 else 0.1
        self.relationIds = rIds
        self.relations = []

class Relation:
    def __init__(self, p, c, v):
        self.parent = p
        self.child = c
        self.value = v


# Config Variables
PERSONALSPACE = 0.5
GRAVITY = 1e-7
CENTER_REPULSION = 5e-4
PARTICLE_REPULSION = 5e-3
EXECUTIONTIME = 1740
CYCLE = 1

# Helper Functions
def populateData():
    global things, cur
    #cur.execute("SELECT * FROM things")
    cur.execute("""
        SELECT  t.*, GROUP_CONCAT(r.child ORDER BY r.value asc) as relations
        FROM    things2 t
        LEFT JOIN    relations2 r
        ON      t.id = r.parent
        GROUP BY
                t.id;
    """)
    dbThings = cur.fetchall()
    # Iterate through each result, create a Thing object, and append it to the global list of things
    for dbThing in dbThings:
        if dbThing['relations'] is not None and len(dbThing['relations']) > 0:
            rIds = map(int, dbThing['relations'].split(','))
        else:
            rIds = []
        '''if (dbThing['posX'] == None or dbThing['posY'] == None):
            x = 0.0
            y = 0.0
            if isinstance(rIds,list) and len(rIds) > 0:
                cur.execute("""
                    select posX, posY from things2 where id = %s
                """,(str(rIds[0]),))
                parent = cur.fetchone()
                if(parent != None and parent['posX'] != None and parent['posY'] != None):
                    x = parent['posX']
                    y = parent['posY']
            random.seed()
            r = 1
            rand = random.random() - 0.5
            dbThing['posX'] = r * math.cos(2 * math.pi * rand) + x
            dbThing['posY'] = r * math.sin(2 * math.pi * rand) + y'''
        things.append(Thing(dbThing['id'], dbThing['posX'], dbThing['posY'], dbThing['mass'], rIds if isinstance(rIds,list) else []))


    # Iterate through each thing,
    for thing in things:
        # Select all relations from DB corresponding to the current thing
        # Iterate through each relation
        valueIterator = 1
        for rId in thing.relationIds:
            # Make sure that the child thing already exists
            child = checkForThing(rId)
            # If the child does not exist, print out an error and continue to the next thing in the list
            if(child == None):
                print "Invalid relation specified; Child does not exist: ",rId
                continue
            # Create a new relation and append it to the thing's relations list
            thing.relations.append(Relation(thing,child,valueIterator))
            child.m += 1
            valueIterator += 1

def checkForThing(thingId):
    global things
    for thing in things:
        if thing.id == thingId:
            return thing

    return None

    '''
    queue = Queue.Queue()
    found = [0]
    result = [None]
    def check(start,end):
        for thing in things[int(start):int(end)]:
            if found[0] == 1: return
            if thing.id == thingId:
                found[0] = 1
                result[0] = thing
                return
    p1 = threading.Thread(target=check, args=(0,math.floor(len(things)/2)-1))
    p1.start()
    p2 = threading.Thread(target=check, args=(math.floor(len(things)/2),math.floor(len(things))-1))
    p2.start()

    p1.join()
    p2.join()
    return result[0]'''

def zeroVals():
    global things
    for thing in things:
        # Reset forces, accelerations, and velocities
        thing.forceX = 0.0
        thing.forceY = 0.0
        thing.accX = 0.0
        thing.accY = 0.0
        thing.velX = 0.0
        thing.velY = 0.0

#Calculation Function
def calculate(dt):
    global things, t1, t2
    # Calculate force, acceleration, velocity, and position for each thing
    for thing in things:

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
        '''
        for thing2 in things:
            if thing2 == thing or thing2 in thing.relations: continue
            deltaX = thing.posX - thing2.posX
            deltaY = thing.posY - thing2.posY
            direction = math.atan2(deltaY, deltaX)
            distance = math.pow(deltaX,2) + math.pow(deltaY,2)
            distance = distance if distance > 0 else 0.00001
            rfScalar = PARTICLE_REPULSION * (1/math.pow(distance,2))
            thing.forceX += rfScalar * math.cos(direction)
            thing.forceY += rfScalar * math.sin(direction)
        '''

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
    things = []
    populateData()

def exitCruncher():
    global cur, con
    print "Exiting at ",datetime.now()
    cur.close()
    con.close()
    sys.exit(0)
# Main

# Make DB Connection or quit
con = None
cur = None

try:
    con = mysql.connect('', 'nollej', 'SU2orange!', 'nollej')
    cur = con.cursor(mysql.cursors.DictCursor)
except mysql.Error, e:
    print "Error %d: %s" % (e.args[0], e.args[1])
    sys.exit(1)

print "Initializing Cruncher at ",datetime.now()
things = []
refreshData()

#Correct the gravity constant
#GRAVITY /= len(things)
print "Starting calculator at ",datetime.now()
while ( True ):
    zeroVals()
    calculate(1)
    if(CYCLE%500 == 0):
        print "Halting calculator at ",datetime.now()
        updateDB()
        refreshData()
        print "Starting calculator at ",datetime.now()
    CYCLE += 1
