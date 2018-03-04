#!/usr/bin/env python3.6

#
# Kingdom Come Deliverance - inventory sorting generator
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

class Kcd_isg:
  def __init__(self, **kwargs):
    self.verbose = False
    self.version = '1.1'
    self.hard = False
    self.description = ''
    self.localizationPath = ''
    self.localizedCategories_ini = None
    self.categorizedItems_ini = None
    self.replacements_ini = None
    self.packagesPerLanguage = {
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
  
  # Start function
  def start(self):
    self.parseArguments()
    self.parseConfigFiles()
    try:
      for lang, pak in self.packagesPerLanguage.items():
          self.modifyPackage(lang)
    except KeyboardInterrupt:
      print(f'WARNING: You have interrupt the script execution. The output is probably broken, you can retry.')
      sys.exit(84);

  # Declare all args of the script
  # Assign variables localizationPath, verbose, hard according to args passed.
  def parseArguments(self):
    parser = argparse.ArgumentParser(
      prog='Kingdom Come Deliverance - inventory sorting generator',
      description=self.description,
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
    parser.add_argument(
      '--version',
      action='version',
      version=self.version,
      help='Print version information and exit'
    )
    args = parser.parse_args()
    self.localizationPath = args.localizationPath
    self.hard = args.hard
    self.verbose = args.verbose
  
  # Parse .ini files and fill localizedCategories_ini, categorizedItems_ini, replacements_ini globals variables.
  def parseConfigFiles(self):
    # Load localizedCategories.ini for prefixer for each language
    self.localizedCategories_ini = configparser.ConfigParser()
    self.localizedCategories_ini.read('localizedCategories.ini')
  
    # Load categorizedItems.ini for item's category association
    self.categorizedItems_ini = configparser.ConfigParser()
    self.categorizedItems_ini.read('categorizedItems.ini')
  
    # Load replacements.ini in order to override item's category association
    self.replacements_ini = configparser.ConfigParser()
    self.replacements_ini.optionxform = str
    self.replacements_ini.read('replacements.ini')
  
  # Open and unzip .pak by path specified as argument.
  # Return xml object representing item list.
  def getVanillaItemsXml(self, packagePath):
    zipFile = zipfile.ZipFile(packagePath)
    xmlFile = zipFile.open('text_ui_items.xml')
    zipFile.close()
    xmlRoot = xml.etree.ElementTree.fromstring(xmlFile.read().decode('utf8'))
    # Lowercase item id
    for itemIdNode in xmlRoot.findall(".//Cell[1]"):
      itemIdNode.text = itemIdNode.text.lower()
    return xmlRoot
  
  # Contains calls about replacements and prefixer adding.
  # Take the xml object representing item list and the wanted lang as parameters.
  def modifyXml(self, xmlRoot, lang):
    self.applyReplacement(xmlRoot, lang)
    self.addItemPrefixes(xmlRoot, lang)
  
  # Modify the xml object with replacement specifications contained in replacements.ini.
  # Take the xml object representing item list and the wanted lang as parameters.
  def applyReplacement(self, xmlRoot, lang):
    itemDescrNodes = xmlRoot.findall(".//Cell[3]")
  
    for pattern in self.replacements_ini[lang]:
      replacement = self.replacements_ini[lang][pattern].strip('"')
      if pattern[0] == 'r' :
        pattern = pattern[1:].strip('"')
      else:
        pattern = re.escape(pattern.strip('"'))
      prog = re.compile(pattern)
      for node in itemDescrNodes:
        if node.text == None: continue
        replacementTuple = prog.subn(replacement, node.text)
        if replacementTuple[1] > 0 :
          if self.verbose: print(f'replaced \'{pattern}\' by \'{replacement}\' {replacementTuple[1]} times')
          if self.verbose: print(f'before: {node.text}')
          node.text = replacementTuple[0].capitalize()
          if self.verbose: print(f'after : {node.text} \n')
  
  # Add prefix to items names.
  # Take the xml object representing item list and the wanted lang as parameters.
  def addItemPrefixes(self, xmlRoot, lang):
    for item,category in self.categorizedItems_ini.items('items'):
      cells = xmlRoot.findall(".//*[Cell='"+item+"']/Cell")
      if len(cells) < 3 :
        print(f'Warning: could not find item {item} for language {lang}.')
        continue
      prefix = self.localizedCategories_ini[lang][category].strip('"')
      # I assume cells[1] is only used for translators, uncomment if the game actually needs it
      #cells[1].text = prefix + str(cells[1].text or '')
      cells[2].text = prefix + str(cells[2].text or '')
  
  # Create the modified package with modified values.
  # Take the wanted lang as parameter.
  def modifyPackage(self, lang):
    packagePath = os.path.join(self.localizationPath, self.packagesPerLanguage[lang])
    if not os.path.exists(packagePath) and not self.hard:
      print(f'WARNING: File {self.packagesPerLanguage[lang]} was not found in {self.localizationPath}. We continue to build other .pak.', file=sys.stderr)
      return
    xmlRoot = self.getVanillaItemsXml(packagePath)
    self.modifyXml(xmlRoot, lang)
  
    modifiedPackagePath = os.path.join('modified', self.packagesPerLanguage[lang])
    if not os.path.exists('modified'):
      print(f'INFO: Create ./modified folder to place modified packages')
      os.makedirs('modified')
    copyfile(packagePath, modifiedPackagePath)
  
    zin = zipfile.ZipFile(packagePath, 'r')
    zout = zipfile.ZipFile(modifiedPackagePath, 'w')
    for item in zin.infolist():
      buffer = zin.read(item.filename)
      if(item.filename != 'text_ui_items.xml'):
        zout.writestr(item, buffer)
      else:
        zout.writestr('text_ui_items.xml', xml.etree.ElementTree.tostring(xmlRoot, encoding='utf8', method='xml'))
    zout.close()
    zin.close()
    modifiedPackagePathFull = os.path.join(os.path.dirname(os.path.realpath(__file__)), modifiedPackagePath)
    print(f'Created modded package {modifiedPackagePathFull}')

# Main function call
if __name__ == '__main__':
  isg = Kcd_isg()
  isg.start()
