from datetime import datetime
from collections import OrderedDict, namedtuple
from tablib.core import Dataset
from constants import *


class Event(object):
    _objects = [
                'calorimeter',
                'clusters',
                'spectrometer',
                'muon',
                'tracks',
                'verteces'
                ]
    _regular = ['particle',
                'datetime',
                'energy']

    def __init__(self, data):

        self.particle = None
        """:type : str"""

        self.datetime = None
        """:type : datetime"""

        self.energy = None
        """:type : str"""

        self.calorimeter = Calorimeter
        """:type : Calorimeter"""

        self.spectrometer = Spectrometer
        """:type : Spectrometer"""

        self.muon = Muon
        """:type : Muon"""

        self.tracks = Tracks
        """:type : Tracks"""

        self.verteces = Verteces
        """:type : Verteces"""

        self.clusters = Clusters
        """:type : Clusters"""

        for key in self._regular:
            if hasattr(data, key):
                value = getattr(data, key)
                setattr(self, key, value)
        if hasattr(data, 'string'):
            text = data.string
        elif isinstance(data, str):
            text = data
        else:
            text = ''
        self.raw = text
        partitions = self._separate(text)
        for key in self._objects:
            obj = getattr(self, key)
            if key in partitions.keys():
                limits = partitions[key]
                string = text[limits[0]:limits[1]]
            else:
                string = ''
            setattr(self, key, obj(string))

    def __str__(self):
        return self.raw

    @staticmethod
    def _separate(text):
        result = OrderedDict(
            calorimeter=CALORIMETER_STRING,
            clusters=EM_CLUSTER,
            spectrometer=SPECTROMETER_STRING,
            muon=MUON_STRING,
            tracks=TRACKS_STRING,
            verteces=VERTECES_STRING
        )
        for key in result.copy():
            value = text.find(result[key])
            if value == -1:
                result.pop(key)
            else:
                result[key] = value

        result['end'] = -1
        former_key = None
        former_value = None
        for key, value in result.copy().items():
            if former_key and former_value:
                result[former_key] = (former_value, value)
            former_key = key
            former_value = value

        result.pop('end')

        return result


class Report(object):

    def __init__(self, string):
        self.raw = string


class Muon(Report):
    def __init__(self, string):
        self.table = self._prepare_table(string)
        super().__init__(string)

    @staticmethod
    def _prepare_table(string):
        dataset = Dataset()
        for i, line in enumerate(string.split('\n')[1:]):
            if '====' in line or not line:
                continue
            row = line.split()
            if i == 1:
                dataset.headers = row
            else:
                dataset.append([numberfy(num) for num in row])
        return dataset


class Verteces(Report):

    def __init__(self, string):
        super().__init__(string)
        self.verteces = self._initial_parse(string)

    @staticmethod
    def _initial_parse(string):
        result = []
        resultant = namedtuple('Vertex', ('name', 'text'))
        separator = re.compile(
            r'\s+(Tracks\s+\d and\s+\d)\n\s+====================\n')
        start = separator.search(string)
        while start:
            former = start
            start = separator.search(string, pos=start.end())
            end = start.start() if start else len(string)
            r = resultant(name=' '.join(former.group(1).split()),
                          text=string[former.end():end])
            result.append(r)
        return [Vertex(vertex) for vertex in result]


class Coordinate(object):

    def __init__(self, value, error):
        self.value = value
        self.error = error

    def __str__(self):
        return '{} +/- {}'.format(self.value, self.error)


class Vertex(Report):

    def __init__(self, data):

        self.x = None
        """:type : Coordinate"""

        self.y = None
        """:type : Coordinate"""

        self.z = None
        """:type : Coordinate"""

        self.phi = None
        """:type : Coordinate"""

        self.name = data.name
        """:type : str"""

        string = data.text
        for key, value in self._parse(string):
            setattr(self, key, value)

        super().__init__(string)

    @staticmethod
    def _parse(string):
        fun = re.compile(r'(\w+)\s*=\s+(-?\d+\.\d+)\s\+/-\s+(\d+\.\d+)')
        start = fun.search(string)
        result = []
        while start:
            result.append((start.group(1).lower(), Coordinate(
                float(start.group(2)), float(start.group(3)))))
            start = fun.search(string, pos=start.end())
        return result


class Calorimeter(Report):

    def __init__(self, string):
        index = self._separate(string)
        table_string = string[:index]
        clusters_string = string[index:]
        self.hit_table = self._prepare_table(table_string)
        self.clusters = Clusters(self._prepare_cluters(clusters_string))

        """:type : Clusters"""
        super().__init__(string)

    @staticmethod
    def _separate(string):
        p = string.find(EM_CLUSTER)
        return p

    @staticmethod
    def _prepare_table(string):

        dataset = Dataset()
        for i, line in enumerate(string.split('\n')[1:]):
            if '*****' in line or not line:
                continue
            row = line.split()
            if i == 1:
                row[4] += ' ' + row[5]
                dataset.headers = row[:5]
            else:
                dataset.append([numberfy(i) for i in row])

        return dataset

    @staticmethod
    def _prepare_cluters(string):
        dataset = Dataset()
        stringRep = string.replace(
            'PULSE HEIGHT', 'PULSE-HEIGHT').replace(' +/-', '_+/-')
        for i, line in enumerate(stringRep.split('\n')[3:]):
            if '*****' in line or not line or 'GEANT' in line:
                continue
            if 'NO.  PULSE-HEIGHT' not in line and '+/-' not in line:
                continue
            parts = line.split()
            if i == 0:
                dataset.headers = parts
            else:
                if '+/-' in line:
                    dataset.append([numberfy(cell.replace('_', ' '))
                                    for cell in parts])
        return dataset


class Clusters(Report):
    def __init__(self, data):
        """

        :param Dataset data:
        """
        if isinstance(data, str):
            self.clusters = Clusters(self._prepare_clusters_str(data))
        else:
            self.clusters = self._prepare_clusters(data)
        """:type : list[Cluster]"""
        super().__init__(data)

    def _prepare_clusters(self, data):
        thing = [Cluster(dict_row) for dict_row in data.dict]

        return thing

    def _prepare_clusters_str(self, data):
        dataset = Dataset()
        stringRep = data.replace(
            'PULSE HEIGHT', 'PULSE-HEIGHT').replace(' +/-', '_+/-')
        for i, line in enumerate(stringRep.split('\n')[3:]):
            if '*****' in line or not line or 'GEANT' in line:
                continue
            if 'NO.  PULSE-HEIGHT' not in line and '+/-' not in line:
                continue
            parts = line.split()
            if i == 0:
                dataset.headers = parts
            else:
                if '+/-' in line:
                    dataset.append([numberfy(cell.replace('_', ' '))
                                    for cell in parts])
        return dataset


class Cluster(Report):

    def __init__(self, data):
        thing = re.compile(r'\s*(-?\d+\.\d+)\s\+/-(\d+\.\d+)\s*')

        self.x = None
        """:type : Coordinate"""

        self.y = None
        """:type : Coordinate"""

        self.z = None
        """:type : Coordinate"""

        self.pulse_height = None
        """:type : float"""

        self.no = None
        """:type : int"""

        self.ywidth = None
        """:type : float"""

        self.zwidth = None
        """:type : float"""

        for key, value in data.items():
            newkey = key.replace('-', '_').lower().replace('.', '')
            newval = value
            if key.replace('-', '_').lower().replace('.', '') in ['x', 'y', 'z']:
                found = thing.search(value)
                newval = Coordinate(numberfy(found.group(1)),
                                    numberfy(found.group(2)))
            setattr(self, newkey, newval)
        super().__init__(data)


class Spectrometer(Report):
    def __init__(self, string):
        string = _escape_minus_signs(string)
        self.table = self._prepare_table(string)
        """:type : Dataset"""

        super().__init__(string)

    @staticmethod
    def _prepare_table(string):
        dataset = Dataset()
        good = None
        for i, line in enumerate(string.split('\n')[1:]):
            if '====' in line or not line:
                continue
            row = line.split()
            if i == 1:
                dataset.headers = row
            else:
                if len(row) == len(dataset.headers):
                    good = line
                    dataset.append([numberfy(num) for num in row])
                else:
                    print(good)
                    print(row)

        return dataset


class Tracks(Report):

    def __init__(self, string):

        super().__init__(string)
        self.tracks = self._parse(string)
        """:type : list[Track]"""

    @staticmethod
    def _parse(string):
        separator = TRACKS_RE
        start = separator.search(string)
        result = []
        while start:
            former = start
            start = separator.search(string, pos=start.end())
            end = start.start() if start else len(string)
            result.append(
                Track(string[former.end():end].strip('\n'), former.group(1)))
        return result


class Track(Report):

    def __init__(self, string, number=0):
        indecies = self._separate(string)
        table_string = string[:indecies[0]]
        param_string = string[indecies[0]:indecies[1]]
        error_string = string[indecies[1]:]

        self.num = number
        """:type : int"""

        self.table = self._prepare_table(table_string)
        """:type : Dataset"""

        self.parameters = Parameters(param_string)
        """:type : Parameters"""

        # self.error_matrix = self._prapare_matrix(error_string)
        # """:type : dict"""


        super().__init__(string)

    @staticmethod
    def _prepare_table(string):
        result = []
        for line in string.split('\n'):
            if '*****' in line or not line:
                continue
            line = line.lstrip().strip('*').split('*')
            row = []
            for cell in line:
                cell = cell.strip()
                row.append(cell)
            result.append(row)
        dataset = Dataset()
        head = 0
        if result[0][0] is '':
            head = 1
        else:
            head = 0
        dataset.headers = result[head]
        for row in result[head+1:]:
            if row[0] is not '':
                dataset.append([numberfy(i) for i in row])
        return dataset

    @staticmethod
    def _separate(string):
        p = string.find(FIT_PARAM)
        e = string.find(FIT_ERROR)
        return p, e

    @staticmethod
    def _prapare_matrix(string):

        result = []

        lines = string.split('\n')[1:][::-1]

        for i, line in enumerate(lines):
            if '*****' in line:
                beginning = i
                lines = lines[beginning:]
                break

        for i, line in enumerate(lines):

            if len(line.lstrip().split('*')) in [4,6]:
                continue
            if '*****' in line or not line or 'Fit' in line or 'Track' in line:
                continue
            line = line.lstrip().lstrip('*').split()
            d = {}
            t = []
            if i == 1:
                headlines = line
            else:
                for j, value in enumerate(line):
                    if value in headlines:
                        continue
                    if j!=0:
                        try:
                            float(value)
                        except ValueError:
                            print('here')

                    if j == 0:
                        t.append(value.lower())
                    else:
                        d[headlines[j - 1].lower()] = float(value)
                t.append(d)
                t = tuple(t)
                result.append(t)


        return dict(result)


class Parameters(Report):
    def __init__(self, string):
        self.akappa = None
        self.phi0 = None
        self.d0 = None
        self.tandip = None
        self.z0 = None
        self.chisq = None
        self.chizq = None
        parsed = self._parse(string)
        for key, value in parsed:
            setattr(self, key, value)
        super().__init__(string)

    @staticmethod
    def _parse(string):
        result = []
        for line in string.split('\n')[1:]:
            if '*****' in line or not line:
                continue
            params = line.lstrip().strip('*').split('*')[0].split()
            pair = (params[1].lower(), float(params[0]))
            result.append(pair)
        return result


def numberfy(string):

    if string.find('.') + 1:
        caster = float
    else:
        caster = int

    try:
        return caster(string)
    except ValueError:
        return string


def _initial_parse(text):

    separator = re.compile(r'GEANT > ([a-z0-]+) ([\d.]+)')
    start = separator.search(text)
    result = []
    resultant = namedtuple('particle_group', ('name', 'energy', 'string'))
    while start:
        former = start
        start = separator.search(text, pos=start.start() + 1)
        end = start.start() if start else len(text)
        r = resultant(
            name=former.group(1), energy=former.group(2),
            string=text[former.end():end]
        )
        result.append(r)
    return result


def _initial_parse_l(text):

    separator = re.compile(
        r'\s+A new event at\s+(\d\d\.\d\d\.\d\d\s\d\d/\d\d/\d\d\d\d)')
    print('text is {}'.format(text))
    start = separator.search(text)
    result = []
    resultant = namedtuple('particle_group', ('number', 'string'))
    i = 1
    while start:
        former = start
        start = separator.search(text, pos=start.start() + 1)
        end = start.start() if start else len(text)
        r = resultant(
            number=i,
            string=text[former.end():end]
        )
        result.append(r)
        i = i+1
    return result


def _secondary_parse(parsed_data):
    resultant = namedtuple(
        'particle', ('particle', 'energy', 'datetime', 'string'))
    separator = re.compile(
        r'GEANT > inject\s+A new event at\s+(\d\d\.\d\d\.\d\d\s\d\d/\d\d/\d\d\d\d)')
    result = []
    for particle_group in parsed_data:
        text = particle_group.string
        start = separator.search(text)

        while start:
            former = start
            start = separator.search(text, pos=start.start() + 1)
            end = start.start() if start else len(text)
            r = resultant(
                particle=particle_group.name, energy=particle_group.energy,
                datetime=datetime.strptime(former.group(1), FORMAT), string=text[former.end():end]
            )
            result.append(r)
    return result


def _loto_parse(parsed_data):
    resultant = namedtuple('particle', ('particle', 'string'))
# (\d\d\.\d\d\.\d\d\s\d\d/\d\d/\d\d\d\d)\s+\*+Event No\.\s+(\d)
    separator = re.compile(
        r'(GEANT > testme)|(\s+\*+\sEvent No\.\s+(\d)\s+\*+\s+)')
    result = []
    for particle_group in parsed_data:
        text = particle_group.string
        if text is '':
            continue
        start = separator.search(text)

        while start:
            former = start
            start = separator.search(text, pos=start.start() + 1)
            end = start.start() if start else len(text)
            r = resultant(
                particle=particle_group.number,
                string=text[former.end():end]
            )
            result.append(r)
    return result


def _escape_minus_signs(string):
    fuck = re.compile('\d+-\d+')
    match = fuck.search(string)
    if not match:
        return string
    minus_location = match.group().find('-') + match.start()
    string = string[:minus_location] + ' ' + string[minus_location:]
    return _escape_minus_signs(string)


def parse(text):
    return [Event(event) for event in _secondary_parse(_initial_parse(text))]


def parseLoto(text):
    return [Event(event) for event in _loto_parse(_initial_parse_l(text))]
