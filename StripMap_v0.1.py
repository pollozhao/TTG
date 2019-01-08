import numpy as np
import matplotlib.pyplot as plt

##########
#file config
##########
route_seg_data  = "Vaires-Blainville.csv"
output_pdf      = "foo_elevation.pdf"
map_title       = "Vaires - Blainville"
map_width       = 200
start_km        = "NA"
end_km          = "NA"
cross_elevation = 1
speed_mph       = 0

##########
#prepare route segment data
##########
SBx, SBy, ELRx, ELRy = [],[],[],[]
ex, ey = [],[]
cx, cy = [],[]
sx, sy = [],[]
kx, kname = [],[]
Pfx, Pfname, Px, px = [],[],[],[]
xx, xy, xname = [],[],[]

tstart, tend = {},{}

fin = open(route_seg_data)
for line in fin:
    line_temp = line.split(',')
    if line_temp[2] == "SB":
        SBx.append(line_temp[0])
        SBy.append(line_temp[3])
    elif line_temp[2] == "ELR":
        ELRx.append(line_temp[0])
        ELRy.append(line_temp[3])
    elif line_temp[2] == "e":
        ex.append(line_temp[0])
        ey.append(line_temp[3])
    elif line_temp[2] == "c":
        cx.append(line_temp[0])
        cy.append(line_temp[3])
    elif line_temp[2] == "s":
        sx.append(line_temp[0])
        sy.append(str(float(line_temp[3])))
    elif line_temp[2] == "f":
        if line_temp[4] == "Pf":
            Pfx.append(line_temp[0])
            Pfname.append(line_temp[5])
        elif line_temp[4] == "x":
            xx.append(line_temp[0])
            xname.append(line_temp[5])
        elif line_temp[4] == "k":
            kx.append(line_temp[0])
            kname.append(line_temp[5])
        elif line_temp[4] == "T":
            tstart[line_temp[5]] = line_temp[0]
        elif line_temp[4] == "t":
            tend[line_temp[5]] = line_temp[0]

#for t in tstart:
#    print(t, ' start at:', tstart[t], ' end at:', tend[t])

sx.insert(0,0)
sy.insert(0,sy[0])
sx.append(ex[len(ex)-1])
sy.append(sy[len(sy)-1])

ex.insert(0,0)
ey.insert(0,0)
ex.append(ex[len(ex)-1])
ey.append(0)

print('Total Distance (km):', ex[len(ex) - 1])


##########
#prepare map layer
##########
fig = plt.figure(figsize=(map_width, 7))

plt.xlabel('EM Distance (km)', size=12)
plt.ylabel(map_title, size=16)
plt.tick_params(axis='both', which='major', labelsize=10)

plt.xticks(np.arange(0, int(float(ex[len(ex) - 1])) + 1, 1))

ax = fig.add_subplot(111)
ax.patch.set_facecolor((0.678,0.847,0.902))
ax.patch.set_alpha(0.5)

ax.set_ylim(0,500)
ax.set_yticklabels([])
ax.tick_params(axis='both', direction='out')
ax.get_xaxis().tick_bottom() 
ax.get_yaxis().tick_left()

ax2 = ax.twinx()
ax2.set_ylim(0, 120)
ax2.set_yticks([])

##########
#plot strip map
##########

#draw elevation
ax.fill(ex, ey, color = (0.565,0.933,0.565), zorder = 1)

#draw speed
ax2.step(sx, sy, where="post", linestyle="-", linewidth=1, color="red", zorder = 2)

#add speed text
if speed_mph:
    for i in range(len(sx)-2):
        ax2.annotate(int(float(sy[i+1])/1.609), size='x-small', color='red', xy=(sx[i+1], sy[i+1]),  xycoords='data',
                    xytext=(1, 2), textcoords='offset points')
else:
    for i in range(len(sx)-2):
        ax2.annotate(int(float(sy[i+1])), size='x-small', color='red', xy=(sx[i+1], sy[i+1]),  xycoords='data',
                    xytext=(1, 2), textcoords='offset points')
#draw Pf
ax.scatter(Pfx, [5] * len(Pfx), s = 100, marker = 's', color = 'black', zorder = 3)

#add Pf name text
for i in range(len(Pfx)):
    ax.annotate(Pfname[i], size='xx-small', color='black', xy=(Pfx[i], 10),  xycoords='data',
                xytext=(0, 2), textcoords='offset points', horizontalalignment = 'center')

#draw x
for i in range(len(xx)):
    xy.append(ey[ex.index(min(ex, key=lambda x:abs(float(x)-float(xx[i]))))])
    
if cross_elevation:
    ax.scatter(xx, xy, s = 100, marker = (5,2,180), color = 'black', zorder = 4)
else:
    ax.scatter(xx, [10]*len(xx), s = 100, marker = (5,2,180), color = 'black', zorder = 4)

#add x name text
if cross_elevation:
        for i in range(len(xx)):
            ax.annotate(xname[i], size='xx-small', rotation=45, color='black', xy=(xx[i], xy[i]),  xycoords='data',
                xytext=(0, 2), textcoords='offset points', horizontalalignment = 'left', verticalalignment = 'bottom')
else:
    for i in range(len(xx)):
        ax.annotate(xname[i], size='xx-small', rotation=45, color='black', xy=(xx[i], 20),  xycoords='data',
                xytext=(0, 2), textcoords='offset points', horizontalalignment = 'left', verticalalignment = 'bottom')

#draw T
for t in tstart:
    ax.fill([tstart[t],tend[t],tend[t],tstart[t]],[0,0,30,30], fill=False, hatch='/////',
            edgecolor='grey', zorder = 5)
        
#add T name text
for t in tstart:
    ax.annotate(t, size='xx-small', color='black', xy=((float(tstart[t])+float(tend[t]))/2, 30),  xycoords='data',
                xytext=(0, 5), textcoords='offset points', horizontalalignment = 'center')

#draw km post line
for km in kx:
    ax.plot([km,km], [0,500], color='0.75', zorder = 2)

#add km post text
for i in range(len(kx)):
    ax.annotate(kname[i], size=10, color='black', xy=(kx[i], 500),  xycoords='data',
                xytext=(0, 5), textcoords='offset points', horizontalalignment = 'center')



if start_km == "NA":
    start_km = float("0")
if end_km == "NA":
    end_km = float(ex[len(ex) - 1])

plt.xlim((start_km,end_km))
plt.tight_layout(2.5)
plt.subplots_adjust(top=0.9, bottom=0.15)
plt.savefig(output_pdf)
print(output_pdf," saved~~!")
