# coding:utf-8
import logging
import sys
from libs.cli_output import banner
from libs.options import options


# if os.path.exists('error.log'):
#     os.remove('error.log')

if sys.version_info.major < 3 or sys.version_info.minor < 7:
    sys.stdout.write("Sorry, SecBlocks requires Python 3.7+ \n")
    sys.exit(1)

if __name__ == "__main__":
    logger = logging.getLogger()
    logger.setLevel(logging.ERROR)
    handler = logging.FileHandler(filename='error.log')
    logger.handlers.append(handler)

    try:
        banner()
        options()

    except KeyboardInterrupt as e:
        print('\nCtrl+C Stop running\n')
        print(e)
        sys.exit(0)
    except Exception as e:
        logging.exception(e)
        print(e)
