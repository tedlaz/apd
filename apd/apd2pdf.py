import os
import argparse
import fpdf
from . import fixed_text_file as ftf
dir_path = os.path.dirname(os.path.realpath(__file__))
font_dir = os.path.join(dir_path, 'fonts')
fnormal = os.path.join(font_dir, 'DejaVuSansMono.ttf')
fbold = os.path.join(font_dir, 'DejaVuSansMono-Bold.ttf')


class PDF(fpdf.FPDF):
    def __init__(self, headdata):
        super().__init__()
        self.headdata = headdata
        self.add_font("fnormal", style="", fname=fnormal, uni=True)
        self.add_font("fnormal", style="b", fname=fbold, uni=True)

    def header(self):
        self.set_font('fnormal', 'b', 12)
        self.cell(0, 5, 'ΣΥΝΟΔΕΥΤΙΚΟ ΕΝΤΥΠΟ Α.Π.Δ.', 0, 1, 'C')
        self.cell(
            0, 5, 'ΥΠΟΒΑΛΛΟΜΕΝΗΣ ΣΕ ΗΛΕΚΤΡΟΝΙΚΗ ΜΟΡΦΗ (Δισκέτα ή CD)', 0, 1, 'C')
        self.ln(10)

    def heada1(self):
        self.set_font('fnormal', '', 12)
        for lin in self.headdata.split('\n'):
            self.cell(0, 5, lin, 0, 1)
        # Line break
        self.ln(3)

    def heada0(self):
        self.set_font('fnormal', 'b', 12)
        self.cell(0, 5, 'ΑΝΑΛΥΤΙΚΗ ΠΕΡΙΟΔΙΚΗ ΔΗΛΩΣΗ', 0, 1, 'C')
        # Line break
        self.ln(3)

    def footer(self):
        # Position at 1.5 cm from bottom
        self.set_y(-15)
        self.set_font('fnormal', '', 8)
        # Page number
        self.cell(0, 10, f'Σελίδα: {self.page_no()} από ' + '{nb}', 0, 0, 'C')


def run(apd_file):
    apd = ftf.apd_builder()
    apd.parse(apd_file)
    lines = apd.for_report()
    head0 = apd.print_company_data()
    head2 = apd.print_header()
    # print(lines)
    synodeytiko = apd.synodeftiko()
    pdf = PDF(head2)
    pdf.alias_nb_pages()
    pdf.add_page()
    pdf.set_font('fnormal', '', 10)
    for lns in synodeytiko.split('\n'):
        pdf.cell(0, 4, f'{lns.rstrip()}', 0, 1)
    pdf.header = pdf.heada0
    pdf.add_page()
    for lns in head0.split('\n'):
        pdf.header = pdf.heada1
        pdf.cell(0, 4, f'{lns.rstrip()}', 0, 1)
    for lin in lines:
        for col in lin:
            pdf.cell(0, 4, f'{col.rstrip()}', 0, 1)
        # pdf.add_page()
    pdf.cell(0, 4, '', 0, 1)
    pdf.cell(0, 4, '', 0, 1)
    final = '       Ο ΔΗΛΩΝ ΕΡΓΟΔΟΤΗΣ                                          Ο ΠΑΡΑΛΑΒΩΝ'
    pdf.cell(0, 4, final, 0, 1)
    out_filename = f'{apd_file}.pdf'
    pdf.output(out_filename, 'F')
    return out_filename


if __name__ == '__main__':
    prs = argparse.ArgumentParser(description='APD to PDF')
    prs.add_argument('apdfile', help='APD file')
    prs.add_argument('--version', action='version', version='0.1')
    arg = prs.parse_args()
    if not os.path.isfile(arg.apdfile):
        print('File %s does not exist' % arg.apdfile)
    else:
        run(arg.apdfile)
