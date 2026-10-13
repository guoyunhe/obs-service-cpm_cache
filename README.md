# obs-service-cpm_cache

An OBS source service that downloads and archives dependencies managed by
[CPM.cmake](https://github.com/cpm-cmake/CPM.cmake), allowing CMake projects to
build offline.

## Install

```bash
sudo zypper install obs-service-cpm_cache
```

## Configure _service

Add the service to `_service`:

```xml
<services>
  <service name="cpm_cache" mode="manual">
    <param name="archive">project-1.0.tar.gz</param>
  </service>
</services>
```

Run it with `osc service manualrun`. The generated archive `cpm_cache.tar.gz` contains the
`.cache/cpm/` directory.

The service also take other advanced parameters:

- The `compression` parameter supports `gz` (default), `bz2`, `xz`, and `tar`.
- Use `basename` and `subdir` when the project is not in the archive's detected
top-level CMake directory.

```xml
<services>
  <service name="cpm_cache" mode="manual">
    <param name="archive">project-1.0.tar.gz</param>
    <param name="compression">xz</param>
    <param name="basename">TheApp</param>
  </service>
</services>
```

## Update *.spec

1. Add `Source1: cpm_cache.tar.gz` (file extension can be different if you choose other compression algorithm)
2. Add `-a1` argument to `%setup` or `%autosetup` macro, extracting `Source1: cpm_cache.tar.gz` to build directory

```sh
Source0: %{name}-%{version}.tar.gz
Source1: cpm_cache.tar.gz

%prep
%autosetup -p1 -a1
```
