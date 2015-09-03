#!/usr/local/bin/python
# encoding: utf-8
'''
applicationtool -- a tool to handle applications

you can register applications with it

@author:     Magosányi Árpád

@copyright:  2015 Informatikusok az e-demokráciáért. All rights reserved.

@license:    GPL v3

@contact:    mag@magwas.rulez.org
@deffield    updated: Updated
'''

import sys
import os

from argparse import ArgumentParser, ONE_OR_MORE
from argparse import RawDescriptionHelpFormatter
from pdoauth.models.Application import Application
from pdoauth.models.AppAssurance import AppAssurance

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
    program_shortdesc = "applicationtool -- a tool to handle applications"
    program_license = '''%s

  Created by Árpád Magosányi on %s.
  Copyright 2015 Informatikusok az catchedException-demokráciáért. All rights reserved.

  Licensed under GNU GPL v3

  Distributed on an "AS IS" basis without warranties
  or conditions of any kind, either express or implied.

USAGE
''' % (program_shortdesc, str(__date__))

    try:
        # Setup argument parser
        parser = ArgumentParser(description=program_license, formatter_class=RawDescriptionHelpFormatter)
        parser.add_argument("-v", "--verbose",dest="verbose", action="count",
            help="set verbosity level [default: %(default)s]")
        parser.add_argument('-V', '--version', action='version', version=program_version_message)
        parser.add_argument(dest="name",
            help="name of the application", metavar="name", nargs=1)
        parser.add_argument(dest="secret",
            help="application secret", metavar="secret", nargs=1)
        parser.add_argument(dest="redirectUri",
            help="the oauth2 redirect uri for the application", metavar="redirectUri", nargs=1)
        parser.add_argument(dest="assurances",
            help="assurances handled by the application", metavar="assurances", nargs=ONE_OR_MORE)

        # Process arguments
        args = parser.parse_args()

        verbose = args.verbose
        name = args.name[0]
        secret = args.secret[0]
        redirectUri = args.redirect_uri[0]
        assurances = args.assurances
        return do_main(verbose, name, secret, redirectUri, assurances)

    except KeyboardInterrupt:
        ### handle keyboard interrupt ###
        return 0
    except Exception, catchedException:
        if DEBUG or TESTRUN:
            raise catchedException
        indent = len(program_name) * " "
        sys.stderr.write(program_name + ": " + repr(catchedException) + "\n")
        sys.stderr.write(indent + "  for help use --help")
        return 2

def do_main(verbose, name, secret, redirectUri, assurances):
    if verbose > 0:
        print("registering application {0} with secret {1} at {2}".format(name, secret, redirectUri))
    app = Application.new(name, secret, redirectUri)
    for assurance in assurances:
        AppAssurance(app,assurance).save()
    if app is None:
        print "already existing app with this name: {0}".format(name)
        return 2
    print "id of the app is: {0}".format(app.appid)
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
