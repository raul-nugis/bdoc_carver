This script will read raw image and apply header and footer to carve DSD (try this to recover BDOC, ACISE, ASC, ADOC, EDOC digitally signed files) data based on certain headers and footers on contiguous clustered media. Alternatively, it will apply ‘algorithmic’ read of ZIP containers' Central Directory End Record's ‘ZIP file comment’. With additional changes in ‘geometry’ section this should enable carving from unstructured media.

Instead of using the header and footer regular expressions provided in the code with a script, use them with a carving tool. Adjustments in syntax may be required.

In X-Ways (tested with 19.5) the following syntax is to be used.
Header: ‘PK\x03\x04(.|\s){26}mimetype(.|\s){0,36}(application/vnd\.etsi\.asic\-e\+zip|K,\(\xc8\xc9LN,\xc9\xcc\xcf\xd3\/\xcbK\xd1K)’
Footer: ‘PK\x05\x06\x00\x00.{14}(\x00{2}|.{2}[ -_0-9a-zA-Z]{0,512})’

A custom file type (for example ‘DSD Archive’ ) must be created and the header and footer signatures must be entered into the configuration file ‘File Type Signatures Search.txt’ as depicted below:

![alt text](http://y.delfi.ee/norm/306085/17256306_rfxjo4.png)

Search at sector boundaries must be enabled as in the picture.

This will create, in the carving results, the files (if there are files to carve) of ‘DSD Archive’ type.
