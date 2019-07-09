import numpy as np
# parse vertices
def parseVRML(file):
    obj_count=0
    no_line =0
    contents,start_v,end_v =[],[],[]
    start_f,end_f=[],[]
    vertex,edge,edges = [],[],[]
    flag1,flag2=0,0
    with open(file) as file_:
    #Finding the number of objects and starting and ending indices of the points list
        for line in file_:
            contents.append(line)
            no_line=no_line+1
            if 'point' in line:
                obj_count = obj_count+1
                start_v.append(no_line)
                flag1=1
            if ']' in line and flag1==1:
                end_v.append(no_line)
                flag1=0
            if 'coordIndex [' in line:
                start_f.append(no_line)
                flag2=1
            if ']' in line and flag2==1:
                end_f.append(no_line)
                flag2=0
                
    """
    Start indices will be the (number) in the list - 'start',
     whereas the ending list will be (number-2) in the list = 'end'
     
    """
    
    #making a list of all the points
    points=[]
    faces=[]
    for j in range(obj_count):
        start_1 = start_v[j]
        end_1 = end_v[j] - 1
        start_2 = start_f[j]
        end_2 = end_f[j] - 1
        points.append(contents[start_1:end_1])
        faces.append(contents[start_2:end_2])
        
    #point size of all the objects
    #points_size=[len(a) for a in points]
    #faces_size = [len(a) for a in faces]
    numbers = []
    values=[]
    checklist=[]
    for i in range(obj_count):
        temp_obj,vertex,numbers=[],[],[]
        temp_obj2,checklist,values=[],[],[]
        temp_obj = points[i]
        for j in temp_obj:
            a = j.strip().split(", ")
            for k in a:
                numbers.append(k.strip().split(" "))
        #removing the commas in some last members - POINTS
        for a in range(len(numbers)):
            if ',' in (numbers[a])[2]:
                b = (numbers[a])[2].strip().split(",")
                (numbers[a])[2]=b[0]
            vertex.append([float((numbers[a])[0]),float((numbers[a])[1]),float((numbers[a])[2])])
        points[i]=np.array(vertex)
        temp_obj2 = faces[i]
        for j in temp_obj2:
            a = j.strip().split(", -1,")
            for k in a:
                values.append(k.strip().split(" "))
        #removing the commas in first two members - FACES
        for c in range(len(values)):
            for e in range(len(values[c])):
                if ',' in (values[c])[e]:
                    d = (values[c])[e].strip().split(",")
                    (values[c])[e]=d[0]
            if np.size(values[c])==3:
                checklist.append([int((values[c])[0]),
                                      int((values[c])[1]),int((values[c])[2])])
        for e in checklist:
            idx1,idx2,idx3 = e[0],e[1],e[2]
            M=[(points[i])[idx1],(points[i])[idx2],(points[i])[idx3]]
            if np.linalg.matrix_rank(M)==3:
                faces[i]=np.array(checklist)
                
        for f in faces[i]:
            edge.append([min(f[0],f[1]),max(f[0],f[1])])
            edge.append([min(f[0],f[2]),max(f[0],f[2])])
            edge.append([min(f[1],f[2]),max(f[1],f[2])])
        edge = [list(s) for s in set([tuple(e) for e in edge])]
        edge = np.array(edge)
        edges.append(edge)
        edge=[]
        
    return obj_count,points,faces,edges

def removeWeirdDuplicate(F):
    F.sort(axis=1)
    F = [f for f in F]
    F.sort(key=lambda x:[x[0],x[1],x[2]])
    N = len(F)
    for i in range(N-1,-1,-1):
        if F[i][0]==F[i-1][0] and F[i][1]==F[i-1][1] and F[i][2]==F[i-1][2]:
            F.pop(i)
    F=np.array(F)
    return F

def edgeLength(V,E,i):
	return np.linalg.norm(V[E[i][0]]-V[E[i][1]])

def pushEtoFandFtoE(EtoF,FtoE,E,f,v1,v2):
	if v1>v2: v1,v2 = v2,v1
	e = np.where(np.all(E==[v1,v2],axis=1))[0][0]
	EtoF[e].append(f)
	FtoE[f].append(e)
    
def pushAndSort(Elist,V,E,ei):
	l = edgeLength(V,E,ei)
	if l>edgeLength(V,E,Elist[0]):
		Elist.insert(0,ei)
	else:
		left,right = 0,len(Elist)
		while left+1<right:
			mid = (left+right)//2
			if edgeLength(V,E,ei)>edgeLength(V,E,Elist[mid]):
				right = mid
			else:
				left = mid
		Elist.insert(left+1,ei)

def densify(V,E,F,EtoF,FtoE,Elist):
	vi_new = len(V)
	ei_new = len(E)
	# longest edge
	eL = Elist.pop(0)
	# create new vertex
	vi1,vi2 = E[eL][0],E[eL][1]
	v_new = (V[vi1]+V[vi2])/2
	V.append(v_new)
	# create new edges
	e_new1 = np.array([vi1,vi_new])
	e_new2 = np.array([vi2,vi_new])
	E.append(e_new1)
	E.append(e_new2)
	EtoF.append([])
	EtoF.append([])
	# push Elist and sort
	pushAndSort(Elist,V,E,ei_new)
	pushAndSort(Elist,V,E,ei_new+1)
	# create new triangles
	for f in EtoF[eL]:
		fi_new = len(F)
		vio = [i for i in F[f] if i not in E[eL]][0]
		f_new1 = np.array([(vi_new if i==vi2 else i) for i in F[f]])
		f_new2 = np.array([(vi_new if i==vi1 else i) for i in F[f]])
		F.append(f_new1)
		F.append(f_new2)
		e_new = np.array([vio,vi_new])
		E.append(e_new)
		EtoF.append([])
		e_out1 = [e for e in FtoE[f] if min(E[e][0],E[e][1])==min(vi1,vio) and
										max(E[e][0],E[e][1])==max(vi1,vio)][0]
		e_out2 = [e for e in FtoE[f] if min(E[e][0],E[e][1])==min(vi2,vio) and
										max(E[e][0],E[e][1])==max(vi2,vio)][0]
		# update EtoF and FtoE
		EtoF[e_out1] = [(fi_new if fi==f else fi) for fi in EtoF[e_out1]]
		EtoF[e_out2] = [(fi_new+1 if fi==f else fi) for fi in EtoF[e_out2]]
		EtoF[ei_new].append(fi_new)
		EtoF[ei_new+1].append(fi_new+1)
		EtoF[-1] = [fi_new,fi_new+1]
		FtoE.append([(e_out1 if i==e_out1 else ei_new if i==eL else len(EtoF)-1) for i in FtoE[f]])
		FtoE.append([(e_out2 if i==e_out2 else ei_new+1 if i==eL else len(EtoF)-1) for i in FtoE[f]])
		FtoE[f] = []
		pushAndSort(Elist,V,E,len(EtoF)-1)
	# # # delete old edge
	E[eL] = np.ones_like(E[eL])*np.nan
	EtoF[eL] = []
	# delete old triangles
	for f in EtoF[eL]:
		F[f] = np.ones_like(F[f])*np.nan
