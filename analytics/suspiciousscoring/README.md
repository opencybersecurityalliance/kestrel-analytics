# Suspicious Process Scoring

## Goal

Implement a rule-based analytics to score process regarding how suspicious they
are.

## Application Scenario

When a user get hundreds of processes in a Kestrel variable, she may want to
prioritize the investigation and start from the ones that are most suspicious.
The user needs an analytics to provide suspicious scores so she can rank them
in Kestrel.

## Basic Idea (Open to Discussion And Upgrade)

A process is more suspicious if it has more activities, or more types of
activities, such as

- writing to system directory
- network connection
- fork other processes
- known suspicious commands such as https://github.com/Neo23x0/sigma/blob/32ecb816307e3639cf815851fac8341a60631f45/rules/linux/lnx_shell_susp_commands.yml

The analytics can count such significant activities (and how many types) to
reason how suspicious a process is. The final score can be normalize into [0,1]
and provided as an additional/customized attribute/column in the output Parquet
table.

## Usage

Build it:
```
docker build -t kestrel-analytics-susp_scoring .
```

Then use it in Kestrel:
```
procs = GET process FROM file://samplestix.json where [process:parent_ref.name = "cmd.exe"]
APPLY docker://susp_scoring ON procs
```

