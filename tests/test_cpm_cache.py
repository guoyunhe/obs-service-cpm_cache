import importlib.machinery
import importlib.util
import logging
from pathlib import Path
import subprocess
import tarfile
import tempfile
import unittest
from unittest import mock


SERVICE_PATH = Path(__file__).resolve().parents[1] / "cpm_cache"
LOADER = importlib.machinery.SourceFileLoader("cpm_cache", str(SERVICE_PATH))
SPEC = importlib.util.spec_from_loader(LOADER.name, LOADER)
cpm_cache = importlib.util.module_from_spec(SPEC)
LOADER.exec_module(cpm_cache)


class CpmCacheTests(unittest.TestCase):
    def test_archive_autodetect_uses_spec_name(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "project.spec").touch()
            archive = root / "project-1.0.tar.xz"
            archive.touch()
            with mock.patch("pathlib.Path.cwd", return_value=root):
                self.assertEqual(cpm_cache.archive_autodetect(), archive)

    def test_resolve_source_rejects_parent_subdirectory(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            project = root / "project"
            project.mkdir()
            (project / "CMakeLists.txt").touch()
            with self.assertRaises(cpm_cache.ServiceError):
                cpm_cache.resolve_source(root, "project", "../outside")

    def test_service_archives_populated_cache(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            project = root / "project"
            project.mkdir()
            (project / "CMakeLists.txt").write_text("cmake_minimum_required(VERSION 3.14)\n")
            output = root / "output"

            def fake_cmake(command, check, env):
                cache = Path(env["CPM_SOURCE_CACHE"]) / "dependency" / "revision"
                self.assertNotIn(
                    "-DCPM_SOURCE_CACHE=" + env["CPM_SOURCE_CACHE"], command
                )
                self.assertEqual(
                    Path(env["CPM_SOURCE_CACHE"]),
                    Path(command[2]) / ".cache" / "cpm",
                )
                cache.mkdir(parents=True)
                (cache / "source.txt").write_text("cached")

            with mock.patch.object(cpm_cache.subprocess, "run", side_effect=fake_cmake):
                result = cpm_cache.main(
                    ["--archive", str(project), "--outdir", str(output)]
                )

            self.assertEqual(result, 0)
            archive_path = output / "cpm_cache.tar.gz"
            self.assertTrue(archive_path.is_file())
            with tarfile.open(archive_path, "r:gz") as archive:
                self.assertEqual(
                    archive.extractfile(".cache/cpm/dependency/revision/source.txt")
                    .read()
                    .decode(),
                    "cached",
                )

    def test_service_fails_when_cmake_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            project = root / "project"
            project.mkdir()
            (project / "CMakeLists.txt").touch()
            with (
                mock.patch.object(
                    cpm_cache.subprocess,
                    "run",
                    side_effect=subprocess.CalledProcessError(1, ["cmake"]),
                ),
                self.assertLogs(cpm_cache.LOG, logging.ERROR),
            ):
                result = cpm_cache.main(["--archive", str(project), "--outdir", str(root)])
            self.assertEqual(result, 1)


if __name__ == "__main__":
    unittest.main()
