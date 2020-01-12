###################################################
# Find the best radius for a Cross-Match          #
# Matheus J. Castro                               #
# Version 1.0                                     #
# Last Modification: 01/12/2020 (month/day/year)  #
###################################################

import numpy as np
import matplotlib.pyplot as plt
import cross_match_catalog as cross_cat
import time


def plot_radius(radius, arcsec, save=False, show=False):

    plt.figure(figsize=(5, 5))
    plt.xlabel("Radius Used (arcsec)")
    plt.ylabel("Founded Objects")
    # plt.xlim(56, 57.8)
    # plt.ylim(23.3, 24.9)
    plt.title("Founded Objects for each Search Radius")
    plt.plot(arcsec, radius, ".", markersize=5, color="blue")

    save=True
    show=True

    if save:
        fmt = "png"
        plt.savefig("Best_Radius.{}".format(fmt), format=fmt)
    if show:
        plt.show()


def main(cat_name_1, cat_name_2, init, end, step):
    inicio = time.time()
    founded = []
    search_radius = np.arange(init, end+step, step)
    for i in search_radius:
        print("Starting measure {}".format(i))
        result = cross_cat.main(cat_name_1, cat_name_2, threshold=i)[2]
        # Receives only the len of the two catalogs and how many objects were found.
        founded.append(result[2])

        print("\033[1;30;41mProgress {}%\033[0;0;0m".format((i/end)*100))
        partial = time.time()
        print("Total time spent: {:.2f}s".format(partial - inicio))

    print(founded)
    fim = time.time()
    print("\033[1;97;42mTime spent to find best radius: {:.2f}s\033[0;0;0m".format(fim - inicio))

    plot_radius(founded, search_radius)


cat_1 = 'j02-20151112T005311-01_proc.proccat'
cat_2 = 'j02-20151112T010354-01_proc.proccat'

init_thresh = 0.25
end_thresh = 10
step_size = 0.25
main(cat_1, cat_2, init_thresh, end_thresh, step_size)
