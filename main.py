import logging

import cleaner

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(name)s %(levelname)s: %(message)s')

if __name__ == '__main__':
    cleaner.start_if_needed()
