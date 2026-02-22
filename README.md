## Financial Data Tracker 


Initial Plan

---

#### Goal:



To create a program that takes in CSV files downloaded from my bank (may expand to others) consolidates them without repeats



Structure:

---

Financial Data Tracker

-> Master Record.csv

-> Read and Clean CSV.py

-> File to Make dashboard



#### Categories:



Housing



Bills

-Household

-Phone

-Insurance

-Other



Transportation

-Public

-Car



Food

-Groceries

-Eating Out



Shopping

-Clothes

\-



Healthcare

-Selfcare

-Medical



Personal

-Gym

-Haircuts

-Supplements



Investments

-Emergency Savings

-Debt

-Retirement

-House

-Holiday



Gifts

-Birthdays

-Christmas 

-Anniversary/Valentines

-Charity

-Other



Entertainment

-Nights out

-Concerts

-Movies

-Subscriptions



#### Problems:



Duplicate checking (if two transactions of same value on same day how do we ensure they aren't deleted?



CSV is read then checked against data based if any dates overlap. Unique ID is assigned to all transitions when stored in the master file.



Categorising spending automatically?



Either ask for all and use repeats to build automatic system (database comparison) or try a ML model? (Is there a training data base available?)



How will we analysing trends?

What Data do we want to see?


### Notes

Format to currency's on output to allow for int based manipulation to occur right until output

Need to consider what happens if data with headers is inputted and later on what happens if names and order are different





