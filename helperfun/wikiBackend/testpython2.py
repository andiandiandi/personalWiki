import itertools

l1 = set([4,7])
l2 = set([5])
l3 = set([6,7])

#4,5,6
#4,5,6
def findout(tupl, linespan = 0):
	for t in tupl:
		found = True
		for x in tupl:
			if t == x:
				continue
			else:
				if not abs(t-x) <= linespan:
					found = False
					break;
		if found:
			print("found:",tupl)
			return True

	print("not found:",tupl)
	return False

concatList = [l1,l2,l3]
def solve(l):

	if len(l) > 1:
		for e in itertools.product(*l):
			findout(e,linespan = 1)
			print("_______")
	else:
		return l

solve(concatList)