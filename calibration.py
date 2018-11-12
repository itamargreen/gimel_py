from tablib.core import Dataset
from gimel_session import GimelSession
from gimel_parser import parse
from parse_txt import do_parse
import json


USER_NAME = ''
PASSWORD = ''
IDNum=''
SESSION_FILE = 'part2_lambda.txt'
EXEL_OUTPUT = 'part2_lambda.xls'

minimum_energy = 5
step_size = 2
number_of_injections = 12
per_energy = 250
particle='lambda'

if __name__ == '__main__':
    with open('auth.json') as f:
        data = json.load(f)
    USER_NAME=data["username"]
    PASSWORD=data["password"]
    IDNum=data["id"]

    with GimelSession(user=USER_NAME, password=PASSWORD, output_file=SESSION_FILE) as g:
        g.start_gimmel()
        g.send_command(IDNum)
        g.send_particles_ascending_energies(particle, minimum_energy, step_size, number_of_injections,per_energy)
    with open(SESSION_FILE) as f:
        text = f.read()
    if particle is 'electron':
        events = parse(text)
        dataset = Dataset()
        dataset.headers = ('P','tandip', 'Kappa', 'd Kappa', 'Calorimeter Pulse Hights')
        for event in events:
            row = []
            row.append(event.energy)
            if len(event.tracks.tracks) is not 0:
                if event.tracks.tracks[0].parameters.tandip is not None:
                    row.append(event.tracks.tracks[0].parameters.tandip)
                else:
                    row.append('No tandip')
                row.append(event.tracks.tracks[0].parameters.akappa)
                row.append(event.tracks.tracks[0].error_matrix['akappa']['akappa'])
            else:
                row.append('no tracks')
                row.append('no tracks')
                row.append('no tracks')
            thing=[]
            for i in range(len(event.calorimeter.clusters.clusters)):
                thing.append(event.calorimeter.clusters.clusters[i].pulse_height)
            row.append(thing)
            dataset.append(row)

        with open(EXEL_OUTPUT, 'wb') as f:
            f.write(dataset.export('xls'))
    else:
        do_parse(SESSION_FILE)

