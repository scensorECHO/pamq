<h1>Python Asset Management Query</h1>
This script utilizes Selenium and Python to parse standardized templates and data files to access the asset management webportal. All data/log files are ignored, and the script is otherwise unable to be utilized outside of the intranet.

Current issues of this version are inconsistent skips on relevant user data.
Possibly narrowed down to:
  - faulty data entry in the webportal, resulting in concatenated serials
  - multiple elements found on page, resulting in inconsistent interaction
  - insufficient delay for data loading, where web elements have not properly loaded yet

<h1>License</h1>
<br>
pamq is released under GNU GPLv3 License.
<br>
Copyright © 2015 Thomas Carrio
