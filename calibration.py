from tablib.core import Dataset
from gimel_session import GimelSession
from gimel_parser import parse


USER_NAME = ''
PASSWORD = ''
SESSION_FILE = 'calibration.txt'
EXEL_OUTPUT = 'calibration_stats.xlsx'

minimum_energy = 1
step_size = 0.2
number_of_injections = 250

if __name__ == '__main__':
    with GimelSession(user=USER_NAME, password=PASSWORD, output_file=SESSION_FILE) as g:
        g.start_gimmel()
        g.send_particles_ascending_energies('electron', minimum_energy, step_size, number_of_injections)
    with open(SESSION_FILE) as f:
        text = f.read()
    events = parse(text)
    dataset = Dataset()
    dataset.headers = ('P', 'Kappa', 'd Kappa', 'Calorimeter Pulse Hight')
    for event in events:
        row = []
        row.append(event.energy)
        row.append(event.tracks.tracks[0].parameters.akappa)
        row.append(event.tracks.tracks[0].error_matrix['akappa']['akappa'])
        row.append(event.calorimeter.clusters['PULSE-HEIGHT'][0])
        dataset.append(row)
    with open(EXEL_OUTPUT, 'wb') as f:
        f.write(dataset.export('xlsx'))
    dataset.export('sheets',name=EXEL_OUTPUT)