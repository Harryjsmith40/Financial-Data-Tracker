from financial_visualiser import FinancialVisualiser
from financial_tracker import FinancialTracker

def main():

    # Allows user to select what they want to do
    while True:
        print('A Upload a file')
        print('B Visualise your account(s)')
        print('C Exit')
        upload_or_visualise = input('Please select an option from the list (A/B/C): ')

        if upload_or_visualise.upper() == "A":
            tracker = FinancialTracker()
            tracker.upload_file()

        elif upload_or_visualise.upper() == "B":
            visualiser = FinancialVisualiser()
            visualiser.visualisation_options()

        elif upload_or_visualise.upper() == "C":
            break

        else:
            print("Invalid input please try again")

if __name__ == '__main__':
    main()