import os

a = "C:\\Users\\Andre\\Desktop\\aWiki\\subfolder\\a.md"
b = "C:\\Users\\Andre\\Desktop\\aWiki\\b.md"

c = "C:\\Users\\Andre\\Desktop\\aWiki\\subfolder\\..\\test.md"
d = " C:/Users/Andre/Desktop/aWiki/subfolder\\..\\test.md"

qq = "C:\\Users\\Andre\\Desktop\\A"
qe = "C:\\Users\\Andre\\Desktop\\A\\b.md"
def path_is_parent(parent_path, child_path):
    # Smooth out relative path names, note: if you are concerned about symbolic links, you should use os.path.realpath too
    parent_path = os.path.abspath(parent_path)
    child_path = os.path.abspath(child_path)

    # Compare the common path of the parent and child path with the common path of just the parent path. Using the commonpath method on just the parent path will regularise the path name in the same way as the comparison that deals with both paths, removing any trailing path separator
    return os.path.commonpath([parent_path]) == os.path.commonpath([parent_path, child_path])

k = [1,2,3]
print(k[:2])