# LaunchParallel
This simple python script takes two parameters:

* a file containing shell commands
* a number of processes to use

# Usage

Example:

```sh
python launch_parallel commands_test2.sh 12
```

The _commands_test2.sh_ file contains the commands to launch with one command per line. The number _12_ correspond to the number of commands to run in parallel. The number of processes to use is limited by the number of cores detected on the machine.

# Remarks

Lines starting with a '#' are considerred either as comments or configuration lines for the script. In these lines, it is possible to use the keywords *@block*, *@echo* and *@time*.

* the *@block* keyword delimits blocks of commands. The command blocks are independant. All the commands from one block will be executed before starting to execute the commands of the next one
* the *@echo* keyword can be used to display information. The syntax is like: _@echo something that you want to say_
* the *@time* keywork can be used to display the time at which the next command is executed