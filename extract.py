#!/usr/local/bin/python

import os
import json
import shutil

from datauri import DataURI
from argparse import ArgumentParser
import logging

logging.basicConfig(level=logging.INFO)


def is_valid_file(parser, arg):
    if not os.path.exists(arg):
        parser.error("The file %s does not exist!" % arg)
    else:
        return arg


class IgnitionExtract(object):

    def __init__(self, ignition_path, base_dir):
        self.ignition = ignition_path
        self.base_dir = base_dir
        # SYSTEMD_PATH is the path systemd modifiable units, services, etc.. reside
        self.systemd_path = os.path.join(self.base_dir, "etc/systemd/system")
        # WANTS_PATH_SYSTEMD is the path where enabled units should be linked
        self.systemd_wants_path = os.path.join(self.base_dir, "etc/systemd/system/multi-user.target.wants/")
        # DEV_NULL_PATH is the systems path to and endless blackhole
        self.dev_null_path = os.path.join(self.base_dir, "dev/null")

    def update_files(self):
        """update_files writes files and systemd units specified in the ignition to disk."""
        ign = json.load(open(self.ignition))
        self.write_files(ign['storage']['files'])
        self.write_units(ign["systemd"]['units'])

    def write_files(self, ignition_files):
        """writes the given files to disk."""
        for f in ignition_files:
            path = self.base_dir + f["path"]
            mode = f["mode"]
            # convert the data to the actual content
            content = DataURI(f["contents"]['source'])
            logging.info("Creating dir: %s", os.path.dirname(path))
            os.makedirs(os.path.dirname(path), exist_ok=True)
            logging.info("Opening file: %s", path)
            with open(path, "w") as f:
                logging.debug("Writing content: %s", content.text)
                f.write(content.text)
            logging.info("Running chmod permissions: %s, path: %s", mode, path)
            os.chmod(path, mode)

    def write_units(self, units):
        """writes the systemd units to disk"""
        for u in units:
            # write the dropin to disk
            for dropin in u.get("dropins", []):
                logging.info("Writing systemd unit dropin %s", dropin["name"])
                path = os.path.join(self.systemd_path, u["name"] + ".d", dropin["name"])
                logging.info("Creating dir: %s", os.path.dirname(path))
                os.makedirs(os.path.dirname(path), exist_ok=True)
                with open(path, "w") as f:
                    logging.debug("Writing content: %s", dropin["contents"])
                    f.write(dropin["contents"])
                logging.info("Wrote systemd unit dropin at %s", path)

            unit_name = u["name"]
            unit_path = os.path.join(self.systemd_path, unit_name)
            # In case the unit is masked. if the unit is masked delete it and write a symlink to /dev/null
            if u.get("mask"):
                logging.info("Systemd unit masked")
                shutil.rmtree(unit_path)
                logging.info("Removed unit %s", unit_name)
                os.symlink(self.dev_null_path, unit_path)
                logging.info("Created symlink unit %s to %s", unit_name, self.dev_null_path)
                continue

            if u.get("contents"):
                logging.info("Writing systemd unit %s", unit_name)
                # write the unit to disk
                with open(unit_path, "w") as f:
                    logging.debug("Writing content: %s", u["contents"])
                    f.write(u["contents"])

                logging.info("Successfully wrote systemd unit %s: ", unit_name)

            # if the unit should be enabled, then enable it, otherwise the unit will ve disabled
            if u.get("enabled"):
                self.enable_unit(unit_name)
            else:
                self.disable_unit(unit_name)

    def enable_unit(self, unit_name):
        """enable_unit enables a systemd unit via symlink"""
        logging.info("Enabling unit: %s", unit_name)
        # The link location
        wants_path = os.path.join(self.systemd_wants_path, unit_name)
        # sanity check that we don't return an error when the link already exists
        if os.path.lexists(wants_path):
            logging.info("%s already exists. Not making a new symlink", wants_path)
            return
        # The originating file to link
        service_path = os.path.join(self.systemd_path, unit_name)
        logging.info("Enabling unit at %s", wants_path)
        os.symlink(service_path, wants_path)
        logging.info("Enabled %s", unit_name)

    def disable_unit(self, unit_name):
        '''disable_unit disables a systemd unit via symlink removal'''
        logging.info("Disabling unit: %s", unit_name)
        # The link location
        wants_path = os.path.join(self.systemd_wants_path, unit_name)
        # sanity check that we don't return an error when the link already exists
        if not os.path.lexists(wants_path):
            logging.info("%s was not present. No need to remove", wants_path)
            return
        logging.info("Disabling unit at %s", wants_path)
        os.remove(wants_path)
        logging.info("Disabled %s", unit_name)


def main():
    parser = ArgumentParser(description="ignition file path")
    parser.add_argument(dest="filename",
                        help="ignition file path",
                        metavar="FILE",
                        type=lambda x: is_valid_file(parser, x))
    parser.add_argument("--base_dir",
                        default="/host",
                        help="path to the host / directory",
                        type=str)

    args = parser.parse_args()
    IgnitionExtract(args.filename, args.base_dir).update_files()


if __name__ == '__main__':
    main()
