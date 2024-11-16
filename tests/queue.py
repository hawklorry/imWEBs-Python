import heapq
from dataclasses import dataclass, field

@dataclass(order=True)
class Task:
    row: int = field(compare=False)
    col: int = field(compare=False)
    streamVal: bool 
    z: float
    flatIndex: int

# Create a list to use as a heap
heap = []

# Add tasks to the heap
heapq.heappush(heap, Task(row=1, col=4, z=400,flatIndex=4, streamVal=True))
heapq.heappush(heap, Task(row=2, col=3,z=200,flatIndex=1, streamVal=False))
heapq.heappush(heap, Task(row=3, col=2,z=200,flatIndex=2, streamVal=False))
heapq.heappush(heap, Task(row=4, col=1,z=100,flatIndex=2, streamVal=False))

# Pop tasks from the heap
while heap:
    task = heapq.heappop(heap)
    print(f"Row: {task.row}, Col: {task.col}, streamVal: {task.streamVal}, z: {task.z}, flatIndex: {task.flatIndex}")