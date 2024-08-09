from invoke import Collection, Program
from rpa_tasks.rpa_tasks.cli.tasks import deploy

namespace = Collection(deploy)

class RPACLI(Program):
    def __init__(self):
        super().__init__(namespace=namespace, name='rpa', version='1.0.0')

program = RPACLI()

if __name__ == "__main__":
    program.run()
