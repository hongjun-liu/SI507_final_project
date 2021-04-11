# SI507_final_project
This program is the final project of SI 507 and aims to facilitate travel to national sites. After implementing the interactive command line tool, the user can enter the state of interest and get useful information about the national site in that state, including the site name, site category (national site, national historical site, etc.), telephone, email, only To give a few examples. Users can also get some charts, showing the trail information of the country's site.

Data sources:                           
1.National park service website https://www.nps.gov/index.htm             
2.National park service data: https://developer.nps.gov/api/v1/parks?                
3.National parks and trails CSV: https://github.com/hongjun-liu/SI507_final_project.git

Getting started:
Prerequisites: python3, plotly, terminal(command line knowledge)

Installing:                          
1. Clone the repository onto your local system.                 
$ git clone https://github.com/hongjun-liu/SI507_final_project.git                       
2. Obtain (or create) the secret_data.py file with the necessary API keys. Please request a free API key from https://www.nps.gov/subjects/digital/nps-data-api.htm                        
3. Place secret_data.py at the root level in the final project directory.

Running the application:                
$ python3 SI507_final_project.py                     
Note: in your terminal, please change the directory to the final project directory before you run the program

Data presentation:                    
Firstly, the user will be asked to input a state name. If the input is not a state, you will be noticed that it is not appropriate and input a state name again.
It will show all national parks in this state.                   

Secondly, you will be asked to input a number which is in the list length. If the input is not a number of out of range, you will be noticed that it is not appropriate and input a valid number gain. In addition, you can input “back” so that you can go back the first input level where you should input a state name and it will show all national parks in this new state.
It will show all activities in this national park and visualize all related trails data by bar charts.(radar chart is not appropriate).In addition, you are asked to input another number to see 1 of 4 bar charts about these trails. And you can input “back” to go to latest level.            

Next, it will not stop when you visualize this national park’s data. And you will be asked to input a number again. This number refers one national park in the list before of the state.              

When you want to exit the program, you can just input “exit” in every input step and the program will exit.               

Built with: python3, beautifulSoup, requests, plotly, SQLite3

Author: hongjunl@umich.edu(Hongjun Liu)      Initial work!!!
