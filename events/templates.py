help_msg = """*Welcome to Moniterzer help page* :robot_face:
{warning0}
{warning1}
[:small_blue_diamond:]  Available commands:-
>> help - prints this message
>> list - list all monitored targets
>> add - add new target(s)
>> remove - remove target(s) from monitoring list
>> ping - check health
>> status - returns application status
>> concurrent - set/get number of concurrent working tools  (recommended= 2)
>> freq - set/get scan frequency (in hours)
"""

update_msg = """[:small_red_triangle:] Updates are required
```
{}
```
"""

run_status_msg = """
[:small_blue_diamond:] Application status:-
Status: {tool} is {status} against the target
Target: {target}
Report: {report_name}
"""
stop_status_msg = """
[:small_blue_diamond:] Application status:-
Status: IDLE
"""

target = "[:round_pushpin:]> {}"
