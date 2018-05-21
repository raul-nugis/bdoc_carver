# coding: utf-8

""" This script will read raw image or raw files and apply
header and footer to carve data based on
those headers and footers. Optionally an
algorithmic approach can be applied to copy file tail
"""

import os
import sys
import glob
import re

# This addresses Dec 2017 bug on Win10
# https://bugs.python.org/issue32245

if os.name == 'nt':
    import win_unicode_console, logging
    win_unicode_console.enable()

# Folder path from command line
# This is for 'raw' files. Their folder path must be
# passed as argument. Otherwise the script will try 
# reading an image file from 'Image' subdirectory

if len(sys.argv) > 1:
    file = str(sys.argv[1])
else:
    file = ''

# Geometry for an image

clusters_per_sectors,sector,cluster_offset,maximum_filesize = 8,512,0,10000
mounted_size = 0
_cluster = clusters_per_sectors * sector
header_lenght = 105

# This is to carve raw files. They have no 'geometry'

files = []
if len(file) > 0:
    clusters_per_sectors,sector,cluster_offset,maximum_filesize = 1,4096,0,80000
    _cluster = clusters_per_sectors * sector
    header_lenght = _cluster # The read of data not at the beginning of cluster
    # But in all of the chunk of data

    # Gather 'raw' files
    files = []
    file = os.path.join(file, '*')
    for filename in sorted(glob.glob(file)):
        files.append(filename)
    print('Found',len(files),'files')

# Image location
# Assume image is in 'Image' subfolder
# This takes only the first file, this is assuming there is only one image

if len(files) == 0:
    path_to_file_under_examination = os.path.join(os.getcwd(), 'Image')
    path_to_file_under_examination = os.path.join(path_to_file_under_examination,
    os.listdir(path_to_file_under_examination)[0])
    print('Found image',path_to_file_under_examination)
else:
    path_to_file_under_examination = []

# 'Algorithmic' or footer

# This is optional 'algorithmic' carving based on discovering 
# Central  Directory End Record signature and reading ZIP Central 
# Directory End Record's 'ZIP file comment' size flag
option = 'algorithm' # else 'algorithm'

# Signature

# Standard ZIP header #
#header_hex_code = re.compile(b'PK\x03\x04')

# Improved DSD header #
#header_hex_code  = re.compile(b'PK\x03\x04(.|\s){26}mimetype')

# IANA header
#header_hex_code = re.compile(b'PK\x03\x04(.|\s){26}mimetype(.|\s){12}vnd\.etsi\.asic\-e\+zip')

# Perfected header #
#header_hex_code  = re.compile(b'PK\x03\x04(.|\s){26}mimetype(.|\s){0,28}(application\/vnd\.etsi\.asic\-e\+zip|K,\(\\\xc8\xc9LN,\xc9\xcc\xcf\xd3\/\xcbK\xd1K)')

# Perfected header further changed #
header_hex_code = re.compile(b'PK\x03\x04(.|\s){26}mimetype(.|\s){0,36}(application\/vnd\.etsi\.asic\-e\+zip|K,\(\\\xc8\xc9LN,\xc9\xcc\xcf\xd3\/\xcbK\xd1K)')

# ZIP standard footer #
#footer_hex_code = re.compile(b'PK\x05\x06(.|\s){18}')

# ZIP Improved footer #
#footer_hex_code = re.compile(b'PK\x05\x06\x00\x00(.|\s){14}.*?(\x00{2}|.*[\w: ])')

# Apply footers #
if option == 'algorithm': # other choice is 'footer'
    footer_hex_code = re.compile(b'PK\x05\x06\x00\x00(.|\s){16}') # for general discovery
    # of Central Directory's "beginning of the end"
else:
    footer_hex_code = re.compile(b'PK\x05\x06\x00\x00(.|\s){14}.*?(\x00{2}|.*[ -~])')
    # This functions as full-scale 'footer' signature

def discover_sectors(path_to_file_under_examination,option):

    """
    This is the function for scanner, which will scan
    DD image or mounted image and find all starts and ends
    or Headers and Footers of corresponding files
    provided contiguous clusters and HDD like geometry
    Mounted images reading rely on MS Windows syntax
    """

    # Variables #

    start_carve_sector, end_carve_sector = [],[]
    current__cluster,_current__cluster = 0,0

    # Pointing to file and of file cluster total
    # number calculation
    # Different methods for raw image file
    # or for mounted drive

    file = open(path_to_file_under_examination, 'rb')

    _clusters_total = int(os.path.getsize(path_to_file_under_examination)/_cluster)
    file.seek(cluster_offset * sector)
    print('Clusters to analyse total:',str(_clusters_total),'...')

    # Scanning for headers and footers #

    while current__cluster <= _clusters_total:

        # This is reading one cluster and then moving
        # the pointer one further cluster
        # This approach will not find
        # NTFS resident files
        # And this will not find ZIP files,
        # which are smaller than a cluster
        # Embedded signature and time-sresponses
        # containing files are appr 13 Kb
        # So they can't really be residents
        # This approach will not find
        # non-contiguously clustered files

        try:
            current_cluster = file.read(_cluster)
        except Exception as e:
            return start_carve_sector, end_carve_sector

        current__cluster += 1

        # This will apply the header #

        #header_lenght is the lenghts required for signature to work
        beginning_string_to_analyze = current_cluster[0:header_lenght]
        result = re.search(header_hex_code,beginning_string_to_analyze)

        # Action if header is present #

        if result:
            if result.group(0):
                
                start_carve_sector.append(int(cluster_offset)  # Will
                # remember where file starts
                 + clusters_per_sectors * (current__cluster - 1))

                _current__cluster = 1

                while _current__cluster <= maximum_filesize:  # Here is
                    #  administratively set max lenght

                    # This will read next cluster and move further one cluster #

                    current_cluster = file.read(_cluster)

                    _current__cluster += 1
                    current__cluster += 1

                    # This will apply the footer, first to the whole cluster
                    # And second to the tail of the next cluster together with the
                    # current cluster

                    result2 = re.search(footer_hex_code,current_cluster)
                    if result2:
                        if result2.group(0):
                            if option == 'algorithm': # 'Algorithmic' read of flag for tail lenght
                                if result2.span()[1] + result2.group(0)[21] + result2.group(0)[20] >= len(current_cluster):
                                    end_carve_sector.append(int(cluster_offset)\
                                    + 1 + (clusters_per_sectors)* (current__cluster))
                                    # result2.group(0)[21] + result2.group(0)[20] are
                                    # the value of the trailer lenght
                                else:
                                    end_carve_sector.append(int(cluster_offset)\
                                    + (clusters_per_sectors)* (current__cluster))
                            else:
                                if result2.span()[1] == len(current_cluster):
                                    end_carve_sector.append(int(cluster_offset)\
                                     + 1 + (clusters_per_sectors)* (current__cluster))
                                else:
                                    end_carve_sector.append(int(cluster_offset)\
                                     + (clusters_per_sectors)* (current__cluster))

                    cluster_tail_2 = file.read(_cluster)[0:sector]  #This
                    # is additional cluster-read, not the same read
                    joined_tail_2 = current_cluster + cluster_tail_2
                    result4 = re.search(footer_hex_code,joined_tail_2)
                    if result4:
                        if result4.group(0):
                            if result2 is None:
                                if option == 'algorithm': # 'Algorithmic' read of flag for tail lenght
                                    if result4.span()[1] + result4.group(0)[21] + result4.group(0)[20] >= len(joined_tail_2):
                                        end_carve_sector.append(int(cluster_offset)\
                                        + 2 + (clusters_per_sectors) * (current__cluster))
                                        # result4.group(0)[21] + result4.group(0)[20] are
                                        # the value of the trailer lenght
                                    else:
                                        end_carve_sector.append(int(cluster_offset)\
                                        + 1 + (clusters_per_sectors) * (current__cluster))
                                else:
                                    if result4.span()[1] == len(joined_tail_2):
                                        end_carve_sector.append(int(cluster_offset)\
                                        + 2 + (clusters_per_sectors) * (current__cluster))
                                    else:
                                        end_carve_sector.append(int(cluster_offset)\
                                        + 1 + (clusters_per_sectors) * (current__cluster))

                    file.seek(cluster_offset*sector
                     + current__cluster*_cluster)

                    if result2 or result4:
                        break
    destination = path_to_file_under_examination.split('\\')[-1]
    print('Scan complete at cluster: ' +str(current__cluster - 1)\
     + ' ' + str(len(start_carve_sector)) +','
     + str(len(end_carve_sector)) + ' start and end sectors found in '\
      + destination)
    file.close()

    return start_carve_sector,end_carve_sector

def recover_data_from_sectors(
    path_to_file_under_examination,
    start_carve_sector,
    end_carve_sector,option):
    """
    This will recover file data based on starting
    and ending sectors in the image.
    """

    # Variable to hold data #

    data = b''

    # Copy sectors #

    if end_carve_sector - start_carve_sector < 51200:  # limitation of size
        # as for appr. 25 MB max. Large-scale web scrapping of registry showed
        # that 72% of documents come with email. It is anecdotically known that
        # frequent max size of email attachments is set to 25 MB
        file = open(path_to_file_under_examination, 'rb')
        file.seek(start_carve_sector*sector)
        data = file.read((end_carve_sector)*sector
         - start_carve_sector*sector)
        file.close()

        # This is a check for carving data with no geometry
        
        if data[0:4] != b'PK\x03\x04': # Excessive data before header
            # This is the case of 'raw' data. Header found not at the 
            # beginning of a chunk but anywhere within a 'data-read'
            result2 = re.search(header_hex_code,data)  # re-apply header
            if result2:
                beginning = result2.span()[0] # cuts away excessive data
                data = data[beginning:]

        result = re.search(footer_hex_code,data)  # Apply footer
        if result:
            if option == 'footer': # Cut based on footer
                end = result.span()[1]
                data = data[0:end]
            else: # Cut based on algorithmic approach
                lenght = result.group(0)[21] + result.group(0)[20] 
                # This is Big Endian
                # Reading of ZIP trail lenght flags
                end = result.span()[1] + lenght
                data = data[0:end]

    return data

def write_recovered_data_to_file(data,destination):

    """
    This will save recovered file data to a file.
    """
    destination = os.path.join(os.getcwd(),destination)
    if len(data) > 0:
        file = open(destination, 'wb')
        file.write(data)
        file.close()

if __name__ == "__main__":

    ''' Carve files '''

    carved_files = 0

    if len(path_to_file_under_examination) > 0:

        if len(files) > 0:
            # This is because 'geometry' was set differently above
            # Therefore either carve an image of files
            print('Found files as well therefore image is not carved')
        else:
            start_carve_sector,end_carve_sector = discover_sectors(
                path_to_file_under_examination,option)

            for start_carve_sector,end_carve_sector in zip(
                start_carve_sector,end_carve_sector):
                data = recover_data_from_sectors(
                    path_to_file_under_examination,start_carve_sector,end_carve_sector,option)
                destination = path_to_file_under_examination.split('\\')[-1]
                destination = destination.split('/')[-1]
                destination = str(start_carve_sector) + '_' + str(end_carve_sector)\
                 + '_' + destination + '.bdoc'
                write_recovered_data_to_file(data,destination)
                carved_files += 1

    if len(files) > 0:
        if len(path_to_file_under_examination) > 0:
            # This is because 'geometry' was set differently above
            # Therefore either carve an image of files
            print('Found image as well therefore files are not carved')
        else:
            for file_ in files:
                start_carve_sector,end_carve_sector = discover_sectors(
                    file_,option)

                for start_carve_sector,end_carve_sector in zip(
                    start_carve_sector,end_carve_sector):
                    data = recover_data_from_sectors(
                        file_,start_carve_sector,end_carve_sector,option)
                    destination = file_.split('\\')[-1]
                    destination = destination.split('/')[-1]
                    destination = str(start_carve_sector) + '_' + str(end_carve_sector)\
                     + '_' + destination + '.bdoc'
                    write_recovered_data_to_file(data,destination)
                    carved_files += 1

    print(carved_files,'files carved.')
