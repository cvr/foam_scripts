#!/usr/bin/python

#Please go to end of this file to modify input parameters!

#DO NOT modify code below
def get_n(delta1,deltan,length,debug=0):
    #given delta1 (size of 1st cell), deltan (size of last cell) and length of the domain
    #giving it a guess of n can accelerate the computation
    #return number of cells, n
    #deltan may be slightly different from given value
    if debug > 0:
        print "call get_n()"

    deltan = float(deltan)
    delta1 = float(delta1)
    length = float(length)
    n = length*2/(delta1+deltan)#initial guess of n
    r1 = deltan/delta1
    if abs(deltan-delta1) < 1e-6:#deltan=delta1
        return int(round(n))#round n into a integer
    max_it = 100000
    convergence_rule = 0.0000001

    #newton-raphson iteration
    #lhs = delta1*(1-r1**(n/(n-1)))/(1-r1**(1/(n-1)))
    #solve for f =  a*(1-b^(x/(x-1)))/(1-b^(1/(x-1)))-L = 0
    f =  delta1*(1-r1**(n/(n-1))) / (1-r1**(1/(n-1)))- length
    from math import log
    for i in range(max_it):
        if debug > 0:
            print "iteration: ",i
            print "n:",n
            print "residual:",f
            print "\n"
        if abs(f) < convergence_rule:
            break
        #f_prime got from wolfram alpha
        f_prime = ( (delta1*  log(r1) )*(r1**(n/(n-1))-r1**(1/(n-1))) ) / ((n-1)**2 * (r1**(1/(n-1))-1)**2)
        n = n - f/f_prime #new n
        f =  delta1*(1-r1**(n/(n-1)))/(1-r1**(1/(n-1)))- length # new f

    if debug > 0 :
        print "total number of iteration for getting n:",i
        print "residual:",abs(f)
        print "n:",n

    return int(round(n))#round n into a integer

################################################################################
def get_r_given_delta1(delta1,length,n,debug=0):
    #return ratio between two adjacent cells, r = delta_{i+1} / delta_{i}
    #solve delta1*(1-r^n)/(1-r) = length to get r
    if debug > 0 :
        print "\n"*3
        print "Given delta1, length of edge, number of cells along this edge"
        print "call get_r_given_delta1"

    delta1 = float(delta1)
    length = float(length)
    n = float(n)
    max_it = 2000
    convergence_rule = 0.0000001
    if length/n > delta1:#cell size is increasing from left to right 
        increase = True
    else:
        increase = False
    r = (length/n/delta1)**(1/(n-1))#initial value for r
    if abs(r - 1) < 1e-6:#uniform grid
        if debug > 0 :
            print "Warning! The inputs indicates a uniform grid!"
        i=0
    else:#nonuniform grid
        #newton-raphson iteration
        #solve for f(r) = (1-r^n)/(1-r) - L/delta1 = 0
        f = (1-r**n)/(1-r) - length/delta1 #f0
        for i in range(max_it):
            if debug == 2:
                print "iteration:",i
                print "r=",r
                print "residual:",f
            if abs(f) < convergence_rule:
                break
            f_prime = ((n-1)*r**(n+1)-n*r**n+r)/((1-r)**2*r)
            r = r - f/f_prime #new r
            f = (1-r**n)/(1-r) - length/delta1 #new f
        if i == max_it-1:
            print "Warning!! Maximum iteration reached. Something was wrong!"
    clusterRatio=r**(n-1)#ratio of size of last cell to first cell, delta_n/delta_1 

    if debug > 0:
        print "#"*80
        print "result summary"
        print "iteration times:", i
        print "ratio between two adjacent cells, r = delta_{i+1} / delta_{i} = ", r
        print "ratio of size of last cell to first cell, delta_n/delta_1 =",clusterRatio
        print "total number of cells along this edge, n =",n
        print "size of first cell:", delta1
        print "size of last cell:", delta1*r**(n-1)

    return clusterRatio
       

################################################################################
def get_r_given_deltan(deltan,length,n,debug=0):
    if debug > 0:
        print "call get_r_given_deltan"
    #return ratio between two adjacent cells, r = delta_{i+1} / delta_{i}
    #solve deltan*(1-r^n)/((1-r)*r^{n-1}) = length to get r
    deltan =  float(deltan)
    length = float(length)
    n = float(n)
    max_it = 10000 
    convergence_rule = 0.0000001
    if length/n > deltan:#cell size is increasing from left to right 
        increase = False 
    else:
        increase = True 

    r = (deltan*n/length)**(1/(n-1))#initial value for r
    if abs(r - 1) < 1e-6:#uniform grid
        if debug > 0 :
            print "Warning! The inputs indicates a uniform grid!"
        i=0
    else:#nonuniform grid
        #newton-raphson iteration
        #solve for f(r) = (1-r^n)/((1-r)*r^(n-1)) - L/deltan = 0
        f = (1-r**n)/((1-r)*r**(n-1)) - length/deltan #f0
        for i in range(max_it):
            if debug == 2:
                print "iteration:",i
                print "r=",r
                print "residual:",f
            if abs(f) < convergence_rule:
                break
            f_prime = -1* (r**(-n)*(r**n-n*r+n-1)) / (1-r)**2
            r = r - f/f_prime #new r
            f = (1-r**n)/((1-r)*r**(n-1)) - length/deltan #new f
        if i == max_it-1:
            print "Warning!! Maximum iteration reached. Something was wrong!"
    if debug > 0 :
        print "#"*80
        print "result summary"
        print "iteration times:", i
        print "ratio between two adjacent cells, r = delta_{i+1} / delta_{i} = ", r
        print "ratio of size of last cell to first cell, delta_n/delta_1 =",r**(n-1)
        print "total number of cells along this edge, n =",n
        print "size of first cell:", deltan/(r**(n-1))
        print "size of last cell:", deltan

    return r

################################################################################
# user input starts here
#3 modes are available

#mode 1
#1.Input length, delta_1 and delta_n
#length is length of the edge
#delta_1 is size of first cell
#delta_n is size of last cell
#e.g. (uncomment and modifiy following 4 lines to use this mode)
#length=14.5
#delta_1=1.1428571
#delta_n=0.06
#get_r_given_delta1(delta_1,length,get_n(delta_1,delta_n,length,debug=1),debug=2)


################################################################################
#mode 2
#2.Input length, delta_1 and n 
#length is length of the edge
#delta_1 is size of first cell
#n is total number of cells along this edge
#e.g. (uncomment and modifiy following 4 lines to use this mode)
length=0.4
delta_1=0.01
n=20
get_r_given_delta1(delta_1,length,n,debug=1)


################################################################################
#mode 3
#3.Input length, delta_n and n 
#length is length of the edge
#delta_n is size of last cell
#n is total number of cells along this edge
#e.g. (uncomment and modifiy following 4 lines to use this mode)
#length=6
#delta_n=0.1
#n=120
#get_r_given_deltan(delta_n,length,n,debug = 2)

#user input ends here
################################################################################
