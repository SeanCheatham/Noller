
# Imports
import MySQLdb as mysql
import sys
import math
import random
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
    print "Initializing World"
    world = []
    for i in range(0,1000):
        inner = []
        for j in range (0,1000):
            inner.append(None)
        world.append(inner)
    print "Populating things"
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

    print "Populating relations"
    cur.execute("SELECT * FROM relations WHERE value <= 10")
    dbRelations = cur.fetchall()
    for dbRelation in dbRelations:
        relations.append({'parent': dbRelation['parent'], 'child': dbRelation['child'], 'value': dbRelation['value']})

def findRandomEmptyLocation():
    random.seed()
    randX = int(random.random() * len(world))
    randY = int(random.random() * len(world[randX]))
    if world[randX][randY] is None:
        return (randX,randY)
    else:
        return findRandomEmptyLocation()

def findEmptyLocationAroundPoint(x, y, radius):
    if(world[x][y] is None):
        return (x,y)
    for i in range(x - radius, x + radius):
        if i < 0 or i >= len(world):
            continue
        for j in range(y - radius, y + radius):
            if j < 0 or j >= len(world[i]):
                continue
            if(world[i][j] is None):
                return (i,j)
    return findEmptyLocationAroundPoint(x, y, radius + 1)

#Calculation Function
def calculateAttractions(start, end):
    global things, relations
    #print "Calculating attractions for section "+str(start)+" through "+str(end)
    for r in relations[start:end]:
        if r['parent'] not in things or r['child'] not in things:
            print "Invalid key for thing"
            continue
        deltaX = things[r['parent']]['posX'] - things[r['child']]['posX']
        deltaY = things[r['parent']]['posY'] - things[r['child']]['posY']
        direction = math.atan2(deltaY, deltaX)
        distance = math.pow(deltaX,2) + math.pow(deltaY,2)
        afScalar = GRAVITY * (1/r['value']) * distance
        things[r['parent']]['forceX'] -= afScalar * math.cos(direction)
        things[r['parent']]['forceY'] -= afScalar * math.sin(direction)

def calculateRepulsions():
    global things
    for t in things:
        for i in range(-5,5):
            if things[t]['posX'] + i < 0 or things[t]['posX'] + i >= len(world):
                continue
            for j in range(-5,5):
                if things[t]['posY'] + j < 0 or things[t]['posY'] + j >= len(world[i]):
                    continue
                if i == 0 and j == 0:
                    continue
                if world[things[t]['posX'] + i][things[t]['posY'] + j] is None:
                    continue
                deltaX = things[t]['posX'] - world[things[t]['posX'] + i][things[t]['posY'] + j]['posX']
                deltaY = things[t]['posY'] - world[things[t]['posX'] + i][things[t]['posY'] + j]['posY']
                direction = math.atan2(deltaY, deltaX)
                distance = abs(math.sqrt(math.pow(deltaX, 2) + math.pow(deltaY, 2)))
                if distance > 0:
                    afScalar = PARTICLE_REPULSION / distance
                    world[things[t]['posX'] + i][things[t]['posY'] + j]['posX'] -= afScalar * math.cos(direction)
                    world[things[t]['posX'] + i][things[t]['posY'] + j]['posY'] -= afScalar * math.sin(direction)

def moveParticles():
    global things, world
    #print "Moving particles"
    random.shuffle(things)
    for t in things:
        targetX = int(things[t]['posX'] + things[t]['forceX'])
        targetY = int(things[t]['posY'] + things[t]['forceY'])
        coordinates = findEmptyLocationAroundPoint(targetX, targetY, 1)
        world[things[t]['posX']][things[t]['posY']] = None
        world[coordinates[0]][coordinates[1]] = things[t]
        things[t]['posX'] = coordinates[0]
        things[t]['posY'] = coordinates[1]
        things[t]['forceX'] = 0
        things[t]['forceY'] = 0

def threadedCalculator(dt):
    random.shuffle(relations)
    threads = []
    t1 = threading.Thread(name='t1', target=calculateAttractions, args=(0,len(relations)/4-1))
    threads.append(t1)
    t1.start()

    t2 = threading.Thread(name='t2', target=calculateAttractions, args=(len(relations)/4,len(relations)/2-1))
    threads.append(t2)
    t2.start()

    t3 = threading.Thread(name='t3', target=calculateAttractions, args=(len(relations)/2,len(relations)/4*3-1))
    threads.append(t3)
    t3.start()

    t4 = threading.Thread(name='t4', target=calculateAttractions, args=(len(relations)/4*3,len(relations)-1))
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
    print "Finished Updating DB at",datetime.now()

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
while ( 1 ):
    threadedCalculator(1)
    if(CYCLE%50 == 0):
        print "Halting calculator at ", datetime.now(), " at cycle ", CYCLE
        updateDB()
        #refreshData()
        #print "Sample output"
        #print things[1]['posX']
        print "Starting calculator at ",datetime.now()
    CYCLE += 1

exitCruncher()