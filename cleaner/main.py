import logging

from cleaner import robot_cleaner

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(name)s %(levelname)s: %(message)s')

if __name__ == '__main__':
    robot_cleaner.start_if_needed()
