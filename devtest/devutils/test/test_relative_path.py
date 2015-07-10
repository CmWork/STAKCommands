from beta.devtest.stakunittest.Level1 import GetValue25
from beta.devtest.stakunittest.Level1_String import GetMyString
from beta.devtest.stakunittest.devutils.Level2 import Get_Both_Level_Values
from beta.devtest.stakunittest.devutils.Level2 import Get_Both_Level_String


def test_All():
    assert GetValue25() == 25
    assert GetMyString() == "My String"
    assert Get_Both_Level_Values() == 20
    assert Get_Both_Level_String() == "Level 2 String and My String 1"
