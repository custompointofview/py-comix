#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import zipfile

from tqdm import tqdm


class Packer:
    """
    Packer has the ability of sweeping a given directory and create cbz archives based on contents
    """

    def __init__(self):
        """Initialize the Packer object
        :return: None
        """
        super().__init__()

    def files(self, source_dir):
        """Returns all files in the path. We already know there should be only images there.
        :param source_dir: <str> Directory where the files are found
        :return: None
        """
        for file_name in os.listdir(source_dir):
            yield os.path.join(source_dir, file_name)

    def pack_collections(self, source_dir):
        print("=" * 75)
        if not os.path.exists(str(source_dir)):
            return
        for collection in tqdm(os.listdir(source_dir), desc="# Archiving", ascii=True):
            coll_path = os.path.join(source_dir, collection)
            if (
                os.path.isfile(coll_path)
                or collection == "Archive"
                or collection.startswith(".")
            ):
                print("## Skipping:", coll_path)
                continue
            self.pack_all(coll_path)
        print("=" * 75)

    def pack_all(self, source_dir):
        """Walks in directory and archives all"""
        if not os.path.exists(str(source_dir)):
            return
        for dirname in tqdm(
            os.listdir(source_dir), desc=f"## Packing {source_dir}", ascii=True
        ):
            imgs_path = os.path.join(source_dir, dirname)
            if dirname == "." or os.path.isfile(imgs_path):
                print("## Skipping file:", imgs_path)
                continue
            print("## Packing:", imgs_path)

            collection_name = os.path.basename(source_dir)
            archive_path = os.path.join(source_dir, collection_name + " - " + dirname + ".cbz")
            self.pack(imgs_path, archive_path)

    def pack(self, imgs_path, archive_path):
        """Pack all the files in the file lists into the archive.
        :param imgs_path: <str> Directory where the images are found
        :param archive_path: <str> Path of the new archive
        :return: None
        """
        try:
            zfile = zipfile.ZipFile(archive_path, "w")
        except Exception as e:
            print("! Could not create archive: {}".format(archive_path))
            print("Error: ", e)
            return
        for i, path in enumerate(self.files(imgs_path)):
            try:
                zfile.write(path, os.path.basename(path), zipfile.ZIP_STORED)
            except Exception:
                print(
                    "! Could not add file {} to add to {}, aborting...".format(
                        path, archive_path
                    )
                )
                zfile.close()
                try:
                    os.remove(archive_path)
                except Exception:
                    pass
                return
        zfile.close()
