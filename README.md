# SmashCalc
Steals frame data from the KuroganeHammer API to calculate nice things like knockback and hitstun.

***

`smashcalc.py`  
**Author:** Euklyd / Fulminant Edge  
**Version:** 0.2

***Contact***  
**Discord:** euklyd (FE)#3650 *(preferred method)*  
**Twitter:** [http://twitter.com/euklydia](http://twitter.com/euklydia) *(rarely used, but I do check it)*  
**Email:** euklyd *(dot)* sf *(at)* gmail.com

***About***

Super barebones applet to calculate knockback and hitstun. Pulls from the KuroganeHammer API. KuroganeHammer and Frannsoft are both absolute saints; I can't believe such a convenient API exists.  
Coded up in about two evenings, and I've never made a GUI anything before, so it's really ugly right now (Euklyd with the sick pre-johns).

Formulas and credits: http://kuroganehammer.com/Smash4/Formulas  
API documentation: https://github.com/Frannsoft/FrannHammer/wiki  
Livedocs: http://api.kuroganehammer.com/swagger/ui/index

***Usage Instructions***

This program requires Python 3.5 or better (3.5.2 at last update), which you can get for free from [the official Python website](https://www.python.org/downloads/).

***EZ Instructions (Mac OS X / Linux)***

(1) Run `python3.5 --version ` in the Terminal application. If it prints out "python 3.5.x" (where x is anything) then skip to step (3)
(2) Download python 3.5 from https://www.python.org/downloads/
(3) Download this and save it to Downloads: https://github.com/euklyd/SmashCalc/archive/master.zip
(4) In Terminal, run `cd ~/Downloads/ && unzip SmashCalc-master.zip && cd SmashCalc-master && python3.5 smashcalc.py`

***EZ Instructions (Windows)***

If you don't already know how to do this stuff on Windows, then uh...

(1) Wait for me to eventually either package this into a standalone app, or port it to Android or something ¯\\\_(ツ)\_/¯

***

***TO-DO:***
- Add actual documetation strings,
- clean up code,
- parse weird percent fields (like Fox's throws),
- make user interface look pretty (or at least not terrible).

**Pipe-dream:**
Implement all this in HTML and JavaScript, so that it could be (potentially) hosted on an actual website. Unfortuantely JS can't make external requests, so the only place that could work is if it were hosted on KuroganeHammer itself.  
...I'm also just not that skilled at JavaScript.

***
