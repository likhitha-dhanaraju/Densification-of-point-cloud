#Libraries to be imported
import os
import util
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

#Variables to be set
data_dir = 'C:/Users/dell/Desktop/IISC/OBJ/Testing'
output_path = 'C:/Users/dell/Desktop/IISC/3D-point-cloud-generation/densify'
densifyN = 10000

filenames = [d for d in os.listdir(data_dir)]
# verify the argument is an stl file
objfilename = []
Densified_points = []
for j in filenames:
    file_lower = j.lower()
    if 'obj' in file_lower:
        objfilename.append(j)

for i in range(len(objfilename)):
    shape_file = os.path.join(data_dir,objfilename[i])
    V,E,F = util.parseObj(shape_file)
    F = util.removeWeirdDuplicate(F)
    Vorig,Eorig,Forig = V.copy(),E.copy(),F.copy()

    # sort by length (maintain a priority queue)
    Elist = list(range(len(E)))
    Elist.sort(key=lambda i:util.edgeLength(V,E,i),reverse=True)
    
    # create edge-to-triangle and triangle-to-edge lists
    EtoF = [[] for j in range(len(E))]
    FtoE = [[] for j in range(len(F))]
    for f in range(len(F)):
         v = F[f] 
         util.pushEtoFandFtoE(EtoF,FtoE,E,f,v[0],v[1])
         util.pushEtoFandFtoE(EtoF,FtoE,E,f,v[0],v[2])
         util.pushEtoFandFtoE(EtoF,FtoE,E,f,v[1],v[2])
    V,E,F = list(V),list(E),list(F)
         
    # repeat densification
    for z in range(densifyN):
        util.densify(V,E,F,EtoF,FtoE,Elist)
    densifyV = np.array(V[-densifyN:])
    
    x=densifyV[:,0]
    y=densifyV[:,1]
    z=densifyV[:,2]

    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.scatter(z, x, y, zdir='z', c= 'red')
    
    if i==0:
        Densified_points=densifyV
    else:   
        Densified_points=np.append(Densified_points,densifyV,axis = 0)

#Data to be saved
np.savez('saved_values',densification = densifyN, obj = objfilename)
#Saving the point cloud as npz file
np.savez('data.npz',points=Densified_points)
