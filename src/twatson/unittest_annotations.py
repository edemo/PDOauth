#!/usr/bin/env python

"""
    this code is stolen from http://code.activestate.com/recipes/511475/,
    and greatly lobotomized
"""
__author__ = "Tim Watson"
__license__ = "Python"

__all__ = [
    'test',
    'Fixture'
]

import unittest

class TestDeclaration( object ):
    declarations = {}
    def __init__( self, func, doc_string=None ):
        if func.func_name.startswith( "test" ): return
        func.__doc__ = doc_string or func.__doc__
        fname = "test_%s" % func.func_name
        if not fname in TestDeclaration.declarations:
            TestDeclaration.declarations[ fname ] = func

class TestFixtureManager( type ):
    def __new__( cls, name, bases, attrs ):
        new_class = type.__new__( cls, name, bases, attrs )
        if not bases: return new_class
        [ setattr( new_class, func_name, func )
            for func_name, func in TestDeclaration.declarations.iteritems() ]
        TestDeclaration.declarations.clear()
        return new_class

    def __init__( cls, name, bases, thedict ):
        #todo: deal with fixture setup/teardown here!
        pass

class Fixture( unittest.TestCase ): __metaclass__ = TestFixtureManager

def test( func, doc_string=None ):
    return TestDeclaration( func, doc_string )

