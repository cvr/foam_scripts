#!/usr/bin/python

def get_n(delta1,deltan,length):
    print "call get_n()"
    #given delta1 (size of 1st cell), deltan (size of last cell) and length of the domain
    #giving it a guess of n can accelerate the computation
    #return number of cells, n
    #deltan may be slightly different from given value

    deltan = float(deltan)
    delta1 = float(delta1)
    length = float(length)
    n = length*2/(delta1+deltan)
    r1 = deltan/delta1
    max_it = 100000
    convergence_rule = 0.001

    lhs = delta1*(1-r1**(n/(n-1)))/(1-r1**(1/(n-1)))
    for i in range(max_it):
        residual = (length-lhs)/length
        #add upper and lower bound for residual in case the iteration oscillate too much
        if residual > 0.1:
            residual = 0.1
        if residual < -0.1:
            residual = -0.1
        #print "residual:",residual
        #print "n=",n
        if abs(residual) < convergence_rule:
            break
        n=(1+residual)*n
        lhs = delta1*(1-r1**(n/(n-1)))/(1-r1**(1/(n-1)))

    return int(round(n))#round n into a integer

def get_r_given_delta1(delta1,length,n):
    print "call get_r_given_delta1"
    #return ratio between two adjacent cells, r = delta_{i+1} / delta_{i}
    #solve delta1*(1-r^n)/(1-r) = length to get r

    delta1 = float(delta1)
    length = float(length)
    n = float(n)
    max_it = 100000
    convergence_rule = 0.0001
    if length/n > delta1:#cell size is increasing from left to right 
        increase = True
    else:
        increase = False
    r = (length/n/delta1)**(1/(n-1))#initial value for r

    lhs = delta1*(1-r**n)/(1-r)
    for i in range(max_it):
        residual = (length-lhs)/length
        #add upper and lower bound for residual in case the iteration oscillate too much
        if residual > 0.1:
            residual = 0.1
        if residual < -0.1:
            residual = -0.1
        #print "iteration:",i+1
        #print "r=",r
        #print "residual:",residual
        if abs(residual) < convergence_rule:
            break
        r=(1+residual)*r
        lhs = delta1*(1-r**n)/(1-r)


    print "#"*80
    print "result summary"
    print "iteration times:", i
    print "ratio between two adjacent cells, r = delta_{i+1} / delta_{i} = ", r
    print "ratio of size of last cell to first cell, delta_n/delta_1 =",r**(n-1)
    print "total number of cells along this edge, n =",n
    print "size of first cell:", delta1
    print "size of last cell:", delta1*r**(n-1)

    return r
       

def get_r_given_deltan(deltan,length,n):
    print "call get_r_given_deltan"
    #return ratio between two adjacent cells, r = delta_{i+1} / delta_{i}
    #solve deltan*(1-r^n)/((1-r)*r^{n-1}) = length to get r

    delta1 = float(deltan)
    length = float(length)
    n = float(n)
    max_it = 10000 
    convergence_rule = 0.001
    if length/n > deltan:#cell size is increasing from left to right 
        increase = False 
    else:
        increase = True 
    r = (deltan*n/length)**(1/(n-1))#initial value for r

    lhs = deltan*(1-r**n)/(1-r)/r**(n-1)
    for i in range(max_it):
        residual = (length-lhs)/length
        #add upper and lower bound for residual in case the iteration oscillate too much
        if residual > 0.2:
            residual = 0.2
        if residual < -0.2:
            residual = -0.2
        #print "iteration:",i+1
        #print "r=",r
        #print "residual:",residual
        if abs(residual) < convergence_rule:
            break
        r=(1-residual)*r
        lhs = deltan*(1-r**n)/(1-r)/r**(n-1)

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
#1.given length, delta_1 and delta_n
#length is length of the edge
#delta_1 is size of first cell
#delta_n is size of last cell
#uncomment the lines below to compute
length=100
delta_1=1
delta_n=10
get_r_given_delta1(delta_1,length,get_n(delta_1,delta_n,length))


################################################################################
#2.given length, delta_1 and n 
#length is length of the edge
#delta_1 is size of first cell
#n is total number of cells along this edge
#length=100
#delta_1=1
#n=25
#get_r_given_delta1(delta_1,length,n)


################################################################################
#3.given length, delta_n and n 
#length is length of the edge
#delta_n is size of last cell
#n is total number of cells along this edge
#length=100
#delta_n=10
#n=25
#get_r_given_deltan(delta_n,length,n)
