import re
from threading import Thread
import paramiko

decode = 'cp862'


class GimelSession(object):

    SERVER = 'gp.tau.ac.il'

    def __init__(self, user, password, output_file):

        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.client.connect(self.SERVER, username=user,password=password)
        self.shell = self.client.invoke_shell()
        self.write_data = self.save_output(output_file)
        """:type : Channel"""

    def __enter__(self):
        self.write_data.start()
        return self

    def __exit__(self, *args):
        self.write_data.join()

    def start_gimmel(self, output_mode=None, changes=None, **kwargs):
        output_mode = output_mode or '0'
        self.send_command('cd gimel')
        self.send_command('gimel')
        self.send_command(output_mode)
        if not changes:
            self.send_command('n')
        if changes == 'magnet':
            self.change_magnetic_field(kwargs.get('alpha',1))

    def change_magnetic_field(self, alpha):
        self.send_command('y')
        self.send_command('y')
        self.send_command(str(alpha))
        for i in range(3):
            self.send_command('n')

    def send_command(self,command=''):
        return self.shell.send(command + '\n')

    def send_particles_in_bulk(self,particle,energie,times):
        self.send_command(particle + ' ' + str(energie))
        for i in range(times):
            self.send_command('inject')

    def send_particles_ascending_energies(self, particle, initial_energie, delta, times):
        for i in range(times):
            self.inject_particle(particle, initial_energie)
            initial_energie += delta

    def inject_particle(self,particle,energie):
        self.send_command(particle + ' ' + str(energie))
        self.send_command('inject')


    def save_output(self,file):
        return Thread(target=self.output_thread, args=(file,))

    def output_thread(self, output_file):
        string = b''
        geant = re.compile(r'GEANT > $')
        with open(output_file, 'wb'):
            pass

        while True:
            if self.shell.recv_ready():
                while self.shell.recv_ready():
                    string += self.shell.recv(1024)
                s = string.decode(decode)
                shit = geant.search(s)
                if shit:
                    string = string[:shit.start()].rstrip()
                with open(output_file, 'ab') as f:
                    f.write(string)
                    string = b''
                if shit:
                    break

if __name__ == '__main__':
    pass
