# groklog

GrokLog is a tool for creating "process trees", that is, a root process (an ordinary shell)
has its output piped into the stdin of other processes. Those other processes can in 
turn have _their_ stdout piped into even more processes. Then, groklog lets you view the 
stdout of every process in the tree. 
 
The benefit of all of this is that you can filter logs or other streams using the 
various unix tools you are already familiar with, and do so in a much more sophisticated 
way. 

On top of that, building profiles is quick and easy, so after spending some time 
configuring, everything is saved to a profile and the next time you run groklog you can 
jump right in where you left off!

## Installation
```shell
poetry install
poetry run pre-commit install
```

## Usage
```shell
groklog
```

GrokLog saves configuration using a concept of profiles. A profile stores all the 
configuration for a process tree. By default GrokLog loads/creates the `default` profile. 
You can load/create a different profile by running:

```shell
groklog profilename
```

## Running tests
```
pytest .
```

## Attributions
1) This code makes heavy use of the fantastic `asciimatics` library for all TUI 
rendering purposes. Some reference code as copied from the 
[terminal.py](https://github.com/peterbrittain/asciimatics/blob/master/samples/terminal.py) 
sample. 

2) Some code was sampled from the OpenVisionCapsules project, specifically for 
   verifying if all threads have been shut down after a unit test. 
[Source file](https://github.com/opencv/open_vision_capsules/blob/master/vcap/vcap/testing/thread_validation.py).
