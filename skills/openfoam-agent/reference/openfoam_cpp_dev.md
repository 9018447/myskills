# OpenFOAM C++ development / build / debug

## Goal

Enable an AI assistant (with limited context) to:

- understand OpenFOAM source layout and the `wmake` build system
- add/modify an OpenFOAM `application` or `solver`
- localize compile errors and runtime errors quickly

This repository targets **ESI/OpenCFD OpenFOAM v2412**.

## Pre-flight checklist

- OpenFOAM environment is sourced correctly (user can provide `WM_PROJECT_DIR`, `FOAM_APPBIN`)
- target version is confirmed (v2412)
- development is done in a user area when possible (typically `$WM_PROJECT_USER_DIR`)

## Common directory conventions

- `applications/solvers/<solverName>/`
- `applications/utilities/<utilName>/`
- `src/<libraryName>/`

Each build target usually contains:

- `Make/files`
- `Make/options`

## Basic `wmake` usage

- build current directory: `wmake`
- clean: `wclean`
- build from a parent directory: depends on how that tree is organized

## `Make/files` (minimal example)

```text
myUtility.C

EXE = $(FOAM_USER_APPBIN)/myUtility
```

## `Make/options` (minimal example)

```text
EXE_INC = \
    -I$(LIB_SRC)/finiteVolume/lnInclude

EXE_LIBS = \
    -lfiniteVolume
```

## Compile error localization (the standard pattern)

- Always start with the **first** error (later errors are often cascading)
- Common categories:
  - missing include paths (add `-I.../lnInclude` in `Make/options`)
  - missing link libs (add `-l...` in `EXE_LIBS`)
  - namespace/type mismatches (OpenFOAM types are typically under `Foam::`)

## Runtime error localization

- `FOAM FATAL IO ERROR`: first inspect case dictionaries and patch naming
- `SIGFPE` / `floating point exception`:
  - validate mesh and input fields
  - then consider numerics/time step/schemes

## Debugging (gdb approach)

Common in Linux/WSL:

- build with debug symbols (distribution-dependent; often via `WM_COMPILE_OPTION=Debug` or an equivalent debug build)
- run under gdb and capture a backtrace

Minimum objective: given a backtrace, pinpoint the function/file/line and propose a minimal reproduction and fix.
