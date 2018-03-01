
Kingdom Come Deliverance - inventory sorting package generator by OVNI

This tool allows to create modified Kingdom Come Deliverance's localization packages
with prefix before items names to sort them as you want.


=== Usage ===

- categorizedItems.ini contains itemId/category pairs. You can create as many categories as you want.
- localizedCategories.ini contains localization for categories, every categories must be localized
(even if just copy/pasted) for every language.
- replacements.ini contains definition for replacements that will be applied before adding prefixes to item descriptions.

launch kcd_inventory_sorting_generator.py using python interpreter. eg:
kcd_inventory_sorting_generator.py --localizationPath=C:\KingdomComeDeliverance\Localization

A new subdirectory will be created among side kcd_inventory_sorting_generator.py, containing new modified packages.
Packages within localizationPath folder won't be modified.


=== Changelog ===

1.1
- added replacement feature
- added verbose option
- added some progress feedback


=== Credit ===

Default localizedCategories.ini is based on Inventory Sorter by papirnehezek ( nexusmods.com/kingdomcomedeliverance/mods/189 )


=== Legal Bullshit ===

Copyright 2018 OVNI
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
