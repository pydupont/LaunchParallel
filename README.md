# LaunchParallel
This simple python script takes two parameters:

* a file containing shell commands
* a number of processes to use


It will launch the shell commands in parallel using the provided number of processes to use.
The number of processes to use is limited by the number of cores detected on the machine.

Lines starting with a '#' are considerred either as comments or configuration lines for the script. In these lines, it is possible to use the keywords *@block*, *@echo* and *@time*.