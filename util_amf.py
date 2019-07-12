import numpy as np

def parseAMF(file):
    obj_count=0
    no_line =0
    obj_id = []
    contents,start_v,end_v =[],[],[]
    start_f,end_f=[],[]
    start_vi,end_vi =[],[]
    start_fi,end_fi=[],[]
    edge,edges =[],[]
    obj_flag=0
    with open(file) as file_:
    #Finding the number of objects and starting and ending indices of the points list
        for line in file_:
            contents.append(line)
            no_line=no_line+1
            if 'object id' in line:
                split = line.index("=")
                obj_id.append(line[split+2])
                obj_count=obj_count+1
                obj_flag=1
            if '<coordinates>' in line and obj_flag==1:
                start_v.append(no_line)
            if '</coordinates>' in line and obj_flag==1:
                end_v.append(no_line)
            if '<triangle>' in line and obj_flag==1:
                start_f.append(no_line)
            if '<color>' in line and obj_flag==1:
                end_f.append(no_line)
            if '</object>' in line:
                obj_flag=0
                start_vi.append(np.array(start_v))
                end_vi.append(np.array(end_v))
                start_fi.append(np.array(start_f))
                end_fi.append(np.array(end_f))
                start_v,end_v,start_f,end_f=[],[],[],[]
    
    p,f,pts,fcs=[],[],[],[]
    for a in range(obj_count):
        for b in range(len(start_vi[a])):
            p.append(contents[(start_vi[a])[b]:(end_vi[a])[b]-1])
        for c in range(len(start_fi[a])):
            if (end_fi[a])[c] -  (start_fi[a])[c] == 4:
                f.append(contents[(start_fi[a])[c]:(end_fi[a])[c]-1])
            else:
                f.append(contents[(start_fi[a])[c]:(end_fi[a])[c]-7])
        pts.append(p)
        fcs.append(f)
        p,f=[],[]
        vertices=[]
        for d in range(len(pts[a])):
            x_=((pts[a])[d])[0].split("<x>")[1]
            y_=((pts[a])[d])[1].split("<y>")[1]
            z_=((pts[a])[d])[2].split("<z>")[1]
            x=float(x_.split("</x>")[0])
            y=float(y_.split("</y>")[0])
            z=float(z_.split("</z>")[0])
            vertices.append([x,y,z])            
        pts[a]=np.array(vertices)
        faces=[]
        for e in range(len(fcs[a])):
            x_f=((fcs[a])[e])[0].split("<v1>")[1]
            y_f=((fcs[a])[e])[1].split("<v2>")[1]
            z_f=((fcs[a])[e])[2].split("<v3>")[1]
            xf = int(x_f.split("</v1>")[0])
            yf = int(y_f.split("</v2>")[0])
            zf = int(z_f.split("</v3>")[0])
            faces.append(np.array([xf,yf,zf]))
        fcs[a]=np.array(faces)
            
        for g in fcs[a]:
            edge.append([min(g[0],g[1]),max(g[0],g[1])])
            edge.append([min(g[0],g[2]),max(g[0],g[2])])
            edge.append([min(g[1],g[2]),max(g[1],g[2])])
        edge = [list(s) for s in set([tuple(e) for e in edge])]
        edge = np.array(edge)
        edges.append(edge)
        edge=[]
        
    return obj_count,pts,fcs,edges

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
