# FireWatch

This is a script that records the websites visited in a Firefox browsing session,
assuming that history recording is enabled. This tool was created to show an example
of how a python script can be used to record Firefox sessions. The associated
blog post, which explains how this tool works, can be found here:
[Link to blog post](https://accentusoft.com/tutorials/recording-browser-sessions-with-100-lines-of-python/).

The names of sites visited are recorded and deduplicated.
Every unique webpage visited is saved to disk, and a full-page, timestamped
screenshot is taken.

## Usage
Clone this repository:

`git clone https://github.com/AccentuSoft/FireWatch`

Install the requirements:

`python3 -m pip install -r requirements.txt`

Get the Chromium browser:

`playwright install chromium`

Open firefox, and then start FireWatch:

`python3 ./FireWatch`

A new folder will be created, whose name will be the timestamp of when FireWatch
was started.
As you browse the internet, FireWatch will record the sites visited in the
'Session.txt' file, which will be generated inside the timestamp folder.
Each site visited will be saved, and screenshots will be taken. FireWatch will
print new sites visited to the terminal as it detects them.

To stop FireWatch, use `Ctrl+C` in the terminal that you launched it from.

## FAQ

### Why is chromium used by FireWatch to visit pages instead of Firefox?
Playwright's Chromium browser is a bit more reliable than Firefox for this sort
of task. Playwright's Firefox sometimes gives errors when visiting a lot of sites
in a single session, which is undesirable. Playwright's Chromium has its own
quirks of course, but it functions well here.

### FireWatch doesn't seem to record anything.
Some browser privacy settings stop Firefox from writing anything to the session file.
Disabling the recording of history is the most likely culprit. Try using FireWatch
with a new, default Firefox profile.

### How do I make this work with Tor?

You have to configure Tor to remember history, adjust the script to
read Tor's session file instead of Firefox's, and route your traffic over TOR.
A good way of doing this programmatically is with the python library 
[Stem](https://stem.torproject.org/tutorials.html).

Do note that having Tor remember the browsing history essentially negates the
privacy benefits of using Tor.

### I closed Firefox and FireWatch, and I noticed that some sites from the end of my browsing session are missing!
There is a delay between visiting a site and Firefox's session file updating.
Wait for a minute or so at the end of your session to make sure that everything
is recorded, or check FireWatch's output on the terminal to see if the last of
the sites visited are being processed.

### I want to extend this and extract cookies from my Firefox session. I understand most of the fields, but what do the numbers in 'sameSite' represent?
0 is "None",
1 is "Lax",
2 is "Strict".
