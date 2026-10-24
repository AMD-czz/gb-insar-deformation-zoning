import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'code'))
import unittest,tempfile
import numpy as np
from sbas_statistics import read_envi


class EnviChecks(unittest.TestCase):
    def test_header_and_big_endian(self):
        with tempfile.TemporaryDirectory() as folder:
            p=Path(folder)
            a=np.array([[1.,2.],[-3.,32767.]],dtype='>f4')
            a.tofile(p/'array')
            (p/'array.hdr').write_text('ENVI\nsamples = 2\nlines = 2\nbands = 1\ndata type = 4\nbyte order = 1\ndata ignore value = 32767\n')
            got,nd=read_envi(p/'array',p/'array.hdr')
            np.testing.assert_equal(got,a)
            self.assertEqual(nd,32767.)


if __name__=='__main__':
    unittest.main()
