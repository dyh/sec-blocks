# coding=utf-8
import time
import pyfiglet
from libs.bcolors import Bcolors


def banner():
    ascii_banner = pyfiglet.figlet_format("SecBlocks")
    print(Bcolors.RED + ascii_banner + Bcolors.ENDC)


def console(blocks="", title="", value=""):
    timestamp = time.strftime("%H:%M:%S", time.localtime())
    timestamp = Bcolors.OKBLUE + '[' + timestamp + ']' + Bcolors.ENDC
    blocks = Bcolors.RED + blocks + Bcolors.ENDC
    value = Bcolors.OKGREEN + value + Bcolors.ENDC
    print(timestamp + ' - ' + blocks + '    ' + title + '    ' + value)


def console_progress(now, total, blocks, title="", value=""):
    timestamp = time.strftime("%H:%M:%S", time.localtime())
    timestamp = Bcolors.OKBLUE + '[' + timestamp + ']' + Bcolors.ENDC
    percent = "%0.1f%%" % (float(now) / float(total) * 100)
    percent = Bcolors.RED + percent + Bcolors.ENDC
    value = Bcolors.OKGREEN + value + Bcolors.ENDC
    print(timestamp + ' - ' + percent + " - " + blocks + '    ' + title + '    ' + value)
