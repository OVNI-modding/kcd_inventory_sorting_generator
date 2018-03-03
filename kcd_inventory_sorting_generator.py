#!/usr/bin/env python3.6

#!python3.6
#
# Kingdom Come Deliverance - inventory sorting generator v1.1
#
# Copyright 2018 OVNI
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

description='''
	Tool to create package with prefix added to items.
	it needs a categorizedItems_ini.ini file containg "item_id = itemcategory" pairs,
	and localizedCategories_ini.ini file contianing "itemcategory=localizedText" pairs.
'''

import argparse
import re
import configparser
import zipfile
import xml.etree.ElementTree
import os.path
import os
import sys
from shutil import copyfile

# Initialize globals variables
verbose = False
localizationPath = ''
localizedCategories_ini = None
categorizedItems_ini = None
replacements_ini = None
packagesPerLanguage = {
	'english': 'english_xml.pak',
	'french': 'french_xml.pak',
	'chinese': 'chineses_xml.pak',
	'czech': 'czech_xml.pak',
	'german': 'german_xml.pak',
	'italian': 'italian_xml.pak',
	'polish': 'polish_xml.pak',
	'russian': 'russian_xml.pak',
	'spanish': 'spanish_xml.pak',
}

# Main function
def main():
	global localizationPath
	global packagesPerLanguage
	parseArguments()
	parseConfigFiles()
	for lang, pak in packagesPerLanguage.items():
		modifyPackage(lang)

# Declare all args of the script
# Assign variables localizationPath, verbose, hard according to args passed.
def parseArguments():
		global localizationPath
		global description
		global verbose
		global hard

		parser = argparse.ArgumentParser(
			prog='Kingdom Come Deliverance - inventory sorting generator',
			description=description,
		)
		parser.add_argument(
			'--hard',
			action='store_true',
			help='Treat warning as error'
		)
		parser.add_argument(
			'--localizationPath',
			'-l',
			required=True,
			help='Path of game\'s Localization folder, where english_xml.pak, etc. are stored'
		)
		parser.add_argument(
			'--verbose',
			action='store_true',
			help='verbose log'
		)

		args = parser.parse_args()
		localizationPath = args.localizationPath
		hard = args.hard
		verbose = args.verbose

# Parse .ini files and fill localizedCategories_ini, categorizedItems_ini, replacements_ini globals variables.
# localizedCategories.ini for prefixer for each language
# categorizedItems.ini for item's category association
# replacements.ini to override item's category association
def parseConfigFiles():
	global localizedCategories_ini
	global categorizedItems_ini
	global replacements_ini

	localizedCategories_ini = configparser.ConfigParser()
	localizedCategories_ini.read('localizedCategories.ini')

	categorizedItems_ini = configparser.ConfigParser()
	categorizedItems_ini.read('categorizedItems.ini')

	replacements_ini = configparser.ConfigParser()
	replacements_ini.optionxform = str
	replacements_ini.read('replacements.ini')

# Open and unzip .pak by path specified as argument.
# Return xml object representing item list.
def getVanillaItemsXml( packagePath ):
	zipFile = zipfile.ZipFile(packagePath)
	xmlFile = zipFile.open('text_ui_items.xml')
	zipFile.close()
	xmlRoot = xml.etree.ElementTree.fromstring( xmlFile.read().decode('utf8') )
	# lower item id
	for itemIdNode in xmlRoot.findall( ".//Cell[1]" ):
		itemIdNode.text = itemIdNode.text.lower()
	return xmlRoot

# Contains calls about replacements and prefixer adding.
# Take the xml object representing item list and the wanted lang as parameters.
def modifyXml( xmlRoot, lang ):
	applyReplacement(xmlRoot, lang)
	addItemPrefixes(xmlRoot, lang)

# Modify the xml object with replacement specifications contained in replacements.ini.
# Take the xml object representing item list and the wanted lang as parameters.
def applyReplacement( xmlRoot, lang ):
	global replacements_ini
	global verbose

	itemDescrNodes = xmlRoot.findall( ".//Cell[3]" )

	for pattern in replacements_ini[lang]:
		replacement = replacements_ini[lang][pattern].strip('"')
		if pattern[0] == 'r' :
			pattern = pattern[1:].strip('"')
		else:
			pattern = re.escape( pattern.strip('"') )
		prog = re.compile(pattern)
		for node in itemDescrNodes:
			if node.text == None: continue
			replacementTuple = prog.subn( replacement, node.text )
			if replacementTuple[1] > 0 :
				if verbose: print( f'replaced \'{pattern}\' by \'{replacement}\' {replacementTuple[1]} times')
				if verbose: print( f'before: {node.text}' )
				node.text = replacementTuple[0].capitalize()
				if verbose: print( f'after : {node.text} \n' )

# Add prefix to items names.
# Take the xml object representing item list and the wanted lang as parameters.
def addItemPrefixes( xmlRoot, lang ):
	global categorizedItems_ini
	global localizedCategories_ini
	
	for item,category in categorizedItems_ini.items('items'):
		cells = xmlRoot.findall( ".//*[Cell='"+item+"']/Cell" )
		if len(cells) < 3 :
			print( f'Warning: could not find item {item} for language {lang}.' )
			continue
		prefix = localizedCategories_ini[lang][category].strip('"')
		# I assume cells[1] is only used for translators, uncomment if the game actually needs it
		#cells[1].text = prefix + str(cells[1].text or '')
		cells[2].text = prefix + str(cells[2].text or '')

# Create the modified package with modified values.
# Take the wanted lang as parameter.
def modifyPackage( lang ):
	global localizationPath
	global packagesPerLanguage

	packagePath = os.path.join( localizationPath, packagesPerLanguage[lang] )
	if not os.path.exists(packagePath) and not hard:
		print( f'WARNING: File {packagesPerLanguage[lang]} was not found in {localizationPath}. We continue to build other .pak.', file=sys.stderr)
		return
	xmlRoot = getVanillaItemsXml(packagePath)
	modifyXml(xmlRoot, lang)

	modifiedPackagePath = os.path.join( 'modified', packagesPerLanguage[lang] )
	if not os.path.exists('modified'):
		os.makedirs('modified')
	copyfile(packagePath, modifiedPackagePath)

	zin = zipfile.ZipFile(packagePath, 'r')
	zout = zipfile.ZipFile(modifiedPackagePath, 'w')
	for item in zin.infolist():
		buffer = zin.read(item.filename)
		if( item.filename != 'text_ui_items.xml' ):
			zout.writestr(item, buffer)
		else:
			zout.writestr('text_ui_items.xml', xml.etree.ElementTree.tostring(xmlRoot, encoding='utf8', method='xml') )
	zout.close()
	zin.close()
	modifiedPackagePathFull = os.path.join( os.path.dirname(os.path.realpath(__file__)), modifiedPackagePath )
	print( f'Created modded package {modifiedPackagePathFull}' )

# Main function call
if __name__ == '__main__':
    main()
