# Usage
 
`python3 stress_test.py [CPU Percentage] [Execution time] [Memory in MB]`

## Default

`python3 stress_test.py`

*Default CPU:* 100%

*Default Time:* 60 sec

*Default Memory:* Total PC memory

## Example

`python stress_test.py 50 10 7000`

Stresses CPU at 50% for 10 sec. Then stresses memory at 7 GB for 10 sec.

`python stress_test.py 60`

Stresses CPU at 60% for 60 sec. Then consumes all memory for 10 sec.
