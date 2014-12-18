__author__ = 'Sean'

import urllib2
import re
import MySQLdb as mysql
import sys
import getopt
import time

def crawl(t,l):
    if (l <= 0):return


    print("Crawling {0} to depth {1}".format(t,l))
    cur.execute("""
        select count(*) as c
        from things2
        where crawled = 1 AND name LIKE "%s"
    """,(str(t),))
    res = cur.fetchone()["c"]
    if(int(res) > 0): return
    links = yank(t)
    length = 0 if links == None else len(links)
    print length

    t = t.replace("'","")
    t = re.sub('[^0-9a-zA-Z ]+', '', t)
    cur.execute("""
        INSERT INTO things2 (name,mass) VALUES (replace("%s", "'", ""),0)
        ON DUPLICATE KEY UPDATE id = id
    """,(str(t),))
    con.commit()
    cur.execute("""
        SELECT id from things2 WHERE name like replace("%s", "'", "")
    """,(str(t),))
    parentId = cur.fetchone()["id"]
    value = 1
    for p in links:
        p = p.replace("'","")
        p = re.sub('[^0-9a-zA-Z ]+', '', p)
        cur.execute("""
            INSERT INTO things2 (name,mass) VALUES (replace("%s", "'", ""),0)
            ON DUPLICATE KEY UPDATE id=id
        """,(str(p),))
        con.commit()
        cur.execute("""
          SELECT id from things2 WHERE name like replace("%s", "'", "")
        """,(str(p),))
        childId = cur.fetchone()["id"]
        try:
            cur.execute("""
                INSERT INTO relations2 (parent,child,value) VALUES (%s,%s,%s)
                ON DUPLICATE KEY UPDATE id=id
            """,(str(parentId),str(childId),str(value)))

        except mysql.Error, e:
            print e

        else:
            cur.execute("""
                UPDATE things2 set mass = mass + 1
                WHERE id = %s
            """,(str(childId),))
            con.commit()

        value += 1
        con.commit()
        crawl(p,l-1)
    cur.execute("""
        update things2 set crawled = 1 where id = %s
    """,(str(parentId),))
    con.commit()

def yank(t):
    time.sleep(8)
    opener = urllib2.build_opener()
    opener.addheaders = [("User-agent", "nollej/1.0 (http://seancheatham.com/nollej)")]
    infile = opener.open('http://en.wikipedia.org/w/api.php?format=json&action=query&prop=revisions&rvprop=content&redirects=true&titles='+t)
    page = infile.read()
    return getLinks(page)

def getLinks(p):
    regex = re.compile('\[\[([a-zA-Z ]*)\]\]')
    vals = re.findall(regex, p)
    return vals

def main(argv):

    STARTVALUE = ""
    LIMIT = 0

    try:
        opts, args = getopt.getopt(argv, "w:d:", ["word=","depth="])
    except getopt.GetoptError:
        print 'crawler.py -w <word> -d <depth>'
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-w","--word"):
            STARTVALUE = str(arg)
        elif opt in ("-d","--depth"):
            LIMIT = int(arg)

    crawl(STARTVALUE,LIMIT)



if __name__ == "__main__":
    try:
        con = mysql.connect('', 'nollej', 'SU2orange!', 'nollej')
        #con.autocommit(True)
        cur = con.cursor(mysql.cursors.DictCursor)
    except mysql.Error, e:
        print "Error %d: %s" % (e.args[0], e.args[1])
        sys.exit(1)
    main(sys.argv[1:])
    cur.close()
    con.close()
