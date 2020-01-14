###################################################
# Combine Fits Catalog                            #
# Matheus J. Castro                               #
# Version 2.1                                     #
# Last Modification: 01/14/2020 (month/day/year)  #
###################################################

import numpy as np
from astropy.table import Table
import manage_catalog as mancat
import time


def main(cat_name_1, cat_name_2, first_combine=0, threshold=3, mag_to_use1="MAG_AUTO", mag_to_use2="MAG_AUTO",
         save_cross_match=False, extent1=2, extent2=2):
    inicio = time.time()

    right_ascension_column = "ALPHA_J2000"
    declination_column = "DELTA_J2000"
    c_code_name = "cross-match.so"

    data, elements = mancat.setup_catalog(cat_name_1, cat_name_2, ext1=extent1, ext2=extent2)

    if first_combine != 0:
        data = [first_combine, data[1]]

    ind_alpha = elements[0].index(right_ascension_column)
    ind_delta = elements[0].index(declination_column)

    mancat.save_all_obj(data, ind_alpha, ind_delta)
    mancat.execute_c(c_code_name, threshold, changedot=0)
    objects = mancat.read_c()
    mancat.del_temp_files()  # Delete the temporary files created because of C code

    # Function used to replace the MAG_AUTO to MAG_AUTO_CORRECTED
    data = mancat.replace_mag_corrected(data, mag_to_use1, mag_to_use2)

    # Function to combine the catalogs
    final_cat = mancat.combine_cat(elements, data, objects)

    if save_cross_match:
        hd = "Number, X_IMAGE, Y_IMAGE, MAG_AUTO, MAGGER_AUTO, FLAGS, FLAGS_WEIGHT, FWHM_IMAGE, " \
             "BACKGROUND, ALPHA_J2000, DELTA_J2000"
        mancat.save_cross_match_csv(final_cat, head=hd)

    fim = time.time()
    print("Time Python: ", fim - inicio)

    return final_cat


cat_base = 'j02_rSDSS_21s.cat'
cat_1 = 'j02_rSDSS_2.1s_corrected.cat'
cat_2 = 'j02_rSDSS_0.21s_corrected.cat'
cat_combined = main(cat_base, cat_1, extent2=1, mag_to_use2="MAG_AUTO_CORRECTED")
cat_combined = main(cat_base, cat_2, first_combine=cat_combined, save_cross_match=True, extent2=1,
                   # mag_to_use2="MAG_AUTO_CORRECTED")
#a = np.array(cat_combined[0][3])
#print(a)  #.write("j02_rSDSS_teste.csv", format="csv")
#print(a.shape)
#print(a.ndim)


# Apagar objetos com flag > que 4?
# Se a flag for igual, verifica a magerr e fica a com menor erro?
# Mostrar grafico topcat_x_python
# Cade o plato dos graficos pro threshold?
