###################################################
# Cross-Match Fits Catalog                        #
# Matheus J. Castro                               #
# Version 6.5                                     #
# Last Modification: 01/12/2020 (month/day/year)  #
###################################################

import numpy as np
import matplotlib.pyplot as plt
import manage_catalog as mancat
import time


def plot_selected(data, ar, dc, ind_ar, ind_dc, save=False, show=False):
    x_position_1 = []
    y_position_1 = []
    x_position_1_c = []
    y_position_1_c = []
    x_position_2 = []
    y_position_2 = []

    cat1_eu = [8186-1]
    cat1_cat = [8199-1]
    cat2 = [7713-1]

    # cat1 = [1392, 2703, 5717]
    # cat2 = [829, 1626, 3345]

    for i in cat1_eu:
        x_position_1.append(data[0][i][ind_ar])
        y_position_1.append(data[0][i][ind_dc])
    for i in cat1_cat:
        x_position_1_c.append(data[0][i][ind_ar])
        y_position_1_c.append(data[0][i][ind_dc])
    for i in cat2:
        x_position_2.append(data[1][i][ind_ar])
        y_position_2.append(data[1][i][ind_dc])

    error = np.asarray([3/(60**2)]*len(y_position_2))

    plt.figure(figsize=(5, 5))
    plt.xlabel(ar)
    plt.ylabel(dc)
    plt.xlim(56, 57.8)
    plt.ylim(23.3, 24.9)
    plt.title("{} and {}".format(ar, dc))
    # plt.errorbar(x_position_1, y_position_1, yerr=error, xerr=error, fmt="none")
    plt.errorbar(x_position_2, y_position_2, yerr=error, xerr=error, fmt="none")
    plt.plot(x_position_1, y_position_1, ".", markersize=5, color="black")
    plt.plot(x_position_1_c, y_position_1_c, ".", markersize=5, color="green")
    plt.plot(x_position_2, y_position_2, ".", markersize=5, color="blue")

    if save:
        fmt = "png"
        plt.savefig("Plot_Mags.{}".format(fmt), format=fmt)
    if show:
        plt.show()


def plot_mags(listofmag, ar, dc, save=False, show=False):
    x_axis = "MAGS of CAT 1"
    y_axis = "MAGS of CAT 2"

    x_points = []
    y_points = []
    x_position = []
    y_position = []
    for i in range(len(listofmag)):
        if listofmag[i][5] <= 30 and listofmag[i][6] <= 30:
            x_points.append(listofmag[i][5])
            y_points.append(listofmag[i][6])
        x_position.append(listofmag[i][3])
        y_position.append(listofmag[i][4])

    xmax = int(max(x_points)) + 1
    xmin = int(min(x_points)) - 1
    ymax = int(max(y_points)) + 1
    ymin = int(min(y_points)) - 1

    if xmax < ymax:
        xmax = ymax
    if xmin > ymin:
        xmin = ymin

    plt.figure(figsize=(12, 5))

    plt.subplot(121)
    plt.xlim(xmin, xmax)
    plt.ylim(xmin, xmax)
    plt.xlabel(x_axis)
    plt.ylabel(y_axis)
    plt.title("{} and {}".format(x_axis, y_axis))
    plt.plot(x_points, y_points, ".", markersize=5)
    plt.plot([xmin, xmax], [xmin, xmax], "-", markersize=5)

    plt.subplot(122)
    plt.xlabel(ar)
    plt.ylabel(dc)
    plt.title("{} and {}".format(ar, dc))
    plt.plot(x_position, y_position, ".", markersize=5)

    if save:
        fmt = "png"
        plt.savefig("Plot_Variation_of_Mags.{}".format(fmt), format=fmt)
    if show:
        plt.show()


def main(cat_name_1, cat_name_2, mag_to_use="MAG_AUTO", threshold=3,
         plot=False, plot_select=False, save_cross_match=False, save_plot=False,
         show_plot=True, c_cross_match=True, read_cross_match=False):
    # This function do the Cross_Match of two catalogs.
    # It returns a header of the results, the result catalog and then
    # the len of the two catalogs and how many objects were found.
    # threshold in arcseconds.
    inicio = time.time()

    csv_to_read = "Magnitudes_compared.csv"
    right_ascension_column = "ALPHA_J2000"
    declination_column = "DELTA_J2000"
    c_code_name = "cross-match.so"

    data, elements = mancat.setup_catalog(cat_name_1, cat_name_2)

    ind_alpha = elements[0].index(right_ascension_column)
    ind_delta = elements[0].index(declination_column)

    if c_cross_match:
        mancat.save_all_obj(data, ind_alpha, ind_delta)
        founded = mancat.execute_c(c_code_name, threshold)
        objects = mancat.read_c()
        mancat.del_temp_files()  # Delete the temporary files created because of C code
    elif read_cross_match:
        objects = mancat.read_cross_match_csv(csv_to_read)
        founded = len(objects)
    else:
        objects = mancat.find_index(data, ind_alpha, ind_delta)
        founded = len(objects)

    mag_pos_list = mancat.get_mag(data, elements, mag_to_use, objects, ind_alpha, ind_delta)[1]

    if save_cross_match:
        mancat.save_cross_match_csv(mag_pos_list, right_ascension_column, declination_column)

    fim = time.time()
    print("Time Python: ", fim - inicio)

    if plot:
        plot_mags(mag_pos_list, right_ascension_column, declination_column, save_plot, show_plot)
    elif plot_select:
        plot_selected(data, right_ascension_column, declination_column, ind_alpha, ind_delta, save_plot, show_plot)

    head = "Number, Number_1, Number_2, " + right_ascension_column + ", " + declination_column + \
           ", MAG_CAT_1, MAG_CAT_2"
    return head, mag_pos_list, (len(data[0]), len(data[1]), founded)


# To run this code independently, uncomment the follow lines:
cat_1 = 'j02-20151112T005311-01_proc.proccat'
cat_2 = 'j02-20151112T010354-01_proc.proccat'
main(cat_1, cat_2, threshold=3, plot=True)
