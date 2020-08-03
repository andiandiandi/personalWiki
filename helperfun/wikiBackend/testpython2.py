d = {"phrase":"phrase2"}

def fun(phrase,linespan=0,filepath=None):
	print(phrase)
	print(linespan)
	print(filepath)

fun(**d)