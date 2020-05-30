###################################################
# Combine Fits Catalog                            #
# Matheus J. Castro                               #
# Version 3.1                                     #
# Last Modification: 05/29/2020 (month/day/year)  #
###################################################

import manage_catalog as mancat
import numpy as np
import time
import sys
import os


def combine(cat_name_1, cat_name_2, first_combine=0, threshold=3, mag_to_use1="MAG_AUTO", mag_to_use2="MAG_AUTO",
            right_ascension_column="ALPHA_J2000", declination_column="DELTA_J2000", save_cross_match=0, extent1=2,
            extent2=2):
    inicio = time.time()

    data, elements = mancat.setup_catalog(cat_name_1, cat_name_2, ext1=extent1, ext2=extent2)

    # data = data[0][0:10], data[1][0:10]  # Just to test (debug) more fast

    # Reorder the catalogs using the base catalog as reference
    data = mancat.reorder_cats(data, elements, mag_to_use1, mag_to_use2)

    if first_combine != 0:
        data = [first_combine, data[1]]

    # Get the indexes from each column in the header of the catalogs
    ind_alpha = elements[0].index(right_ascension_column)
    ind_delta = elements[0].index(declination_column)

    ##################################################################################
    # C Execution
    c_code_name = "cross-match.so"
    mancat.save_all_obj(data, ind_alpha, ind_delta)
    mancat.execute_c(c_code_name, threshold, changedot=0)
    objects = mancat.read_c()
    mancat.del_temp_files()  # Delete the temporary files created because of C code
    ##################################################################################

    # Function used to replace the MAG_AUTO to MAG_AUTO_CORRECTED
    if mag_to_use1 != mag_to_use2:
        data[1] = mancat.replace_mag_corrected(data[1], mag_to_use1, mag_to_use2)

    # Function to combine the catalogs
    final_cat = mancat.combine_cat(elements, data, objects)

    if save_cross_match != 0:
        cat_to_save = []
        for i in final_cat:
            cat_to_save.append(i.tolist())

        if save_cross_match == 1 or save_cross_match == 3:
            mancat.save_cross_match_cat(cat_to_save, head=elements[0])
        if save_cross_match == 2 or save_cross_match == 3:
            hd = "Number, X_IMAGE, Y_IMAGE, MAG_AUTO, MAGGER_AUTO, FLAGS, FLAGS_WEIGHT, FWHM_IMAGE, " \
                 "BACKGROUND, ALPHA_J2000, DELTA_J2000"
            mancat.save_cross_match_csv(cat_to_save, head=hd)

    fim = time.time()
    print("Time Python: ", fim - inicio)

    return final_cat


def main(cats_names, save, thresh, exten, exten_def, ra, dc, mags, mag_def):
    inicio_global = time.time()

    # cats_names = ['j02_rSDSS_21s.cat', 'j02_rSDSS_2.1s_corrected.cat', 'j02_rSDSS_0.21s_corrected.cat']

    for i in range(len(cats_names)):
        if i < len(exten) and exten[i] == 0:
            exten[i] = exten_def
        else:
            exten.append(exten_def)
        if i < len(mags) and mags[i] == 0:
            mags[i] = mag_def
        else:
            mags.append(mag_def)

    cat_combined = 0
    for i in range(1, len(cats_names)):
        print("############### ITERATION {} ###############".format(i))
        cat_combined = combine(cats_names[0], cats_names[i], extent1=exten[0], extent2=exten[i],
                               mag_to_use1=mags[0], mag_to_use2=mags[i], save_cross_match=save,
                               right_ascension_column=ra, declination_column=dc,
                               first_combine=cat_combined, threshold=thresh)

    print("################### END ###################")
    fim_global = time.time()
    print("Total Time: ", fim_global - inicio_global)


def args_menu(args):

    if len(args) != 0 and not any((i == "-h" or i == "--h" or i == "-help" or i == "--help") for i in args):
        if any(i == "-s" for i in args):
            ind = args.index("-s") + 1
            try:
                save = int(args[ind])
            except ValueError:
                sys.exit("\033[1;31mError: Argument for -s not valid.\033[m")
            del args[ind]
            args.remove("-s")
        else:
            save = 0
        if any(i == "-t" for i in args):
            ind = args.index("-t") + 1
            try:
                thresh = float(args[ind])
            except ValueError:
                sys.exit("\033[1;31mError: Argument for -t not valid.\033[m")
            del args[ind]
            args.remove("-t")
        else:
            thresh = 3
        if any(i == "-e" for i in args):
            ind = args.index("-e") + 1
            try:
                exten = list(map(int, args[ind].split(",")))
            except ValueError:
                sys.exit("\033[1;31mError: Argument for -e not valid.\033[m")
            del args[ind]
            args.remove("-e")
        else:
            exten = [0]
        if any(i == "-ep" for i in args):
            ind = args.index("-ep") + 1
            try:
                exten_def = int(args[ind])
            except ValueError:
                sys.exit("\033[1;31mError: Argument for -ep not valid.\033[m")
            del args[ind]
            args.remove("-ep")
        else:
            exten_def = 1
        if any(i == "-ra" for i in args):
            ind = args.index("-ra") + 1
            ra = args[ind]
            del args[ind]
            args.remove("-ra")
        else:
            ra = "ALPHA_J2000"
        if any(i == "-dc" for i in args):
            ind = args.index("-dc") + 1
            dc = args[ind]
            del args[ind]
            args.remove("-dc")
        else:
            dc = "DELTA_J2000"
        if any(i == "-m" for i in args):
            ind = args.index("-m") + 1
            mags = args[ind].split(",")
            del args[ind]
            args.remove("-m")
        else:
            mags = [0]
        if any(i == "-mp" for i in args):
            ind = args.index("-mp") + 1
            mag_def = args[ind]
            del args[ind]
            args.remove("-mp")
        else:
            mag_def = "MAG_AUTO"

        cats_names = []
        for i in range(len(args)):
            if args[i][-4:] == ".lis":
                if os.path.exists(args[i]):
                    values = np.loadtxt(args[i], dtype="str")
                    if values.size > 1:
                        cats_names += list(values)
                    elif values.size == 1:
                        cats_names += ["{}".format(values)]
                else:
                    sys.exit("\033[1;31mError: file {} not found.\033[m".format(args[i]))
            else:
                cats_names += [args[i]]

        if len(cats_names) == 0 or len(cats_names) == 1:
            sys.exit("\033[1;31mError: At least two arguments must be passed.\033[m")

        for i in cats_names:
            if not os.path.exists(i):
                sys.exit("\033[1;31mError: file {} not found.\033[m".format(i))

        main(cats_names, save, thresh, exten, exten_def, ra, dc, mags, mag_def)
    else:
        help_msg = "\n\t\tHelp Section\ncombine_catalog.py v3.1\n" \
                   "Usage: python3 combine_catalog.py [options] arguments\n\n" \
                   "Written by Matheus J. Castro <matheusj_castro@usp.br>\nUnder MIT License.\n\n" \
                   "This program combine FITS catalogs and generate one as output.\n\n" \
                   "Arguments need to be file names of FITS catalogs or a list of files.\n" \
                   "Each list must contain only names of files, one per line, lists need\n" \
                   "to have the extension \".lis\".\n\n" \
                   "Options are:\n\t -h,  -help\t|\tShow this help;\n\t--h, --help\t|\tShow this help;\n" \
                   "\t-s [option]\t|\tSave or not the output catalog\n\t\t\t|\t\t0 to not save " \
                   "the output (default);\n\t\t\t|\t\t1 to save a \".cat\" file;\n" \
                   "\t\t\t|\t\t2 to save \".csv\" file;\n\t\t\t|\t\t3 to save both;\n" \
                   "\t-t [option]\t|\tInteger to set the cross-match radius in arc-second;\n" \
                   "\t\t\t|\t\t(by default is 3)\n" \
                   "\t-e [options]\t|\tA list with the extension needs to use for each file.\n" \
                   "\t\t\t|\tIt need to be in this format n,n,n... changing \"n\"\n\t\t\t|\tby " \
                   "the extension you want to use. The order is the\n\t\t\t|\torder of your files " \
                   "input. 1 is the default value,\n\t\t\t|\tif one argument is missing, the default is " \
                   "considered. Zero\n\t\t\t|\tvalues (like ...n,0,n...) makes the file correspondent" \
                   "\n\t\t\t|\tbe set to the default value;\n" \
                   "\t-ep [option]\t|\tChange the default value for the extensions;\n" \
                   "\t-ra [option]\t|\tThe name of the column for Right Ascension;\n\t\t\t|\t" \
                   "\t(the default is ALPHA_J2000)\n" \
                   "\t-dc [option]\t|\tSame as -ra but for Declination;\n\t\t\t|\t" \
                   "\t(the default is DELTA_J2000)\n" \
                   "\t-m [options]\t|\tSame as -e but for the column names of the magnitudes,\n\t\t\t|\t" \
                   "The values need to be in format n,n,n... and the\n\t\t\t|\tdefault value is MAG_AUTO;" \
                   "\n\t-mp [option]\t|\tChange the default value for the column name of the magnitudes." \
                   "\n\nExample:\npython3 combine_catalog.py -s 1 -e 2,1,3,0 -ra MAG_AUTO combine.lis " \
                   "catalog1.cat catalog2.cat\n"
        print(help_msg)


if __name__ == '__main__':
    arg = sys.argv[1:]
    args_menu(arg)
