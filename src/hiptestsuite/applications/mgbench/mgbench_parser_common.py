# Copyright (c) 2021 Advanced Micro Devices, Inc. All rights reserved.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import os
import re

class MgbenchParser():
    def __init__(self, results):
        results.seek(0)
        logbytes = results.read()
        self.results = logbytes

    def parse(self, test):
        numgpus = 0
        gpumatch = re.search("GPUs: *\d+\s", self.results)
        if gpumatch:
            gpunum = re.split(":", gpumatch.group(0))
            numgpus = int(gpunum[1])
        else:
            return False

        result1 = self.results.count("Exchanging between")
        result2 = self.results.count("Copying from")
        passed = False
        if "fullduplex" == test:
            if numgpus > 1:
                if result1 > 0:
                    passed = True
            else:
                if result1 == 0:
                    passed = True
        else:
            if result2 > 0:
                passed = True

        return passed
