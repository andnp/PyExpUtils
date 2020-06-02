import unittest
from PyExpUtils.runner.Slurm import Options

class TestSlurm(unittest.TestCase):
    def test_Options(self):
        opts = Options({
            'account': 'def-whitem',
            'time': '2:59:59',
            'cores': 1,
            'memPerCpu': '4G',
            'sequential': 30,
        })

        got = opts.cmdArgs()
        expected = '--account=def-whitem --time=2:59:59 --ntasks=1 --mem-per-cpu=4G --output=$SCRATCH/job_output_%j.txt'
        self.assertEqual(got, expected)

        opts = Options({
            'account': 'def-whitem',
            'time': '2:59:59',
            'nodes': 1,
            'coresPerNode': 40,
        })

        got = opts.cmdArgs()
        expected = '--account=def-whitem --time=2:59:59 --nodes=1 --ntasks-per-node=40 --output=$SCRATCH/job_output_%j.txt'
        self.assertEqual(got, expected)
