# Root project license decision

`ROOT_LICENSE_SELECTED=false`

`PUBLIC_DISTRIBUTION_AUTHORIZED=false`

The repository does not contain a human-selected root `LICENSE`. This document
records options only and is not legal advice. No root license, tag, or GitHub
Release may be created by the agent.

## Options for human review

| option | practical implication | unresolved review |
|---|---|---|
| MIT | short permissive code license | patent language and notice policy |
| BSD-3-Clause | permissive code license with non-endorsement clause | notice policy and compatibility review |
| Apache-2.0 | permissive code license with explicit patent terms | NOTICE workflow and compatibility review |
| keep private / all rights reserved | no public OSS grant | collaborator and demo-distribution permissions |

The code license does not replace dataset terms. OSM-derived databases,
official open data, PLATEAU assets, papers, screenshots, and third-party binary
components require separate review and attribution.

## Required owner decision

1. select the root code license and copyright holder wording;
2. approve `NOTICE`/attribution placement;
3. approve dataset-by-dataset redistribution and database-rights handling;
4. approve whether an internal RC may become a public source archive;
5. approve the public version/tag independently from the fixed baseline tag.
