import util
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import scipy.io as sio

densifyN = 200000

output_path = '/media/mancmanomyst/D6B7-3CAD/Surface reconstruction matlab'
shape_file = '/media/mancmanomyst/D6B7-3CAD/Surface reconstruction matlab/bed.obj'
V,E,F_ = util.parseObj(shape_file)
F = util.removeWeirdDuplicate(F_)
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
plt.savefig("demo.png")

output_file= {
		"V": Vorig,
		"E": Eorig,
		"F": Forig,
		"Vd": densifyV
	}

x=densifyV[:,0]
y=densifyV[:,1]
z=densifyV[:,2]
points = {
        "x":x,
        "y":y,
        "z":z
    }
sio.savemat("bed.mat",{
		"V": Vorig,
		"E": Eorig,
		"F": Forig,
		"Vd": densifyV
	})
  
np.savetxt('bed.txt',densifyV)

pcd = o3d.geometry.PointCloud()
pcd.points = o3d.utility.Vector3dVector(densifyV)

o3d.io.write_point_cloud('bed.ply',pcd)

# Load saved point cloud and visualize it
pcd_load = o3d.io.read_point_cloud("bed.ply")
o3d.visualization.draw_geometries([pcd_load])
