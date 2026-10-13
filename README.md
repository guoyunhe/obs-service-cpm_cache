# obs-service-cpm_cache

An OBS source service that downloads and archives dependencies managed by
[CPM.cmake](https://github.com/cpm-cmake/CPM.cmake), allowing CMake projects to
build offline.

The service configures the project with `CPM_SOURCE_CACHE` set and writes the
result to `cpm_cache.tar.gz`. It accepts source tar archives (`.tar`, `.tar.gz`,
`.tar.bz2`, and `.tar.xz`) or an unpacked source directory. A matching source
archive is detected from the package's `.spec` file by default.

Add the service to `_service`:

```xml
<services>
  <service name="cpm_cache" mode="manual">
    <param name="archive">project-1.0.tar.gz</param>
  </service>
</services>
```

Run it with `osc service manualrun`. The generated archive contains a
`cpm_cache/` directory. Extract it and point CPM at that directory when
configuring the project:

```sh
tar -xf cpm_cache.tar.gz
CPM_SOURCE_CACHE="$PWD/cpm_cache" cmake -S . -B build
```

The `compression` parameter supports `gz` (default), `bz2`, `xz`, and `tar`.
Use `basename` and `subdir` when the project is not in the archive's detected
top-level CMake directory.
