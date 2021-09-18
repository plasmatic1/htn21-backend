from PIL import Image, ImageOps
import numpy as np
from typing import List

HEAT_LO = 5
HEAT_HI = 13

ALPHABET = 'abcdefghijklmnopqrstuvwxyz'

def convert_range(x, lo, hi):
	# return x * 2
	return lo + (x * (hi - lo) // 255)

def rgb2gray(img, size):
	img = img.resize((size, size), Image.ANTIALIAS)
	# img.show()
	gray_img = ImageOps.grayscale(img)
	grid = np.array(gray_img)
	print(grid)
	for i in range(size):
		for j in range(size):
			grid[i][j] = convert_range(grid[i][j], HEAT_LO, HEAT_HI)
	print(grid)
	

def generate_map(n: int) -> List[List[str]]:
    """
    Generate a nxn map of strings, where the length of each
    string is between HEAT_LO and HEAT_HI inclusive.
    Also enforces that for all A_ij, A_(i-1)(j+1) shares
    no characters with it.
    """
    heat = [
        [random.randint(HEAT_LO, HEAT_HI) for j in range(n)]
        for i in range(n)
    ]
    mp = [[''] * n for i in range(n)]
    for i in range(n):
        for j in range(n):
            cands = set(ALPHABET)
            if i - 1 >= 0 and j + 1 < n:
                cands -= set(mp[i - 1][j + 1])
            ltrs = random.sample(list(cands), heat[i][j])
            mp[i][j] = ''.join(ltrs)
    return mp

img = Image.open("secks.jpg")
rgb2gray(img, 10)
# print(convert_range(207, 5, 13))