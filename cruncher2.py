
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
    global things, cur, world
    world = []
    for i in range (0,1000):
        inner = []
        for j in range (0,1000):
            inner.append(None)
        world.append(inner)

    cur.execute("SELECT * FROM things")
    dbThings = cur.fetchall()
    for dbThing in dbThings:
        if(dbThing['posX'] is None or dbThing['posY'] is None):
            coords = findRandomEmptyLocation()
            dbThing['posX'] = coords[0]
            dbThing['posY'] = coords[1]
        thing = {'posX': dbThing['posX'], 'posY': dbThing['posY'], 'forceX': 0.0, 'forceY': 0.0}
        things[dbThing['id']] = thing
        world[thing['posX']][thing['posY']] = thing
    cur.execute("SELECT * FROM relations")
    dbRelations = cur.fetchall()
    for dbRelation in dbRelations:
        relations.append({'parent': dbRelation['parent'], 'child': dbRelation['child'], 'value': dbThing['value']})

def findRandomEmptyLocation():
    random.seed()
    randX = math.floor(random.random() * len(world))
    randY = math.floor(random.random() * len(world[randX]))
    if world[randX][randY] is None:
        return (randX,randY)
    else:
        return findRandomEmptyLocation()

def findEmptyLocationAroundPoint(x, y, radius):
    if(world[x][y] is None):
        return (x,y)
    for i in random.shuffle(range(x - radius, x + radius)):
        if i < 0 or i >= len(world):
            continue
        for j in random.shuffle(range(y - radius, y + radius)):
            if j < 0 or j > len(world[i])-1:
                continue
            if(world[i][j] is None):
                return (i,j)
    return findEmptyLocationAroundPoint(x, y, radius + 1)

#Calculation Function
def calculateAttractions(indices):
    global things, relations
    for r in indices:
        deltaX = things[relations[r]['parent']]['posX'] - things[relations[r]['child']]['posX']
        deltaY = things[relations[r]['parent']]['posY'] - things[relations[r]['child']]['posY']
        direction = math.atan2(deltaY, deltaX)
        distance = math.pow(deltaX,2) + math.pow(deltaY,2)
        afScalar = GRAVITY * (1/r.value) * distance
        things[[r]['parent']]['forceX'] -= afScalar * math.cos(direction)
        things[[r]['parent']]['forceY'] -= afScalar * math.sin(direction)

def moveParticles():
    global things, world
    for t in things:
        targetX = math.floor(things[t]['posX'] + things[t]['forceX'])
        targetY = math.floor(things[t]['posY'] + things[t]['forceY'])
        coordinates = findEmptyLocationAroundPoint(targetX, targetY, 1)
        world[things[t]['posX']][things[t]['posY']] = None
        world[coordinates[0]][coordinates[1]] = things[t]
        things[t]['posX'] = coordinates[0]
        things[t]['posY'] = coordinates[1]

def threadedCalculator(dt):
    random.shuffle(relations)
    threads = []
    t1 = threading.Thread(name='t1', target=calculateAttractions, args=(range(0,len(relations)/4-1)))
    threads.append(t1)
    t1.start()

    t2 = threading.Thread(name='t2', target=calculateAttractions, args=(range(len(relations)/4,len(relations)/2-1)))
    threads.append(t2)
    t2.start()

    t3 = threading.Thread(name='t3', target=calculateAttractions, args=(range(len(relations)/2,len(relations)/4*3-1)))
    threads.append(t3)
    t3.start()

    t4 = threading.Thread(name='t4', target=calculateAttractions, args=(range(len(relations)/4*3,len(relations)-1)))
    threads.append(t4)
    t4.start()

    t1.join()
    t2.join()
    t3.join()
    t4.join()

    moveParticles()


#Update Database
def updateDB():
    global cur, things
    print "Updating DB at ",datetime.now()
    i = 0
    for t in things:
        cur.execute("""
            UPDATE things
            SET posX = %s, posY = %s
            WHERE id = %s
        """,(str(things[t]['posX']), str(things[t]['posY']), str(t)))
        if(i%10 == 0): con.commit()
        i += 1
    con.commit()
    print "Finished Updating DB"

def refreshData():
    global things, relations, world
    print "Refreshing data at ",datetime.now()
    things = {}
    relations = []
    world = None
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
world = None
dbConnect()
refreshData()

print "Starting calculator at ",datetime.now()
while ( True ):
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
