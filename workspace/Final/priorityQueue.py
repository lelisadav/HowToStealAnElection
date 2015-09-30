# -*- coding: utf-8 -*-
"""
Created on Tue Sep 29 10:03:08 2015

@author: ellie
"""

class PriorityHeap():
    REMOVED = '<removed-task>'
    def __init__(self, items, heuristic=None):
        self.queue = []                         # list of entries arranged in a heap
        self.entry_finder = {}               # mapping of tasks to entries
              # placeholder for a removed task
        self.counter = itertools.count()     # unique sequence count
        if (heuristic==None):
            self.heuristic=lambda item: 0
        else:
            self.heuristic= lambda item: heuristic(item)

    def add(task):
        'Add a new task or update the priority of an existing task'
        if task in self.entry_finder:
            remove_task(task)
        count = next(self.counter)
        priority=self.heuristic(task)
        entry = [priority, count, task]
        self.entry_finder[task] = entry
        heappush(self.queue, entry)

    def remove(task):
        'Mark an existing task as REMOVED.  Raise KeyError if not found.'
        entry = self.entry_finder.pop(task)
        entry[-1] = REMOVED

    def pop():
    'Remove and return the lowest priority task. Raise KeyError if empty.'
        while self.queue:
            priority, count, task = heappop(self.queue)
            if task is not REMOVED:
                del self.entry_finder[task]
                return task
        raise KeyError('pop from an empty priority queue')