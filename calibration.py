from tablib.core import Dataset
from gimel_session import GimelSession
from gimel_parser import parse
from parse_txt import do_parse
import re
import json


USER_NAME = ''
PASSWORD = ''
IDNum = ''
SESSION_FILE = 'kshort.txt'
EXEL_OUTPUT = 'kshort.xls'

minimum_energy = 7
step_size = 0
number_of_injections = 1
per_energy = 3000
particle = 'k-short'

if __name__ == '__main__':
    with open('auth.json') as f:
        data = json.load(f)
    USER_NAME = data["username"]
    PASSWORD = data["password"]
    IDNum = data["id"]

    with GimelSession(user=USER_NAME, password=PASSWORD, output_file=SESSION_FILE) as g:
        g.start_gimmel()
        g.send_command(IDNum)
        g.send_particles_ascending_energies(particle, minimum_energy, step_size, number_of_injections,per_energy)
    with open(SESSION_FILE) as f:
        text = f.read()
    if particle is 'photon':
        events = parse(text)
        dataset = Dataset()
        dataset.headers = ('P', 'pulseheight', 'x', 'dx', 'y',
                           'dy', 'z', 'dz', 'ywidth', 'zwidth')
        for event in events:
            row = []
            if len(event.clusters.clusters.clusters) is 1:
                row.append(event.energy)
                row.append(event.clusters.clusters.clusters[0].pulse_height)
                row.append(event.clusters.clusters.clusters[0].x.value)
                row.append(event.clusters.clusters.clusters[0].x.error)
                row.append(event.clusters.clusters.clusters[0].y.value)
                row.append(event.clusters.clusters.clusters[0].y.error)
                row.append(event.clusters.clusters.clusters[0].z.value)
                row.append(event.clusters.clusters.clusters[0].z.error)
                row.append(event.clusters.clusters.clusters[0].ywidth)
                row.append(event.clusters.clusters.clusters[0].zwidth)
                dataset.append(row)
        with open(EXEL_OUTPUT, 'wb') as f:
            f.write(dataset.export('xls'))

    elif particle is 'electron' or particle is 'muon':
        events = parse(text)
        dataset = Dataset()
        dataset.headers = ('P', 'tandip', 'Kappa', 'd Kappa',
                           'Calorimeter Pulse Heights')
        for event in events:
            row = []
            row.append(event.energy)
            if len(event.tracks.tracks) is not 0:
                if event.tracks.tracks[0].parameters.tandip is not None:
                    row.append(event.tracks.tracks[0].parameters.tandip)
                else:
                    row.append('No tandip')
                tmpTrk = event.tracks.tracks[0]
                row.append(event.tracks.tracks[0].parameters.akappa)
                if 'akappa' in tmpTrk.error_matrix['akappa']:
                    row.append(tmpTrk.error_matrix['akappa']['akappa'])
                else:
                    row.append('no dk')
            else:
                row.append('no tracks')
                row.append('no tracks')
                row.append('no tracks')
            thing = []
            for i in range(len(event.calorimeter.clusters.clusters)):
                thing.append(
                    event.calorimeter.clusters.clusters[i].pulse_height)
            row.append(','.join(str(e) for e in thing))
            dataset.append(row)

        with open(EXEL_OUTPUT, 'wb') as f:
            f.write(dataset.export('xls'))
    elif particle is 'k-short':
        events = parse(text)
        dataset = Dataset()
        dataset.headers = ('event number','P', 'track 1','track 2', 'phi',
                           'dphi','x','dx','y','dy','z','dz','trk1Kappa','trk2Kappa')
        names=re.compile(r'\s+[a-zA-Z]*\s+(\d+)\s+[a-zA-Z]*\s+(\d+)\s*')
        eventNum=0
        for event in events:
            eventNum+=1
            for vertex in event.verteces.verteces:
                trks=vertex.name.lstrip(' ').split()
                if len(trks) is 4:
                    trk1=int(trks[1])
                    trk2=int(trks[3])
                    if len(event.tracks.tracks)>=max(trk1,trk2):
                        row=[]
                        row.append(eventNum)
                        row.append(event.energy)
                        row.append(trk1)
                        row.append(trk2)
                        row.append(vertex.phi.value)
                        row.append(vertex.phi.error)
                        try:
                            row.append(vertex.x.value)
                            row.append(vertex.x.error)
                            row.append(vertex.y.value)
                            row.append(vertex.y.error)
                            row.append(vertex.z.value)
                            row.append(vertex.z.error)
                        except AttributeError:
                            row.append(0)
                            row.append(0)
                            row.append(0)
                            row.append(0)
                            row.append(0)
                            row.append(0)

                        row.append(event.tracks.tracks[trk1-1].parameters.akappa)
                        row.append(event.tracks.tracks[trk2-1].parameters.akappa)
                        dataset.append(row)
        with open(EXEL_OUTPUT, 'wb') as f:
            f.write(dataset.export('xls'))
    elif particle is 'pi-0':
        events = parse(text)
        dataset = Dataset()
        dataset.headers = ('P', 'cluster num', 'pulse height',
                           'x', 'dx', 'y', 'dy', 'z', 'dz', 'ywidth', 'zwidth')
        for event in events:
            if len(event.calorimeter.clusters.clusters) is 2:
                for i in range(len(event.calorimeter.clusters.clusters)):
                    row = []
                    row.append(event.energy)
                    row.append(event.calorimeter.clusters.clusters[i].no)
                    row.append(
                        event.calorimeter.clusters.clusters[i].pulse_height)
                    row.append(event.calorimeter.clusters.clusters[i].x.value)
                    row.append(event.calorimeter.clusters.clusters[i].x.error)
                    row.append(event.calorimeter.clusters.clusters[i].y.value)
                    row.append(event.calorimeter.clusters.clusters[i].y.error)
                    row.append(event.calorimeter.clusters.clusters[i].z.value)
                    row.append(event.calorimeter.clusters.clusters[i].z.error)
                    row.append(event.calorimeter.clusters.clusters[i].ywidth)
                    row.append(event.calorimeter.clusters.clusters[i].zwidth)
                    dataset.append(row)
            elif len(event.clusters.clusters.clusters) is 2:
                for i in range(len(event.clusters.clusters.clusters)):
                    row = []
                    row.append(event.energy)
                    row.append(event.clusters.clusters.clusters[i].no)
                    row.append(
                        event.clusters.clusters.clusters[i].pulse_height)
                    row.append(event.clusters.clusters.clusters[i].x.value)
                    row.append(event.clusters.clusters.clusters[i].x.error)
                    row.append(event.clusters.clusters.clusters[i].y.value)
                    row.append(event.clusters.clusters.clusters[i].y.error)
                    row.append(event.clusters.clusters.clusters[i].z.value)
                    row.append(event.clusters.clusters.clusters[i].z.error)
                    row.append(event.clusters.clusters.clusters[i].ywidth)
                    row.append(event.clusters.clusters.clusters[i].zwidth)
                    dataset.append(row)
        with open(EXEL_OUTPUT, 'wb') as f:
            f.write(dataset.export('xls'))
    else:
        do_parse(SESSION_FILE)
