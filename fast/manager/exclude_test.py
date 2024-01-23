import json
import os

test_modules = ['mocha']


def processCmd(cmd):
    global test_modules
    wholeCmd = cmd.replace("\\", "")
    wholeCmd = wholeCmd.replace("\n", " ")
    wholeCmd = wholeCmd.split(" ")
    wholeCmd = [i.strip() for i in wholeCmd]
    wholeCmd = [i for i in wholeCmd if i != ""]

    i = 0
    testFiles = 'test/'
    while i in range(0, len(wholeCmd)):
        for j in test_modules:
            if j in wholeCmd[i]:
                i = i + 1
                break
        if wholeCmd[i].startswith("NODE_ENV"):
            i = i + 1
            continue
        elif wholeCmd[i].startswith('--'):
            i = i + 2
            continue
        if i < len(wholeCmd):
            testFiles = wholeCmd[i]
            break
    return testFiles


def exclude_test(pkgpath):
    global test_modules
    exclude_dir = ''
    jsonfile = os.path.join(pkgpath, "package.json")
    Makefile = os.path.join(pkgpath, "Makefile")

    with open(jsonfile) as f:
        jsonContent = json.load(f)

    testDir = ''
    if 'scripts' in jsonContent:
        for command in jsonContent['scripts']:
            # print("command:", command)
            if command == 'test':
                commandContent = jsonContent['scripts'][command]
                for j in test_modules:
                    if j in commandContent:
                        # print("===test modules used:===")
                        # print(commandContent)
                        testDir = processCmd(commandContent)  # the default dir for mocha
                        # print("===test dir we should ignore:===")
                        # print(testDir)
                        exclude_dir = testDir
                if 'make' in commandContent:
                    # print(commandContent)
                    shellCmd = commandContent.split("make")[1].strip()
                    with open(Makefile) as f:
                        makefile = f.read()
                    if shellCmd + ':' in makefile:
                        # print(shellCmd,"found in makefile")
                        # print(commandContent)
                        os.chdir(pkgpath)
                        os.system(commandContent + ' --just-print > exclude_command.txt')
                        with open("exclude_command.txt") as f:
                            wholeCmd = f.read()
                        # print(wholeCmd)
                        # print("===test modules used:===")
                        # print(wholeCmd)
                        testFiles = processCmd(wholeCmd)
                        # print("===test dir we should ignore:===")
                        # print(testFiles)
                        exclude_dir = testFiles
    return exclude_dir


if __name__ == '__main__':
    # pkgpath = "/Users/susie/Documents/projects/columbia/RogueOneSamples_2/RandomBenignSamples2/proxy_1.0.1-->1.0.2/proxy-1.0.2"
    # pkgpath = '/Users/susie/Documents/projects/columbia/RogueOneSamples_2/RandomBenignSamples2/box_0.0.3-->0.0.4/box-0.0.4'
    pkgpath = '/Users/susie/Documents/projects/columbia/RogueOneSamples_2/RandomBenignSamples2/fed_0.1.2-->0.1.3/fed-0.1.3'
    res = exclude_test(pkgpath)
    print(res)