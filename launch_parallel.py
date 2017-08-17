'''
Created on Aug 11, 2017

@author: pydupont
'''


import multiprocessing
import os
import sys
import time
import datetime
from commands import getoutput

def run(x):
    """
    Run the command
    """
    return os.system(x)

def parallel_run(t, nb_cores):
    """
    Runs a list of commands in parallel using a given number of processes
    """
    sys.stdout.write("%s commands to execute on %s cores\n" %(len(t), nb_cores))    
    for i,tt in enumerate(t):
        if "@echo" in tt:
            if tt.startswith('#'): tt = tt[1:]
            line = " ".join([x for x in tt.split() if not x.startswith("@")])
            if "@time" in tt:
                line += " `date`"
            t[i] = "echo \"%s\r\n\"" % line
        elif "@time" in tt:
            t[i] = "echo `date`\r\n"
    num_tasks = len(t)
    p = multiprocessing.Pool(processes=nb_cores)
    rs = p.imap_unordered(run, t)
    p.close()
    while (True):
      completed = rs._index
      if (completed == num_tasks): break
      sys.stderr.write("Waiting for %s tasks to complete...\r" % (num_tasks-completed))
      time.sleep(1)

def main():
    NB_ARGS = 2
    """
    I dont use argument parsing libraries here to be compatible with python 2.6 and 2.7
    """
    if len(sys.argv) != NB_ARGS + 1:
        sys.stderr.write("Give two parameters: input command file and number of cores to use\n")
        exit(2)

    infile, nb_cores = sys.argv[1:]
    try:
        nb_cores = int(nb_cores)
        if nb_cores > multiprocessing.cpu_count(): raise ValueError()
        if nb_cores <= 0: raise ValueError()
    except ValueError:
        sys.stderr.write("%s is not a valid core number (should be an integer between 0 and %s)\n" % (nb_cores, multiprocessing.cpu_count()))
        exit(3)

    if not os.path.isfile(infile):
        sys.stderr.write("%s not a valid file\n" % infile)
        exit(3)

    #Create the list of commands. In case of blocks: it is a list of lists with one list of commands per blocks
    t = []
    blocks = False
    with open(infile) as f:
        for line in f:
            if "@block" in line:
                t.append("@echo @time %s\n" % line[line.index("@block") + len("@block"):].strip())
                if not blocks:
                    t = [list(t)]
                    blocks = True
                t.append([])
                continue
            if "#@exit" in line: break #usefull for debug
            if line.startswith('#') and "@" not in line: continue
            if not line.strip(): continue
            if blocks:
                t[-1].append(line.strip())
            else:
                t.append(line.strip())
                
    #In case of blocks, many parallel_runs are started sequencially
    if blocks:
        sys.stderr.write("%s command blocks containing %s commands to run in total\n" % (len(t), sum([len(x) for x in t])))
        for tt in t:
            parallel_run(tt, nb_cores)
    else:
        parallel_run(t, nb_cores)

if __name__ == "__main__":
    main()
