###################################################
# Manage Fits Catalog                             #
# Matheus J. Castro                               #
# Version 4.0                                     #
# Last Modification: 01/12/2020 (month/day/year)  #
###################################################

import numpy as np
from astropy.io import fits


######################################################################################


def save_catalog(catalog_file, ext_names, str_element):
    data = get_data(catalog_file)  # Get the data
    col = len(data[0])  # length of columns
    line = len(data)  # length of lines

    # create a list new_data of all the data and reformulating the ndarrays found inside data array
    # useful for save in csv file
    new_data = []
    for i in range(line):
        for j in range(col):
            if type(data[i][j]) == np.ndarray:
                array = ""
                for k in range(len(data[i][j])):
                    array = array + " " + repr(data[i][j][k])
                array = array[1:]
                new_data.append(array)
            else:
                new_data.append(data[i][j])
        print("Save Catalog: {:.2f}%".format(((i + 1) / line) * 100))
    new_data = np.asarray(new_data).reshape(line, col)

    np.savetxt("Extension{}_{}.csv".format(2, ext_names[2]), new_data, header=str_element, fmt="%s", delimiter=",")


######################################################################################


def get_header(catalog_file, save=False, extension=2):
    if save:
        # save the header of extension of interest
        header = np.array(repr(catalog_file[extension].header))
        np.savetxt("Header.txt", [header], fmt="%s")

    # create the elemente list with names of the collumns of the catalog
    dic = np.array(catalog_file[extension].header)
    header = catalog_file[extension].header
    element = []
    for i in range(len(dic)):
        if "TTYPE" in dic[i]:
            element.append(header[i])

    # transfor element array into a string of the elements
    str_element = ""
    for i in range(len(element)):
        str_element = str_element + "," + repr(element[i])
    str_element = str_element[1:].replace("'", "")
    # print(str_element)

    return element, str_element
    # return elements of the header on first variable
    # and the string of it on the second variable


######################################################################################


def get_data(catalog_file, extension=2):
    # Save the data
    data = catalog_file[extension].data

    return data


######################################################################################


def get_info(catalog_file, print_info=False):
    # Get information about names of extension of the .proccat
    info = catalog_file.info(0)
    size = len(info)

    if print_info:
        print(catalog_file.info())

    # Create a list of the names of the extensions
    ext_names = []
    for i in range(size):
        ext_names.append(info[i][1])

    info = catalog_file.info()

    return info, ext_names


######################################################################################


def cat_open(cat_name):
    # Open the catalog
    catalog_file = fits.open(cat_name)

    return catalog_file


######################################################################################


def close(catalog_file):
    catalog_file.close()


######################################################################################


def setup_catalog(cat_name_1, cat_name_2, show_info=False):
    # Configure catalogs
    catalog_1 = cat_open(cat_name_1)
    catalog_2 = cat_open(cat_name_2)

    # show info about catalogs
    if show_info:
        print(get_info(catalog_1)[0])
        print(get_info(catalog_2)[0])

    elements = (get_header(catalog_1)[0], get_header(catalog_2)[0])
    # elements of catalog 1 and 2

    if elements[0] != elements[1]:
        print("Error: Catalogs are different.")
        return -1

    data = (get_data(catalog_1), get_data(catalog_2))  # data of catalogs
    close(catalog_1)
    close(catalog_2)

    return data, elements


######################################################################################


def check_equal(n, m, x, y, threshold=3, value=False):
    # This function detects if one object, with AR and DEC (x and y), are inside a
    # circle with radius "threshold" and center set by another object (n and m).
    # It can returns True, False or de module of the distance.

    # threshold in given in arcsecond
    # it's needed to transform to degrees
    threshold = threshold / 60**2
    module = np.sqrt((n-x)**2 + (m-y)**2)

    if value:
        return module
    elif module <= threshold:
        return True
    else:
        return False


######################################################################################


def find_index(data, ind_ar, ind_dc):
    # Detects which objects on two given catalogs (data) are the same object
    # (CROSS-MATCH). Returns the indexes of the cross-matched objects.

    ar_list_1 = []
    dc_list_1 = []
    ar_list_2 = []
    dc_list_2 = []
    for i in range(len(data[0])):
        ar_list_1.append(data[0][i][ind_ar])
        dc_list_1.append(data[0][i][ind_dc])
    for i in range(len(data[1])):
        ar_list_2.append(data[1][i][ind_ar])
        dc_list_2.append(data[1][i][ind_dc])

    equal_objects = []
    tam = len(data[0])
    tam2 = list(range(len(data[1])))
    for i in range(tam):
        found = False
        x = 0
        j_list = []
        for j in tam2:
            check = check_equal(ar_list_1[i], dc_list_1[i], ar_list_2[j], dc_list_2[j])
            if check:
                j_list.append(j)
                found = True
            if found:
                x += 1
                if x >= 100:
                    break
        if found:
            result = []
            for j in j_list:
                result.append(check_equal(ar_list_1[i], dc_list_1[i], ar_list_2[j], dc_list_2[j],
                                          value=True))
            best = j_list[result.index(min(result))]
            equal_objects.append((i, best))
            tam2.remove(best)
        print("Load: {:.2f}%".format(((i+1)/tam)*100))
    print(equal_objects)
    print("Number of founded objects:", len(equal_objects))

    return equal_objects


######################################################################################


def read_cross_match_csv(name_csv):
    # Read the csv file Magnitudes_compared.csv and returns the indexes of the
    # cross-matched objects.

    loaded = np.loadtxt(name_csv, delimiter=",")

    equal_objects = []
    for i in range(len(loaded)):
        equal_objects.append((int(loaded[i][1]-1), int(loaded[i][2]-1)))

    return equal_objects


######################################################################################


def save_cross_match_csv(list_of_mag, ar, dc):
    # Save a csv file that contain the cross-matched objects, their positional in sky
    # and the two mags from both catalogs.
    head = "Number, Number_1, Number_2, " + ar + ", " + dc + ", MAG_CAT_1, MAG_CAT_2"
    np.savetxt("Magnitudes_compared.csv", list_of_mag, header=head, fmt="%s", delimiter=",")


######################################################################################


def save_all_obj(data, ind_ar, ind_dc):
    # Save a csv file to C code read and do the cross-match.
    ar_list_1 = []
    dc_list_1 = []
    ar_list_2 = []
    dc_list_2 = []
    for i in range(len(data[0])):
        ar_list_1.append(data[0][i][ind_ar])
        dc_list_1.append(data[0][i][ind_dc])
    for i in range(len(data[1])):
        ar_list_2.append(data[1][i][ind_ar])
        dc_list_2.append(data[1][i][ind_dc])

    lista = [(len(data[0]), len(data[1]))]

    if len(data[0]) >= len(data[1]):
        for i in range(len(data[0])):
            if i < len(data[1]):
                lista.append((ar_list_1[i], dc_list_1[i], ar_list_2[i], dc_list_2[i]))
            else:
                lista.append((ar_list_1[i], dc_list_1[i], 0., 0.))
    else:
        for i in range(len(data[1])):
            if i < len(data[0]):
                lista.append((ar_list_1[i], dc_list_1[i], ar_list_2[i], dc_list_2[i]))
            else:
                lista.append((0., 0., ar_list_2[i], dc_list_2[i]))

    np.savetxt(".entrada.csv", lista, fmt="%s", delimiter=";")


######################################################################################


def execute_c(c_name, threshold, changedot = 0):
    # Execute the function py_script from a C code with the name c_name.
    import ctypes

    c_lib = ctypes.CDLL("./{}".format(c_name))
    c_lib.py_script.argtypes = (ctypes.c_double, ctypes.c_int)
    c_lib.py_script_resttype = ctypes.c_int
    founded = c_lib.py_script(threshold, changedot)  # Call function py_script on C code
    # c_lib.main(None)  # Call function main on C code

    return founded
    # Just execute this return if you are executing the py_script function on C,
    # if you are executing the main function, comment the return line.


######################################################################################


def read_c():
    # Read the output csv file generated by the C code and returns the indexes of the
    # cross-matched objects.
    name_csv = ".saida.csv"

    loaded = np.loadtxt(name_csv, delimiter=",")

    equal_objects = []
    for i in range(len(loaded)):
        equal_objects.append((int(loaded[i][0] - 1), int(loaded[i][1] - 1)))

    return equal_objects


######################################################################################


def get_mag(data, elements, mag, obj, ind_ar, ind_dc):
    # Get the magnitudes of the cross-matched objects and return two lists:
    # The first one has only the two mags from both catalogs;
    # The second one is formatted to have index from both catalogs, the sky position
    # and the mags.
    ind = elements[0].index(mag)

    mags = []
    for i in range(len(obj)):
        mags.append((data[0][obj[i][0]][ind], data[1][obj[i][1]][ind]))

    new_mags = []
    for i in range(len(mags)):
        new_mags.append(("{:d}".format(i+1), obj[i][0]+1, obj[i][1]+1, data[0][obj[i][0]][ind_ar],
                         data[0][obj[i][0]][ind_dc], mags[i][0], mags[i][1]))

    return mags, new_mags


######################################################################################

def del_temp_files(files_names=(".entrada.csv", ".saida.csv")):
    # Delete the files listed on files_names variable
    import os

    message = ""

    for i in files_names:
        if os.path.exists(i):  # Check if the file exists
            os.remove(i)
            message = message + "Temp File deleted: " + i + "\n"
        else:
            message = message + "No such file: " + i + "\n"

    print(message)

######################################################################################
