__author__ = 'Sean'

import threading

arr = range(0,1000)

def calculate(start,end):
    for t in arr[start:end]:
        print threading.currentThread().getName(), t

threads = []
t1 = threading.Thread(name='t1', target=calculate, args=(0,len(arr)/4-1))
threads.append(t1)
t1.start()

t2 = threading.Thread(name='t2', target=calculate, args=(len(arr)/4,len(arr)/2-1))
threads.append(t2)
t2.start()

t3 = threading.Thread(name='t3', target=calculate, args=(len(arr)/2,len(arr)/4*3-1))
threads.append(t3)
t3.start()

t4 = threading.Thread(name='t4', target=calculate, args=(len(arr)/4*3,len(arr)-1))
threads.append(t4)
t4.start()

t1.join()
t2.join()
t3.join()
t4.join()

