# LearnVault AI --- Problem & Solution Log

This file records real problems encountered while building LearnVault
AI, how they were diagnosed, the solution applied, and what was learned.

**Rule:** Record the actual error and fix. Do not add guessed problems
or claim a fix worked until it has been tested.

## How to use this log

Whenever something goes wrong:

1.  Copy the exact error message or describe the unexpected behavior.
2.  Record the command, code, or action that triggered it.
3.  Note the likely cause after investigating.
4.  Record the fix you applied.
5.  Test the fix and write down the result.
6.  Add a short lesson so the same issue is easier to solve next time.

Keep secrets out of this file. Never paste API keys, passwords, access
tokens, or private environment-variable values.

## Problem log

Use one entry per issue. Add new entries at the top so the latest issue
is easiest to find.

### Issue template

-   **ID:** LV-XXX
-   **Date:**
-   **Project stage:**
-   **Area:** (setup / YouTube / transcripts / chunking / embeddings /
    Qdrant / RAG / API / frontend / deployment)
-   **Problem / expected behavior:**
-   **Actual behavior:**
-   **Exact error or relevant log:**
-   **Steps to reproduce:**
-   **Investigation / root cause:**
-   **Solution applied:**
-   **Verification:** (How was the fix tested? What was the result?)
-   **Lesson learned:**
-   **Related files / commit:**

------------------------------------------------------------------------

## Project setup record

### Setup status --- Step 1

-   **Date:** 2026-11-06
-   **Area:** Project setup / Git
-   **Status:** Completed
-   **What was done:**
    -   Created the local `LearnVault-AI` project structure.
    -   Initialized the local Git repository.
    -   Created a `.gitignore` to exclude items such as the Python
        virtual environment and environment files.
    -   Created a GitHub repository and connected the local project.
    -   Set up the initial FastAPI application and its health/root
        endpoints as part of Step 1.
-   **Problems encountered:** No specific technical error has been
    reported in the project conversation so far.
-   **Solution:** Not applicable; do not invent an issue where none was
    reported.
-   **Verification to keep:** Confirm that the GitHub repository
    contains the intended source files, does not contain `.venv` or
    `.env`, and that the FastAPI `/`, `/health`, and `/docs` endpoints
    work.
-   **Lesson learned:** Git tracks the project locally; GitHub hosts the
    remote repository. A local `git init` does not by itself create or
    connect a GitHub repository.

------------------------------------------------------------------------

## Useful commands

Check working-tree status:

``` bash
git status
```

See recent commits:

``` bash
git log --oneline -5
```

See configured remotes:

``` bash
git remote -v
```

After fixing an issue, commit the change with a message that describes
the fix:

``` bash
git add .
git commit -m "fix: describe the issue that was resolved"
```

## Change history

  -----------------------------------------------------------------------
  Date                                Update
  ----------------------------------- -----------------------------------
  2026-11-06                          Created the project problem and
                                      solution log; recorded Step 1 setup
                                      status.

  -----------------------------------------------------------------------
