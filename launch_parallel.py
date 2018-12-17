'''
Created on Aug 11, 2017

@author: pydupont
'''


import ezpq
import subprocess
import click
import shlex
import os
import sys
import time
import datetime
import multiprocessing

def run(t):
    """
    Run the command
    """
    if "@echo" in t:
        if t.startswith('#'): t = t[1:]
        line = " ".join([x for x in t.split() if not x.startswith("@")])
        if "@time" in t:
            line += " `date`"
        t = "echo \"%s\r\n\"" % line
    elif "@time" in t:
        t = "echo `date`\r\n"
    output = subprocess.check_output(t, shell=True).decode('utf-8')
    if len(output.strip()):
        sys.stderr.write(output)

def print_sizes(Q):
    msg = 'Total: {0}; Waiting: {1}; Working: {2}; Completed: {3}'.format(
        Q.size(),
        Q.size(waiting=True),
        Q.size(working=True),
        Q.size(completed=True)
    )
    print(msg)

def parallel_run(t, nb_cores):
    """
    Runs a list of commands in parallel using a given number of processes
    """
    with ezpq.Queue(n_workers=nb_cores) as Q:
        # enqueue jobs
        for tt in t:
            Q.put(run, args=[tt])

        # repeatedly wait 1 second for jobs to finish until n_remaining == 0.
        n_remaining = Q.wait(timeout=2)
        while n_remaining > 0:
            print('{0:5} jobs remain.'.format(n_remaining))
            n_remaining = Q.wait(timeout=2)
        print('{0:5} jobs remain.'.format(n_remaining))

def read_input(infile):
    """Create the list of commands. In case of blocks: it is a list of lists with one list of commands per blocks
    
    :param infile: Input file
    :type infile: file

    :return: tasks list
    :rtype: list
    """
    t = []
    blocks = False
    lines = infile.readlines()
    if "@block" in "\n".join(lines):
        blocks = True
    if blocks:
        tt = []
        for line in lines:
            if "@block" in line:
                if tt:
                    t.append(tt)
                tt = ["#@echo @time %s" % line[line.index("@block") + len("@block"):].strip()]
            else:
                if "#@exit" in line: break #usefull for debug
                if line.startswith('#') and "@" not in line: continue
                if not line.strip(): continue
                tt.append(line.strip())
        t.append(tt)
    else:
        for line in lines:
            if "#@exit" in line: break #usefull for debug
            if line.startswith('#') and "@" not in line: continue
            if not line.strip(): continue
            t.append(line.strip())
    return t, blocks

def process(t, blocks, nb_cores):
    #In case of blocks, many parallel_runs are started sequencially
    if blocks:
        cmds = []       
        for tt in t:
            cmds.append(sum([1 for x in tt if(not(x.startswith("@")) and not(x.startswith("#")))]))
        sys.stderr.write("%s command blocks containing %s commands to run in total\n" % (len(t), sum(cmds)))
        for tt in t:
            parallel_run(tt, nb_cores)
    else:
        parallel_run(t, nb_cores)

@click.command()
@click.option("-t", "nb_cores", help="Number of threads to use", default=1, type=int)
@click.argument("infile", required=True, type=click.File('r'))
def main(nb_cores, infile):
    """This python utility helps starting tasks on many cores for parallel processing.
    \b
    Example:
        launch_parallel -t 24 commands_test1.sh
    """
    try:
        if nb_cores > multiprocessing.cpu_count(): raise ValueError()
        if nb_cores <= 0: raise ValueError()
    except ValueError:
        sys.stderr.write("%s is not a valid core number (should be an integer between 0 and %s)\n" % (nb_cores, multiprocessing.cpu_count()))
        exit(3)

    t, blocks = read_input(infile)
    process(t, blocks, nb_cores)


if __name__ == "__main__":
    main()
