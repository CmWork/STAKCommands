from beta.devtest.stakunittest.Level1 import GetValue10
import beta.devtest.stakunittest.Level1_String


def Get_Both_Level_Values():
    return 10 + GetValue10()


def Get_Both_Level_String():
    return "Level 2 String and " + \
           beta.devtest.stakunittest.Level1_String.GetMyString2()
