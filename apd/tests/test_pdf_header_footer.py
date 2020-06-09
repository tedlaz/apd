import os
from apd import pdf_header_footer as phf

dir_path = os.path.dirname(os.path.realpath(__file__))


def test1():
    bfile = os.path.join(dir_path, 'apd.txt')
    phf.makepdf_from_txt(bfile)
