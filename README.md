# groklog

A tool for filtering logs quickly and easily

## Installation
```shell
poetry install
poetry run pre-commit install
```

## Running
```
groklog --help
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
   verifying if all threads have been shut down after a test. 
[Source file](https://github.com/opencv/open_vision_capsules/blob/master/vcap/vcap/testing/thread_validation.py).
