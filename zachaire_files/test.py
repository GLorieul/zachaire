
import io
from build import *

def runTest(test):
    print(f"Running test \"{test.__name__}\"", end="")
    test()
    print()

def assert_true(statement):
    print(".", end="")
    assert(statement)

def assert_false(statement):
    assert_true(not statement)

def assert_eq(testedValue, refValue):
    print(".", end="")
    if testedValue != refValue:
        raise Exception(  "No equality:\n"
                       + f"\ttestedValue = \"{testedValue}\"\n"
                       + f"\trefValue    = \"{refValue}\"")

def test_getThumbnailName():
    assert_eq( getThumbnailName("abc.jpg"), "abc_thumb.jpg")



def test_isHeader():
    assert_true (isHeader("#Abc"))
    assert_true (isHeader("# Abc"))
    assert_true (isHeader("##Abc def"))
    assert_true (isHeader("## Abc def"))
    assert_false(isHeader("Abc def"))
    assert_false(isHeader("[Abc def"))

def test_parseHeaderLine():
    assert_eq( parseHeaderLine("#Abc")          , (1, "Abc"))
    assert_eq( parseHeaderLine("# Abc")         , (1, "Abc"))
    assert_eq( parseHeaderLine("##My header")   , (2, "My header"))
    assert_eq( parseHeaderLine("## My header  "), (2, "My header"))

def test_translateHeader():
    assert_eq(translateHeader("#Abc")          , "<h1>Abc</h1>")
    assert_eq(translateHeader("## My header  "), "<h2>My header</h2>")


def test_isEmptyLine():
    assert_true (isEmptyLine(""))
    assert_true (isEmptyLine(" "))
    assert_true (isEmptyLine("     "))
    assert_false(isEmptyLine("abc"))



def test_isImageLine():
    assert_true (isImageLine("[ainets][aisetn]"))
    assert_false(isImageLine("anisten"))
    assert_false(isImageLine("[ainset]"))
    assert_false(isImageLine("[ainset](naiste)"))
    assert_true (isImageLine("[][]"))

def test_parseImageLine():
    assert_eq( parseImageLine("[img.jpg][My image]"), ('img.jpg', 'My image') )
    assert_eq( parseImageLine("[img.jpg][ My image ]"), ('img.jpg', 'My image') )



runTest(test_getThumbnailName)

runTest(test_isHeader)
runTest(test_parseHeaderLine)
runTest(test_translateHeader)

runTest(test_isEmptyLine)

runTest(test_isImageLine)
runTest(test_parseImageLine)

