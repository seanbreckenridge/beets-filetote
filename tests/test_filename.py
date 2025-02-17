import os

import beets
import pytest
from beets import config

from tests import _common
from tests.helper import FiletoteTestCase


class FiletoteFilename(FiletoteTestCase):
    """
    Tests to check handling of artifacts with filenames containing unicode characters
    """

    def setUp(self):
        super().setUp()

        self._set_import_dir()
        self.album_path = os.path.join(self.import_dir, b"the_album")
        self.rsrc_mp3 = b"full.mp3"
        os.makedirs(self.album_path)

        self._setup_import_session(autotag=False)

        config["filetote"]["extensions"] = ".file"

    def test_import_dir_with_unicode_character_in_artifact_name_copy(self):
        self._create_file(
            self.album_path, beets.util.bytestring_path("\xe4rtifact.file")
        )
        medium = self._create_medium(
            os.path.join(self.album_path, b"track_1.mp3"), self.rsrc_mp3
        )
        self.import_media = [medium]

        self._run_importer()

        self.assert_in_lib_dir(
            b"Tag Artist",
            b"Tag Album",
            beets.util.bytestring_path("\xe4rtifact.file"),
        )

    def test_import_dir_with_unicode_character_in_artifact_name_move(self):
        config["import"]["move"] = True

        self._create_file(
            self.album_path, beets.util.bytestring_path("\xe4rtifact.file")
        )
        medium = self._create_medium(
            os.path.join(self.album_path, b"track_1.mp3"), self.rsrc_mp3
        )
        self.import_media = [medium]

        self._run_importer()

        self.assert_in_lib_dir(
            b"Tag Artist",
            b"Tag Album",
            beets.util.bytestring_path("\xe4rtifact.file"),
        )

    @pytest.mark.skipif(_common.PLATFORM == "win32", reason="win32")
    def test_import_with_illegal_character_in_artifact_name_obeys_beets(
        self,
    ):
        config["import"]["move"] = True
        config["filetote"]["extensions"] = ".log"
        config["paths"]["ext:.log"] = str("$albumpath/$album - $old_filename")

        self.lib.path_formats[0] = (
            "default",
            os.path.join("$artist", "$album", "$album - $title"),
        )

        self._create_file(
            self.album_path,
            b"CoolName: Album&Tag.log",
        )
        medium = self._create_medium(
            os.path.join(self.album_path, b"track_1.mp3"),
            self.rsrc_mp3,
            album="Album: Subtitle",
        )
        self.import_media = [medium]

        self._run_importer()

        self.assert_in_lib_dir(
            b"Tag Artist",
            b"Album_ Subtitle",
            beets.util.bytestring_path(
                "Album_ Subtitle - CoolName_ Album&Tag.log"
            ),
        )

    def test_import_dir_with_illegal_character_in_album_name(self):
        config["paths"]["ext:file"] = str("$albumpath/$artist - $album")

        # Create import directory, illegal filename character used in the album name
        self._create_file(self.album_path, b"artifact.file")
        medium = self._create_medium(
            os.path.join(self.album_path, b"track_1.mp3"),
            self.rsrc_mp3,
            album=b"Tag Album?",
        )
        self.import_media = [medium]

        self._run_importer()

        self.assert_in_lib_dir(
            b"Tag Artist", b"Tag Album_", b"Tag Artist - Tag Album_.file"
        )
