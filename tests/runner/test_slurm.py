import unittest
from PyExpUtils.runner.Slurm import MultiNodeOptions, SingleNodeOptions, to_cmdline_flags

class TestSlurm(unittest.TestCase):
    def test_Options(self):
        opts = SingleNodeOptions(
            account='def-whitem',
            time='2:59:59',
            cores=2,
            mem_per_core=4,
            sequential=30,
        )

        got = to_cmdline_flags(opts)
        expected = '--account=def-whitem --mem-per-cpu=4096M --nodes=1 --ntasks=1 --ntasks-per-node=2 --output=$SCRATCH/job_output_%j.txt --time=2:59:59'
        self.assertEqual(got, expected)

        opts = MultiNodeOptions(
            account='def-whitem',
            time='2:59:59',
            cores=8,
            mem_per_core=4,
            sequential=30,
        )

        got = to_cmdline_flags(opts)
        expected = '--account=def-whitem --cpus-per-task=1 --mem-per-cpu=4096M --ntasks=8 --output=$SCRATCH/job_output_%j.txt --time=2:59:59'
        self.assertEqual(got, expected)
