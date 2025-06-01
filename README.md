# TLDModCompatibilityChecker
Web crawler to check patch mapping for tld mods. Intended for use with invasive frameworks to ensure you aren't breaking other mods, or so you can reach out and discuss fixes *before* breaks occur.

Usage:

1) Run Test.py, ensure it works.

2) Run Checker.py with argument --site-data-url with a valid URL for list of mod lists. This one uses the same list as tldmods.com. 

(I am not going to publish any URLs here as they may change, if you need ask in the modding discord for help locating the needed URL for your purposes)

3) Check the folder you ran Checker.py in for "patch_map.json" which maps mods against patches, and "mod_cache.json" which keeps track of last time each mod was analyzed to reduce subsequent run times. Also provides a map of patches against mods in case it's helpful to someone.
