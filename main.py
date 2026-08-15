from financial_visualiser import FinancialVisualiser
from financial_tracker import FinancialTracker
from data_repository import DataRepository
import logging

def main():
    # Creates a single instance of DataRepository, then uses direct injection to call the methods
    # This is done to mitigate the risk of more than one instance once the database is established

    repo = DataRepository()

    # Allows user to select what they want to do
    while True:
        print('A Upload a file')
        print('B Visualise your account(s)')
        print('C Exit')
        upload_or_visualise = input('Please select an option from the list (A/B/C): ')

        if upload_or_visualise.upper() == "A":
            tracker = FinancialTracker(repo)
            tracker.upload_file()

        elif upload_or_visualise.upper() == "B":
            visualiser = FinancialVisualiser(repo)
            visualiser.visualisation_options()

        elif upload_or_visualise.upper() == "C":
            break

        else:
            print("Invalid input please try again")
            logging.info('Main - Invalid input please try again')

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
logging.getLogger('matplotlib').setLevel(logging.WARNING)

formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

file_handler = logging.FileHandler('log_info.log')
stream_handler = logging.StreamHandler()

stream_handler.setLevel(logging.INFO)
file_handler.setFormatter(formatter)
stream_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(stream_handler)

if __name__ == '__main__':
    main()