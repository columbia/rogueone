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
  python -m pytest tests/test_dual_trust_domains.py
  ```
  
As part of the container creation process, all the files in the host dir are copied under `/RO`
  
The expected result's final line should look like this:
 ```
 ================== 17 passed, 24 warnings in 7.56s =================
  ```
  or 
   ```
 ================== 17 passed in 6.56s =================
  ```

# Single Update Analysis

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

This version of RogueOne comes with one benign update and one rogue update sample, stored in `/RO/Data`.

We will first experiment with scanning the benign one stored at "Data/file-loader_6.1.1--\>6.2.0/", by running:
```bash
 python rogue_one_runner.py --no_redo --log_level WARNING --single /RO/Data/file-loader_6.1.1--\>6.2.0/ 
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
```
"error": "OK",
"suspicious": false,
"new_rels": [],
"before_rels": {
    "(':caller', ':local:loader')": [
        [
            "2315",
            "2315"
        ],
        [
            "2315",
            "2319"
        ]
    ],
    <...clipped...>
}
"after_rels": {
    "(':caller', ':local:loader')": [
        [
            "2593",
            "2597"
        ],
        [
            "2593",
            "2593"
        ]
    ],
    "(':caller', ':local:1')": [
        [
}
```

The field `"error": "OK"` means that the analysis for the package pair terminated successfully. The field `new_rels` is a list of new "rels" (shorthand for relationships), which are new trust-domains. As this list is empty, the field `suspicious` was set to false. The specific trust domains in the version before and after are detailed in `before_rels` and `after_rels` respectively.

To view the full JSON file you can use the following command:
```bash
cat /RO/Data/file-loader_6.1.1--\>6.2.0/rogue_one_output.json | python -m json.tool
```


To analyze the rogue update, run the following command:
```bash
python rogue_one_runner.py --single /host/Data/conventional-changelog_1.1.12--\>1.2.0/ --no_redo --log_level WARNING
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
