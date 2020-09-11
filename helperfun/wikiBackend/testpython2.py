import os

a = "C:\\Users\\Andre\\Desktop\\aWiki\\subfolder\\a.md"
b = "C:\\Users\\Andre\\Desktop\\aWiki\\b.md"

c = "C:\\Users\\Andre\\Desktop\\aWiki\\subfolder\\..\\test.md"
d = " C:/Users/Andre/Desktop/aWiki/subfolder\\..\\test.md"

print(os.path.normpath(d))