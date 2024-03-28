'''Plot.'''

from typing import List
from matplotlib import pyplot as plt
from matplotlib.container import BarContainer
from ..model.domain import (Job, Machine)
from ..model.variable import OperationStep



def plot_gantt_chart_axes(jobs:List[Job], machines:List[Machine], optimum:float=None):
    '''Initialize empty Gantt chart with `matplotlib`.

    Args:
        jobs (List[Job]): jobs list.
        machines (List[Machine]): machines list
        optimum (float, optional): optimized value to display. Defaults to None.

    Returns:
        tuple: (figure with 2x1 subplots, job axis, machine axis)
    '''
    # two subplots
    fig, (gnt_job, gnt_machine) = plt.subplots(2,1, sharex=True)

    # title and sub-title
    fig.suptitle('Gantt Chart', fontweight='bold')
    if optimum is not None:
        gnt_job.set_title(f'Optimum: {optimum}', color='gray', fontsize='small')

    # axes style
    gnt_job.set(ylabel='Job', \
        yticks=range(len(jobs)), \
        yticklabels=[f'J-{job.id}' for job in jobs])
    gnt_job.grid(which='major', axis='x', linestyle='--')

    gnt_machine.set(xlabel='Time', ylabel='Machine',\
        yticks=range(len(machines)), \
        yticklabels=[f'M-{machine.id}' for machine in machines])
    gnt_machine.grid(which='major', axis='x', linestyle='--')

    return fig, gnt_job, gnt_machine


def plot_gantt_chart_bars(axis_job, axis_machine, ops:List[OperationStep]=None, makespan:float=None):
    '''Plot Gantt chart.'''
    # title
    axis_job.set_title(f'Result: {makespan or "n.a."}',
                        color='gray',
                        fontsize='small',
                        loc='right')

    # clear plotted bars
    bars = [b for b in axis_job.containers if isinstance(b, BarContainer)]
    bars.extend([b for b in axis_machine.containers if isinstance(b, BarContainer)])
    for b in bars: b.remove()

    # plot new bars
    for op in (ops or []):
        axis_job.barh(op.source.job.id,
                        op.source.duration,
                        left=op.start_time,
                        height=0.5)
        axis_machine.barh(op.source.machine.id,
                            op.source.duration,
                            left=op.start_time,
                            height=0.5)

    # reset x-limit
    for axis in (axis_job, axis_machine):
        axis.relim()
        axis.autoscale()
