__author__ = 'smcheath'


# Imports
import MySQLdb as mysql
import sys
import math
import random
import threading
from datetime import datetime

# Config Variables
PERSONALSPACE = 0.5
GRAVITY = 1e-3
CENTER_REPULSION = 5e-4
PARTICLE_REPULSION = 1e-5
PARTICLE_REPULSION_RADIUS = 5
EXECUTIONTIME = 1740
CYCLE = 1
WORLD_SIZE = 1000

# Helper Functions
def populateData():
    global things, cur
    print "Populating things"
    cur.execute("SELECT id, name FROM things")
    dbThings = cur.fetchall()
    for dbThing in dbThings:
        thing = {'name': dbThing['name']}
        things[dbThing['id']] = thing

def fixMasses():
    for t in things:
        cur.execute("""
            SELECT COUNT(*) as c FROM relations WHERE child = %s
        """,(str(t),))
        res = int(cur.fetchone()["c"])
        cur.execute("""
            UPDATE things SET mass = %s WHERE id = %s
        """,(str(res),str(t)))
        con.commit()

def refreshData():
    global things, relations, world
    print "Refreshing data at ",datetime.now()
    things = {}
    relations = []
    world = None
    populateData()

def cleanExit():
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
print "Initializing mass updater at",datetime.now()
con = None
cur = None
things = {}
dbConnect()
refreshData()
fixMasses()

cleanExit()