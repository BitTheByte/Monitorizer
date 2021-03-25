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
>> concurrent - set/get number of concurrent working tools  (recommended=2)
>> acunetix - enable/disable sending new discoverd targets to acunetix (default=disabled)
>> freq - set/get scan frequency in hours (default=24)
"""

update_msg_toolkit = """[:small_red_triangle:] New version of the toolkit is released (this is optional)
```
{}
```
"""
update_msg_codebase = """[:small_red_triangle:] New version of Moniterizer is released (updates are required to maintain stability)
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
