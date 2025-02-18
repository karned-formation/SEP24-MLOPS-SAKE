# Project folder structure
```
┌──────────────────────────────────────────────────────────────────────────────────────
│ TESTS of the source folders "src" and "docker"
├── tests
│   ├── functional      Tests at a functional level checking one Docker
│   │   └── docker
│   │       ├── etl
│   │       ├── ocr
│   │       ├── orchestrator
│   │       └── predict
│   ├── integration     Integration Tests of Dockers
│   ├── requests        End to End test of high level interface
│   └── unit            Unitary test of functions in "src" folder
└──────────────────────────────────────────────────────────────────────────────────────