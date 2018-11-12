from collections import namedtuple
import re
from tablib.core import Dataset


def numberfy(string):

    if string.find('.') + 1:
        caster = float
    else:
        caster = int

    try:
        return caster(string)
    except ValueError:
        return string





SESSION_FILE = 'calibration_3.txt'


def do_parse(SESSION_FILE):

    injection = namedtuple('Injection', ('energy', 'clusters', 'tracks'))
    track = namedtuple('Track', ('num', 'kappa', 'dkappa'))
    cluster = namedtuple('Cluster', ('num', 'height', 'x', 'dx',
                                     'y', 'dy', 'z', 'dz', 'ywidth', 'zwidth'))
    block_tup=namedtuple('Block',('energy','actual_lines'))


    lines = []
    with open(SESSION_FILE) as f:
        lines = f.readlines()
    lines = [line for line in lines if line is not '\n']
    start_index = -1
    starting_energy = -1
    block_start = []
    energy_lines = []
    definition_re = re.compile(r'GEANT\s+>\s+[a-zA-Z-]*\s(\d+)\s*')
    for i in range(len(lines)):

        if 'GEANT > inject' in lines[i]:
            starting_energy = numberfy(
                definition_re.search(lines[i-1]).group(1))
            start_index = i
            break

    lines = lines[start_index:len(lines)]
    def find_energy(line_num, energies):
        prev = energies[0]
        for energy_line in energies:
            if line_num < energy_line:
                return numberfy(definition_re.search(lines[prev]).group(1))
            prev = energy_line
        return starting_energy

    for i in range(len(lines)):

        if 'GEANT > inject' in lines[i]:
            block_start.append(i)
        if definition_re.search(lines[i]) is not None:
            energy_lines.append(i)

    blocks = []

    for i2 in range(len(block_start)):

        if i2+1 >= len(block_start):
            blocks.append(block_tup(energy=find_energy(
                block_start[i2], energy_lines), actual_lines=lines[block_start[i2]:len(lines)]))
        else:
            blocks.append(block_tup(energy=find_energy(
                block_start[i2], energy_lines), actual_lines=lines[block_start[i2]:block_start[i2+1]]))

    injections = []
    cluster_re = re.compile(
        r'\s+(\d)\s+(\d+\.\d+)\s+(\d+\.\d+)\s\+/-(\d+\.\d+)\s+(-?\d+\.\d+)\s\+/-(\d+\.\d+)\s+(-?\d+\.\d+)\s\+/-(\d+\.\d+)\s+(\d+\.\d+)\s+(\d+\.\d+)\s*')
    kappa_re = re.compile(r'\s+\*\s+(-?\d+\.\d+E?-?\d+)')

    dkappa_re = re.compile(r'AKAPPA\s+(-?\d+\.\d+E?-?\d+)')
    for i in range(len(blocks)):
        single = blocks[i].actual_lines
        tracks_arr = []
        clusters_arr = []
        for j in range(len(single)):
            data_line = single[j]
            if cluster_re.fullmatch(data_line) is not None:
                result = cluster_re.search(data_line)
                cl = cluster(
                    num=numberfy(result.group(1)),
                    height=numberfy(result.group(2)),
                    x=numberfy(result.group(3)),
                    dx=numberfy(result.group(4)),
                    y=numberfy(result.group(5)),
                    dy=numberfy(result.group(6)),
                    z=numberfy(result.group(7)),
                    dz=numberfy(result.group(8)),
                    ywidth=numberfy(result.group(9)),
                    zwidth=numberfy(result.group(10))
                )
                clusters_arr.append(cl)
            elif '       AKAPPA  *  Curvature' in data_line:
                err_line = single[j+10]
                result = kappa_re.search(data_line)
                er = dkappa_re.search(err_line)
                tr = track(
                    num=len(tracks_arr)+1,
                    kappa=numberfy(result.group(1)),
                    dkappa=numberfy(er.group(1))
                )
                tracks_arr.append(tr)
        injections.append(injection(
            energy=blocks[i].energy,
            clusters=clusters_arr,
            tracks=tracks_arr
        ))

    final_text = ''

    for i in range(len(injections)):
        current = injections[i]
        section = 'injection #{}. E: {}\n'.format(i,current.energy)
        section += 'clusters:\n'
        section += 'No,P.H,x,dx,y,dy,z,dz,yW,zW\n'
        for j in range(len(current.clusters)):
            clust = current.clusters[j]
            section += '{},{},{},{},{},{},{},{},{},{}\n'.format(
                clust.num, clust.height, clust.x, clust.dx, clust.y, clust.dy, clust.z, clust.dz, clust.ywidth, clust.zwidth)
        section += '\n'
        section += 'tracks:\n'
        section += 'No,kappa,dkappa\n'
        for j in range(len(current.tracks)):
            trk = current.tracks[j]
            section += '{},{},{}\n'.format(
                trk.num, trk.kappa, trk.dkappa)
        section += '\n'
        final_text += section+'\n\n'

    output = open('result.txt', 'w')
    output.write(final_text)
