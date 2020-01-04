#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import zipfile


class Packer:
    """
    Packer has the ability of sweeping a given directory and create cbz archives based on contents
    """
    def __init__(self, source_dir):
        """Initialize the Packer object
        :param source_dir: <str> Archives directory where all the directories are found
        :return: None
        """
        super().__init__()
        if not os.path.isdir(source_dir):
            sys.stderr.write("The directory does not exist! Exiting")
            sys.exit(1)
        self.source_dir = source_dir
        self.formats = ["png", "jpg", "jpeg"]

    def files(self, source_dir):
        """Returns all files in the path. We already know there should be only images there.
        :param source_dir: <str> Directory where the files are found
        :return: None
        """
        for file_name in os.listdir(source_dir):

            yield os.path.join(source_dir, file_name)

    def pack_all(self):
        """Walks in directory and archives all"""
        for (dirpath, dirnames, filenames) in os.walk(self.source_dir):
            for d in dirnames:
                imgs_path = os.path.join(dirpath, d)
                archive_path = os.path.join(dirpath, d + ".cbz")
                print("=" * 75)
                print("## Archiving: ", imgs_path)
                self.pack(imgs_path, archive_path)
        print("=" * 75)

    def pack(self, imgs_path, archive_path):
        """Pack all the files in the file lists into the archive.
        :param imgs_path: <str> Directory where the images are found
        :param archive_path: <str> Path of the new archive
        :return: None
        """
        try:
            zfile = zipfile.ZipFile(archive_path, 'w')
        except Exception:
            print('! Could not create archive: {}'.format(archive_path))
            return
        for i, path in enumerate(self.files(imgs_path)):
            try:
                zfile.write(path, os.path.basename(path), zipfile.ZIP_STORED)
            except Exception:
                print('! Could not add file {} to add to {}, aborting...'.format(path, archive_path))
                zfile.close()
                try:
                    os.remove(archive_path)
                except Exception:
                    pass
                return
        zfile.close()
