# Combine Catalogs Steps
This tutorial shows how to, using raw data from a set of reduced images from same filter, create and combine catalogs using this images.  

*Written by Matheus J. Castro <matheusj_castro@usp.br>
Under MIT License.*


## Getting the Data
Download in TACDATA website **(OAJ)**  inside the TACDATA_1500052 observations the images with the filters you want.  

**[https://tacdata.cefca.es/](https://tacdata.cefca.es/)**

## Extracting
Open DS9 and transform the `.fz` files in the `.fits` just saving again.  

## SWarp - Astromatic
Combine each of the images you get for each exposion time using SWarp. To do that follow this steps:  

- Create the configuration file:  
	1. `swarp -d > default.swarp`
	2. Change the IMAGEOUT_NAME and the WEIGHTOUT_NAME to what you want
	3. Change the WEIGHT_TYPE from NONE to BACKGROUND
	4. The COMBINE_TYPE to MIN
	5. SUBTRACT_BACK to N

- Create a list with the `.fits` you want to combine:  
```bash
ls *.fits > list_name.lis
```
- Run SWarp:  
```bash
swarp @list_name.lis -c default.swarp
```

## SExtractor - Astromatic
Now run SExtracor to generate the catalog file following this steps:  

- Create the extended configuration file and the parameters file:  
```bash
sex -dd > default.sex
sex -dp > default.param
```

- Inside the config file (`.sex`), modify:
	1. CATALOG_NAME to what you want
	2. CATALOG_TYPE to FITS_LDAC
	3. DETECT_THRESH to 5
	4. FILTER to N
	5. WEIGHT_TYPE to MAP_WEIGHT
	6. WEIGHT_IMAGE to the name of SWarp generated weight

- Now, on the parameters file leave only this params:  
```text
NUMBER
X_IMAGE
Y_IMAGE
MAG_AUTO
MAGERR_AUTO
FLAGS
FLAGS_WEIGHT
FWHM_IMAGE
BACKGROUND
ALPHA_J2000
DELTA_J2000
```

- Finally, run SExtractor:
```bash
sex name_of_the_combined_image.fits
```

With that, now we have a nice catalog for this exposure time. Do the same for the other exposures.  

## Zero-Point with TOPCAT
For the last modification before combining the catalogs, we need to correct the zero-point based on one of them. To do that we need TOPCAT:

- Match the base catalog with one another (max error 3").  

- Then open the table, click with right mouse anywhere and select "New Synthetic Column", this will open a window, fill the boxes whit the information bellow:  

	- Name: **MAG_DIF**
	- Expression: **MAG_AUTO_1-MAG_AUTO_2**

- Close the table and open the box with sigma symbol, will open a table with statistcs of each column of your table. Go to the column that we just created, **MAG_DIF** (Note if nothing appear, click on the reload box at the top of the window). We are looking for the ***Mean* value**, save this to later use.  

- Now, open the catalog table that we used to match with the base catalog and add a synthetic column whit this fields:  
	- Name: **MAG_AUTO_CORRECTED**
	- Expression: **MAG_AUTO**+(the ***Mean* value** that we saved in the previous step, note that if the value is negative it will subtract)  
	Allways verify if the result values agree with the base catalog.  

- Repeat the process with the other catalogs, allways using the same base catalog that before.  

- Finally, verify the results ploting an histogram.  

## Runing Python3
Now you problably have 3 catalogs for each filter, it's time to run the combine_catalogs.py script to combine them. Here is how to use it:  

- On terminal type: 
```bash
python3 combine_catalog.py [options] arguments
```

- Arguments need to be file names of FITS catalogs or a list of files.  
- Each list must contain only names of files, one per line, and need to have the extension ".lis".
- The first input catalog will be the base for others, and only their columns will be present in the output catalog.

- The [options] are:
```bash
 -h,  -help		|	Show this help;
--h, --help		|	Show this help;
-s  [option]	|	Save or not the output catalog
				|		0 to not save the output (default);
				|		1 to save a ".cat" file;
				|		2 to save ".csv" file;
				|		3 to save both;
-t  [option]	|	Integer to set the cross-match radius in arc-second;
				|		(by default is 3)
-e  [options]	|	A list with the extension needs to use for each file.
				|	It need to be in this format n,n,n... changing "n"
				|	by the extension you want to use. The order is the
				|	order of your files input. 1 is the default value,
				|	if one argument is missing, the default is considered. Zero
				|	values (like ...n,0,n...) makes the file correspondent
				|	be set to the default value;
-ep [option]	|	Change the default value for the extensions;
-ra [option]	|	The name of the column for Right Ascension;
				|		(the default is ALPHA_J2000)
-dc [option]	|	Same as -ra but for Declination;
				|		(the default is DELTA_J2000)
-m  [options]	|	Same as -e but for the column names of the magnitudes,
				|	The values need to be in format n,n,n... and the
				|	default value is MAG_AUTO;
-mp [option]	|	Change the default value for the column name of the magnitudes;
-o  [option]	|	The name of the output catalog WITHOUT extension and spaces. 
				|	Also option -s must be given. The default it "Results_Combined".

```



