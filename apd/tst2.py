import fpdf


class PDF(fpdf.FPDF):
    def header(self):
        # Logo
        #self.image('logo_pb.png', 10, 8, 33)
        # Arial bold 15
        self.set_font('calibri', '', 12)
        # Move to the right
        #self.cell(80)
        # Title
        self.cell(0, 5, 'ΣΥΝΟΔΕΥΤΙΚΟ ΕΝΤΥΠΟ Α.Π.Δ.', 0, 1, 'C')
        self.cell(0, 5, 'ΥΠΟΒΑΛΛΟΜΕΝΗΣ ΣΕ ΗΛΕΚΤΡΟΝΙΚΗ ΜΟΡΦΗ (Δισκέτα ή CD)', 0, 1, 'C')
        # Line break
        self.ln(1)

    # Page footer
    def footer(self):
        # Position at 1.5 cm from bottom
        self.set_y(-15)
        # Arial italic 8
        self.set_font('calibri', '', 8)
        # Page number
        self.cell(0, 10, f'Σελίδα: {self.page_no()} ' + '/ {nb}', 0, 0, 'C')

# Instantiation of inherited class
pdf = PDF()
pdf.add_font("calibri", style="", fname="./fonts/DejaVuSansMono.ttf", uni=True)
pdf.alias_nb_pages()
pdf.add_page()
pdf.set_font('calibri', '', 10)
pdf.cell(0, 4, f'123456789 123456789 123456789 123456789 123456789 123456789 123456789 123456789 1234567', 0, 1)
for i in range(1, 1200):
    pdf.cell(0, 4, f'Εκτύπωση γραμμής {i:5} 10.000,23', 0, 1)
    pdf.cell(0, 4, f'Εκτύπωση γραμμής {i+1:5} 10.000,24', 0, 1)
pdf.output('tuto2.pdf', 'F')
