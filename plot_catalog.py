###########################################
# Plot Fits Catalog                       #
# Matheus J. Castro                       #
# Version 2.4                             #
# Last Modification: 22/09/2019           #
###########################################

import matplotlib.pyplot as plt
import manage_catalog as mancat

catalog = mancat.cat_open('j02-20170711T001143-01_proc.proccat')

# save catalog in a csv file
# mancat.save_catalog(catalog, mancat.get_info(catalog)[1], mancat.get_header(catalog)[1])

# get info about catalog
# check the extension do you want to use, the default is 2.
# info = mancat.get_info(catalog)[0]

elements = mancat.get_header(catalog, extension=2)[0]  # elements of catalog
data = mancat.get_data(catalog, extension=2)  # data of catalog
mancat.close(catalog)

choose = True
if choose:
    print("Available options for plot:\n|", end="")
    for i in range(len(elements)):
        print("{:2}- {:{}}|".format(i+1, elements[i], len(max(elements, key=len))+1), end="")
        if (i+1) % 6 == 0:
            print("\n|", end="")
    print("")
    x, y = input("Enter chosen options separated by spaces (can be numbers or names): ").upper().split()

    if x.isnumeric():
        x_axis = elements[int(x)-1]
    else:
        x_axis = x

    if y.isnumeric():
        y_axis = elements[int(y)-1]
    else:
        y_axis = y
else:
    x_axis = "ALPHA_J2000"
    y_axis = "DELTA_J2000"
    # x_axis = "MAG_AUTO"
    # y_axis = "MAGERR_AUTO"

fmt = "png"
x_column = elements.index(x_axis)
y_column = elements.index(y_axis)

x_points = []
y_points = []
for i in range(len(data)):
    x_points.append(data[i][x_column])
    y_points.append(data[i][y_column])

plt.figure(figsize=(5, 5))
plt.xlabel(x_axis)
plt.ylabel(y_axis)
plt.title("{} and {}".format(x_axis, y_axis))
plt.plot(x_points, y_points, ".", markersize=1)
plt.savefig("Plot_{}_{}.{}".format(x_axis, y_axis, fmt), format=fmt)

plt.show()
