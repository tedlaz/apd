from collections import defaultdict
from abc import ABC, abstractmethod
from apd.utils import grup, dec2gr


class ColumnType(ABC):
    @abstractmethod
    def render(self, value, size: int) -> str:
        pass

    @abstractmethod
    def reverse(self, textline):
        pass

    def fill_front_zeros(self, txtval: str, size: int) -> str:
        len_txtval = len(txtval)
        if len_txtval > size:
            raise ValueError('Value is bigger than size')
        return '0' * (size - len_txtval) + txtval

    def fill_back_spaces(self, txtval: str, size: int) -> str:
        len_txtval = len(txtval)
        if len_txtval > size:
            raise ValueError('Value is bigger than size')
        return txtval + ' ' * (size - len_txtval)

    def grformat(self, value):
        return value


class ColText(ColumnType):
    def render(self, value, size: int) -> str:
        return self.fill_back_spaces(value, size)

    def reverse(self, txtvalue: str):
        return txtvalue.strip()

    def grformat(self, value):
        return value.strip()


class ColTextCapital(ColText):
    def render(self, value, size: int) -> str:
        return self.fill_back_spaces(grup(value), size)


class ColDate(ColumnType):
    def render(self, value, size: int) -> str:
        if value.strip() == '':
            return self.fill_back_spaces(value, size)
        yyyy, mm, dd = value.split('-')
        return f'{dd}{mm}{yyyy}'

    def reverse(self, txtvalue: str):
        if txtvalue.strip() == '':
            return ''
        dd = txtvalue[:2]
        mm = txtvalue[2:4]
        yyyy = txtvalue[4:8]
        return f'{yyyy}-{mm}-{dd}'

    def grformat(self, value):
        if value.strip() == '':
            return ''
        yyyy, mm, dd = value.split('-')
        return f'{dd}/{mm}/{yyyy}'
        # return f'{value}'


class ColPoso(ColumnType):
    def render(self, poso, size: int) -> str:
        poso = f'{poso:.2f}'.replace('.', '')
        return self.fill_front_zeros(poso, size)

    def reverse(self, txtvalue):
        return float(f'{txtvalue[:-2]}.{txtvalue[-2:]}')

    def grformat(self, value):
        return dec2gr(value)


class ColInt(ColumnType):
    def render(self, poso, size: int) -> str:
        poso = int(poso)
        return self.fill_front_zeros(str(poso), size)

    def reverse(self, txtvalue):
        return int(txtvalue)

    def grformat(self, value):
        return int(value)


class ColIntSpace(ColumnType):
    def render(self, poso, size: int) -> str:
        poso = int(poso)
        return self.fill_front_zeros(str(poso), size)

    def reverse(self, txtvalue):
        return int(txtvalue)

    def grformat(self, value):
        if int(value) == 0:
            return ''
        return int(value)


class ColTextInt(ColumnType):
    def render(self, poso, size: int) -> str:
        poso = int(poso)
        return self.fill_front_zeros(str(poso), size)

    def reverse(self, txtvalue):
        return txtvalue.strip()

    def grformat(self, value):
        return value.strip()


class Col:
    def __init__(self, name: str, lbl: str, typos: ColumnType, size: int) -> None:
        self.name = name
        self.lbl = lbl
        self.column_type = typos
        self.size = size

    def render(self, value):
        return self.column_type.render(value, self.size)

    def read(self, txtvalue):
        return self.column_type.reverse(txtvalue)

    def with_greek_lbl(self, value):
        return f'{self.lbl:25} {self.column_type.grformat(value)}'

    def __str__(self):
        return f'{self.name:30} {self.size:4}'


class LineType:
    def __init__(self, name, prefix):
        self.name = name
        self.prefix = prefix
        self.columns = []
        self.colbyname = {}

    def __str__(self):
        st1 = f'LineType {self.name!r}, lineSize={self.size}\n'
        st1 += f"{'prefix':30} {self.prefix:>4}\n"
        for col in self.columns:
            st1 += f'{str(col)}\n'
        return st1

    @property
    def size(self):
        return sum(c.size for c in self.columns) + len(self.prefix)

    def add_col(self, column: Col) -> None:
        self.columns.append(column)
        self.colbyname[column.name] = column

    def render(self, data: dict) -> str:
        stx = f'{self.prefix}'
        for column in self.columns:
            stx += column.render(data[column.name])
        return stx

    def with_greek_lbl(self, data: dict) -> str:
        return '\n'.join([c.with_greek_lbl(data[c.name]) for c in self.columns])

    def for_report(self, data: dict) -> str:
        return '\n'.join([c.with_greek_lbl(data[c.name]) for c in self.columns])

    def read(self, textline: str):
        if not textline.startswith(self.prefix):
            raise ValueError(f'textline({textline}) is not compatible')
        if len(textline) != self.size:
            raise ValueError(
                f'textline({textline}) size ({len(textline)}) is not correct')
        arr = {}
        apo = eos = len(self.prefix)
        for column in self.columns:
            eos = column.size + apo
            arr[column.name] = column.read(textline[apo:eos])
            apo = eos
        return arr


class LineTypeTotals(LineType):
    def __init__(self, name, prefix):
        super().__init__(name, prefix)
        self.linetype = '1.Genika'

    def for_report(self, data):
        return [c.with_greek_lbl(data[c.name]) for c in self.columns]


class LineTypeErg(LineType):
    def __init__(self, name, prefix):
        super().__init__(name, prefix)
        self.linetype = '2.StoixeiaAsfalismenoy'

    def for_report(self, data):
        return [c.with_greek_lbl(data[c.name]) for c in self.columns]


class LineTypeApod(LineType):
    def __init__(self, name, prefix):
        super().__init__(name, prefix)
        self.linetype = '3.StoixeiaAsfalisis'

    def for_report(self, data):
        vls = []
        vls.append(
            f"{'ΑΡ.ΠΑΡΑΡΤ/ΚΑΔ':25} {data['parartima_no']}/{data['kad']}")
        pro = 'OXI' if data['plires_orario'] == '0' else 'NAI'
        oer = 'OXI' if data['oles_ergasimes'] == '0' else 'NAI'
        vls.append(f"{'ΠΛΗΡΕΣ ΩΡΑΡΙΟ':25} {pro}")
        vls.append(f"{'ΟΛΕΣ ΕΡΓΑΣΙΜΕΣ':25} {pro}")
        vls = vls + [c.with_greek_lbl(data[c.name]) for c in self.columns[4:8]]
        vls.append(
            f"{'ΜΙΣΘΟΛ.ΠΕΡΙΟΔOΣ':25} {data['mismina']} / {data['misetos']}")
        vls = vls + [c.with_greek_lbl(data[c.name]) for c in self.columns[10:]]
        vls.append('\n')
        return vls


class LineTypeTerminator(LineType):
    def __init__(self, name, prefix):
        super().__init__(name, prefix)
        self.linetype = '4.eof'

    def for_report(self, data):
        return []


class Document:
    def __init__(self) -> None:
        self.linetypes = {}
        self.lines = []
        self.ergnoi = {}
        self.total_ergnoi = 0

    def __str__(self):
        lines = ['ΑΠΔ Αναλυτικά']
        for line in self.lines:
            for key, val in line.items():
                lines.append(f'{key:<30}: {val:14}')
            lines.append('')
        return '\n'.join(lines)

    def add_linetype(self, linetype) -> None:
        if linetype.prefix in self.linetypes.keys():
            raise ValueError(
                f'Linetype with code={linetype.prefix!r} already exists')
        if linetype.name in self.linetype_names:
            raise ValueError(
                f'Linetype with name={linetype.name!r} already exists')
        self.linetypes[linetype.prefix] = linetype

    @property
    def linetype_names(self) -> list:
        return [i.name for i in self.linetypes.values()]

    def add_line(self, line):
        self.lines.append(line)

    def linetypes_report(self):
        st1 = 'Document with template lines:\n'
        st1 += '\n'.join(str(ltype) for ltype in self.linetypes.values())
        return st1

    def render(self):
        lst = [self.linetypes[i['line_code']].render(i) for i in self.lines]
        return '\n'.join(lst)

    def synodeftiko(self):
        lin = self.lines[0]
        apod = dec2gr(lin['apodoxes'])
        eisf = dec2gr(lin['eisfores'])
        as1 = f"ΤΥΠΟΣ ΔΗΛΩΣΗΣ:     {lin['dilosityp']}\n"
        as1 += "ΥΠΟΚΑΤΑΣΤΗΜΑ ΙΚΑ \n"
        as1 += f"ΥΠΟΒΟΛΗΣ:          {lin['ypma']} {lin['ypname']}\n"
        as1 += f"ΕΠΩΝΥΜΙΑ ΕΡΓΟΔΟΤΗ: {lin['epon']}\n"
        as1 += '\n'
        as1 += f"Α.Μ.Ε.: {lin['ame']}\n"
        as1 += f"Α.Φ.Μ.: {lin['afm']}\n"
        as1 += '\n'
        as1 += f"ΔΙΕΥΘΥΝΣΗ :        {lin['odos']} {lin['arithmos']}\n"
        as1 += f"                   {lin['tk']} {lin['poli']}\n"
        as1 += "\n"
        as1 += f"ΑΠΟ ΜΗΝΑ/ΕΤΟΣ:     {lin['apomina']}/{lin['apoetos']}\n"
        as1 += f"ΕΩΣ ΜΗΝΑ/ΕΤΟΣ:     {lin['eosmina']}/{lin['eosetos']}\n"
        as1 += f"{'':28}{'ΗΜΕΡΩΝ':^9}{'ΑΠΟΔΟΧΩΝ':^14}{'ΚΑΤΑΒΛΗΘΕΙΣΩΝ':^14}{'ΣΥΝΟΛΟ':^12}\n"
        as1 += f"{'':28}{'ΑΣΦΑΛΙΣΗΣ':^9}{'':^14}{'ΕΙΣΦΟΡΩΝ':^14}{'ΑΣΦΑΛΙΣΜΕΝΩΝ':^12}\n"
        as1 += '\n'
        aes = f"{lin['apomina']}/{lin['apoetos']}"
        as1 += f"{'ΣΥΝΟΛΑ ΑΝΑ ΜΗΝΑ:':19}{aes:7}{lin['totalmeres']:^9}{apod:>14}{eisf:>14}\n"
        as1 += '\n'
        as1 += f"{'':19}{'ΣΥΝΟΛΑ:':7}{lin['totalmeres']:^9}{apod:>14}{eisf:>14}{self.total_ergnoi:^12}\n"
        as1 += '\n\n'
        t18 = self.totals_by_18_gr()
        if t18['18'] != ['', '', '']:
            as1 += f"{'':15}{'(ΧΩΡΙΣ 18):':>11}{t18['no'][0]:^9}{t18['no'][1]:>14}{t18['no'][2]:>14}\n"
            as1 += f"{'':15}{'(ME 18):':>11}{t18['18'][0]:^9}{t18['18'][1]:>14}{t18['18'][2]:>14}\n"
            as1 += '\n\n'
        as1 += 'Δηλώνω υπεύθυνα, ότι τα αναγραφόμενα συγκεντρωτικά στοιχεία του παρόντος εντύπου,\n'
        print(len('Δηλώνω υπεύθυνα, ότι τα αναγραφόμενα συγκεντρωτικά στοιχεία του παρόντος εντύπου,\n'))
        as1 += 'περιέχονται στο υποβαλλόμενο ηλεκτρονικό μέσο.\n'
        as1 += '\n\n'
        as1 += 'Ο ΔΗΛΩΝ ΕΡΓΟΔΟΤΗΣ                                          Ο ΠΑΡΑΛΑΒΩΝ\n'
        as1 += '\n\n\n'
        as1 += 'Ημερομηνία Υποβολής'
        return as1

    def print_company_data(self):
        lin = self.lines[0]
        aes = f"{lin['apomina']}/{lin['apoetos']}"
        as1 = f"ΤΥΠΟΣ ΔΗΛΩΣΗΣ:             {lin['dilosityp']}\n"
        as1 += f"ΥΠΟΚΑΤΑΣΤΗΜΑ ΙΚΑ ΥΠΟΒΟΛΗΣ: {lin['ypma']} {lin['ypname']}\n"
        as1 += f"ΕΠΩΝΥΜΙΑ ΕΡΓΟΔΟΤΗ:         {lin['epon']}\n"
        as1 += '\n'
        as1 += f"Α.Μ.Ε.: {lin['ame']:10}             ΔΙΕΥΘΥΝΣΗ\n"
        as1 += f"Α.Φ.Μ.: {lin['afm']:10} {lin['odos']} {lin['arithmos']}\n"
        as1 += f"        {'        ':10} {lin['tk']} {lin['poli']}\n"
        as1 += "\n"
        as1 += f"        {'        ':10} ΑΠΟ ΜΗΝΑ/ΕΤΟΣ: {lin['apomina']}/{lin['apoetos']}   "
        as1 += f"ΕΩΣ ΜΗΝΑ/ΕΤΟΣ: {lin['eosmina']}/{lin['eosetos']}\n"
        as1 += "\n"
        as1 += f"{'ΣΥΝΟΛΑ ΑΝΑ ΜΗΝΑ:':19} {aes:>14} {'':>14} {'':>14} {'ΣΥΝΟΛΑ':>14}\n"
        as1 += f"{'ΗΜΕΡΩΝ ΑΣΦΑΛΙΣΗΣ:':19} {lin['totalmeres']:>14} {'':>14} {'':>14} {lin['totalmeres']:>14}\n"
        apod = dec2gr(lin['apodoxes'])
        as1 += f"{'ΑΠΟΔΟΧΩΝ:':19} {apod:>14} {'':>14} {'':>14} {apod:>14}\n"
        eisf = dec2gr(lin['eisfores'])
        as1 += f"{'ΚΑΤΑΒΛ.ΕΙΣΦΟΡΩΝ:':19} {eisf:>14} {'':>14} {'':>14} {eisf:>14}\n"
        return as1

    def print_header(self):
        lin = self.lines[0]
        aes = f"{lin['apomina']}/{lin['apoetos']}"
        as1 = ''
        as1 += f"Α.Μ.Ε.:        {lin['ame']:24} Α.Φ.Μ.:        {lin['afm']}\n"
        as1 += f"ΑΠΟ ΜΗΝΑ/ΕΤΟΣ: {aes:24} ΕΩΣ ΜΗΝΑ/ΕΤΟΣ: {lin['eosmina']}/{lin['eosetos']}\n"
        return as1

    def with_greek_lbl(self):
        lst = [self.linetypes[i['line_code']].with_greek_lbl(
            i) for i in self.lines]
        return '\n'.join(lst)

    def for_report(self):
        # lst = [self.linetypes[i['line_code']].for_report(
        #     i) for i in self.lines]
        # return lst
        # append header
        lst = []
        for ergline, aplines in self.ergnoi.items():
            # print(ergline)
            for apodline in aplines:
                erdata = self.lines[ergline]
                er_line_code = erdata['line_code']
                apdata = self.lines[apodline]
                ap_line_code = apdata['line_code']
                lst.append(self.linetypes[er_line_code].for_report(erdata))
                lst.append(self.linetypes[ap_line_code].for_report(apdata))
        return lst

    def render2file(self, filename):
        with open(filename, 'w', encoding='WINDOWS-1253') as fil:
            fil.write(self.render())
        print(f'File {filename} created !!!')

    def parse(self, filename):
        with open(filename, encoding='WINDOWS-1253') as fil:
            lines = fil.read().split('\n')
        currentergline = 0
        for i, lin in enumerate(lines):
            for code, linetype in self.linetypes.items():
                if lin.startswith(code):
                    if code == '2':
                        self.ergnoi[i] = []
                        self.total_ergnoi += 1
                        currentergline = i
                    elif code == '3':
                        self.ergnoi[currentergline].append(i)
                    ldic = linetype.read(lin)
                    ldic['line_code'] = code
                    self.add_line(ldic)

    def get_totals(self):
        apodoxes = eisfores = meres = 0
        for line in self.lines:
            if line['line_code'] == '3':
                apodoxes += line['apodoxes']
                eisfores += line['katablitees_eisfores']
                meres += line['imeres_asfalisis']
        return round(apodoxes, 2), round(eisfores, 2), meres

    def totals_by_18(self):
        tot = {'18': [0, 0, 0], 'no': [0, 0, 0]}
        for line in self.lines:
            if line['line_code'] == '3':
                if line['apodoxes_type'] == '18':
                    tot['18'][0] += line['imeres_asfalisis']
                    tot['18'][1] += line['apodoxes']
                    tot['18'][2] += line['katablitees_eisfores']
                else:
                    tot['no'][0] += line['imeres_asfalisis']
                    tot['no'][1] += line['apodoxes']
                    tot['no'][2] += line['katablitees_eisfores']
        return tot

    def totals_by_18_gr(self):
        tot = {'18': [0, 0, 0], 'no': [0, 0, 0]}
        for line in self.lines:
            if line['line_code'] == '3':
                if line['apodoxes_type'] == '18':
                    tot['18'][0] += line['imeres_asfalisis']
                    tot['18'][1] += line['apodoxes']
                    tot['18'][2] += line['katablitees_eisfores']
                else:
                    tot['no'][0] += line['imeres_asfalisis']
                    tot['no'][1] += line['apodoxes']
                    tot['no'][2] += line['katablitees_eisfores']
        for val in tot.values():
            if val[0] == 0:
                val[0] = ''
            else:
                val[0] = str(val[0])
            val[1] = dec2gr(val[1])
            val[2] = dec2gr(val[2])
        return tot

    def correct_header(self):
        l_apodoxes, l_eisfores, l_meres = self.get_totals()
        self.lines[0]['apodoxes'] = l_apodoxes
        self.lines[0]['eisfores'] = l_eisfores
        self.lines[0]['totalmeres'] = l_meres

    def errors_found(self):
        l_apodoxes, l_eisfores, l_meres = self.get_totals()
        errors = []
        if l_apodoxes != self.lines[0]['apodoxes']:
            errors.append(
                f"header apdoxes ({self.lines[0]['apodoxes']}) != total apodoxes({l_apodoxes})")
        if l_eisfores != self.lines[0]['eisfores']:
            errors.append(
                f"header eisfores ({self.lines[0]['eisfores']}) != total eisfores({l_eisfores})")
        if l_meres != self.lines[0]['totalmeres']:
            errors.append(
                f"header eisfores ({self.lines[0]['totalmeres']}) != total eisfores({l_meres})")
        return errors

    def DublicateLines(self):
        pos = []
        val = []
        for i, lin in enumerate(self.lines):
            if lin['line_code'] == '3':
                ndic = dict(lin)
                ndic['apodoxes_type'] = 18
                ndic['apoapasxolisi'] = '2020-03-15'
                ndic['eosapasxolisi'] = '2020-03-31'
                val.append(ndic)
                pos.append(i)
        pos.reverse()
        val.reverse()
        print(pos)
        for i, ps in enumerate(pos):
            self.lines.insert(ps + 1, val[i])
        self.correct_header()


def apd_builder():
    li1 = LineTypeTotals(name='Header', prefix='1')
    li1.add_col(Col('plithos', 'ΠΛΗΘΟΣ', ColTextInt(), 2))
    li1.add_col(Col('aa', 'ΑΑ', ColTextInt(), 2))
    li1.add_col(Col('fname', 'ΟΝΟΜΑ ΑΡΧΕΙΟΥ', ColText(), 8))
    li1.add_col(Col('ekdosi', 'ΕΚΔΟΣΗ', ColTextInt(), 2))
    li1.add_col(Col('dilosityp', 'ΤΥΠΟΣ ΔΗΛΩΣΗΣ', ColTextInt(), 2))
    li1.add_col(Col('ypma', 'ΥΠΟΚΑΤΑΣΤΗΜΑ ΙΚΑ', ColTextInt(), 3))
    li1.add_col(Col('ypname', 'ΟΝΟΜΑΣΙΑ ΥΠΟΚ/ΤΟΣ ΙΚΑ', ColText(), 50))
    li1.add_col(Col('epon', 'ΕΠΩΝΥΜΙΑ ΕΡΓΟΔΟΤΗ', ColText(), 80))
    li1.add_col(Col('onoma', 'ΟΝΟΜΑ ΕΡΓΟΔΟΤΗ', ColText(), 30))
    li1.add_col(Col('pateras', 'ΟΝΟΜΑ ΠΑΤΡΟΣ ΕΡΓ/ΤΗ', ColText(), 30))
    li1.add_col(Col('ame', 'Α.Μ.Ε.', ColTextInt(), 10))
    li1.add_col(Col('afm', 'Α.Φ.Μ.', ColTextInt(), 9))
    li1.add_col(Col('odos', 'ΟΔΟΣ', ColText(), 50))
    li1.add_col(Col('arithmos', 'ΑΡΙΘΜΟΣ', ColText(), 10))
    li1.add_col(Col('tk', 'Τ.Κ.', ColTextInt(), 5))
    li1.add_col(Col('poli', 'ΠΟΛΗ', ColText(), 30))
    li1.add_col(Col('apomina', 'ΑΠΟ ΜΗΝΑ', ColTextInt(), 2))
    li1.add_col(Col('apoetos', 'ΑΠΟ ΕΤΟΣ', ColTextInt(), 4))
    li1.add_col(Col('eosmina', 'ΈΩΣ ΜΗΝΑ', ColTextInt(), 2))
    li1.add_col(Col('eosetos', 'ΈΩΣ ΕΤΟΣ', ColTextInt(), 4))
    li1.add_col(
        Col('totalmeres', 'ΣΥΝΟΛΟ ΗΜΕΡΩΝ ΑΣΦΑΛΙΣΗΣ', ColInt(), 8))
    li1.add_col(Col('apodoxes', 'ΣΥΝΟΛΟ ΑΠΟΔΟΧΩΝ', ColPoso(), 12))
    li1.add_col(Col('eisfores', 'ΣΥΝΟΛΟ ΕΙΣΦΟΡΩΝ', ColPoso(), 12))
    li1.add_col(Col('ypoboli', 'ΗΜ/ΝΙΑ ΥΠΟΒΟΛΗΣ', ColDate(), 8))
    li1.add_col(Col('pafsi', 'ΗΜ/ΝΙΑ ΠΑΥΣΗΣ ΕΡΓΑΣΙΩΝ', ColDate(), 8))
    li1.add_col(Col('filler', 'ΚΕΝΑ', ColText(), 30))

    li2 = LineTypeErg(name='Stoixeia Ergazomenoy', prefix='2')
    li2.add_col(Col('ama', 'ΑΡ.ΜΗΤΡΩΟΥ ΑΣΦ.', ColTextInt(), 9))
    li2.add_col(Col('amka', 'Α.Μ.Κ.Α.', ColTextInt(), 11))
    li2.add_col(Col('asf_eponymo', 'ΕΠΩΝΥΜΟ', ColText(), 50))
    li2.add_col(Col('asf_onoma', 'ΟΝΟΜΑ', ColText(), 30))
    li2.add_col(Col('asf_pateras', 'ΟΝΟΜΑ ΠΑΤΡΟΣ', ColText(), 30))
    li2.add_col(Col('asf_mitera', 'ΟΝΟΜΑ ΜΗΤΡΟΣ', ColText(), 30))
    li2.add_col(Col('asf_gennisi', 'ΗΜ/ΝΙΑ ΓΕΝΝΗΣΗΣ', ColDate(), 8))
    li2.add_col(Col('asf_afm', 'Α.Φ.Μ.', ColTextInt(), 9))

    li3 = LineTypeApod(name='Stoixeia misthodosias', prefix='3')
    li3.add_col(Col('parartima_no', 'ΑΡ.ΠΑΡΑΡΤ.', ColTextInt(), 4))
    li3.add_col(Col('kad', 'ΚΑΔ', ColTextInt(), 4))
    li3.add_col(Col('plires_orario', 'ΠΛΗΡΕΣ ΩΡΑΡΙΟ', ColTextInt(), 1))
    li3.add_col(Col('oles_ergasimes', 'ΟΛΕΣ ΕΡΓΑΣΙΜΕΣ', ColTextInt(), 1))
    li3.add_col(Col('kyriakes', 'ΚΥΡΙΑΚΕΣ', ColInt(), 1))
    li3.add_col(Col('eid', 'ΚΩΔ.ΕΙΔΙΚΟΤΗΤΑΣ', ColTextInt(), 6))
    li3.add_col(Col('eid_per_asfalisis', 'ΕΙΔ.ΠΕΡΙΠΤ.ΑΣΦΑΛ.', ColIntSpace(), 2))
    li3.add_col(Col('kpk', 'ΠΑΚΕΤΟ ΚΑΛΥΨΗΣ', ColInt(), 4))
    li3.add_col(Col('mismina', 'ΜΙΣΘ.ΠΕΡ.ΜΗΝΑΣ', ColTextInt(), 2))
    li3.add_col(Col('misetos', 'ΜΙΣΘ.ΠΕΡ.ΕΤΟΣ', ColTextInt(), 4))
    li3.add_col(Col('apoapasxolisi', 'ΑΠΟ ΗΜ/ΝΙΑ ΑΠΑΣΧ.', ColDate(), 8))
    li3.add_col(Col('eosapasxolisi', 'ΈΩΣ ΗΜ/ΝΙΑ ΑΠΑΣΧ.', ColDate(), 8))
    li3.add_col(Col('apodoxes_type', 'ΤΥΠΟΣ ΑΠΟΔΟΧΩΝ', ColTextInt(), 2))
    li3.add_col(Col('imeres_asfalisis', 'ΗΜΕΡΕΣ ΑΣΦΑΛΙΣΗΣ', ColInt(), 3))
    li3.add_col(Col('imeromisthio', 'ΗΜΕΡΟΜΙΣΘΙΟ', ColPoso(), 10))
    li3.add_col(Col('apodoxes', 'ΑΠΟΔΟΧΕΣ', ColPoso(), 10))
    li3.add_col(Col('eisf_asfalismenoy', 'ΕΙΣΦΟΡΕΣ ΑΣΦΑΛΙΣΜ.', ColPoso(), 10))
    li3.add_col(Col('eisf_ergodoti', 'ΕΙΣΦΟΡΕΣ ΕΡΓΟΔΟΤΗ', ColPoso(), 10))
    li3.add_col(Col('eisf_total', 'ΣΥΝΟΛΙΚΕΣ ΕΙΣΦΟΡΕΣ', ColPoso(), 11))
    li3.add_col(Col('epid_asfalismenoy_poso',
                    'ΕΠΙΔΟΤ.ΑΣΦΑΛ.(ΠΟΣΟ)', ColPoso(), 10))
    li3.add_col(Col('epid_ergodoti_pososto', 'ΕΠΙΔΟΤ.ΕΡΓΟΔ.(%)', ColPoso(), 5))
    li3.add_col(Col('epid_ergodoti_poso', 'ΕΙΔΟΤ.ΕΡΓΟΔ.(ΠΟΣΟ)', ColPoso(), 10))
    li3.add_col(Col('katablitees_eisfores', 'ΚΑΤΑΒΛ.ΕΙΣΦΟΡΕΣ', ColPoso(), 11))
    leof = LineType(name='Terminator line', prefix='EOF')

    do1 = Document()
    do1.add_linetype(li1)
    do1.add_linetype(li2)
    do1.add_linetype(li3)
    do1.add_linetype(leof)
    return do1
