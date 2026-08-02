# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project overview

`cmkr` ("cmaker") is a build system that generates a modern, idiomatic `CMakeLists.txt` from a `cmake.toml` file. It is a C++11 command-line tool. This repository is a **fork** of [build-cpp/cmkr](https://gitee.com/cmkr_lib/cmkr) (source moved to gitee); the bootstrapping script `cmake/cmkr.cmake` is configured to fetch from `https://gitee.com/cmkr_lib/cmkr`, and the git history has been squashed to a single commit.

Core workflow: edit `cmake.toml`, run `cmkr gen`, and a `CMakeLists.txt` is produced. The generated `CMakeLists.txt` is checked into source control and used directly by CMake — it is regenerated automatically when `cmake.toml` changes.

## Build

The project bootstraps itself via `cmake/cmkr.cmake` and its own generated `CMakeLists.txt`.

```sh
cmake -B build            # configure
cmake --build build       # build
```

Prerequisites: CMake and a C++11 compiler. Build dirs (`build*`, `cmake-build*`) are git-ignored; in-tree builds are forbidden by the generated `CMakeLists.txt`.

Useful CMake options (set by CI):
- `-DCMAKE_UNITY_BUILD=ON` — faster builds
- `-DCMKR_GENERATE_DOCUMENTATION=OFF` — skip regenerating docs examples from tests (ON by default for the root project)

## Regenerating CMakeLists.txt

The checked-in `CMakeLists.txt` is generated from `cmake.toml` — **never edit it by hand**. After changing `cmake.toml`:

```sh
cmake --build build --target regenerate-cmake
```

or run the built binary directly: `build/cmkr gen`. CI runs the built cmkr's `gen` and fails if `git diff` is non-empty, so keep `CMakeLists.txt` in sync with `cmake.toml` in every commit.

## Tests

Tests are CTest fixtures. Each `tests/<name>/` directory is a complete mini `cmake.toml` project; the test invokes the freshly-built `cmkr build` inside that directory, which must configure and compile successfully. The test list is defined in `tests/cmake.toml`.

```sh
ctest --test-dir build/tests --output-on-failure            # run all
ctest --test-dir build/tests -R basic --output-on-failure   # single test
```

Or via CMake target: `cmake --build build --target run-tests`.

Notes:
- `msvc-runtime` runs only under MSVC; `relative-paths` only under WIN32.
- Tests actually compile projects, so a full C++ toolchain is required.

## Code architecture

The binary is split into small modules under `include/` + `src/`:

- `src/main.cpp` — entry point; prints `cmkr::args::handle_args` result to stderr.
- `src/arguments.cpp` (`include/arguments.hpp`) — CLI dispatch for `init`, `gen`, `build`, `install`, `clean`, `help`, `version`.
- `src/project_parser.cpp` (`include/project_parser.hpp`) — parses `cmake.toml` (via toml11) into the `cmkr::parser::Project` tree. Supports nested projects: a `Project` holds a `parent` pointer; the root project seeds default conditions, children inherit `conditions` and `templates`. `parser::is_root_path` detects subdirs that contain their own root `[project]`.
- `src/cmake_generator.cpp` (`include/cmake_generator.hpp`) — `gen::generate_cmake(path, parent)` emits a `CMakeLists.txt` and recurses into subdirectories that have a `cmake.toml`. `gen::generate_project(type)` scaffolds a new project from the templates in `include/literals.hpp`.
- `src/build.cpp` (`include/build.hpp`) — `build`/`install`/`clean` subcommands; re-parses `cmake.toml` for `[cmake]` settings (`build-dir`, `generator`, `config`, `gen-args`) then shells out to CMake.
- `src/help.cpp` (`include/help.hpp`) — usage text and version. The version string comes from a generated `include/resources/version.hpp` header.
- `include/fs.hpp` — `std::filesystem` with a `ghc::filesystem` fallback; prefer it over including `<filesystem>` directly.

### Conditions system

`cmake.toml` supports conditional keys like `windows.sources = [...]` or `custom.cmake-after = ...`, resolved into CMake `if()` blocks. Predefined conditions (windows, macos, linux, unix, msvc, gcc, clang, root, x64, ...) are seeded in the `Project` constructor; users override them under `[conditions]`. Condition names are lowercase `[0-9a-z-]`. Raw CMake expressions in quoted conditions can reference other conditions via `$<name>`.

### The cmkr() macro / bootstrapping

`cmake/cmkr.cmake` is both a standalone bootstrap script (`cmake -P cmkr.cmake`) and the `cmkr()` macro included from generated `CMakeLists.txt`. Key behaviors:

- Clones and builds a `cmkr` binary from `CMKR_REPO` (default `https://gitee.com/cmkr_lib/cmkr`) into a cache dir (`_cmkr_<tag>`), honoring `CMKR_TAG`, `CMKR_COMMIT_HASH`, and the `CMKR_CACHE` env var.
- The `cmkr()` macro SHA256-hashes `CMakeLists.txt` before and after running `cmkr gen`; if generation changed the file, it `include()`s a copy (`CMakerLists.txt`) so the current configure always reflects the fresh `cmake.toml`.
- Generation is skipped when the `CI` env var, `CMKR_SKIP_GENERATION`, or `CMKR_BUILD_SKIP_GENERATION` is set (the latter is set by `cmkr build` to avoid infinite loops).
- In script mode with no `cmake.toml`, it runs `cmkr init`; otherwise `cmkr gen`.

### Resource generation

`cmake/generate_resources.cmake` turns `.cmake` sources into C++ headers under the build dir's `include/resources/` (e.g. `cmkr.cmake` → `resources/cmkr.cmake.hpp`), embedded into the binary. `.in` files are processed with `configure_file(... @ONLY)`.

### Documentation

`docs/` is a Jekyll site (published at cmkr.build). Example pages under `docs/examples/` are auto-generated from the test fixtures at configure time by `cmake/generate_documentation.cmake`; the leading/trailing `#` comments in each `tests/<name>/cmake.toml` become the page content. Serve locally with `docs/serve.sh` (requires Ruby/Jekyll).

## Vendor dependencies

`third_party/` is vendored (to speed up fetching) as CMake INTERFACE libraries:
- `toml11` — TOML parsing
- `ghc_filesystem` — filesystem fallback
- `mpark_variant` — `std::variant` fallback
- `ordered_map` — `tsl::ordered_map`/`ordered_set`

## Linting / formatting

- C++ formatting: `clang-format` using the repo's `.clang-format` (150-column limit, C++11 standard, 4-space indent). CI runs clang-format v15 excluding `third_party/`. Fix with: `clang-format -style=file -i <files>`.
- `.editorconfig`: LF endings, UTF-8, 4-space indent for C/C++/TOML, tabs for CMake files. CI runs `editorconfig-checker`.
