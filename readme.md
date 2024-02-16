RogueOne is a static analysis tool which compares two versions of a JavaScript package and determines whether 
that package has suspicious changes.

RogueOne is implemented in a combination of Python and Javascript, and prerequisites must be installed 
in both languages.  

# Installation

## Docker

The easiest way to set up RogueOne is using our dockerfile.
Run these commands from the directory where this README file is located
 ```bash
  sudo docker build -t ro . 
  sudo docker run -it ro /bin/bash
  ```

It is not required, but very helpful to map this directory into the container. To do so use this command instead:
```bash
sudo docker run -v $PWD:/host -it ro /bin/bash
```

FYI - The docker container building step might take a few minutes (~7).
  
Inside the docker container, run tests to make sure the installation went well:
 ```bash
  cd /RO
  python -m pytest tests
  ```
  
As part of the container creation process, all the files in the host dir are copied under `/RO`
  
The expected result's final line should look like this:
 ```
================= 104 passed, 3 skipped in 95.92s (0:01:35) =====================
  ```

# Trust Domain Single Update Analysis

RogueOne's main interface is the update-focused trust domain interface mainly intended for batch analysis and malware detection.

## Update Directory Structure 
A single update consists of a package pair (before and after) stored on the file system.
A package pair dir structure must have the following format:
```commandline
pack-name_0.0.1-->0.0.2/
├── pack-name_0.0.1
│   ├── package.json
│   ├── ... other files ...
└── pack-name_0.0.2
    ├── package.json
    └── ... other files ...
```

## Scanning Single Updates using RogueOne

This version of RogueOne comes with a variety of test samples stored in `/RO/tests/dataflow_fixtures`.

We will first experiment with scanning the benign one stored at "dual_version/file-loader_6.1.1--\>6.2.0/", by running:
```bash
 python rogue_one_runner.py --no_redo --log_level WARNING --single /RO/tests/dataflow_fixtures/dual_version/file-loader_6.1.1--\>6.2.0/ 
```
Note that you must use **absolute paths** as inputs to RogueOne.

The output should resemble the following:
```
Starting analysis on pair_dir: /RO/Data/file-loader_6.1.1-->6.2.0/ 

Logging to package dir (/RO/Data/file-loader_6.1.1-->6.2.0/file-loader-6.1.1) 

2397 {}
{"Statements:": " 41 43", "Functions:": " 2 3", "Time spent: ": " 0.460s", "res_pathes": [], "node_attrs": {}, "Success: ": "Detection: failed", "Exploit": "turned off", "running_time": 0.4797794818878174, "Vulnerable files": [], "Number of CF Paths": 0, "Number of Preceding CF Paths": 0, "Number of Full CF Paths": 0, "Number of CF Edges: ": 477, "Number of Real CF Edges: ": 46, "Number of Call Edges: ": 13, "Number of Real Call Edges: ": 1, "additional_files": ["dist/index.js", "dist/utils.js"], "Number of Dynamically Resolvable Calls: ": 19, "Number of Statically Resolvable Calls: ": 2, "Number of Unresolvable Calls: ": 0, "Number of Function Calls: ": 21, "Number of Rerun: ": 0}
Package analysis finished successfully (/RO/Data/file-loader_6.1.1-->6.2.0/file-loader-6.1.1) 

Logging to package dir (/RO/Data/file-loader_6.1.1-->6.2.0/file-loader-6.2.0) 

2675 {}
{"Statements:": " 70 71", "Functions:": " 3 4", "Time spent: ": " 0.432s", "res_pathes": [], "node_attrs": {}, "Success: ": "Detection: failed", "Exploit": "turned off", "running_time": 0.4610416889190674, "Vulnerable files": [], "Number of CF Paths": 0, "Number of Preceding CF Paths": 0, "Number of Full CF Paths": 0, "Number of CF Edges: ": 668, "Number of Real CF Edges: ": 83, "Number of Call Edges: ": 26, "Number of Real Call Edges: ": 2, "additional_files": ["dist/index.js", "dist/utils.js"], "Number of Dynamically Resolvable Calls: ": 30, "Number of Statically Resolvable Calls: ": 2, "Number of Unresolvable Calls: ": 0, "Number of Function Calls: ": 32, "Number of Rerun: ": 0}
Package analysis finished successfully (/RO/Data/file-loader_6.1.1-->6.2.0/file-loader-6.2.0) 
```

The results summary JSON file will be created in the root of the package pair directory. 
For the `file-loader` example, the JSON result should contain the following fields:

``cat /RO/tests/dataflow_fixtures/dual_version/file-loader_6.1.1--\>6.2.0/rogue_one_output.json | jq 'del(.system_extra_info)'``
```
{
  "package_name": "file-loader",
  "label": "BEN",
  "group": "dual_version",
  "system": "rogue_one",
  "run_timestamp": "2024-02-16 18:15:15.880204",
  "sinks_added": 0,
  "sinks_removed": 0,
  "sinks_changed": 0,
  "fast_mode": false,
  "esprima_info": {},
  "before": {
    "version": "6.1.1",
    "folder": "/RO/tests/dataflow_fixtures/dual_version/file-loader_6.1.1-->6.2.0/file-loader-6.1.1",
    "running_time": 3.587908,
    "weakly_connected_components": 1,
    "error": "OK",
    "file_node_nums": {
      "dist/index.js": 454
    },
    "odg_time": "0:00:03.341625",
    "idg_time": "0:00:00.244198",
    "graph_size": {
      "odg": {
        "nodes": 4571,
        "edges": 8406
      },
      "idg": {
        "nodes": 1961,
        "edges": 3552
      }
    }
  },
  "after": {
    "version": "6.2.0",
    "folder": "/RO/tests/dataflow_fixtures/dual_version/file-loader_6.1.1-->6.2.0/file-loader-6.2.0",
    "running_time": 4.697887,
    "weakly_connected_components": 1,
    "error": "OK",
    "file_node_nums": {
      "dist/utils.js": 175,
      "dist/index.js": 551
    },
    "odg_time": "0:00:04.167507",
    "idg_time": "0:00:00.529721",
    "graph_size": {
      "odg": {
        "nodes": 7725,
        "edges": 15126
      },
      "idg": {
        "nodes": 2962,
        "edges": 5450
      }
    }
  },
  "error": "OK",
  "suspicious": false
}
```

The field `"error": "OK"` means that the analysis for the package pair terminated successfully. The field `new_rels` is a list of new "rels" (shorthand for relationships), which are new trust-domains. As this list is empty, the field `suspicious` was set to false. The specific trust domains in the version before and after are detailed in `before_rels` and `after_rels` respectively.

To view the full JSON file you can use the following command:
```bash
cat /RO/tests/dataflow_fixtures/dual_version/file-loader_6.1.1--\>6.2.0/rogue_one_output.json | python -m json.tool
```


To analyze the rogue update, run the following command:
```bash
python rogue_one_runner.py --single /RO/tests/dataflow_fixtures/dual_version/file-loader_6.1.1--\>6.r.1/ --no_redo --log_level WARNING
```

In this case, looking in the JSON file summarizing the results of this analysis should contain the following fields:
```
"suspicious": true,
"new_rels": [
    [
        ":local",
        "conventional-changelog-preset-loader"
    ],
    [
        ":local",
        "conventional-changelog-core"
    ],
    [
        ":local",
        "child_process"
    ]
]
```

Showing that this update is rogue.

## Mass Analysis

To analyze the entire dataset in /RO/Samples, run `python rogue_one_runner.py --sample_folder=/RO/Samples/`.
This process will be slow (12 hours with 8 cores and 32GB memory) but can be stopped and resumed without losing all data.
It will place tabular data in `rogue_one_mass_analysis.csv`, and complete JSON data in `rogue_one_output.json` in
each sample folder.

# Caveats
For practical reasons, RogueOne is an unsound analysis which does not always terminate.
We describe some major caveats to the use of RogueOne below.

## Asynchronous Operation Reordering
JavaScript's built-in asynchronous features make some code unpredictable.
By creating a set of callbacks which are unpredictably interleaved and modify the data
and code used in the other callbacks, the programmer can create a large number of implicit branches.
RogueOne's underlying abstract interpretation engine, ODGen, only explores the branch corresponding to immediate
execution of a callback once the current entry point (exported function) is complete.  Increasing the sophistication
of this system to take into account when asynchronous blocks refer to the same objects and consider reordering them as needed is left for future work.
A simple example of this may be seen in the sample at `tests/dataflow_fixtures/dual_version/design_ex`.

## Loop Abort Heuristic
RogueOne analyzes many non-terminating packages.  The analysis engine measures statement coverage
during consecutive loop or recursive evaluations to attempt to abort loop evaluation once no new
code is being checked. This can result in code not being evaluated (being incorrectly ignored as dead),
if the abort heuristic is triggered before the problematic code is reached.

## Third Party Object Modification
RogueOne's abstract interpretation engine does not currently establish dataflow edges from a function
to mutable arguments to that function.  This can result in a break in a dataflow which occurs through
mutation of a local object.  An example of this can be seen in `tests/dataflow_fixtures/single_version/third_party_injection`

## Timeouts
RogueOne is susceptible to timeouts.  In particular, loops with heavily branching loop bodies that require
the abstract interpretation engine to explore an exponentially expanding tree of branches can stop the analysis from completing.
An example of this can be seen in the package `jade`, included at `tests/dataflow_fixtures/dual_version/jade`.
A two-pass method for avoiding these situations can be seen in https://ieeexplore.ieee.org/document/10179352,
but enabling these mitigations is experimental in RogueOne (`use_two_pass` branch).

# Capability-Based analysis
An interface modeled on the CapsLock JSON format is available in the `caps.py` file in the root directory.  This interface is not part of the work described in the RogueOne ICSE 2024 paper, but is a separate effort.
The goal of this interface is to have a machine-readable, fairly human-readable, and diffable summary of the 
cross-domain data-flows in a JavaScript package.

## Single Version Capability analysis

RogueOne can be used to generate the capability summary for a Node package as follows:
```commandline
python ./caps.py --single tests/dataflow_fixtures/dual_version/jas_authsync/v1
```
Add the `--with-deps` option, and RogueOne will also analyze packages present in the `node_modules`
folder of the target and include the result of that analysis.

```commandline
python ./caps.py --with-deps --single tests/dataflow_fixtures/with_dependencies/mkdirp
```

## Update Capability analysis

RogueOne can also be used to generate and compare the capabilities for two versions of a package.
```commandline
python ./caps.py --before tests/dataflow_fixtures/dual_version/jas_authsync/v1 --after tests/dataflow_fixtures/dual_version/jas_authsync/v2
```
Since a package generally contains many data flows, this is useful for quickly viewing what has changed between two versions. This comparison does not support the `--with-deps` option.
