from Config.config import schema, data_folder, master_record_path, account_info_path
from matplotlib.dates import DateFormatter as DF, WeekdayLocator as WL, MonthLocator as MnL, DayLocator as DL, num2date
from matplotlib.ticker import AutoMinorLocator, AutoLocator, FuncFormatter

import matplotlib.pyplot as plt
import pandas as pd
import sys

class FinancialVisualiser:
    # Defines the data types of the files and the date formatting
    schema = schema

    def read_master(self):
        '''Reads the master file'''
        master_record = pd.read_csv(master_record_path, dtype=self.schema['dtypes'], parse_dates=self.schema['date_columns'], date_format=self.schema['date_format']
)
        return master_record

    def networth_plot(self, master_record):
        '''Displays a graph of networth over time'''

        # Prepares data for plotting by filtering out all but the last transaction on each day and filling days with no transactions
        pivot_master = master_record.pivot_table(index='Date', columns='Account Name', values='Balance', aggfunc='last')
        filled_master = pivot_master.ffill(axis='index')
        daily_networth = filled_master.sum(axis='columns')

        self.format_graph(daily_networth)

    def month_formatter(self, x, pos):
        date = num2date(x)
        if date.month == 1:
            return date.strftime('%b \n %Y')
        return date.strftime('%b')

    def format_graph(self, data):
        '''Configures all amount time graphs'''
        fig, ax = plt.subplots()
        ax.plot(data)
        
        # Sets the minor locators and formats them
        ax.xaxis.set_minor_locator(DL([8,16,24]))
        ax.xaxis.set_minor_formatter(DF(self.schema['minor_date_format']))
        
        ax.yaxis.set_minor_locator(AutoMinorLocator())

        # Sets the major locators and formats them
        ax.xaxis.set_major_locator(MnL(interval=1))
        ax.xaxis.set_major_formatter(FuncFormatter(self.month_formatter))

        ax.yaxis.set_major_locator(AutoLocator())
        ax.yaxis.set_major_formatter(self.schema['minor_currency_format'])

        plt.grid()
        plt.show()


    def spending_or_income_plot(self, master_record, transaction_type):
        '''Displays a graph of income or expenses and cleans out internal transfers'''

        # Branches for expenses or income graphs
        if transaction_type == 'Expenses':
            filtered_current = master_record[master_record['Amount'] < 0]

        elif transaction_type == 'Income':
            filtered_current = master_record[master_record['Amount'] > 0]
        
        # Filters out transfer to and froms within the same online banking account (internal transfers)
        # Potential Data Error - So far data shows xx\d{4} for internal transfers only and names for all externals
        mask = filtered_current['Desc'].str.contains(r'Transfer.*xx\d{4}', case=False, na=False)
        filtered_current= filtered_current[~mask]

        # Converts to pivot table and sums daily transactions across all accounts into one datum
        pivot_filter_current = filtered_current.pivot_table(index='Date', columns='Account Name', values='Amount', aggfunc='sum')
        daily_transactions = pivot_filter_current.sum(axis='columns')
        
        ###################################################################################################################################
        # Add a function which does the locators and formaters and finish style sheet for visuals e.g. grid lines, font, figure, colours, #
        ###################################################################################################################################

        self.format_graph(daily_transactions)

    def visualisation_options(self):
        '''Allows the user to select what they want to plot'''
        
        master_record = self.read_master()
        
        while True:
            print('A Networth')
            print('B Expenses')
            print('C Income')
            print('D Back to main menu')
            print('E Exit')

            plot_option = input('Please provide the letter of the plot you would like to make: ')

            if plot_option.upper() == 'A':
                self.networth_plot(master_record)

            elif plot_option.upper() == 'B':
                self.spending_or_income_plot(master_record, 'Expenses')

            elif plot_option.upper() == 'C':
                self.spending_or_income_plot(master_record, 'Income')

            elif plot_option.upper() == 'D':
                break

            elif plot_option.upper() == 'E':
                sys.exit()
            
            else:
                print('Invalid Input Please Try Again')