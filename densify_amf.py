import util_amf as U
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

densifyN = 2000

file = 'F:\\cube.amf'

obj_count,Vert,Fac_,Edg = U.parseAMF(file)

Points = []
for i in range(obj_count):
    V = Vert[i]
    E = Edg[i]
    F1 = Fac_[i]
    F = U.removeWeirdDuplicate(F1)
    Vorig,Eorig,Forig = V.copy(),E.copy(),F.copy()
    # sort by length (maintain a priority queue)
    Elist = list(range(len(E)))
    Elist.sort(key=lambda i:U.edgeLength(V,E,i),reverse=True)
    
    # create edge-to-triangle and triangle-to-edge lists
    EtoF = [[] for j in range(len(E))]
    FtoE = [[] for j in range(len(F))]
    
    for f in range(len(F)):
         v=F[f]
         U.pushEtoFandFtoE(EtoF,FtoE,E,f,v[0],v[1])
         U.pushEtoFandFtoE(EtoF,FtoE,E,f,v[0],v[2])
         U.pushEtoFandFtoE(EtoF,FtoE,E,f,v[1],v[2])
    V,E,F = list(V),list(E),list(F)
    
    # repeat densification
    for z in range(densifyN):
        U.densify(V,E,F,EtoF,FtoE,Elist)
    
    densifyV = np.array(V[-densifyN:])
    
    x=densifyV[:,0]
    y=densifyV[:,1]
    z=densifyV[:,2]

    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.scatter(z, x, y, zdir='z', c= 'red')
    
    Points.append(densifyV)

np.savez('data.npz',points=Points)