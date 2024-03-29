'''Plot.'''

from typing import List
import networkx as nx
import matplotlib.pyplot as plt
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


def plot_gantt_chart_bars(axis_job,
                          axis_machine,
                          ops:List[OperationStep]=None,
                          makespan:float=None):
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


def plot_disjunctive_graph(num_jobs:int,
                           num_machines:int,
                           pos:dict,
                           job_edges:list,
                           machine_edges:list):
    '''Plot disjunctive graph.'''
    # adaptive size based on machine and job numbers
    W, H = int(2.0*(num_machines+2)), int(1.2*(num_jobs+1)) # figure size
    t = min(W/num_machines, H/num_jobs) # font size scale
    node_size, font_size = 800*t, 8*t

    # basic graph with job chain
    G = nx.DiGraph()
    for s, e, w in job_edges:
        if w:
            G.add_edge(s, e, weight=w)
        else:
            G.add_edge(s, e) # no weight for dummy start node

    # nodes
    options = {
        "node_size": node_size,
        "node_color": "white",
        "edgecolors": "black",
        "linewidths": 2
    }
    nx.draw_networkx_nodes(G, pos, **options)

    # job chain edge
    edges = [(u, v) for (u, v, d) in G.edges(data=True)]
    nx.draw_networkx_edges(G,
                           pos,
                           edgelist=edges,
                           node_size=node_size,
                           width=2)

    # machine chain edge in different style
    nx.draw_networkx_edges(G,
                           pos,
                           edgelist=machine_edges,
                           node_size=node_size,
                           width=2.5,
                           edge_color='b',
                           alpha=0.3,
                           style='--')

    # node labels
    nx.draw_networkx_labels(G, pos, font_size=font_size)

    # weight labels
    edge_labels = nx.get_edge_attributes(G, "weight")
    nx.draw_networkx_edge_labels(G, pos, edge_labels)

    # plot
    plt.rcParams['figure.figsize']= (W, H) # figure size
    plt.axis("off")
    plt.show()
