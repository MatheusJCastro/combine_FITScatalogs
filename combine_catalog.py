###################################################
# Combine Fits Catalog                            #
# Matheus J. Castro                               #
# Version 1.0                                     #
# Last Modification: 01/13/2020 (month/day/year)  #
###################################################

import numpy as np
import matplotlib.pyplot as plt
import manage_catalog as mancat
import time


def main(cat_name_1, cat_name_2, mag_to_use1="MAG_AUTO", mag_to_use2="MAG_AUTO", threshold=3,
         plot=False, plot_select=False, save_cross_match=False, save_plot=False,
         show_plot=True, c_cross_match=True, read_cross_match=False, extent1=2, extent2=2):
    # This function do the Cross_Match of two catalogs.
    # It returns a header of the results, the result catalog and then
    # the len of the two catalogs and how many objects were found.
    # threshold in arcseconds.
    inicio = time.time()

    right_ascension_column = "ALPHA_J2000"
    declination_column = "DELTA_J2000"
    c_code_name = "cross-match.so"

    data, elements = mancat.setup_catalog(cat_name_1, cat_name_2, ext1=extent1, ext2=extent2)

    ind_alpha = elements[0].index(right_ascension_column)
    ind_delta = elements[0].index(declination_column)

    mancat.save_all_obj(data, ind_alpha, ind_delta)
    mancat.execute_c(c_code_name, threshold)
    objects = mancat.read_c()
    mancat.del_temp_files()  # Delete the temporary files created because of C code

    # funcao para ver qual catalogo fica os dados
    mag_pos_list = mancat.combine_cat(data, objects)

    if save_cross_match:
        mancat.save_cross_match_csv(mag_pos_list, right_ascension_column, declination_column)

    fim = time.time()
    print("Time Python: ", fim - inicio)


cat_base = 'j02_rSDSS_21s.cat'
cat_1 = 'j02_rSDSS_2.1s_corrected.cat'
cat_2 = 'j02_rSDSS_0.21s_corrected.cat'
main(cat_base, cat_1, extent2=1)
