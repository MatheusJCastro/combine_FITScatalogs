###################################################
# Find the best radius for a Cross-Match          #
# Matheus J. Castro                               #
# Version 1.3                                     #
# Last Modification: 01/12/2020 (month/day/year)  #
###################################################

import numpy as np
import matplotlib.pyplot as plt
import cross_match_catalog as cross_cat
import time


def plot_radius(radius, arcsec, step_show=1, save=False, show=False):

    plt.figure(figsize=(5, 5))
    plt.grid(True)
    plt.xticks(np.arange(0, max(arcsec)+1, step_show))
    plt.xlim(0, max(arcsec))
    plt.xlabel("Radius Used (arcsec)")
    plt.ylabel("Founded Objects")
    plt.title("Founded Objects for each Search Radius")
    plt.plot(arcsec, radius, ".", markersize=5, color="blue")

    if save:
        fmt = "png"
        plt.savefig("Best_Radius.{}".format(fmt), format=fmt)
    if show:
        plt.show()


def main(cat_name_1, cat_name_2, init, end, step, show_plot=False, save_plot=False):
    inicio = time.time()
    founded = []
    search_radius = np.arange(init, end+step, step)
    for i in search_radius:
        print("Starting measure {}".format(i))
        result = cross_cat.main(cat_name_1, cat_name_2, threshold=i, extent2=1)[2]
        # Receives only the len of the two catalogs and how many objects were found.
        founded.append(result[2])

        print("\033[1;30;41mProgress {}%\033[0;0;0m".format((i/end)*100))
        partial = time.time()
        print("Total time spent: {:.2f}s".format(partial - inicio))

    fim = time.time()
    print("\033[1;97;42mTime spent to find best radius: {:.2f}s\033[0;0;0m".format(fim - inicio))

    plot_radius(founded, search_radius, show=show_plot, save=save_plot)


cat_base = 'j02_rSDSS_21s.cat'
cat_1 = 'j02_rSDSS_2.1s_corrected.cat'
cat_2 = 'j02_rSDSS_0.21s_corrected.cat'

init_thresh = 0.25
end_thresh = 10
step_size = 0.25
main(cat_base, cat_1, init_thresh, end_thresh, step_size, show_plot=True, save_plot=False)
