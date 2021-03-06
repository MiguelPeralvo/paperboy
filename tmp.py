import os
import os.path

with open('./examples/sample.ipynb', 'r') as fp:
    NOTEBOOK = fp.read()
with open('./examples/requirements.txt', 'r') as fp:
    REQUIREMENTS = fp.read()

NAME = 'test-job1'
DOKKU_SRC = 'dokku@host1.paine.nyc'


def launch(notebook_string, name, dokku_source):
    directory = new_directory()
    print(directory)
    print('voila starting')
    make_voila_proj(notebook_string, name, directory, REQUIREMENTS)
    print('voila done')
    print('dokku starting')
    remote = make_dokku_proj(directory, name, dokku_source)
    print('dokku done')
    print('deploy starting')
    dokku_deploy(remote)
    print('deploy done')


def new_directory():
    # try:
    #     from tempfile import TemporaryDirectory
    # except ImportError:
    #     from backports.tempfile import TemporaryDirectory
    # return TemporaryDirectory()
    from tempfile import mkdtemp
    return mkdtemp()


def make_voila_proj(notebook, name, directory, requirements):
    with open(os.path.join(directory, name + '.ipynb'), 'w') as fp:
        fp.write(notebook)

    with open(os.path.join(directory, 'run_job.py'), 'w') as fp:
        fp.write('''
import os
from voila.app import Voila

def launch_voila():
    v = Voila()
    v.notebook_path = os.path.join(os.path.dirname(__file__), '{}') + '.ipynb'
    v.port = int(os.environ.get('PORT', 5000))
    v.start()

if __name__ == '__main__':
    launch_voila()
'''.format(name))

    with open(os.path.join(directory, 'Procfile'), 'w') as fp:
        fp.write('web: python3 run_job.py')

    with open(os.path.join(directory, 'requirements.txt'), 'w') as fp:
        fp.write(requirements)


def make_dokku_proj(directory, name, dokku_source):
    from git import Repo
    repo = Repo.init(directory)

    track = [f for f in os.listdir(directory) if f not in ('.git')]
    repo.index.add(track)
    repo.index.commit('Readying repo for deploy')
    remote = repo.create_remote('dokku', url='{}:{}'.format(dokku_source, name))
    return remote


def dokku_deploy(remote):
    remote.push(refspec='master:master')

if __name__ == '__main__':
    launch(NOTEBOOK, NAME, DOKKU_SRC)
