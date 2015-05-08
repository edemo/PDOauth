#!/usr/local/bin/python2.7
# encoding: utf-8
'''
assurancetool -- a tool to handle assurances

you can add assurance to users with it

It defines classes_and_methods

@author:     Magosányi Árpád

@copyright:  2015 Informatikusok az e-demokráciáért. All rights reserved.

@license:    GPL v3

@contact:    mag@magwas.rulez.org
@deffield    updated: Updated
'''

import sys
import os

from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter
from pdoauth.models.User import User
from pdoauth.models.Assurance import Assurance
import time

__all__ = []
__version__ = 0.1
__date__ = '2015-05-09'
__updated__ = '2015-05-09'

DEBUG = 0
TESTRUN = 0
PROFILE = 0

class CLIError(Exception):
    '''Generic exception to raise and log different fatal errors.'''
    def __init__(self, msg):
        super(CLIError).__init__(type(self))
        self.msg = "E: %s" % msg
    def __str__(self):
        return self.msg
    def __unicode__(self):
        return self.msg

def main(argv=None): # IGNORE:C0111
    '''Command line options.'''

    if argv is None:
        argv = sys.argv
    else:
        sys.argv.extend(argv)

    program_name = os.path.basename(sys.argv[0])
    program_version = "v%s" % __version__
    program_build_date = str(__updated__)
    program_version_message = '%%(prog)s %s (%s)' % (program_version, program_build_date)
    program_shortdesc = "assurancetool -- a tool to handle assurances"
    program_license = '''%s

  Created by Árpád Magosányi on %s.
  Copyright 2015 Informatikusok az e-demokráciáért. All rights reserved.

  Licensed under GNU GPL v3

  Distributed on an "AS IS" basis without warranties
  or conditions of any kind, either express or implied.

USAGE
''' % (program_shortdesc, str(__date__))

    try:
        # Setup argument parser
        parser = ArgumentParser(description=program_license, formatter_class=RawDescriptionHelpFormatter)
        parser.add_argument("-v", "--verbose",dest="verbose", action="count", help="set verbosity level [default: %(default)s]")
        parser.add_argument('-V', '--version', action='version', version=program_version_message)
        parser.add_argument(dest="email",
            help="email address of the user", metavar="email", nargs=1)
        parser.add_argument(dest="assurer",
            help="email address of the assurer, or 'self' for the user", metavar="assurer", nargs=1)
        parser.add_argument(dest="assurance",
            help="assurance to add", metavar="assurance", nargs='+')

        # Process arguments
        args = parser.parse_args()

        verbose = args.verbose
        email = args.email[0]
        assurer_email = args.assurer[0]
        assurances = args.assurance
        return do_main

    except KeyboardInterrupt:
        ### handle keyboard interrupt ###
        return 0
    except Exception, e:
        if DEBUG or TESTRUN:
            raise(e)
        indent = len(program_name) * " "
        sys.stderr.write(program_name + ": " + repr(e) + "\n")
        sys.stderr.write(indent + "  for help use --help")
        return 2

def do_main(verbose, email, assurer_email, assurances):
        if verbose > 0:
            print("Setting assurances {0} for user {1} by {2}".format(assurances, email, assurer_email))
        user = User.getByEmail(email)
        if user is None:
            print "no such user: {0}".format(email)
            return 2
        if assurer_email == 'self':
            assurer = user
        else:
            assurer = User.getByEmail(assurer_email)
        if user is None:
            print "no such assurer: {0}".format(assurer_email)
            return 2
        for ass in assurances:
            if verbose > 1:
                print("Setting assurance {0} for user {1} by {2}".format(ass, email, assurer_email))
            Assurance.new(user, ass, assurer, time.time())
        return 0

if __name__ == "__main__":
    if DEBUG:
        sys.argv.append("-h")
        sys.argv.append("-v")
        sys.argv.append("-r")
    if TESTRUN:
        import doctest
        doctest.testmod()
    if PROFILE:
        import cProfile
        import pstats
        profile_filename = 'assurancetool_profile.txt'
        cProfile.run('main()', profile_filename)
        statsfile = open("profile_stats.txt", "wb")
        p = pstats.Stats(profile_filename, stream=statsfile)
        stats = p.strip_dirs().sort_stats('cumulative')
        stats.print_stats()
        statsfile.close()
        sys.exit(0)
    sys.exit(main())