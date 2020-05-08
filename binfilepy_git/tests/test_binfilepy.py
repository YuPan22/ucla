"""
MIT License

Copyright (c) 2019 UCSF Hu Lab

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import os
import sys
from pathlib import Path
from binfilepy import BinFile
from binfilepy import CFWBINARY
from binfilepy import CFWBCHANNEL
from binfilepy import constant


def test_binfilewriter():
    filename = "mytest.bin"
    outfile = Path(filename)
    if outfile.exists():
        outfile.unlink()
    with BinFile(filename, "w") as f:
        header = CFWBINARY()
        header.setValue(1.0 / 240.0, 2019, 1, 28, 8, 30, 0.0, 0.0, 2, 0)
        f.setHeader(header)
        channel1 = CFWBCHANNEL()
        channel1.setValue("I", "mmHg", 1.0, 0.0)
        f.addChannel(channel1)
        channel2 = CFWBCHANNEL("II", "mmHg", 1.0, 0.0)
        f.addChannel(channel2)
        chanData = []
        d1 = [1, 2, 3, 4, 5, 6, 7, 8, 8, 7, 6, 5, 4, 3, 2, 1]
        d2 = [8, 7, 6, 5, 4, 3, 2, 1, 1, 2, 3, 4, 5, 6, 7, 8]
        data1 = []
        data2 = []
        for i in range(500):
            data1 = data1 + d1
            data2 = data2 + d2
        chanData.append(data1)
        chanData.append(data2)
        f.writeHeader()
        f.writeChannelData(chanData)
        f.updateSamplesPerChannel(8000, True)
    with BinFile(filename, "r") as g:
        g.readHeader()
        arr = g.readChannelData(0, 8000, False, False, 2.0)
        assert(len(g.channels) == 2)
        assert(g.header.SamplesPerChannel == 8000)
    # remove temporary file created
    try:
        outfile = Path(filename)
        if outfile.exists():
            outfile.unlink()
    except:
        # ignore error
        pass
    return
