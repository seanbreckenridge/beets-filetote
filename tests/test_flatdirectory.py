import logging
import os

from beets import config

from tests.helper import FiletoteTestCase

log = logging.getLogger("beets")


class FiletoteFromFlatDirectoryTest(FiletoteTestCase):
    """
    Tests to check that Filetote copies or moves artifact files from a
    flat directory (e.g., all songs in an album are imported from a single
    directory). Also tests `extensions` and `filenames` config options.
    """

    def setUp(self):
        super().setUp()

        self._create_flat_import_dir()
        self._setup_import_session(autotag=False)

        self._base_file_count = self._media_count + self._pairs_count

    def test_only_copy_artifacts_matching_configured_extension(self):
        config["filetote"]["extensions"] = ".file"

        self._run_importer()

        self.assert_number_of_files_in_dir(
            self._media_count + 2, self.lib_dir, b"Tag Artist", b"Tag Album"
        )

        self.assert_in_lib_dir(b"Tag Artist", b"Tag Album", b"artifact.file")
        self.assert_in_lib_dir(b"Tag Artist", b"Tag Album", b"artifact2.file")

        self.assert_in_import_dir(b"the_album", b"artifact.nfo")
        self.assert_in_import_dir(b"the_album", b"artifact.lrc")

        self.assert_not_in_lib_dir(b"Tag Artist", b"Tag Album", b"artifact.nfo")
        self.assert_not_in_lib_dir(b"Tag Artist", b"Tag Album", b"artifact.lrc")

    def test_exact_matching_configured_extension(self):
        config["filetote"]["extensions"] = ".file"

        self._create_file(
            os.path.join(self.import_dir, b"the_album"), b"artifact.file2"
        )

        self._run_importer()

        self.assert_number_of_files_in_dir(
            self._media_count + 2, self.lib_dir, b"Tag Artist", b"Tag Album"
        )

        self.assert_in_lib_dir(b"Tag Artist", b"Tag Album", b"artifact.file")
        self.assert_in_lib_dir(b"Tag Artist", b"Tag Album", b"artifact2.file")

        self.assert_in_import_dir(b"the_album", b"artifact.file2")
        self.assert_not_in_lib_dir(
            b"Tag Artist", b"Tag Album", b"artifact.file2"
        )

    def test_exclude_artifacts_matching_configured_exclude(self):
        config["filetote"]["extensions"] = ".file"
        config["filetote"]["exclude"] = "artifact2.file"

        self._run_importer()

        self.assert_number_of_files_in_dir(
            self._media_count + 1, self.lib_dir, b"Tag Artist", b"Tag Album"
        )

        self.assert_in_lib_dir(b"Tag Artist", b"Tag Album", b"artifact.file")

        self.assert_not_in_lib_dir(
            b"Tag Artist", b"Tag Album", b"artifact2.file"
        )
        self.assert_not_in_lib_dir(b"Tag Artist", b"Tag Album", b"artifact.nfo")
        self.assert_not_in_lib_dir(b"Tag Artist", b"Tag Album", b"artifact.lrc")

    def test_only_copy_artifacts_matching_configured_filename(self):
        config["filetote"]["extensions"] = ""
        config["filetote"]["filenames"] = "artifact.file"

        self._run_importer()

        self.assert_number_of_files_in_dir(
            self._media_count + 1, self.lib_dir, b"Tag Artist", b"Tag Album"
        )

        self.assert_in_lib_dir(b"Tag Artist", b"Tag Album", b"artifact.file")

        self.assert_not_in_lib_dir(
            b"Tag Artist", b"Tag Album", b"artifact2.file"
        )
        self.assert_not_in_lib_dir(b"Tag Artist", b"Tag Album", b"artifact.nfo")
        self.assert_not_in_lib_dir(b"Tag Artist", b"Tag Album", b"artifact.lrc")

    def test_only_copy_artifacts_matching_configured_extension_and_filename(
        self,
    ):
        config["filetote"]["extensions"] = ".file"
        config["filetote"]["filenames"] = "artifact.nfo"

        self._run_importer()

        self.assert_number_of_files_in_dir(
            self._media_count + 3, self.lib_dir, b"Tag Artist", b"Tag Album"
        )

        self.assert_in_lib_dir(b"Tag Artist", b"Tag Album", b"artifact.file")
        self.assert_in_lib_dir(b"Tag Artist", b"Tag Album", b"artifact2.file")
        self.assert_in_lib_dir(b"Tag Artist", b"Tag Album", b"artifact.nfo")

        self.assert_not_in_lib_dir(b"Tag Artist", b"Tag Album", b"artifact.lrc")

    def test_copy_all_artifacts_by_default(self):
        self._run_importer()

        self.assert_number_of_files_in_dir(
            self._base_file_count + 4, self.lib_dir, b"Tag Artist", b"Tag Album"
        )

        self.assert_in_lib_dir(b"Tag Artist", b"Tag Album", b"artifact.file")
        self.assert_in_lib_dir(b"Tag Artist", b"Tag Album", b"artifact2.file")
        self.assert_in_lib_dir(b"Tag Artist", b"Tag Album", b"artifact.nfo")
        self.assert_in_lib_dir(b"Tag Artist", b"Tag Album", b"artifact.lrc")

    def test_copy_artifacts(self):
        self._run_importer()

        self.assert_number_of_files_in_dir(
            self._base_file_count + 4, self.lib_dir, b"Tag Artist", b"Tag Album"
        )

        self.assert_in_lib_dir(b"Tag Artist", b"Tag Album", b"artifact.file")
        self.assert_in_lib_dir(b"Tag Artist", b"Tag Album", b"artifact2.file")
        self.assert_in_lib_dir(b"Tag Artist", b"Tag Album", b"artifact.nfo")
        self.assert_in_lib_dir(b"Tag Artist", b"Tag Album", b"artifact.lrc")

    def test_ignore_media_files(self):
        self._run_importer()

        self.assert_not_in_lib_dir(b"Tag Artist", b"Tag Album", b"track_1.mp3")

    def test_move_artifacts(self):
        config["import"]["move"] = True

        self._run_importer()

        self.assert_number_of_files_in_dir(
            self._base_file_count + 4, self.lib_dir, b"Tag Artist", b"Tag Album"
        )

        self.assert_in_lib_dir(b"Tag Artist", b"Tag Album", b"artifact.file")
        self.assert_in_lib_dir(b"Tag Artist", b"Tag Album", b"artifact2.file")
        self.assert_in_lib_dir(b"Tag Artist", b"Tag Album", b"artifact.nfo")
        self.assert_in_lib_dir(b"Tag Artist", b"Tag Album", b"artifact.lrc")

        self.assert_not_in_import_dir(b"the_album", b"artifact.file")
        self.assert_not_in_import_dir(b"the_album", b"artifact2.file")
        self.assert_not_in_import_dir(b"the_album", b"artifact.nfo")
        self.assert_not_in_import_dir(b"the_album", b"artifact.lrc")

    def test_do_nothing_when_not_copying_or_moving(self):
        """
        Check that plugin leaves everything alone when not
        copying (-C command line option) and not moving.
        """
        config["import"]["copy"] = False
        config["import"]["move"] = False

        self._run_importer()

        self.assert_number_of_files_in_dir(
            self._base_file_count + 4, self.import_dir, b"the_album"
        )

        self.assert_in_import_dir(b"the_album", b"artifact.file")
        self.assert_in_import_dir(b"the_album", b"artifact2.file")
        self.assert_in_import_dir(b"the_album", b"artifact.nfo")
        self.assert_in_import_dir(b"the_album", b"artifact.lrc")

    def test_artifacts_copymove_on_first_media_by_default(self):
        """By default, all eligible files are grabbed with the first item."""
        config["filetote"]["extensions"] = ".file"
        config["paths"]["ext:file"] = str(
            "$albumpath/$medianame_old - $old_filename"
        )

        self._run_importer()

        self.assert_in_lib_dir(
            b"Tag Artist", b"Tag Album", b"track_1 - artifact.file"
        )
        self.assert_in_lib_dir(
            b"Tag Artist", b"Tag Album", b"track_1 - artifact2.file"
        )
