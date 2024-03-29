# VHDLTestBenchGenerator
VHDL Test Bench Generator in Python 3.

This script takes a single VHDL file containing one entity declaration and one or more architectures, and produces a test bench file that does the following: 
* Declares and uses all packages from the input file
* Creates and assigns all relevant inputs and output ports, as well as generics
* Groups clocks and resets separately from GPIO
* Drives all clocks using a constant for the clock period
* Asserts, then deasserts, resets with a decent guess on its polarity
* Leaves a blank space for stimulus to go into
* Reports a failure to cut off simulations where the runtime isnt exactly known

Right now, its limitations are the following:
* Can't handle multiple entities 
* Only uses the first architecture for information
* Doesn't try to guess clock frequency, just assigns everything to 10ns period
* Doesn't use archiceture to guess reset polarity, only name
* Makes no guesses at GPIO stimulus
* Asserts and deasserts all resets at once

TODO:
* Detect multiple entites and group into different test bench files 
* Check all architectures for relevant info
* Attempt to use clock name for frequency guess (i.e. CLK_100MHz)
* Use architecture to determine reset polarities
* parse "range" attributes in ports and geenrics
