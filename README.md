The script is not finished yet however it is possible to use it already on Windows.

For using:

1) Download chromedriver from http://chromedriver.chromium.org and put it in the script folder.
2) Create file "destinations.txt" (yep, on this stage it's still hardcoded) and write there list of locations (one location per line). Location is a group of key words to search it on map and first suitable pattern will be chosen
3) run "RUN.bat"


Output:
1) log
2) csv file compatible to gmail contact's csv file. The file containes phone numbers of youla's traders and it is possible to import it into your google contacts app

known issues:

1) Stack trace for web page elements which weren't clickable in time
2) Some contacts were noticed as not beeing imported
3) venv seems does not contain some modules. It was discovered that still necessary to install python3 to run it
4) On linux venv fails to find web driver


To add:

1) Console interface and replace console options with hardcoded parameters
2) Switch selenium to headless mode
3) General refactoring
4) Filter for too active traders. The customer is not interested in professional traders, i.e. those who whave too many opened positions
