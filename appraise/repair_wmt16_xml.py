#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Project: Appraise evaluation system
 Author: Christian Federmann <cfedermann@gmail.com>

usage: python repair_wmt16_xml.py
               [-h] [--dry-run]
               hits-file

Checks and repairs a given XML file containing HITs for WMT16. Uses
appraise.wmt16.validators.validate_hits_xml_file() for validation.

positional arguments:
  hits-file             XML file(s) containing HITs. Can be multiple files
                        using patterns such as '*.xml' or similar.

optional arguments:
  -h, --help            Show this help message and exit.
  --dry-run             Enable dry run to simulate repair.

"""
from django.core.exceptions import ValidationError

from time import sleep
import argparse
import os
import re
import sys

from xml.etree.ElementTree import fromstring, tostring

PARSER = argparse.ArgumentParser(description="Checks and repairs a given " \
  "XML file containing HITs for WMT16. Uses\nappraise.wmt16.validators." \
  "validate_hits_xml_file() for validation.")
PARSER.add_argument("hits_file", metavar="hits-file", help="XML file " \
  "containing HITs.")
PARSER.add_argument("--dry-run", action="store_true", default=False,
  dest="dry_run_enabled", help="Enable dry run to simulate repair.")


XML_REPAIR_PATTERNS = [
  ('& ', '&amp; '),
  ('&amp ', '&amp; '),
  ('&quot ', '&quot; '),
  ('R&D', 'R&amp;D'),
  ('R & D', 'R &amp; D'),
  ('A&E', 'A&amp;E'),
  ('CD&V', 'CD&amp;V'),
  ('CD & V', 'CD &amp; V'),
  ('>Grub<', '&gt;Grub&lt;'),
  ('S&P', 'S&amp;P'),
  ('S & P', 'S &amp; P'),
  ('&Poor ', '&amp;Poor '),
  ('&.', '&amp;.'),
  ('<службе', '&lt;службе'),
  ('<security', '&lt;security'),
  ('< ', '&lt; '),
  ('B&Q', 'B&amp;Q'),
  ('B&F', 'B&amp;F'),
  ('Q&A', 'Q&amp;A'),
  ('</p >', '&lt;/p &gt;'),
  ('<dollar-symbol>', '&lt;dollar-symbol&gt;'),
  ('Б&', 'Б&amp;'),
  ('B&S', 'B&amp;S'),
  ('b&', 'b&amp;'),
  ('B & Q', 'B &amp; Q'),
]


if __name__ == "__main__":
    args = PARSER.parse_args()
    
    # Properly set DJANGO_SETTINGS_MODULE environment variable.
    os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
    PROJECT_HOME = os.path.normpath(os.getcwd() + "/..")
    sys.path.append(PROJECT_HOME)
    
    # We have just added appraise to the system path list, hence this works.
    from appraise.wmt16.validators import validate_hits_xml_file

    with open(args.hits_file) as infile:
        hits_xml_string = str(infile.read(), "utf-8")
        loop_counter = 0
        
        while loop_counter < 10:
            print(("loop counter: ", loop_counter))
            loop_counter += 1

            try:
                # Validate XML before trying to import anything from the given file.
                validate_hits_xml_file(hits_xml_string)
                break

            except ValidationError as msg:
                print(msg)
                for key, value in XML_REPAIR_PATTERNS:
                    print((repr(key), "-->", repr(value)))
                    patched_hits_xml_string = str.replace(hits_xml_string, key, value)
                    hits_xml_string = patched_hits_xml_string
                    
                continue

    if not args.dry_run_enabled:
        fixed_filename = '{0}.fixed'.format(args.hits_file)
        print(('Writing fixed file to "{0}"...'.format(fixed_filename)))
        with open(fixed_filename, 'w') as outfile:
            outfile.write(hits_xml_string.encode('utf-8'))

