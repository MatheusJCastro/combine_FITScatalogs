###################################################
# Combine Fits Catalog                            #
# Matheus J. Castro                               #
# Version 3.4                                     #
# Last Modification: 05/31/2020 (month/day/year)  #
###################################################

import manage_catalog as mancat
import numpy as np
import time
import sys
import os
from astropy.table import Table


def combine(cat_name_1, cat_name_2, first_combine=Table(), threshold=3, mag_to_use1="MAG_AUTO", mag_to_use2="MAG_AUTO",
            right_ascension_column="ALPHA_J2000", declination_column="DELTA_J2000", save_cross_match=0, extent1=2,
            extent2=2, output_name="Results_Combined"):
    inicio = time.time()

    data, elements = mancat.setup_catalog(cat_name_1, cat_name_2, ext1=extent1, ext2=extent2)

    data = [Table(data[0]), Table(data[1])]

    # data = data[0][0:15], data[1][0:10]  # Just to test (debug) more fast

    if len(first_combine) != 0:
        data = [first_combine, data[1]]

    # Function used to replace the MAG_AUTO to MAG_AUTO_CORRECTED
    if mag_to_use1 != mag_to_use2:
        data = mancat.replace_mag_corrected(data, mag_to_use1, mag_to_use2)

    # Reorder the catalogs using the base catalog as reference
    data = mancat.reorder_cats(data)

    ##################################################################################
    # C Execution
    c_code_name = "cross-match.so"
    mancat.save_all_obj(data, right_ascension_column, declination_column)
    mancat.execute_c(c_code_name, threshold, changedot=0)
    objects = mancat.read_c()
    mancat.del_temp_files()  # Delete the temporary files created because of C code
    ##################################################################################

    # Function to combine the catalogs
    final_cat = mancat.combine_cat(data, objects, "MAGERR_AUTO", "FLAGS")

    if save_cross_match != 0:
        if save_cross_match == 1 or save_cross_match == 3:
            mancat.save_cross_match_cat(final_cat, name=output_name, fmt="fits")
        if save_cross_match == 2 or save_cross_match == 3:
            mancat.save_cross_match_cat(final_cat, name=output_name, fmt="csv")

    fim = time.time()
    print("Time Python: ", fim - inicio)

    return final_cat


def main(cats_names, save, thresh, exten, exten_def, ra, dc, mags, mag_def, op_name):
    inicio_global = time.time()

    # cats_names = ['j02_rSDSS_21s.cat', 'j02_rSDSS_2.1s_corrected.cat', 'j02_rSDSS_0.21s_corrected.cat']

    for i in range(len(cats_names)):
        if i < len(exten) and exten[i] == 0:
            exten[i] = exten_def
        else:
            exten.append(exten_def)
        if i < len(mags) and mags[i] == "0":
            mags[i] = mag_def
        else:
            mags.append(mag_def)

    cat_combined = Table()
    for i in range(1, len(cats_names)):
        print("############### ITERATION {} ###############".format(i))
        cat_combined = combine(cats_names[0], cats_names[i], extent1=exten[0], extent2=exten[i],
                               mag_to_use1=mags[0], mag_to_use2=mags[i], save_cross_match=save,
                               right_ascension_column=ra, declination_column=dc,
                               first_combine=cat_combined, threshold=thresh, output_name=op_name)

    print("################### END ###################")
    fim_global = time.time()
    print("Total Time: ", fim_global - inicio_global)


def args_menu(args):

    if len(args) != 0 and not any((i == "-h" or i == "--h" or i == "-help" or i == "--help") for i in args):
        if any(i == "-s" for i in args):
            ind = args.index("-s") + 1
            try:
                save = int(args[ind])
            except (ValueError, IndexError):
                sys.exit("\033[1;31mError: Argument for -s not valid.\033[m")
            del args[ind]
            args.remove("-s")
        else:
            save = 0
        if any(i == "-t" for i in args):
            ind = args.index("-t") + 1
            try:
                thresh = float(args[ind])
            except (ValueError, IndexError):
                sys.exit("\033[1;31mError: Argument for -t not valid.\033[m")
            del args[ind]
            args.remove("-t")
        else:
            thresh = 3
        if any(i == "-e" for i in args):
            ind = args.index("-e") + 1
            try:
                exten = list(map(int, args[ind].split(",")))
            except (ValueError, IndexError):
                sys.exit("\033[1;31mError: Argument for -e not valid.\033[m")
            del args[ind]
            args.remove("-e")
        else:
            exten = [0]
        if any(i == "-ep" for i in args):
            ind = args.index("-ep") + 1
            try:
                exten_def = int(args[ind])
            except (ValueError, IndexError):
                sys.exit("\033[1;31mError: Argument for -ep not valid.\033[m")
            del args[ind]
            args.remove("-ep")
        else:
            exten_def = 1
        if any(i == "-ra" for i in args):
            ind = args.index("-ra") + 1
            try:
                ra = args[ind]
            except IndexError:
                sys.exit("\033[1;31mError: Argument for -ra not valid.\033[m")
            del args[ind]
            args.remove("-ra")
        else:
            ra = "ALPHA_J2000"
        if any(i == "-dc" for i in args):
            ind = args.index("-dc") + 1
            try:
                dc = args[ind]
            except IndexError:
                sys.exit("\033[1;31mError: Argument for -dc not valid.\033[m")
            del args[ind]
            args.remove("-dc")
        else:
            dc = "DELTA_J2000"
        if any(i == "-m" for i in args):
            ind = args.index("-m") + 1
            try:
                mags = args[ind].split(",")
            except IndexError:
                sys.exit("\033[1;31mError: Argument for -m not valid.\033[m")
            del args[ind]
            args.remove("-m")
        else:
            mags = [0]
        if any(i == "-mp" for i in args):
            ind = args.index("-mp") + 1
            try:
                mag_def = args[ind]
            except IndexError:
                sys.exit("\033[1;31mError: Argument for -mp not valid.\033[m")
            del args[ind]
            args.remove("-mp")
        else:
            mag_def = "MAG_AUTO"
        if any(i == "-o" for i in args):
            ind = args.index("-o") + 1
            try:
                output_name = args[ind]
            except IndexError:
                sys.exit("\033[1;31mError: Argument for -o not valid.\033[m")
            del args[ind]
            args.remove("-o")
        else:
            output_name = "Results_Combined"

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

        main(cats_names, save, thresh, exten, exten_def, ra, dc, mags, mag_def, output_name)
    else:
        help_msg = "\n\t\tHelp Section\ncombine_catalog.py v3.4\n" \
                   "Usage: python3 combine_catalog.py [options] arguments\n\n" \
                   "Written by Matheus J. Castro <matheusj_castro@usp.br>\nUnder MIT License.\n\n" \
                   "This program combine FITS catalogs and generate one as output.\n\n" \
                   "Arguments need to be file names of FITS catalogs or a list of files.\n" \
                   "Each list must contain only names of files, one per line, and need\n" \
                   "to have the extension \".lis\".\nThe first input catalog will be the base for " \
                   "others, and only their columns\nwill be present in the output catalog.\n\n" \
                   "Options are:\n -h,  -help\t\t|\tShow this help;\n--h, --help\t\t|\tShow this help;\n" \
                   "\t-s  [option]\t|\tSave or not the output catalog\n\t\t\t|\t\t0 to not save " \
                   "the output (default);\n\t\t\t|\t\t1 to save a \".cat\" file;\n" \
                   "\t\t\t|\t\t2 to save \".csv\" file;\n\t\t\t|\t\t3 to save both;\n" \
                   "\t-t  [option]\t|\tInteger to set the cross-match radius in arc-second;\n" \
                   "\t\t\t|\t\t(by default is 3)\n" \
                   "\t-e  [options]\t|\tA list with the extension needs to use for each file.\n" \
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
                   "\t-m  [options]\t|\tSame as -e but for the column names of the magnitudes,\n\t\t\t|\t" \
                   "The values need to be in format n,n,n... and the\n\t\t\t|\tdefault value is MAG_AUTO;" \
                   "\n\t-mp [option]\t|\tChange the default value for the column name of the magnitudes;" \
                   "\n\t-o  [option]\t|\tThe name of the output catalog WITHOUT extension and spaces. " \
                   "\n\t\t\t|\tAlso option -s must be given. The default it \"Results_Combined\"." \
                   "\n\nExample:\npython3 combine_catalog.py -s 1 -e 2,1,3,0 -ra MAG_AUTO combine.lis " \
                   "catalog1.cat catalog2.cat\n"
        print(help_msg)


if __name__ == '__main__':
    arg = sys.argv[1:]
    args_menu(arg)
