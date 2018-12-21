The script is not finished yet however it is possible to use it already on Windows with venv or on Linux without it

For using:

1) Download chromedriver from http://chromedriver.chromium.org and put it in the script folder (or specify existing via cli interface, the details in -h option of selenium_youla.py).
2) Create file "destinations.txt" (yep, on this stage it's still hardcoded) and write there list of locations (one location per line). Location is a group of key words to search it on map and first suitable pattern will be chosen
3) Fill past_output.csv by numbers you want to ignore
4) run "RUN.bat"


Output:
1) log
2) csv file compatible to gmail contact's csv file. The file containes phone numbers of youla's traders and it is possible to import it into your google contacts app

known issues:

1) Stack trace for web page elements which weren't clickable in time
2) venv seems does not contain some modules. It was discovered that still necessary to install python3 to run it


To add:

1) Switch selenium to headless mode
2) Filter for too active traders. The customer is not interested in professional traders, i.e. those who whave too many opened positions
