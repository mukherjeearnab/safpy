import jpype
from jpype import startJVM, shutdownJVM, addClassPath, JClass, JInt

startJVM(classpath=['/home/arnab/.apron_bin/apron.jar',
                    '/home/arnab/.apron_bin/gmp.jar'])


class apron(object):
    '''
    Apron Wrapper Class
    '''

    Abstract0 = jpype.JClass("apron.Abstract0")
    Manager = jpype.JClass("apron.Manager")
    Interval = jpype.JClass("apron.Interval")
    Abstract0 = jpype.JClass("apron.Abstract0")
    Box = jpype.JClass("apron.Box")
    Octagon = jpype.JClass("apron.Octagon")
    ApronException = jpype.JClass("apron.ApronException")
    MpqScalar = jpype.JClass("apron.MpqScalar")
    Linterm0 = jpype.JClass("apron.Linterm0")
    Linexpr0 = jpype.JClass("apron.Linexpr0")
    Texpr0BinNode = jpype.JClass("apron.Texpr0BinNode")
    Texpr0CstNode = jpype.JClass("apron.Texpr0CstNode")
    Texpr0Node = jpype.JClass("apron.Texpr0Node")
    Texpr0Intern = jpype.JClass("apron.Texpr0Intern")
    Texpr0DimNode = jpype.JClass("apron.Texpr0DimNode")


class java(object):
    '''
    Java Utilitites Wrapper Class
    '''

    Arrays = jpype.JClass("java.util.Arrays")
