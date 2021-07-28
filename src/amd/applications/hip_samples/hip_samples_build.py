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
from amd.common.hip_shell import execshellcmd

class BuildRunCommon():
    '''
    In this class insert the build and execution steps for test cases
    which are identical across different platforms (amd/nvidia/intel).
    '''
    def __init__(self, path, logfile):
        self.thistestpath = path
        self.logfile = logfile

    def buildtest(self, env = None):
        cmdcd = "cd " + self.thistestpath + ";"
        cmd_clean = "make clean;"
        cmd_build = "make"
        cmdexc = cmdcd + cmd_clean + cmd_build
        execshellcmd(cmdexc, self.logfile, env)

    def clean(self):
        cmdcd = "cd " + self.thistestpath + ";"
        cmd_clean = "make clean;"
        cmdexc = cmdcd + cmd_clean
        execshellcmd(cmdexc, None, None)


class BuildRunAmd(BuildRunCommon):
    def __init__(self, path, logfile):
        BuildRunCommon.__init__(self, path, logfile)

    def buildtest(self):
        # In this function put the build steps for test cases
        # which differ across platforms (amd/nvidia/intel) else
        # invoke BuildRunCommon.buildtest
        ret = BuildRunCommon.buildtest(self)
        return ret


class BuildRunNvidia(BuildRunCommon):
    def __init__(self, path, logfile):
        self.hippath = os.path.join(os.getcwd(), "src/amd/conformance/HIP/")
        self.hipamdpath = os.path.join(os.getcwd(),"src/amd/conformance/HIPAMD/")
        BuildRunCommon.__init__(self, path, logfile)

    def getenvironmentvariables(self):
        envtoset = os.environ.copy()
        envtoset["HIP_PLATFORM"] = "nvidia"
        envtoset["HIP_COMPILER"] = "nvcc"
        envtoset["HIP_RUNTIME"] = "cuda"
        envtoset["HIP_DIR"] = self.hippath
        envtoset["HIP_AMD_DIR"] = self.hipamdpath
        envtoset["HIP_PATH"] = os.path.join(self.hipamdpath, "build")
        return envtoset

    def setupenvironmentfornvcc(self):
        cmdcd = "cd " + self.hipamdpath + ";"
        envtoset = self.getenvironmentvariables()
        cmdsetenv = "rm -Rf build/;mkdir build;cd build;"
        cmdbuildinstall =\
        "cmake -DHIP_PLATFORM=nvidia -DCMAKE_INSTALL_PREFIX=$PWD/install -DHIP_COMMON_DIR=\"$HIP_DIR\" -DHIP_AMD_BACKEND_SOURCE_DIR=\"$HIP_AMD_DIR\" ..;"
        cmdbuildinstall += "make install;"
        cmdexc = cmdcd + cmdsetenv + cmdbuildinstall
        execshellcmd(cmdexc, self.logfile, envtoset)

    def applypatch(self): # To be deleted
        cmd = "cd " + self.hippath + ";"
        cmd += "patch -p0 < ../../applications/hip_samples/Samples_Patch_4.2.x;"
        execshellcmd(cmd, self.logfile, None)

    def buildtest(self):
        buildbindirpresent = os.path.isdir(\
        os.path.join(self.hipamdpath, "build/bin"))
        buildincludedirpresent = os.path.isdir(\
        os.path.join(self.hipamdpath, "build/include"))
        buildinstalldirpresent = os.path.isdir(\
        os.path.join(self.hipamdpath, "build/install"))
        if not (buildbindirpresent & buildincludedirpresent & buildinstalldirpresent):
            self.setupenvironmentfornvcc()
        envtoset = self.getenvironmentvariables()
        # In this function put the build steps for test cases
        # which differ across platforms (amd/nvidia/intel) else
        # invoke BuildRunCommon.buildtest

        # Apply Patch. This is temporary and will be removed once Hip Samples changes
        # are available in HIP public repository.
        self.applypatch()
        ret = BuildRunCommon.buildtest(self, envtoset)
        return ret
