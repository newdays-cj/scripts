#!/usr/bin/python3

import os
import sys
import re
import Color

def ObjConfig(obj, content):
    while obj:
        for line in content:
            line = line.split(" ")
            if obj in line:
                target = line[0]
                temp = target.rsplit("-", 1)
                if len(temp) == 1:
                    continue

                obj, mod = temp[0], temp[1]
                # find xxx-$(CONFIG_xxx)
                match = re.search("\$\(CONFIG_.*\)", mod)
                if match:
                    config = re.split("\(|\)", mod)[1]
                    return config
                # obj-x: find in upper dir Makefile
                if obj == "obj":
                    return "Upper"

                # ext4-y: find ext4.o in current makefile
                obj = obj + ".o"
                break
        else:   # not find obj
            return "Not Found"
    return "Not Found"
            
def ObjsConfig(objs, makefile):
    if os.path.exists(makefile) == False:
        return "Upper"

    content = os.popen("cat " + makefile).read()
    content = content.replace("\\\n", " ").replace("\t", " ")
    content = re.sub(" +", " ", content)
    content = content.split("\n")
    print("find", objs, "in", makefile)

    for obj in objs:
        config = ObjConfig(obj, content)
        if config == "Not Found":
            continue
        return config
   
    return "Not Found"

def GetFileConfig(file):
    file = file.strip("\n")
    if file[len(file) - 2:] != ".c":
        return None
    
    directory, file = os.path.split(file)
    objs = [file[:len(file) - 2] + ".o"]
    
    while directory:
        makefile = directory + "/Makefile"
        directory, file = os.path.split(directory)
        config = ObjsConfig(objs, makefile)
        if config == "Not Found":
            return None
        if config == "Upper":
            for i in range(0, len(objs)):
                objs[i] = file + "/" + objs[i]
            objs = objs + [file + "/"]
            continue
        return config
    return None

def GetConfigs(commit):
    configs = []
    files = os.popen("git log --no-merges --pretty= --name-only -n 1 " + commit)
    for file in files:
        config = GetFileConfig(file)
        if config:
            configs.append(config)
    # Deduplication
    return list(set(configs))

def test():
            #some case can not handled
            #drivers/gpu/drm/amd will get None ##TODO
            #"ebc77bcc6e1660a011483c035d53c461c8dcc4f5": [],
            #
            #obj is controled by CONFIG
            #ifneq ($(CONFIG_SMP),y)
            #obj-y += up.o
            #endif
            #
            #obj for host, or sample
            #

    testcases = {
            #obj-$(CONFIG_xxx)
            "3aee752cd0b880b052b2757278227d09673a2abd": ["CONFIG_MAGIC_SYSRQ"],
            #ext4-$(CONFIG_xxx)
            "3f706c8c9257e0a90d95e8a1650139aba33d0906": ["CONFIG_EXT4_FS_SECURITY"],
            #obj-$(CONFIG_EXT4_FS) += ext4.o
            #ext4-y := super.o
            "4c2467287779f744cdd70c8ec70903034d6584f0": ["CONFIG_EXT4_FS"],
            #obj-y += char/
            #obj-y += mem.o random.o
            "e5f71d60ff167d0caa491659d65551a55ea6b406": [],
            #obj-$(CONFIG_SUN3) += config.o mmu_emu.o leds.o dvma.o intersil.o prom/
            #obj-y := init.o console.o printf.o  misc.o
            "d670b479586e457c7c36604cea08ae236fb933ac": ["CONFIG_SUN3"],
    }
    for case in testcases:
        configs = GetConfigs(case)
        if configs != testcases[case]:
            print(Color.red("test " + case + " failed"))
            print(Color.red("expect:"))
            print(testcases[case])
            print(Color.red("but:"))
            print(configs)
        else:
            print(Color.green("test " + case + " succes"))

def main():
    if sys.argv[1] == "test":
        test()

if __name__ == '__main__':
    main()

