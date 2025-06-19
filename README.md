# ShipmentScrapers

---

## Quick Start Guide

### 1. Download and Open

- Download the ShipmentScrapers zip file and extract it to a folder on your computer.
- Open the folder in Visual Studio Code (VS Code).

### 2. Set Up Python

- In VS Code, open a new terminal window (View > Terminal).

### 3. Create a Virtual Environment

Type the following command in the terminal and press Enter:

```
python -m venv venv
```

4. Run:

'''
venv/Scripts/activate
'''

5. Click CTRL and SHIFT and P
6. Select Python Interpreter -> Click the recommended one
7. Close the terminal and open a new one
8. Run:
'''
pip list
'''
Must only show 1 library (pip)
9. Run: 
'''
pip install -r requirements.txt
'''
10. Run scrapers:

- Before running, make sure to modify the INPUT and OUTPUT FILE PATH in Maersk.py, One.py, and CMA.py
- The scraper might malfunction when it is running the first time, in such case, simply re-run it.
- Make sure the browser window is open, and free from interruption of mouse movements
- The error 'Bad gateway' appearing on website (CMA-CGM) is out of scope of the scraper, it is the website problem, simply reload the page as soon as possible

- Maersk
'''
python -m Maersk.Maersk
'''

- One
'''
python -m OneEcomm.One
'''

- CMA
'''
python -m CMA.CMA
'''

