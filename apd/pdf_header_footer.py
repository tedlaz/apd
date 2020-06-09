import os
import fpdf
dir_path = os.path.dirname(os.path.realpath(__file__))
font_dir = os.path.join(dir_path, 'fonts')
fnormal = os.path.join(font_dir, 'DejaVuSansMono.ttf')
fbold = os.path.join(font_dir, 'DejaVuSansMono-Bold.ttf')


class PDF(fpdf.FPDF):
    def __init__(self, head1, head2):
        super().__init__()
        self.head1 = head1
        self.head2 = head2
        self.add_font("fnormal", style="", fname=fnormal, uni=True)
        self.add_font("fnormal", style="b", fname=fbold, uni=True)

    def header(self):
        self.set_font('fnormal', 'b', 12)
        self.cell(0, 5, self.head1, 0, 1, 'C')
        self.cell(0, 5, self.head2, 0, 1, 'C')
        # Line break
        self.ln(10)

    def footer(self):
        # Position at 1.5 cm from bottom
        self.set_y(-15)
        self.set_font('fnormal', '', 8)
        # Page number
        self.cell(0, 10, f'Σελίδα: {self.page_no()} ' + '/ {nb}', 0, 0, 'C')


def makepdf_from_txt(txtfile):

    with open(txtfile) as fil:
        pdf = PDF(next(fil).rstrip(), next(fil).rstrip())
        pdf.alias_nb_pages()
        pdf.add_page()
        pdf.set_font('fnormal', '', 10)
        # print('---->', pdf.head1)
        for lin in fil.readlines():
            pdf.cell(0, 4, f'{lin.rstrip()}', 0, 1)
        pdf.output('tuto2.pdf', 'F')
