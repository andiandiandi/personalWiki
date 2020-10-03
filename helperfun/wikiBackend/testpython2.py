import os

a = "C:\\Users\\Andre\\Desktop\\aWiki\\subfolder\\a.md"
b = "C:\\Users\\Andre\\Desktop\\aWiki\\b.md"

c = "C:\\Users\\Andre\\Desktop\\aWiki\\subfolder\\..\\test.md"
d = " C:/Users/Andre/Desktop/aWiki/subfolder\\..\\test.md"

def a(s):
	try:
		print("a")
		return s
	except Exception as E:
		print("exception: " + str(E))
	finally:
		print("finally")

a(2)