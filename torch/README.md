# Overview

## Software Architecture
The software comprises of the backend and the frontend system.  The backend system identifies the file folders and their files, and sends to the frontend system.  It also does the processing of file comparison.  The frontend system displays the User Interface (UI), which includes showing the output of file comparison, as well as a "slideshow" that broadens the display of each file selectively.

## UI Layout
The basic UI layout consists of an upper section, lower left section, and lower right section.  The upper section displays the names of the file folders.  The lower left section displays the files inside the folders, and contains the Load Files, Compare, Start Slideshow, and Stop Slideshow buttons.  The lower right section is divided into 3 parts sitting side by side, displaying the content of the files of the selected folders.

## Usage
- First, select the folders in the upper section, up to a maximum of 3.
- Next, select the files in the lower left section, up to a maximum of 3.
- Then, click the Load Files button.
- To have a wider view of the files after loading, click the Start Slideshow button.  Then press the left and right arrow keys on the keyboard to move the slide views.  Remember to click the Stop Slideshow button after you are done viewing the slides.
- To Compare files, only two files must be selected and loaded.  Click the Compare button after clicking the Load Files button.  Do not surf away from the webpage or click on any buttons until the results are shown.  The processing may about 8 minutes to compare two files of about 800 words each, and about 80 minutes to compare two files of about 4000 words each.
- To continue doing your work by surfing the Internet after pressing the Compare button, you may open another browser tab or window and use that to surf the Internet.

# Setup Procedures

## Start a Python virtual environment and install the requisite packages
- First, delete the package-lock.json file.
- Open your command line terminal.
- Run this command in the terminal:
```
npm install
```
- Ensure that python3 is installed:
```
python3 --version
```
- Create the directories:
```
mkdir ~/virtual
mkdir ~/virtual/test
```
- Create and start the virtual environment:
```
python3 -m venv ~/virtual/test
source ~/virtual/test/bin/activate
```
- Install all these packages:
```
pip install Flask Flask-Cors transformers bs4 html5lib lxml nltk beautifulsoup4 torch sentence-transformers
```

## Start the BackEnd Server
- Run this command in the terminal at the torch folder:
```
bash runserve.sh
```

## Start the FrontEnd Server
- Open up another terminal window.
- Run these commands in this new terminal at the torch folder:
```
npm start
```
