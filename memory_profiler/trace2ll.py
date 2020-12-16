#!/usr/bin/python3.6
# Developed for Python version 3.6.9

"""
trace2ll.py

Converts a sequence of traces of memory access strides into a linked list
Also removes small strides and store accesses and classifies array accesses
"""

import os
import sys
import json
import math
import time
import argparse
import collections
import warnings
import multiprocessing as mp
from copy import copy
from textwrap import dedent
from queue import Empty
from typing import List, Dict, Tuple
from functools import total_ordering
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd

Page_Size_B = 1 << 12
List_Entry_Size_B = 8

"""
Formats a time (in seconds) as D:HH:MM:SS.mmm
"""
def format_time(time_s: float) -> str:
    if np.isnan(time_s):
        return "?:??:??:??"
    ms = int(time_s * 1000) % 1000
    int_time = int(time_s)
    if (ms >= 500):
        int_time += 1
    s = int_time % 60
    int_time //= 60
    m = int_time % 60
    int_time //= 60
    h = int_time % 24
    d = int_time // 24
    return f"{d}:{h:02}:{m:02}:{s:02}"

"""
Redirects the stdout of the wrapped function to a pipe
Useful for multiprocessing
"""
def wrap_mp_stdout(_w, _q, name, func, args):
    os.dup2(_w.fileno(), sys.stdout.fileno()) # Redirect stdout to pipe write port
    ret = func(**args)
    _q.put({name: ret})
    _w.close()

"""
Parallelize calling independent functions with args
"""
def parallelize_func_calls(functions, args, names, max_processes):
    print(f"Running in parallel on {min(max_processes, len(functions))} processes")
    if args is None:
        args = [{}]*len(functions)
    if names is None:
        names = [f"process{i}" for i in range(len(functions))]
    pending_processes = [p for p in zip(functions, args, names)]
    active_processes = []
    q = mp.Queue()
    ret_data = {}
    while len(pending_processes) > 0 or len(active_processes) > 0:
        while len(active_processes) < max_processes and len(pending_processes) > 0:
            process_func, process_args, process_name = pending_processes.pop(0)
            print(f"Starting process {process_name}")
            r, w = mp.Pipe(duplex=False) # We're going to redirect stdout from the child process to this pipe
            active_processes.append({"name": process_name, "process": mp.Process(target=wrap_mp_stdout, args=(w,q,process_name,process_func,process_args,)), \
                "reader": r, "fhandle": os.fdopen(r.fileno(), "r")})
            active_processes[-1]["process"].start()
            w.close() # We won't need to access this port from the parent process, so we'll go ahead and close it off here
        
        # Check if the running processes have anything new to print
        for process_info in active_processes:
            if process_info["reader"].poll(): # Changing this to "while" causes readline to block indefinitely for some reason...
                stripped_line = process_info["fhandle"].readline().strip()
                if len(stripped_line) > 0:
                    print(f"{process_info['name']}: {stripped_line}")

        while True:
            try:
                ret_data.update(q.get(block=False))
            except Empty:
                break

        new_active_processes = []
        for process_info in active_processes:
            if not process_info["process"].is_alive():
                print(f"Process {process_info['name']} has exited")
                for line in process_info["fhandle"]:
                    stripped_line = line.strip()
                    if len(stripped_line) > 0:
                        print(f"{process_info['name']}: {stripped_line}")

                if process_info["process"].exitcode != 0:
                    sys.exit(f"Process {process_info['name']} exited with error code {process_info['process'].exitcode}")
                print(f"Process {process_info['name']} exited successfully")
            else:
                new_active_processes.append(process_info)
        active_processes = new_active_processes
        
        time.sleep(0.01)
    waited = False
    while len(ret_data) < len(names):
        try:
            ret_data.update(q.get(block=False))
            waited = False
        except Empty:
            if not waited:
                time.sleep(1)
                waited = True
            else:
                sys.exit("Fewer items than expected returned from parallel run")

    print(f"Parallel run finished")
    del q
    return ret_data

"""
Returns a string which will fill specified number of list entries with specified value
"""
def fill_entries_with_value(entries_to_fill: int, value: int, to_hex: bool = False) -> str:
    count = entries_to_fill * 2
    repeat_str = "REPEAT("
    repeat_str += str((count//10000000000)%10) + ","
    repeat_str += str((count//1000000000)%10) + ","
    repeat_str += str((count//100000000)%10) + ","
    repeat_str += str((count//10000000)%10) + ","
    repeat_str += str((count//1000000)%10) + ","
    repeat_str += str((count//100000)%10) + ","
    repeat_str += str((count//10000)%10) + ","
    repeat_str += str((count//1000)%10) + ","
    repeat_str += str((count//100)%10) + ","
    repeat_str += str((count//10)%10) + ","
    repeat_str += str((count//1)%10) + ","
    if to_hex:
        repeat_str += f" {hex(value)},) "
    else:
        repeat_str += f" {value},) "
    return repeat_str

"""
Class for representing logarithmic strides
"""
@total_ordering
class LogStride:
    """
    Returns the "next larger" stride:
      -n -> -(n-1) for n > 0; -> *0 for n == 0
      *0 -> +0
      +n -> +(n+1)
    """
    def next_larger(self):
        next_stride = LogStride(0)
        next_stride.is_infinitesimal = self.is_negative and self.magnitude == 0
        next_stride.is_negative = self.is_negative and self.magnitude > 0
        if self.is_negative and self.magnitude == 0:
            next_stride.magnitude = 0
        elif not self.is_negative and self.is_infinitesimal:
            next_stride.magnitude = 0
        elif self.is_negative:
            next_stride.magnitude = self.magnitude - 1
        else:
            next_stride.magnitude = self.magnitude + 1
        return next_stride

    def __hash__(self):
        return hash((self.is_infinitesimal, self.is_negative, self.magnitude))

    def __eq__(self, other):
        return self.is_negative == other.is_negative and self.magnitude == other.magnitude

    def __lt__(self, other):
        if self.is_negative and not other.is_negative:
            return True
        elif not self.is_negative and other.is_negative:
            return False
        elif self.is_infinitesimal:
            return not other.is_infinitesimal # infinitesimal is < all positive except another infinitesimal
        elif self.is_negative:
            return self.magnitude > other.magnitude
        else:
            return self.magnitude < other.magnitude

    def __abs__(self):
        abs_stride = copy(self)
        abs_stride.is_negative = False
        return abs_stride

    def __int__(self):
        if not self.is_infinitesimal:
            int_repr = int((2 ** self.magnitude) + (2 ** (self.magnitude-1)))
            if self.is_negative:
                int_repr *= -1
        else:
            int_repr = 0
        int_repr *= List_Entry_Size_B
        return int_repr

    def __str__(self):
        if self.is_infinitesimal:
            return f"*{self.magnitude}"
        elif self.is_negative:
            return f"-{self.magnitude}"
        else:
            return f"+{self.magnitude}"

    def __repr__(self):
        return str(self)

    def __init__(self, stride: int):
        if abs(stride) < List_Entry_Size_B:
            self.is_infinitesimal = True
            self.is_negative = False
            self.magnitude = 0
        else:
            self.is_infinitesimal = False
            self.is_negative = (stride < 0)
            # Actually no point in rounding, since the target is ~= 1.5 * 2**self.magnitude
            # If you do the math, rounding down will always be better
            self.magnitude = int(math.log(abs(stride//List_Entry_Size_B), 2))
        self.linear_value = stride // List_Entry_Size_B
        self.linear_fractional_err = self.linear_value - (stride / List_Entry_Size_B) # Gap between achieved and ideal

"""
A single node in a linked list; "wants" to be a certain distance from its predecessor (unless it's the first item in the list)
"""
class LLNode:
    """
    Recalculate a node's stress and update the global stress - should be done after moving a node or its predecessor
    """
    def update(self) -> None:
        if self.node_id == 0: # The first node inherently has zero stress
            self.stress = 0
            return

        self.target_location = self.prev.location + self.target_offset
        deviance = abs(self.location - self.target_location)
        # Basically a backwards Huber function - mildly penalize small deviance, heavily penalize large deviance
        if deviance <= self.linear_deviance_range:    # Small deviances have a linear penalty function
            new_stress = abs((deviance << 10) >> self.log_deviance_range)
        else:                                        # Larger deviances have a quadratic penalty function
            new_stress = ((deviance << 5) >> self.log_deviance_range) ** 2
        d_stress = new_stress - self.stress
        self.parent_list.global_stress += d_stress
        self.stress = new_stress

    """
    Sets a node's location to a new position WITHOUT performing a check to make sure the position is unoccupied
    Unsafe accesses are required to support swapping nodes
    """
    def set_location(self, new_location):
        if self.location is not None:
            del self.parent_list.nodes_by_location[self.location]

        self.location = new_location 

        self.parent_list.nodes_by_location.update({self.location : self})
        self.update()
        self.next.update()
    
    """
    Updates a node's location to a new position after first making sure that position is unoccupied.
    """
    def move_to_location(self, new_location):
        if new_location in self.parent_list.nodes_by_location:
            sys.exit("Attempted to move a node to an occupied location")
        self.set_location(new_location)

    """
    Swaps the locations of this and another node
    """
    def swap_locations(self, other):
        self_loc = self.location
        other_loc = other.location
        self.set_location(other_loc)
        other.location = None # Invalidate location without deleting entry in nodes_by_location (which would clobber node A)
        other.set_location(self_loc) 
    
    def __init__(self, parent_list, log_stride):
        self.parent_list = parent_list
        self.node_id = len(self.parent_list)

        if self.node_id == 0: # First node in list
            self.prev = self
            self.next = self
            self.target_offset = 0
            init_location = 0
            ideal_location = 0
        else:
            self.prev = self.parent_list[-1]
            self.next = self.parent_list[0]
            self.prev.next = self
            self.next.prev = self

            self.target_offset = log_stride.linear_value #int(log_stride) // List_Entry_Size_B
            self.log_deviance_range = max((log_stride.magnitude-1), 0)
            self.linear_deviance_range = 2 ** self.log_deviance_range

            init_location = None
            ideal_location = self.prev.location + self.target_offset # Zero-stress location
            min_displacement = min(-2*self.linear_deviance_range, -self.parent_list.cluster_placement_delta)    # First location to test
            max_displacement = max(2*self.linear_deviance_range, self.parent_list.cluster_placement_delta)      # Last location to test
            # Test locations in the order that improves cluster_placement_delta by most to least (want cluster_placement_delta to stay close to 0)
            displacements = sorted(range(min_displacement, max_displacement+1), key=lambda x: abs(x + self.parent_list.cluster_placement_delta))
            for displacement in displacements:
                test_location = ideal_location + displacement
                if test_location not in self.parent_list.nodes_by_location:
                    init_location = test_location
                    break
            if init_location is None: # Try one more thing before we fall back to the failure case
                extra_displacements = sorted([x for x in range(-1024,1024+1) if x not in displacements], key=lambda x: abs(x + self.parent_list.cluster_placement_delta))
                for displacement in extra_displacements:
                    test_location = ideal_location + displacement
                    if test_location not in self.parent_list.nodes_by_location:
                        init_location = test_location
                        break

        if init_location is not None:
            self.parent_list.cluster_placement_delta += init_location - ideal_location # Running total of our deviance from the ideal trace
            
        if init_location is None:                           # Assignment failed; no free locations nearby
            print(f"At node {self.node_id}: no nearby free location, falling back to edge-of-list placement", flush=True)
            #self.parent_list.cluster_placement_delta = float("inf") if self.parent_list.cluster_placement_delta >= 0 else -(float("inf"))
            self.parent_list.cluster_placement_delta = \
                float("inf") if ((ideal_location - self.parent_list.min_location) < (self.parent_list.max_location - ideal_location)) \
                else -(float("inf"))
       
        """
        If the node is truly unable to be placed, the generator will fall back to creating a new "cluster"
        A "cluster" is ideally an accurate representation of the trace, but with a DC offset from the ideal
        Normally, clusters are placed immediately before or after the existing list - we call this a "desynchronization"
        But, in some cases, it's actually possible to resynchronize with the original trace (i.e. make the DC offset zero)
        This can happen if, for instance, a trace begins dense and becomes sparse later on - good if it happens!!
        """

        if abs(self.parent_list.cluster_placement_delta) > (1 << 12): # We're off from where we should be, so we're going to add a DC offset to the target and hope for the best
            direction = "negative" if self.parent_list.cluster_placement_delta < 0 else "positive"
            print(f"At node {self.node_id}: large {direction} delta; giving up on this cluster and starting a new one", flush=True)
            self.parent_list.fallback_nodes += 1 # Keep track of when this happens, because it's bad if this is frequent 
            if not (self.parent_list.min_location <= (ideal_location - self.parent_list.permanent_placement_delta) <= self.parent_list.max_location):
                print("  Resynchronizing with target trace", flush=True)
                init_location = ideal_location - self.parent_list.permanent_placement_delta # Resynchronize
            else:
                print("  Desynchronized from target trace", flush=True)
                # Jump to closest edge of list
                init_location = \
                    self.parent_list.min_location-1024 if ((ideal_location - self.parent_list.min_location) < (self.parent_list.max_location - ideal_location)) \
                    else self.parent_list.max_location+1024
            self.parent_list.cluster_placement_delta = 0 # Now in a new cluster

        assert init_location not in self.parent_list.nodes_by_location
        self.parent_list.permanent_placement_delta += init_location - ideal_location
        if init_location > self.parent_list.max_location:
            self.parent_list.max_location = init_location
        if init_location < self.parent_list.min_location:
            self.parent_list.min_location = init_location
        self.stress = 0
        self.location = None
        self.move_to_location(init_location)

"""
Linked list which attempts to determine target memory locations for its nodes based on specified log strides
"""
class LinkedList:
    """
    "Flattens" data structure to avoid recursion limit issues with pickling
    """
    def flatten(self) -> None:
        if self.flattened:
            warnings.warn("Tried to flatten an already flat list")
            return
        for node in self.nodes:
            node.prev = node.prev.location
            node.next = node.next.location
        self.flattened = True

    """
    Undoes the flattening operation
    """
    def unflatten(self) -> None:
        if not self.flattened:
            warnings.warn("Tried to unflatten an already unflat list")
            return
        for node in self.nodes:
            node.prev = self.nodes_by_location[node.prev]
            node.next = self.nodes_by_location[node.next]
        self.flattened = False

    """
    Adds a new node to the tail of the linked list
    """
    def add_node(self, log_stride: LogStride) -> None:
        flattened = self.flattened
        if flattened:
            self.unflatten()

        self.nodes.append(LLNode(self, log_stride))

        if flattened:
            self.flatten()

    """
    Optimizes the locations of nodes within the linked list to attempt to minimize an objective function ("stress")
    Uses a variant of the threshold accepting optimization algorithm, similar to a non-stochastic simulated annealing
    Consists of two pass types with subtly different objectives: "aggressive" and "consolidation" passes
    During an aggressive pass, nodes attempt to minimize their stress w.r.t. the previous node, without paying attention to the next node
    During a consolidation pass, nodes attempt to minimize the global stress (i.e. they also check how their decisions affect the next node)
    """
    def optimize(self, initial_threshold: int=1<<24, threshold_decay: float=0.98, max_iterations: int=500):
        if self.flattened:
            self.unflatten()

        optimization_start_time = time.monotonic()

        # Active nodes are defined as those that are actively trying to move to a new, better position
        # Nodes that are "close enough" to a good position become inactive, which can make the algorithm run (much!) faster
        total_nodes_in_list = len(self)
        active_nodes_in_list = total_nodes_in_list # Initially, all nodes are considered active

        print(f"Beginning optimization of a linked list with {total_nodes_in_list} total nodes")
        print(f"  Parameters: initial_threshold = {initial_threshold}; threshold_decay = {threshold_decay}; max_iterations = {max_iterations}")
        sys.stdout.flush()

        threshold = initial_threshold   # How "bad" of a choice the algorithm will make; decays over time
        marginal_progress_count = 0     # How many iterations in a row the algorithm has detected marginal progress; too many will cause an early halt
        marginal_iteration_cutoff = 24  # Terminate after this many marginal iterations in a row
        progress_never_marginal = True  # Passes are always aggressive until the first marginal iteration; this speeds up convergence

        # Parameters for marginal progress calculation
        # These are interesting to play around with - we're checking for forward progress comparing regions of various lengths
        comparison_history_length = marginal_iteration_cutoff // 2
        comparison_history = [float("nan")]*comparison_history_length
        stress_history_lengths = [32, 64, 128, 256, 512]                # Remember the previous <n> entries
        #stress_marginality_thresholds = [0.95, 0.90, 0.60, 0.30, 0.10]  # Marginal if <m> < current/avg < <1/m>
        stress_marginality_thresholds = [0.95, 0.90, 0.80, 0.70, 0.60]  # Marginal if <m> < current/avg < <1/m>
        stress_histories = [[float("nan")]*n for n in stress_history_lengths]

        pass_elapsed_time = float("NaN")
        elapsed_time_history = []
        iteration = -1
        for iteration in range(max_iterations):
            pass_start_time = time.monotonic()

            # Should this be an aggressive pass (local optimal) or a consolidation pass (global optimal)?
            aggressive_pass = ((marginal_progress_count < (marginal_iteration_cutoff//2)) and   # Not close to termination due to marginality and
                (max_iterations - iteration > (marginal_iteration_cutoff//2)) and               # Not close to termination due to max_iterations and
                ((iteration % 4 == 0) or progress_never_marginal))                              # 25/75 UNLESS never marginal

            print(f"At beginning of iteration {iteration}:")
            if aggressive_pass:
                print("  Pass type: Aggressive (local optimal)")
            else:
                print("  Pass type: Consolidation (global optimal)")
            print(f"  threshold = {threshold}; global_stress = {self.global_stress}; marginal_progress_count = {marginal_progress_count}")
            print(f"  active_nodes_in_list = {active_nodes_in_list} ({(100 * active_nodes_in_list) / float(total_nodes_in_list)}%)")
            total_elapsed_time = time.monotonic() - optimization_start_time
            try:
                #eta = total_elapsed_time * ((max_iterations - iteration) / iteration)
                eta = (sum(elapsed_time_history)/len(elapsed_time_history)) * (max_iterations - iteration)
            except ZeroDivisionError:
                eta = float("NaN")
            print(f"  total elapsed time: {format_time(total_elapsed_time)}; last pass: {format_time(pass_elapsed_time)}; ETA: {format_time(eta)}")
            sys.stdout.flush()
            self.global_stress_history.append(self.global_stress)
            
            high_stress_nodes = sum(n.stress > (1 << 10) for n in self.nodes) # Nodes that are outside the linear deviance range
            self.high_stress_node_history.append(high_stress_nodes)
            active_nodes_in_list = total_nodes_in_list # Reset this to make sure stresses are still below the threshold

            # Main optimization loop within an iteration: move nodes to decrease stress
            for node in self.nodes:

                # Remove low-stress nodes from consideration on this pass
                if node.stress <= (1 << 8): # TODO testing with lower value for this
                    active_nodes_in_list -= 1
                    continue
                    
                target_move = node.target_location - node.location # Optimal displacement for this node
                if target_move > 0:
                    target_direction = 1
                else:
                    target_direction = -1
                    target_move *= -1

                # Note that moving node n can only possibly impact the stresses of nodes n and n+1 (unless it swaps with another node)
                # The "threshold" parameter will allow decisions that increase stress with the objective of eventually reaching a better target
                if aggressive_pass: # Ignore the component of stress provided by the next element of the list - this makes optimization more local
                    best_stress = self.global_stress + threshold - node.next.stress
                else: # Look at the entire global stress - this penalizes decisions that reduce a node's stress at the cost of the next node
                    best_stress = self.global_stress + threshold

                best_move = 0

                # Try moves of n, n/2, n/4, ... - maybe a smaller move will be an improvement, even if the full-sized move isn't
                # TODO: There might be a better way to determine multiple moves.
                while target_move > 0:
                    test_location = node.location + (target_move * target_direction)
                    old_location = node.location
                    if test_location not in self.nodes_by_location:
                        node.move_to_location(test_location)
                    else:
                        node.swap_locations(self.nodes_by_location[test_location])

                    if aggressive_pass:
                        test_stress = self.global_stress - node.next.stress
                    else:
                        test_stress = self.global_stress

                    if test_stress < best_stress:
                        best_stress = test_stress
                        best_move = target_move

                    if old_location not in self.nodes_by_location:
                        node.move_to_location(old_location)
                        #break # You wouldn't expect breaking here to hurt accuracy, but it does - dramatically!
                    else:
                        node.swap_locations(self.nodes_by_location[old_location])

                    target_move >>= 1

                if best_move == 0:
                    continue
                best_location = node.location + (best_move * target_direction)
                if best_location not in self.nodes_by_location:
                    node.move_to_location(best_location)
                else:
                    node.swap_locations(self.nodes_by_location[best_location])
            
            threshold = int(threshold * threshold_decay)

            # Check stress histories for indicators of marginal progress
            comparison_history.insert(0, self.global_stress)
            del comparison_history[-1]
            for hist_idx in range(len(stress_histories)):
                stress_histories[hist_idx].insert(0, self.global_stress)
                del stress_histories[hist_idx][-1]
            avg_comparison_history = sum(comparison_history) / float(comparison_history_length)
            marginal = []
            for hist_idx in range(len(stress_histories)):
                avg_stress = sum(stress_histories[hist_idx]) / float(stress_history_lengths[hist_idx])
                stress_factor = avg_comparison_history / avg_stress
                min_factor = stress_marginality_thresholds[hist_idx]
                #max_factor = 1 / min_factor
                max_factor = float("inf") # Allowing increasing stress to count as non-marginal results in bad learning curves
                if np.isnan(stress_factor):
                    marginal.append(False)
                else:
                    marginal.append(min_factor < stress_factor < max_factor)
            if any(marginal):
                marginal_progress_count += 1
                progress_never_marginal = False
                if marginal_progress_count == marginal_iteration_cutoff:
                    print(f"Marginal improvement for {marginal_iteration_cutoff} sequential iterations; stopping early")
                    break
            else:
                marginal_progress_count = 0

            # Another early termination condition: a near-perfect solution!
            if self.global_stress == 0 or active_nodes_in_list == 0:
                print("Optimization has achieved a low-stress solution; stopping early")
                break
            
            pass_elapsed_time = time.monotonic() - pass_start_time
            elapsed_time_history.insert(0, pass_elapsed_time)
            if len(elapsed_time_history) > 8:
                del elapsed_time_history[-1]
        
        print(f"Optimization finished after {iteration+1} iterations with global_stress = {self.global_stress}")
        high_stress_nodes = sum(n.stress > (1 << 10) for n in self.nodes) # Nodes that are outside the linear deviance range
        print(f"High stress nodes: {high_stress_nodes} ({(100*float(high_stress_nodes)) / len(self)}%)")
        severe_stress_nodes = sum(n.stress > (1 << 14) for n in self.nodes) # Nodes that are WAY outside the linear deviance range - major sources of noise
        print(f"Severe stress nodes: {severe_stress_nodes} ({(100*float(severe_stress_nodes)) / len(self)}%)")
        node_locations = {l for l in self.nodes_by_location.keys()}
        sparsity = 100.0 - ((100.0 * len(self)) / (max(node_locations) + 1 - min(node_locations))) # What portion of locations are occupied?
        print(f"Sparsity: {sparsity}%")
        sys.stdout.flush()
        self.global_stress_history.append(self.global_stress)
        
        print("Performing post-optimization cleanup")

        # Quick check to make sure our bookkeeping was accurate
        for node in self.nodes:
            if node.location not in self.nodes_by_location or self.nodes_by_location[node.location] is not node:
                sys.exit(f"Node {node.id} is not mapped correctly in nodes_by_location")

        # Shift all nodes so that the first occupied location is at offset 0
        # This shouldn't have any impact on stress - but we'll check to make sure!
        min_location = min(node_locations)
        for node in self.nodes:
            node.location -= min_location
        for node in self.nodes:
            old_stress = node.stress
            node.update()
            if node.stress != old_stress:
                sys.exit(f"Node {node.id} stress changed after list offset! (from {old_stress} to {node.stress})")
        self.nodes_by_location = {node.location: node for node in self.nodes}

        sys.stdout.flush()
        self.flatten()

        # Run audit() next for more in-depth bookkeeping checks

    """
    Returns the location of the first element of the linked list
    """
    def start_location(self) -> int:
        return self.nodes[0].location

    """
    Expands the linked list from its sparse, compressed format (using a dict to map node IDs to locations) to an actual list
    """
    def expand_list(self) -> List[int]:
        if self.expanded_list is not None:
            return self.expanded_list

        sorted_locations = sorted(l for l in self.nodes_by_location.keys())
        if sorted_locations[0] != 0:
            sys.exit("Minimum location of linked list is not 0")
        self.expanded_list = []
        for node_location in sorted_locations:
            zeros_to_pad = node_location - len(self.expanded_list)
            self.expanded_list += [0]*zeros_to_pad
            self.expanded_list.append(self.nodes_by_location[node_location].next.location)
        return self.expanded_list

    def __len__(self):
        return len(self.nodes)
    
    def __getitem__(self, key):
        return self.nodes[key]

    def __init__(self):
        self.global_stress = 0
        self.nodes_by_location = {}
        self.min_location = 0
        self.max_location = 0
        self.fallback_nodes = 0
        self.cluster_placement_delta = 0
        self.permanent_placement_delta = 0
        self.nodes = []
        self.nodes.append(LLNode(self, None)) # Each list has a special first node which always has zero stress
        self.expanded_list = None
        self.global_stress_history = []
        self.high_stress_node_history = []
        self.flattened = False

"""
Stride-trace data structure for handling a linked list
"""
class Trace:
    """
    Remove (cull) trace strides in order to satisfy store_ratio, min_array_access_ratio, and min_list_stride constraints
    Also generates histogram info and adjusts the trace footprint to match the original
    """
    def cull(self, fixed_cull_ratio: float=None):
        if self.culled and fixed_cull_ratio is None:
            warnings.warn("Performing a secondary culling using initial parameters! (i.e. NOT with fixed_cull_ratio!)")

        # Get the counts of all log strides in the trace
        pre_cull_counts = {}
        for stride in self.log_strides:
            if stride not in pre_cull_counts:
                pre_cull_counts.update({copy(stride): 1})
            else:
                pre_cull_counts[stride] += 1
        strides_present = sorted([k for k in pre_cull_counts.keys()])
        check_stride = copy(strides_present[0]) # Make sure all intermediate strides have entries (e.g. if -9 and -7 are present, but -8 is not, add -8 with a count of 0)
        while check_stride != strides_present[-1]:
            check_stride = check_stride.next_larger()
            if check_stride not in pre_cull_counts:
                pre_cull_counts.update({copy(check_stride): 0})
        if self.pre_cull_counts is None:
            self.pre_cull_counts = pre_cull_counts

        # Get the counts of absolute strides - e.g. -2 and 2 map to the same bin here
        abs_counts = {}
        for stride, count in pre_cull_counts.items():
            abs_stride = abs(stride)
            if abs_stride not in abs_counts:
                abs_counts.update({copy(abs_stride): count})
            else:
                abs_counts[abs_stride] += count
        abs_strides = sorted([k for k in abs_counts.keys()]) # smallest to largest magnitude of displacement

        # Get target numbers of array (i.e. not linked-list) load and store accesses
        if fixed_cull_ratio is None: 
            array_store_accesses = int((len(self.log_strides) * self.store_ratio) + 0.5)
            array_ratio_accesses = int((len(self.log_strides) * self.min_array_access_ratio) + 0.5)
            array_small_accesses = 0
            if self.min_list_stride is not None:
                for stride in abs_strides:
                    if stride.is_infinitesimal:
                        array_small_accesses += abs_counts[stride]
                    elif stride.magnitude < self.min_list_stride:
                        array_small_accesses += abs_counts[stride]
                    else:
                        break
            array_total_accesses = max(array_ratio_accesses, array_small_accesses, array_store_accesses)
            array_load_accesses = array_total_accesses - array_store_accesses
        else:
            array_store_accesses = 0
            array_total_accesses = array_load_accesses = int((len(self.log_strides) * fixed_cull_ratio) + 0.5)

        # Get target numbers of each absolute stride size to cull
        abs_stride_cull_targets = {}
        total_strides_to_cull = 0
        for stride in abs_strides:
            count = abs_counts[stride]
            remaining_strides_to_cull = array_total_accesses - total_strides_to_cull
            if remaining_strides_to_cull == 0:
                break
            if count <= remaining_strides_to_cull:
                abs_stride_cull_targets.update({stride: count})
                total_strides_to_cull += count
            else:
                abs_stride_cull_targets.update({stride: remaining_strides_to_cull})
                total_strides_to_cull += remaining_strides_to_cull

        # Perform culling - try to distribute culled strides as evenly as possible
        # TODO: May want to consider handling culling on positive and negative strides separately
        abs_culled_strides = {stride: 0 for stride, count in abs_stride_cull_targets.items()}
        if self.culled_strides is None:
            self.culled_strides = {}
        encountered_counts = {stride: 0 for stride, count in abs_stride_cull_targets.items()}
        post_cull_log_strides = []
        for stride_idx, stride in enumerate(self.log_strides):
            abs_stride = abs(stride)
            if abs_stride not in abs_stride_cull_targets:
                keep = True
            else:
                encountered_counts[abs_stride] += 1
                target_culled_count = int(((encountered_counts[abs_stride] * abs_stride_cull_targets[abs_stride]) / abs_counts[abs_stride]) + 0.5)
                if abs_culled_strides[abs_stride] < target_culled_count:
                    keep = False
                    abs_culled_strides[abs_stride] += 1
                    if stride.linear_value not in self.culled_strides:
                        self.culled_strides.update({stride.linear_value: 1})
                    else:
                        self.culled_strides[stride.linear_value] += 1
                else:
                    keep = True

            if keep:
                if not stride.is_infinitesimal:
                    min_stride = max((2 ** stride.magnitude), int(abs(stride.linear_value) / 1.2))
                    max_stride = min(((2 ** (stride.magnitude+1)) - 1), int(abs(stride.linear_value) * 1.2))
                    if stride.is_negative:
                        old_max_stride = max_stride
                        max_stride = -min_stride
                        min_stride = -old_max_stride
                    target_stride = stride.linear_value - int(self.stride_delta)
                    new_stride = min(max(min_stride, target_stride), max_stride)
                    old_stride_delta = self.stride_delta
                    self.stride_delta += new_stride - stride.linear_value
                    assert(abs(self.stride_delta) <= abs(old_stride_delta))
                    stride.linear_value = new_stride
                post_cull_log_strides.append(stride)
            else:
                self.stride_delta -= stride.linear_value
            self.stride_delta += stride.linear_fractional_err # Keep track of "fractional errors", which can add up to be significant
            stride.linear_fractional_err = 0 # Avoid double counting if culling multiple times

        for stride, count in abs_culled_strides.items(): # make sure the correct number of strides were removed
            assert count == abs_stride_cull_targets[stride]

        # Update log strides
        self.log_strides = post_cull_log_strides

        # Get the counts of all log strides again
        self.post_cull_counts = {}
        for stride in self.log_strides:
            if stride not in self.post_cull_counts:
                self.post_cull_counts.update({copy(stride): 1})
            else:
                self.post_cull_counts[stride] += 1
        strides_present = sorted([k for k in self.post_cull_counts.keys()])
        check_stride = copy(strides_present[0]) # Make sure all intermediate strides have entries (e.g. if -9 and -7 are present, but -8 is not, add -8 with a count of 0)
        while check_stride != strides_present[-1]:
            check_stride = check_stride.next_larger()
            if check_stride not in self.post_cull_counts:
                self.post_cull_counts.update({copy(check_stride): 0})

        # Done culling
        self.culled = True
        print(f"Final culling stride delta: {self.stride_delta}")

        # Relevant when multiprocessing
        return self

    """
    Generates a linked list using the log strides
    Should be performed after culling
    """
    def make_list(self, prune_bad_lists=True):
        if not self.culled:
            sys.exit("Linked list generation must occur after culling")
        if self.linked_list is not None:
            sys.exit("Linked list already exists!")

        accept_list = False
        while not accept_list:
            self.linked_list = LinkedList()
            for stride in self.log_strides:
                self.linked_list.add_node(stride)

            if not prune_bad_lists:
                accept_list = True
            else:
                ideal_min_offset = ideal_max_offset = current_offset = self.linked_list[0].location
                ideal_locations = [self.linked_list[0].location]
                for n in range(1,len(self.linked_list)):
                    current_offset += self.linked_list[n].target_offset
                    ideal_max_offset = max(ideal_max_offset, current_offset)
                    ideal_min_offset = min(ideal_min_offset, current_offset)
                    ideal_locations.append(ideal_locations[-1] + self.linked_list[n].target_offset)
                ideal_footprint = ideal_max_offset + 1 - ideal_min_offset

                achieved_footprint = self.linked_list.max_location + 1 - self.linked_list.min_location
                achieved_locations = [self.linked_list[n].location for n in range(len(self.linked_list))]

                footprint_ratio = achieved_footprint / ideal_footprint
                footprint_ratio_limit = 1.3

                correlation = pd.Series(achieved_locations).corr(pd.Series(ideal_locations))
                correlation_limit = 0.75

                if footprint_ratio > footprint_ratio_limit:
                    cull_ratio = max(0.1, (1 - 4*(1/footprint_ratio)))
                    print(f"Achieved footprint ratio of {footprint_ratio} exceeds limit of {footprint_ratio_limit}; pruning {cull_ratio*100}% of nodes")
                elif correlation < correlation_limit:
                    cull_ratio = 0.1
                    print(f"Achieved correlation of {correlation} is lower than limit of {correlation_limit}; pruning {cull_ratio*100}% of nodes")
                else:
                    accept_list = True
                if not accept_list:
                    self.cull(fixed_cull_ratio = cull_ratio)

        print(f"Fallback node placements: {self.linked_list.fallback_nodes} ({(100*self.linked_list.fallback_nodes)/len(self.linked_list)}%)")
        self.linked_list.flatten()
        # Relevant when multiprocessing
        return self

    """
    Wrapper for LinkedList optimize
    """
    def optimize(self, initial_threshold: int=1<<24, threshold_decay: float=0.98, max_iterations: int=500):
        if self.linked_list is None:
            sys.exit("Can't optimize a non-existent linked list!")
        self.linked_list.optimize(initial_threshold, threshold_decay, max_iterations)

        # Relevant when multiprocessing
        return self

    """
    Checks the output linked list for correctness
    Also sets up post_opt_counts
    """
    def audit(self):
        if self.linked_list is None:
            sys.exit("Can't audit a non-existent linked list!")
        
        self.linked_list.unflatten()

        occupied_locations = set()
        self.post_opt_counts = {}

        start_location = self.linked_list.start_location()
        expanded_list = self.linked_list.expand_list()
        trace_length = len(self.log_strides)
        node = self.linked_list.nodes_by_location[start_location]
        calculated_global_stress = node.stress
        for idx in range(trace_length):
            if expanded_list[node.location] != node.next.location:
                sys.exit(f"Node {idx} has incorect value in expanded list: expected {node.next.location}, actual {expanded_list[node.location]}")
            node = node.next
            if node.location == start_location:
                sys.exit(f"Reached start of linked list early! (after {idx+1} hops, expected {trace_length+1})")
            if node.location in occupied_locations:
                sys.exit("Reached same node multiple times, OR multiple nodes at same location")
            node_stress = node.stress
            node.update()
            if (node_stress != node.stress):
                sys.exit(f"Node {idx+1} stress changed on update (from {node_stress} to {node.stress})")
            calculated_global_stress += node.stress
            stride = LogStride((node.location - node.prev.location) * List_Entry_Size_B) # Get LogStride from actual memory stride
            if stride not in self.post_opt_counts:
                self.post_opt_counts.update({copy(stride): 1})
            else:
                self.post_opt_counts[stride] += 1
        if node.next.location != start_location:
            sys.exit("Didn't reach end of list in expected number of hops")
        if expanded_list[node.location] != node.next.location:
            sys.exit(f"Last node has incorect value in expanded list: expected {node.next.location}, actual {expanded_list[node.location]}")
        if calculated_global_stress != self.linked_list.global_stress:
            sys.exit(f"Global stress mismatch: expected {self.linked_list.global_stress}; got {calculated_global_stress}")
        strides_present = sorted([k for k in self.post_opt_counts.keys()])
        check_stride = copy(strides_present[0]) # Make sure all intermediate strides have entries (e.g. if -9 and -7 are present, but -8 is not, add -8 with a count of 0)
        while check_stride != strides_present[-1]:
            check_stride = check_stride.next_larger()
            if check_stride not in self.post_opt_counts:
                self.post_opt_counts.update({copy(check_stride): 0})
        
        self.linked_list.flatten()

        # Relevant when multiprocessing
        return self
        
    def __init__(self, strides: List[int], store_ratio: float=0.0, min_array_access_ratio: float=0.0, min_list_stride: int=None):
        self.log_strides = [LogStride(s) for s in strides]
        self.pre_cull_counts = None
        self.culled_strides = None
        self.stride_delta = 0
        self.store_ratio = store_ratio
        self.min_array_access_ratio = min_array_access_ratio
        self.min_list_stride = min_list_stride
        self.culled = False
        self.linked_list = None
        
"""
Top-level class for managing a collection of traces
"""
class TraceManager:
    """
    Registers a new trace with the manager
    """
    def add_trace(self, trace_name, base_page: int, strides: List[int], store_ratio: float=0.0, min_array_access_ratio: float=0.0, min_list_stride: int=None) -> None:
        if base_page in self.trace_pages:
            sys.exit(f"Already have trace {self.trace_pages[base_page]} with base page {base_page}!")
        self.traces.update({trace_name: Trace(strides, store_ratio, min_array_access_ratio, min_list_stride)})
        self.trace_pages.update({base_page: trace_name})
        self.orig_trace_lengths.update({trace_name: len(strides)})

    """
    "Cull" trace strides to remove store + array accesses
    """
    def cull_traces(self) -> None:
        if self.max_processes == 1 or len(self.traces) <= 1:
            for trace_name, trace in self.traces.items():
                print(f"Culling trace {trace_name}")
                trace.cull()
        else:
            print(f"Running culling in parallel")
            trace_names = [n for n in self.traces.keys()]
            traces = [t for t in self.traces.values()]
            trace_functions = [t.cull for t in traces]
            new_traces = parallelize_func_calls(trace_functions, None, trace_names, self.max_processes)
            for trace_name, trace in new_traces.items():
                self.traces[trace_name] = trace

    """
    Generate lists for each trace
    """
    def make_lists(self, prune_bad_lists: bool=True) -> None:
        if self.max_processes == 1 or len(self.traces) <= 1:
            for trace_name, trace in self.traces.items():
                print(f"Generating unoptimized linked list for trace {trace_name}")
                trace.make_list(prune_bad_lists=prune_bad_lists)
        else:
            print(f"Running make_lists in parallel")
            trace_names = [n for n in self.traces.keys()]
            traces = [t for t in self.traces.values()]
            trace_functions = [t.make_list for t in traces]
            trace_args = [{"prune_bad_lists": prune_bad_lists} for _ in self.traces.items()]
            new_traces = parallelize_func_calls(trace_functions, trace_args, trace_names, self.max_processes)
            for trace_name, trace in new_traces.items():
                self.traces[trace_name] = trace

    """
    Optimize each trace
    """
    def optimize_lists(self, max_iterations: int=500) -> None:
        if self.max_processes == 1 or len(self.traces) <= 1:
            for trace_name, trace in self.traces.items():
                print(f"Optimizing linked list for trace {trace_name}")
                trace.optimize(max_iterations=max_iterations)
        else:
            print(f"Running optimization in parallel")
            trace_names = [n for n in self.traces.keys()]
            traces = [t for t in self.traces.values()]
            trace_functions = [t.optimize for t in traces]
            trace_args = [{"max_iterations": max_iterations} for _ in self.traces.items()]
            new_traces = parallelize_func_calls(trace_functions, trace_args, trace_names, self.max_processes)
            for trace_name, trace in new_traces.items():
                self.traces[trace_name] = trace
    
    """
    Audit lists from each trace for correctness
    """
    def audit_lists(self) -> None:
        if self.max_processes == 1 or len(self.traces) <= 1:
            for trace_name, trace in self.traces.items():
                print(f"Auditing list for trace {trace_name}")
                trace.audit()
        else:
            print(f"Running auditing in parallel")
            trace_names = [n for n in self.traces.keys()]
            traces = [t for t in self.traces.values()]
            trace_functions = [t.audit for t in traces]
            new_traces = parallelize_func_calls(trace_functions, None, trace_names, self.max_processes)
            for trace_name, trace in new_traces.items():
                self.traces[trace_name] = trace

    """
    Generates the header file containing info on these lists
    """
    def make_header(self, fname: str = None) -> str:
        out_str = ""
        if fname is not None:
            include_guard_name = f"_{os.path.splitext(os.path.basename(fname))[0].upper()}_H_"
            out_str += f"#ifndef {include_guard_name}\n"
            out_str += f"#define {include_guard_name}\n\n"

        out_str += dedent("""\
            #include <stdint.h>

            // Preprocessor black magic which duplicates the last given parameter 1-99,999,999,999 times
            // Each digit of the # of times to duplicate needs to be passed separately, including leading 0s
            #define REP0(...)
            #define REP1(...) __VA_ARGS__
            #define REP2(...) REP1(__VA_ARGS__) __VA_ARGS__
            #define REP3(...) REP2(__VA_ARGS__) __VA_ARGS__
            #define REP4(...) REP3(__VA_ARGS__) __VA_ARGS__
            #define REP5(...) REP4(__VA_ARGS__) __VA_ARGS__
            #define REP6(...) REP5(__VA_ARGS__) __VA_ARGS__
            #define REP7(...) REP6(__VA_ARGS__) __VA_ARGS__
            #define REP8(...) REP7(__VA_ARGS__) __VA_ARGS__
            #define REP9(...) REP8(__VA_ARGS__) __VA_ARGS__
            #define REP10(...) REP9(__VA_ARGS__) __VA_ARGS__
            #define REPEAT(TB,B,HM,TM,M,HT,TT,T,H,t,O,...) \\
                REP##TB (REP10(REP10(REP10(REP10(REP10(REP10(REP10(REP10(REP10(REP10(__VA_ARGS__))))))))))) \\
                REP##B  (REP10(REP10(REP10(REP10(REP10(REP10(REP10(REP10(REP10(__VA_ARGS__)))))))))) \\
                REP##HM (REP10(REP10(REP10(REP10(REP10(REP10(REP10(REP10(__VA_ARGS__))))))))) \\
                REP##TM (REP10(REP10(REP10(REP10(REP10(REP10(REP10(__VA_ARGS__)))))))) \\
                REP##M  (REP10(REP10(REP10(REP10(REP10(REP10(__VA_ARGS__))))))) \\
                REP##HT (REP10(REP10(REP10(REP10(REP10(__VA_ARGS__)))))) \\
                REP##TT (REP10(REP10(REP10(REP10(__VA_ARGS__))))) \\
                REP##T  (REP10(REP10(REP10(__VA_ARGS__)))) \\
                REP##H  (REP10(REP10(__VA_ARGS__))) \\
                REP##t  (REP10(__VA_ARGS__)) \\
                REP##O  (__VA_ARGS__)\n\n""")

        # Get largest positive and negative array strides from all traces
        min_culled_stride = 0
        max_culled_stride = 0
        for trace_name, trace in self.traces.items():
            culled_stride_sizes = {s for s in trace.culled_strides.keys()}
            if len(culled_stride_sizes) == 0:
                continue
            if min(culled_stride_sizes) < min_culled_stride:
                min_culled_stride = min(culled_stride_sizes)
            if max(culled_stride_sizes) > max_culled_stride:
                max_culled_stride = max(culled_stride_sizes)
        min_culled_stride = LogStride(min_culled_stride)
        max_culled_stride = LogStride(max_culled_stride)
        # Determine how many pages to prepend / append
        if min_culled_stride.is_infinitesimal:
            pages_to_prepend = 1
        else:
            pages_to_prepend = max(math.ceil(((2 ** (min_culled_stride.magnitude+1)) * List_Entry_Size_B) / Page_Size_B), 1)
        if max_culled_stride.is_infinitesimal:
            pages_to_append = 1
        else:
            pages_to_append = max(math.ceil(((2 ** (max_culled_stride.magnitude+1)) * List_Entry_Size_B) / Page_Size_B), 1)

        # Get target pages for traces
        # traces are an OrderedDict, so can guarantee element access ordering
        target_pages = {}
        min_page = min(self.trace_pages.keys())
        for trace_page, trace_name in self.trace_pages.items():
            target_pages.update({trace_page - min_page + pages_to_prepend: trace_name})

        out_str += "uint32_t Memory[] = {\n"
        entry_points = {}
        entries_in_page = Page_Size_B // List_Entry_Size_B
        # Iterate through traces from lowest to highest target page, adding lists
        sorted_target_page_numbers = sorted(p for p in target_pages.keys())
        pages_in_trace = 0
        for page_no in sorted_target_page_numbers:
            if page_no > pages_in_trace: # Add extra buffer pages as needed between/before traces
                pages_to_fill = page_no - pages_in_trace
                entries_to_fill = pages_to_fill * entries_in_page
                out_str += f"    {fill_entries_with_value(entries_to_fill, 0xBFF0BFF0, True)}\n"
                pages_in_trace += pages_to_fill

            trace_name = target_pages[page_no]
            region_base = pages_in_trace * entries_in_page # Should be added to all entries of trace
            entry_points.update({trace_name: self.traces[trace_name].linked_list.start_location() + region_base}) # Location of first node of trace

            trace_list = self.traces[trace_name].linked_list.expand_list() # Python linked list representation
            out_str += f"/* Linked list for trace {trace_name} */\n"
            out_str += "    "
            sequential_zero_entries = 0 # Keep track of sequential "zero" (region_base) entries so they can be compressed to a single REPEAT invocation
            entries_in_line = 0
            for entry in trace_list:
                if entry == 0:
                    sequential_zero_entries += 1
                else:
                    if sequential_zero_entries > 0:
                        out_str += f"{fill_entries_with_value(sequential_zero_entries, region_base)}"
                        entries_in_line += 1
                        if entries_in_line == 16:
                            out_str += "\n    "
                            entries_in_line = 0
                    sequential_zero_entries = 0
                    out_str += f"{entry + region_base},0x0,"
                    entries_in_line += 1
                    if entries_in_line == 16:
                        out_str += "\n    "
                        entries_in_line = 0
            if sequential_zero_entries > 0: # Catch tailing zero entries
                out_str += f"{fill_entries_with_value(sequential_zero_entries, region_base)}"
            trace_length = len(trace_list)
            if trace_length % entries_in_page != 0:
                entries_to_pad = entries_in_page - (trace_length % entries_in_page)
                out_str += f"\n    {fill_entries_with_value(entries_to_pad, 0xBFF0BFF0, True)}"
                trace_length += entries_to_pad
            assert(trace_length % entries_in_page == 0)
            pages_in_trace += trace_length // entries_in_page
            out_str += "\n"
        if pages_to_append > 0:
            entries_to_append = pages_to_append * entries_in_page
            out_str += f"    {fill_entries_with_value(entries_to_append, 0xBFF0BFF0, True)}\n"
        out_str += "};\n\n"

        # List start offsets for traces
        out_str += "uint32_t EntryPoints[] = {\n"
        for trace_name, trace in self.traces.items():
            out_str += f"    {str(entry_points[trace_name]) + ',':<11} /* {trace_name}; len={len(trace.linked_list)} */\n"
        out_str += "};\n\n"

        out_str += "uint32_t *ReadBase = &Memory[0];\n"
        out_str += "uint32_t *WriteBase = &Memory[1];\n\n"

        if fname is not None:
            out_str += "#endif\n"

        return out_str

    def make_json(self) -> str:
        trace_array_load_ratios = {}
        trace_array_store_ratios = {}
        trace_array_stride_ratios = {}
        for trace_name, trace in self.traces.items():
            trace_culled_strides = {}
            culled_stride_count = sum(c for c in trace.culled_strides.values())
            array_access_ratio = culled_stride_count / (culled_stride_count + len(trace.log_strides))
            trace_array_store_ratios.update({trace_name: min(trace.store_ratio, array_access_ratio)})
            trace_array_load_ratios.update({trace_name: max(array_access_ratio - trace.store_ratio, 0)})
            trace_array_stride_ratios.update({trace_name: {stride: count/culled_stride_count for stride, count in trace.culled_strides.items()}})

        sum_orig_trace_lengths = sum(self.orig_trace_lengths.values())
        trace_access_ratios = {name: length/sum_orig_trace_lengths for name, length in self.orig_trace_lengths.items()}

        out_str = "{\n"
        for trace_idx, (trace_name, trace) in enumerate(self.traces.items()):
            out_str += f"  \"{trace_name}\": {{\n"
            out_str += f"    \"access_ratio\": {trace_access_ratios[trace_name]},\n"
            out_str += f"    \"array_load_ratio\": {trace_array_load_ratios[trace_name]},\n"
            out_str += f"    \"array_store_ratio\": {trace_array_store_ratios[trace_name]},\n"
            out_str += "    \"array_stride_ratios\": {\n"
            array_strides = sorted(s for s in trace_array_stride_ratios[trace_name].keys())
            for stride_idx, array_stride in enumerate(array_strides):
                out_str += f"      \"{array_stride}\": {trace_array_stride_ratios[trace_name][array_stride]}"
                if stride_idx < len(array_strides)-1:
                    out_str += ","
                out_str += "\n"
            out_str += "    }\n"
            out_str += "  }"
            if trace_idx < len(self.traces)-1:
                out_str += ","
            out_str += "\n"
        out_str += "}\n"

        return out_str

    def visualize(self, out_dir: str) -> None:
        # Identify unique strides
        pre_cull_strides = set()
        post_cull_strides = set()
        final_list_strides = set()
        for trace in self.traces.values():
            trace_pre_cull_strides = {s for s in trace.pre_cull_counts.keys()}
            trace_post_cull_strides = {s for s in trace.post_cull_counts.keys()}
            trace_final_list_strides = {s for s in trace.post_opt_counts.keys()}
            pre_cull_strides = pre_cull_strides.union(trace_pre_cull_strides)
            post_cull_strides = post_cull_strides.union(trace_post_cull_strides)
            final_list_strides = final_list_strides.union(trace_final_list_strides)
        pre_cull_strides = sorted(list(pre_cull_strides))
        post_cull_strides = sorted(list(post_cull_strides))
        final_list_strides = sorted(list(final_list_strides))

        # Identify ratios of each stride in each trace
        pre_cull_ratios = []
        post_cull_ratios = []
        final_list_ratios = []
        for trace in self.traces.values():
            trace_pre_cull_ratios = []
            trace_post_cull_ratios = []
            trace_final_list_ratios = []
            for stride in pre_cull_strides:
                total_pre_cull_counts = sum(s for s in trace.pre_cull_counts.values())
                if stride not in trace.pre_cull_counts:
                    trace_pre_cull_ratios.append(0)
                else:
                    trace_pre_cull_ratios.append(trace.pre_cull_counts[stride]/total_pre_cull_counts)

            for stride in post_cull_strides:
                if stride not in trace.post_cull_counts:
                    trace_post_cull_ratios.append(0)
                else:
                    trace_post_cull_ratios.append(trace.post_cull_counts[stride]/len(trace.log_strides))

            for stride in final_list_strides:
                if stride not in trace.post_opt_counts:
                    trace_final_list_ratios.append(0)
                else:
                    trace_final_list_ratios.append(trace.post_opt_counts[stride]/len(trace.log_strides))

            pre_cull_ratios.append(trace_pre_cull_ratios.copy())
            post_cull_ratios.append(trace_post_cull_ratios.copy())
            final_list_ratios.append(trace_final_list_ratios.copy())

        pre_cull_ratios = np.array(pre_cull_ratios).transpose()
        post_cull_ratios = np.array(post_cull_ratios).transpose()
        final_list_ratios = np.array(final_list_ratios).transpose()
        trace_names = [t for t in self.traces.keys()]

        df_pre_cull = pd.DataFrame(pre_cull_ratios, index=pre_cull_strides, columns=trace_names)
        df_pre_cull.plot.bar(figsize=(20,10))
        plt.xlabel("Log Stride")
        plt.ylabel("Fraction of Strides")
        plt.title("Pre-Cull Input Stride Ratios")
        savepath = os.path.join(out_dir, "pre_cull_ratios.png")
        plt.savefig(savepath, bbox_inches = "tight")
        
        df_post_cull = pd.DataFrame(post_cull_ratios, index=post_cull_strides, columns=trace_names)
        df_post_cull.plot.bar(figsize=(20,10))
        plt.xlabel("Log Stride")
        plt.ylabel("Fraction of Strides")
        plt.title("Post-Cull Input Stride Ratios")
        savepath = os.path.join(out_dir, "post_cull_ratios.png")
        plt.savefig(savepath, bbox_inches = "tight")
       
        df_final_list = pd.DataFrame(final_list_ratios, index=final_list_strides, columns=trace_names)
        df_final_list.plot.bar(figsize=(20,10))
        plt.xlabel("Log Stride")
        plt.ylabel("Fraction of Strides")
        plt.title("Linked List Stride Ratios")
        savepath = os.path.join(out_dir, "final_list_ratios.png")
        plt.savefig(savepath, bbox_inches = "tight")
                
        # Plot train error
        longest_global_stress_history = max(len(t.linked_list.global_stress_history) for t in self.traces.values())
        global_stress_histories = []
        for trace in self.traces.values():
            history = trace.linked_list.global_stress_history.copy()
            for entry_idx in range(len(history)):
                history[entry_idx] /= len(trace.linked_list)
            history += [float("NaN")]*(longest_global_stress_history-len(history))
            global_stress_histories.append(history)
        global_stress_histories = np.array(global_stress_histories).transpose()
        df_global_stress = pd.DataFrame(global_stress_histories, index=[x for x in range(longest_global_stress_history)], columns=trace_names)
        df_global_stress.plot.line(figsize=(20,10), logy=True)
        plt.xticks(range(0, longest_global_stress_history, 10 ** int(math.log(longest_global_stress_history//2, 10))))
        plt.xlabel("Optimization Iteration")
        plt.ylabel("Average Stress per Node")
        plt.title("Stress Over Optimization")
        savepath = os.path.join(out_dir, "optimization_loss.png")
        plt.savefig(savepath, bbox_inches = "tight")

        # Plot high-stress node ratio history
        # This can fail if there are never any high-stress nodes (won't happen with real data); handling for this is a hack
        try:
            longest_node_stress_history = max(len(t.linked_list.high_stress_node_history) for t in self.traces.values())
            node_stress_histories = []
            for trace in self.traces.values():
                history = trace.linked_list.high_stress_node_history.copy()
                history += [float("NaN")]*(longest_node_stress_history-len(history))
                history = np.array(history) / len(trace.linked_list)
                node_stress_histories.append(history)
            node_stress_histories = np.array(node_stress_histories).transpose()
            df_node_stress = pd.DataFrame(node_stress_histories, index=[x for x in range(longest_node_stress_history)], columns=trace_names)
            df_node_stress.plot.line(figsize=(20,10))
            plt.xticks(range(0, longest_node_stress_history, 10 ** int(math.log(longest_node_stress_history//2, 10))))
            plt.xlabel("Optimization Iteration")
            plt.ylabel("Fraction of High Stress Nodes")
            plt.title("High Stress Nodes Over Optimization")
            savepath = os.path.join(out_dir, "optimization_high_stress.png")
            plt.savefig(savepath, bbox_inches = "tight")
        except:
            pass

        # Plot node locations over the list
        for trace_name, trace in self.traces.items():
            list_length = len(trace.linked_list)
            list_locations = [trace.linked_list[n].location for n in range(list_length)]
            ideal_locations = [trace.linked_list[0].location]
            for n in range(1,list_length):
                ideal_locations.append(ideal_locations[-1] + trace.linked_list[n].target_offset)
            corr = pd.Series(list_locations).corr(pd.Series(ideal_locations))

            node_locations = np.array([list_locations, ideal_locations]).transpose()
            df_node_location = pd.DataFrame(node_locations, index=[x for x in range(list_length)], columns=["Achieved Trace", "Target Trace"])
            df_node_location.plot.line(figsize=(20,10))
            high_stress_node_ids = [trace.linked_list[n].node_id for n in range(len(trace.linked_list)) if trace.linked_list[n].stress > (1 << 10)]
            high_stress_node_locs = [trace.linked_list[n].location for n in high_stress_node_ids]
            plt.scatter(high_stress_node_ids, high_stress_node_locs, marker='o', s=15, c='red')
            plt.xticks(range(0, list_length, 10 ** int(math.log(list_length//2, 10))))
            plt.xlabel("Node ID")
            plt.ylabel("Location")
            plt.title(f"Trace {trace_name} Linked List Visualization (r={corr:.4f})")
            savepath = os.path.join(out_dir, f"trace_{trace_name.lower()}.png")
            plt.savefig(savepath, bbox_inches = "tight")


    """
    Automatically runs all necessary steps
    """
    def autorun(self, max_iterations: int=500, strict_pruning: bool=False) -> None:
        self.cull_traces()
        self.make_lists(prune_bad_lists = not strict_pruning)
        self.optimize_lists(max_iterations=max_iterations)
        self.audit_lists()

    def __init__(self, max_processes: int=1):
        self.traces = collections.OrderedDict()
        self.trace_pages = {}
        self.orig_trace_lengths = {}
        if max_processes < 1:
            sys.exit("Attempted to create a TraceManager with zero or negative max_processes")
        elif max_processes > mp.cpu_count():
            warnings.warn("Creating a TraceManager with max_processes > physical CPUs; this is probably a bad idea")
        self.max_processes = max_processes

"""
Creates a TraceManager structure from JSONized data
Pass input as a string, not as a filename
"""
def create_traces_from_json(json_data: str, max_processes: int=1) -> TraceManager:
    config = json.loads(json_data)

    if "min_list_stride" in config:
        min_list_stride = config["min_list_stride"]
        if type(min_list_stride) is not int:
            warnings.warn("Type of min_list_stride should be int")
            min_list_stride = int(min_list_stride)
    else:
        min_list_stride = None

    if "min_array_access_ratio" in config:
        min_array_access_ratio = config["min_array_access_ratio"]
        if type(min_array_access_ratio) is not float:
            warnings.warn("Type of min_array_access_ratio should be float")
            min_array_access_ratio = float(min_list_stride)
    else:
        min_array_access_ratio = 0.0

    if "trace_data" not in config or len(config["trace_data"]) == 0:
        sys.exit("Input must contain at least one trace")

    tman = TraceManager(max_processes)

    for trace_idx, (trace_name, trace) in enumerate(config["trace_data"].items()):
        if "store_ratio" in trace:
            store_ratio = trace["store_ratio"]
            if type(store_ratio) is not float:
                warnings.warn("Type of store_ratio should be float")
                store_ratio = float(store_ratio)
        else:
            store_ratio = 0.0

        if "base_page" in trace:
            base_page = trace["base_page"]
            if type(base_page) is not int:
                warnings.warn("Type of base_page should be int")
                base_page = int(base_page)
        else:
            warnings.warn(f"Trace {trace_name} does not have a base_page specified")
            base_page = trace_idx
        tman.add_trace(trace_name, base_page, trace["strides"], store_ratio, min_array_access_ratio, min_list_stride)

    return tman

"""
Read command-line arguments
"""
def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", type=str, required=True, help="Input JSON with traces and configuration information")
    parser.add_argument("-e", "--header", type=str, default="out.h", help="Output header file containing linked list(s) and start offset(s)")
    parser.add_argument("-m", "--metadata", type=str, default="out.json", help="Output JSON with metadata on array and store accesses")
    parser.add_argument("-s", "--strict_pruning", action="store_true", help="By default, extra nodes are pruned as necessary to get a good list; specifying this flag disables that")
    parser.add_argument("-c", "--concurrent", type=int, action="store", nargs="?", default=1, const=mp.cpu_count()-1, \
        help="!!!EXPERIMENTAL!!! Optimize multiple regions in parallel; defaults to 1 if not provided or (# physical CPUs)-1 if provided without an argument"
    )
    parser.add_argument("-d", "--outputdir", type=str, help="If specified, store all output files under this directory")
    parser.add_argument("-v", "--visualizations", type=str, nargs="?", default=None, const=True, help="If provided, store visualizations to specified directory, or to outputdir if no directory specified")
    parser.add_argument("-t", "--maxiterations", type=int, default=500, help="Maximum iterations for optimization")
    args = parser.parse_args()

    # I had a problem, so I parallelized it
    # Now five have problems I
    # (Python gets cranky and throws weird warnings, but this SEEMS to work)
    if args.concurrent != 1:
        warnings.warn("Multiprocessing support is EXPERIMENTAL, use at your own risk")

    return args

"""
Top-level function for command-line invocation
"""
def main():
    args = parse_args()
    if args.outputdir:
        header_fname = os.path.join(args.outputdir, args.header)
        metadata_fname = os.path.join(args.outputdir, args.metadata)
        os.makedirs(args.outputdir, exist_ok=True)
    else:
        header_fname = args.header
        metadata_fname = args.metadata

    if args.visualizations is True:
        visualization_dirname = args.outputdir
    else:
        visualization_dirname = args.visualizations

    with open(args.input, "r") as in_f:
        tman = create_traces_from_json(in_f.read(), args.concurrent)
    tman.autorun(max_iterations = args.maxiterations, strict_pruning = args.strict_pruning)
    with open(header_fname, "w") as header_f:
        header_f.write(tman.make_header(args.header))
    with open(metadata_fname, "w") as metadata_f:
        metadata_f.write(tman.make_json())

    if args.visualizations is not None:
        os.makedirs(visualization_dirname, exist_ok=True)
        tman.visualize(visualization_dirname)

if __name__ == "__main__":
    main()

