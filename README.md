This script will read raw image and carve DSD (try this to recover BDOC, ACISE, ASC, ADOC, EDOC digitally signed files) data based on certain headers and footers (in the code) on contiguous clustered media. Alternatively, it can apply ‘algorithmic’ read of ZIP containers' Central Directory End Record's ‘ZIP file comment’. With additional changes in ‘geometry’ section this should enable carving from unstructured media.

##### Carving DSD files with a forensic tool

Instead of using the header and footer regular expressions provided in the code with a script, use them with a carving tool. Adjustments in syntax may be required.

In X-Ways (tested with 19.5) the following syntax is to be used. The syntax difference, as compared to the signature used in Python, is removal of some slashes

Header: ‘PK\x03\x04.{26}mimetype.{0,36}(application/vnd\.etsi\.asic\-e\+zip|K,\(\xc8\xc9LN,\xc9\xcc\xcf\xd3\/\xcbK\xd1K)’

Footer: ‘PK\x05\x06\x00\x00.{14}(\x00{2}|.{2}[ -_0-9a-zA-Z]{0,512})’

A custom file type (for example ‘DSD Archive’) must be created and the header and footer signatures must be entered into the configuration file ‘File Type Signatures Search.txt’ as depicted below:


![alt text](http://y.delfi.ee/norm/306085/17256306_rfxjo4.png)

"Search at sector boundaries" must be enabled as in the picture.

This will create, in the carving results, the files (if there are files to carve) of ‘DSD Archive’ type.

##### Carving DSD files from a PCAP

This script, even though intended for disk media, is likely capable of carving DSD files from some other sources as well. In this Youtube video carving from network capture (PCAP) is shown. The PCAP is created by downloading a couple of DSD files and one MS Office Word file, situated in between DSD files, from a public organization's open document registry and recording the traffic with Wireshark. The script should and does carve out candidate DSD files only, and not MS Word Office document because of the custom DSD signature. For better results, script's 'algorithmic' option for footer identification can be enabled (in the code). This option can hopefully produce better results on 'raw' data, while 'footer' option is more friendly to geometric, "zero-slack" media images such as NTFS volumes on HDD. After carving the candidate DSD files from the PCAP with this script, an extra step is required to remove the so-called packet headers from the carved candidate files. This will produce the correct DSD files. In this video, uploaded to Youtube on 29 of May, the file-carving of DSD files from the network capture with an extra step of after-cutting the 'packet headers' is demonstrated. The removal of 'packet headers' from the candidate files as seen in the second part of video is based on a protocol-dependent regular expression in a separate "quick-fix" script. This after-cutting method is not recommended as long-term solution, used here for demonstration purposes only.

Youtube: https://youtu.be/a4eTfJsmeps

##### Integrating DSD file carving script with EnCase, a mainstream forensic suite

This Youtube video, uploaded on 28 of May, shows that the carving script can easily be integrated with such forensic GUI examination suite as EnCase (trademark of the respective owner). In the example the so-called 'unallocated clusters' file-object is passed to the script, to retrieve deleted DSD files. In the video, the script is launched from "File Viewer". A change of about two lines in the script code is required, to receive the passed file-object as commandline argument.

Youtube: https://youtu.be/gakuu6DHuPM

##### Integrating DSD file carving script with EnCase's EnScript, a mainstream forensic suite

This Youtube video, uploaded on 28 of May, takes as example the published Webinar (https://youtu.be/ZJ0Fr_Fmbig) dedicated to EnScript / Python integration. The video shows the EnScript code (based on the Webinar example) operating the DSD file carving script to carve files from the so-called 'unallocated clusters' of a foresic image. A change of about two lines or so in the script code is required, to receive the passed file-object as commandline argument and display resulting CSV file name.

Youtube: https://youtu.be/EhFVuHVSvd4
