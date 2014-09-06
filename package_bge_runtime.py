#!/usr/bin/env python3
 
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# Data concatenation
# Copyright Mitchell Stokes
#
# Zip and tar file manipulation
# Copyright 2013 Alex Fraser
#
 
'''
Creates an executable game by combining a Blender file with the blenderplayer.
Asset files can be included. The blenderplayer is sourced from a Blender release
archive.
 
This script can be run from the command line. For detailed instructions, run
 
    package_bge_runtime.py -h
'''
 
import argparse
import fnmatch
import io
import logging
import os
import re
import struct
import sys
import tarfile
import zipfile
 
 
log = logging.getLogger('package_bge_runtime')
 
class Error(Exception):
    pass
 
class TranslationError(Error):
    def __init__(self, message):
        self.message = message
    def __str__(self):
        return repr(self.message)
 
 
class GameMeta:
    def __init__(self, game_name, dir_suffix, zip_suffix, mainfile, assets, docs, doc_strip):
        self.name = game_name
        self.mainfile = mainfile
        self.assets = assets
        self.docs = docs
        self.doc_strip = doc_strip
 
        self.dir_suffix = dir_suffix
        if dir_suffix == '':
            self.archive_root = self.name
        else:
            self.archive_root = '{0}-{1}'.format(self.name, self.dir_suffix)
 
        self.zip_suffix = zip_suffix
        if zip_suffix == '':
            self.archive_name = self.name
        else:
            self.archive_name = '{0}-{1}'.format(self.name, self.zip_suffix)
 
        self.base_directory = os.path.dirname(self.mainfile)
        for asset in assets:
            rel = os.path.relpath(asset, start=self.base_directory)
            if '..' in rel:
                raise TranslationError('Mainfile must not be in an asset '
                    'directory (but it may have assets as siblings).')
 
 
class Mapper:
 
    def __init__(self, game_meta, exclude):
        self.game_meta = game_meta
        self.exclude = exclude
        self.executable = None
 
    SPLITTER = re.compile('[/\\\\]')
    def map_doc_file(self, name):
        if self.exclude(os.path.basename(name)):
            return None
        components = OsxMapper.SPLITTER.split(name)
        components = components[self.game_meta.doc_strip:]
        if len(components) == 0:
            return None
        rel = '/'.join(components)
        return '{0}/{1}'.format(self.game_meta.archive_root, rel)
 
 
class PatchingMapper(Mapper):
 
    def map_asset_file(self, name):
        if self.exclude(os.path.basename(name)):
            return None
        rel = os.path.relpath(name, start=self.game_meta.base_directory)
        return '{0}/{1}'.format(self.game_meta.archive_root, rel)
 
    def patch(self, name, data):
        '''Modify data before writing.'''
        if name == self.executable:
            log.debug('\tPatching...')
            with open(self.game_meta.mainfile, 'rb') as mf:
                data = concat_game(data, mf.read())
        return data
 
    @property
    def primary_resource(self):
        '''@return the name of the primary resource.'''
        # No primary resource: it is patched into the player executable instead.
        return None
 
 
class OsxMapper(Mapper):
    '''
    Re-maps Blender's Mac OSX file paths to suit the target package name.
 
        archive_root/
            name.app/ <- executable
                Contents/
                    _CodeSignature/
                    MacOS/
                        2.XX/
                        lib/
                        blenderplayer <- actual executable
                    Resources/
                        game.blend <- mainfile
                        *assets
    '''
 
    PLAYER_PATTERN = re.compile('^[Bb]lender[^/]*/blenderplayer.app(.*)$')
    ROOT_PATTERN = re.compile('^[Bb]lender[^/]*([^/]*)$')
    EXCLUDE_PATTERNS = re.compile('^/readme.html$')
 
    def map_blender_file(self, name):
        original_filename = name
 
        if '.DS_Store' in original_filename:
            name = None
 
        elif OsxMapper.PLAYER_PATTERN.search(original_filename) is not None:
            match = OsxMapper.PLAYER_PATTERN.search(original_filename)
            if match.group(1) == '/Contents/MacOS/blenderplayer':
                name = '{0}/{1}.app{2}'.format(self.game_meta.archive_root, self.game_meta.name, match.group(1))
                self.executable = '{0}/{1}.app'.format(self.game_meta.archive_root, self.game_meta.name)
            else:
                name = '{0}/{1}.app{2}'.format(self.game_meta.archive_root, self.game_meta.name, match.group(1))
 
        elif OsxMapper.ROOT_PATTERN.search(original_filename) is not None:
            match = OsxMapper.ROOT_PATTERN.search(original_filename)
            sub_path = match.group(1)
            if WinMapper.EXCLUDE_PATTERNS.search(sub_path) is not None:
                name = None
            else:
                if sub_path == '/copyright.txt':
                    sub_path = '/Blender-copyright.txt'
                name = '{0}{1}'.format(self.game_meta.archive_root, sub_path)
 
        else:
            # Don't copy main blender app directory.
            name = None
 
        return name
 
    def map_asset_file(self, name):
        if self.exclude(os.path.basename(name)):
            return None
        rel = os.path.relpath(name, start=self.game_meta.base_directory)
        return '{0}/{1}.app/Contents/Resources/{2}'.format(self.game_meta.archive_root, self.game_meta.name, rel)
 
    def patch(self, name, data):
        '''Modify data before writing.'''
        # No files need patching on Mac; the resource is included as a separate
        # file.
        return data
 
    @property
    def primary_resource(self):
        '''@return the name of the primary resource.'''
        return '{0}/{1}.app/Contents/Resources/game.blend'.format(self.game_meta.archive_root, self.game_meta.name)
 
 
class WinMapper(PatchingMapper):
    '''
    Re-maps Blender's Windows file paths to suit the target package name.
 
        archive_root/
            2.68/
                datafiles/
                python/lib
                scripts/modules/
            name.exe <- executable (blenderplayer + mainfile)
            *blender DLLs etc.
            *assets
    '''
 
    PATTERN = re.compile('^[^/]+(.*)$')
    EXCLUDE_PATTERNS = re.compile('^/blender\\.exe|^/BlendThumb.*\\.dll$|'
        '^/readme.html$|'
        '^/[0-9]\\.[0-9][0-9]/scripts/(?!modules)')
 
    def map_blender_file(self, name):
        match = WinMapper.PATTERN.match(name)
        if match is None:
            return None
        sub_path = match.group(1)
        if WinMapper.EXCLUDE_PATTERNS.search(sub_path) is not None:
            name = None
        elif sub_path == '/blenderplayer.exe':
            name = '{0}/{1}.exe'.format(self.game_meta.archive_root, self.game_meta.name)
            self.executable = name
        elif sub_path == '/copyright.txt':
            name = '{0}/Blender-copyright.txt'.format(self.game_meta.archive_root)
        else:
            name = '{0}{1}'.format(self.game_meta.archive_root, sub_path)
        return name
 
 
class LinMapper(PatchingMapper):
    '''
    Re-maps Blender's Linux file paths to suit the target package name.
 
        archive_root/
            2.68/
                datafiles/
                python/lib
                scripts/modules/
            name <- executable (blenderplayer + mainfile)
            *blender libs etc.
            *assets
    '''
 
    PATTERN = re.compile('^[^/]+(.*)$')
    EXCLUDE_PATTERNS = re.compile('^/blender$|^/blender-softwaregl$|^/blender-thumbnailer.py$|'
        '^/readme.html$|^/icons|'
        '^/[0-9]\\.[0-9][0-9]/scripts/(?!modules)')
 
    def map_blender_file(self, name):
        match = LinMapper.PATTERN.match(name)
        if match is None:
            return None
        sub_path = match.group(1)
        if LinMapper.EXCLUDE_PATTERNS.search(sub_path) is not None:
            name = None
        elif sub_path == '/blenderplayer':
            name = '{0}/{1}'.format(self.game_meta.archive_root, self.game_meta.name)
            self.executable = name
        elif sub_path == '/copyright.txt':
            name = '{0}/Blender-copyright.txt'.format(self.game_meta.archive_root)
        else:
            name = '{0}{1}'.format(self.game_meta.archive_root, sub_path)
        return name
 
 
def translate(game_meta, blend_dist, mapper, arcadapter):
    target_path = "{}{}".format(game_meta.archive_name, arcadapter.EXTENSION)
    with arcadapter.open(blend_dist, 'r') as blender, \
            arcadapter.open(target_path, 'w') as game:
 
        # First, copy over blenderplayer contents, but rename to game name.
        for ti in blender:
            name = mapper.map_blender_file(ti.name)
            if name is None:
                log.debug('\tIgnoring %s', ti.name)
                continue
 
            log.info(name)
            # Special handling for links
            if ti.is_link():
                ti.name = name
                game.writestr(ti)
            else:
                data = blender.read(ti)
                ti.name = name
                if data != None:
                    data = mapper.patch(name, data)
                    ti.size = len(data)
                game.writestr(ti, data=data)
 
        if mapper.executable is None:
            raise TranslationError('blenderplayer not present in archive')
 
        # On OSX (for example), the primary resource is not concatenated with
        # the executable; instead, it's included in a subdirectory. The
        # behaviour here will be determined by the mapper.
        if mapper.primary_resource is not None:
            log.debug('\tWriting mainfile %s', game_meta.mainfile)
            log.info(mapper.primary_resource)
            game.write(game_meta.mainfile, arcname=mapper.primary_resource)
 
        # Copy game resources.
        for path in full_listings(game_meta.assets):
            arcname = mapper.map_asset_file(path)
            if arcname is None:
                log.debug('\tIgnoring %s', path)
                continue
            log.info(arcname)
            game.write(path, arcname=arcname)
 
        # Copy documentation.
        for path in full_listings(game_meta.docs):
            arcname = mapper.map_doc_file(path)
            if arcname is None:
                log.debug('\tIgnoring %s', path)
                continue
            log.info(arcname)
            game.write(path, arcname=arcname)
 
    return target_path, mapper.executable
 
def full_listings(paths):
    '''Iterates over all files and subdirectories in a set of paths.'''
    for path in paths:
        if os.path.isfile(path):
            yield path
        else:
            for dirpath, _, filenames in os.walk(path):
                yield dirpath
                for f in filenames:
                    yield os.path.join(dirpath, f)
 
def concat_game(playerfile, mainfile):
    '''
    Concatenate the primary game data file onto the blenderplayer executable.
    '''
    buf = io.BytesIO()
    offset = buf.write(playerfile)
    buf.write(mainfile)
 
    # Store the offset (an int is 4 bytes, so we split it up into 4 bytes and save it)
    buf.write(struct.pack('B', (offset>>24)&0xFF))
    buf.write(struct.pack('B', (offset>>16)&0xFF))
    buf.write(struct.pack('B', (offset>>8)&0xFF))
    buf.write(struct.pack('B', (offset>>0)&0xFF))
    buf.write(b'BRUNTIME')
    buf.seek(0)
    return buf.read()
 
 
class ExGlobber:
    '''Filter used to exclude files.'''
    def __init__(self):
        self.patterns = []
 
    @staticmethod
    def from_file(file_name):
        globber = ExGlobber()
        with open(file_name) as f:
            for line in f:
                if line.startswith('#') or line.strip() == '':
                    continue
                if line.endswith('\n'):
                    line = line[:-1]
                globber.add(line)
        return globber
 
    def add(self, pattern):
        '''Exclude files matching this pattern.'''
        regex = fnmatch.translate(pattern)
        self.patterns.append(re.compile(regex))
 
    def __call__(self, filename):
        '''Returns False iff the file should be included.'''
        for p in self.patterns:
            if p.match(filename) is not None:
                return True
        return False
 
 
MAPPERS = {
    ('gnu+linux', '64'): LinMapper,
    ('gnu+linux', '32'): LinMapper,
    ('mac_osx', '64'): OsxMapper,
    ('mac_osx', '32'): OsxMapper,
    ('windows', '64'): WinMapper,
    ('windows', '32'): WinMapper,
    }
 
 
def guess_platform(blender_dist):
    # If need be, this could peek inside the files to be sure. But for now, just
    # check file name.
    if re.search('64\\.tar(.bz2|.gz)$', blender_dist) is not None:
        return 'gnu+linux', '64'
    elif re.search('\\.tar(.bz2|.gz)$', blender_dist) is not None:
        return 'gnu+linux', '32'
    elif re.search('OSX.*64\\.zip$', blender_dist) is not None:
        return 'mac_osx', '64'
    elif re.search('OSX.*\\.zip$', blender_dist) is not None:
        return 'mac_osx', '32'
    elif re.search('win(dows)?64\\.zip$', blender_dist) is not None:
        return 'windows', '64'
    elif re.search('win(dows)?32\\.zip$', blender_dist) is not None:
        return 'windows', '32'
    else:
        raise ValueError("Can't determine target platform from archive name.")
 
 
class ZipAdapter:
    '''
    Provides limited support for zip files with an interface that is shared with
    TarAdapter.
    '''
 
    EXTENSION = '.zip'
 
    def __init__(self):
        self.tf = None
        self.contents = set()
 
    @classmethod
    def open(cls, path, mode):
        instance = cls()
        if 'w' in mode:
            instance.tf = zipfile.ZipFile(path, mode, compression=zipfile.ZIP_DEFLATED)
        else:
            instance.tf = zipfile.ZipFile(path, mode)
        return instance
 
    def close(self):
        self.tf.close()
 
    # to support with statement
    def __enter__(self):
        self.tf.__enter__()
        return self
    def __exit__(self, *exc_info):
        self.tf.__exit__(*exc_info)
 
    def __iter__(self):
        for ti in self.tf.infolist():
            yield ZipInfoAdapter(ti)
 
    def read(self, info):
        return self.tf.read(info.name)
 
    def write(self, name, arcname=None):
        if arcname is None:
            arcname = name
        if arcname in self.contents:
            if not os.path.isdir(name):
                print('WARNING: Not adding duplicate file %s' % arcname)
            return
        if os.path.isdir(name):
            self.tf.write(name, arcname=arcname, compress_type=zipfile.ZIP_STORED)
        else:
            self.tf.write(name, arcname=arcname)
        self.contents.add(arcname)
 
    def writestr(self, info, data=None):
        if info.name in self.contents:
            print('WARNING: Not adding duplicate file %s' % info.name)
            return
        # Disable writing header information after file - the default utility on
        # OSX doesn't like it.
        info.ti.flag_bits &= ~8
        if data is None:
            self.tf.writestr(info.ti, b'', compress_type=zipfile.ZIP_STORED)
        else:
            self.tf.writestr(info.ti, data)
        self.contents.add(info.name)
 
class ZipInfoAdapter:
    def __init__(self, ti):
        self.ti = ti
 
    @property
    def name(self):
        return self.ti.filename
    @name.setter
    def name(self, value):
        self.ti.filename = value
 
    @property
    def size(self):
        return self.ti.file_size
    @size.setter
    def size(self, value):
        self.ti.file_size = value
 
    def is_link(self):
        # Not implemented - although it could be.
        return False
 
 
class TarAdapter:
    '''
    Provides limited support for zip files with an interface that is shared with
    ZipAdapter.
    '''
 
    EXTENSION = '.tar.bz2'
 
    def __init__(self):
        self.tf = None
        self.contents = set()
 
    @classmethod
    def open(cls, path, mode):
        if mode == 'w':
            mode = 'w:bz2'
        instance = cls()
        instance.tf = tarfile.open(path, mode)
        return instance
 
    def close(self):
        self.tf.close()
 
    # to support with statement
    def __enter__(self):
        self.tf.__enter__()
        return self
    def __exit__(self, *exc_info):
        self.tf.__exit__(*exc_info)
 
    def __iter__(self):
        for ti in self.tf:
            yield TarInfoAdapter(ti)
 
    def read(self, info):
        data = self.tf.extractfile(info.ti)
        if data is None:
            return None
        else:
            return data.read()
 
    def write(self, name, arcname=None):
        if arcname is None:
            arcname = name
        if arcname in self.contents:
            if not os.path.isdir(name):
                print('WARNING: Not adding duplicate file %s' % arcname)
            return
        self.tf.add(name, arcname=arcname, recursive=False)
        self.contents.add(arcname)
 
    def writestr(self, info, data=None):
        if info.name in self.contents:
            print('WARNING: Not adding duplicate file %s' % info.name)
            return
        if data is None:
            self.tf.addfile(info.ti)
        else:
            self.tf.addfile(info.ti, fileobj=io.BytesIO(data))
        self.contents.add(info.name)
 
class TarInfoAdapter:
    def __init__(self, ti):
        self.ti = ti
 
    @property
    def name(self):
        return self.ti.name
    @name.setter
    def name(self, value):
        self.ti.name = value
 
    @property
    def size(self):
        return self.ti.size
    @size.setter
    def size(self, value):
        self.ti.size = value
 
    def is_link(self):
        return self.ti.type in {tarfile.LNKTYPE, tarfile.SYMTYPE}
 
 
def get_adapter(blender_dist):
    '''
    Get an adapter that can read and write the format of the archive pointed to
    by `blender_dist`.
    '''
    # If need be, this could peek inside the files to be sure. But for now, just
    # check file name.
    if re.search('\\.tar(.bz2|.gz)$', blender_dist) is not None:
        return TarAdapter
    elif re.search('\\.zip$', blender_dist) is not None:
        return ZipAdapter
    else:
        raise ValueError("Can't determine file type.")
 
 
def run(argv):
    parser = argparse.ArgumentParser(
        description="Package a Blender Game Engine game for publishing.",
        epilog="The name of the mainfile is used to name the package. The "
            "mainfile must not be in an asset directory, however it may have "
            "other assets as siblings. The Blender archive dictates the "
            "architecture that is being targeted and the format of the "
            "resulting package.")
    parser.add_argument('blender_dist',
        help="Blender distributable archive.")
    parser.add_argument('mainfile',
        help=".blend file that runs when the game starts.")
    parser.add_argument('assets', nargs='*',
        help="Data files or directories to be used by the game.")
    parser.add_argument('--name', dest='name',
        help="Game name. If not given, it is taken from the name of the main "
            ".blend file.")
    parser.add_argument('--docs', dest='docs', nargs='*',
        help="Non-game assets that should be included: readme files and such. "
        "Should be specified after `assets`.")
    parser.add_argument('-v', '--version', dest='version',
        help="Optional release version string.")
    parser.add_argument('-x', '--exclude', dest='exclude',
        help="File that contains exclusion rules as file glob strings (e.g. "
            "*.blend1), one per line. Any asset files that match will be "
            "excluded from the package.")
    parser.add_argument('-p', '--strip', dest='strip', type=int, default='0',
        help="Strip this number of parent directories from the docs when "
        "writing to the archive, starting with the top-level directory. For "
        "example, `-p2 --docs=../foo/bar/baz.txt` would become "
        "`game_name/bar/baz.txt`. This does not affect the asset files, "
        "because they need to be placed in special directories for the game to "
        "run.")
    parser.add_argument('-q', '--quiet', dest='quiet', action='store_true',
        help="Don't print each file to output.")
    args = parser.parse_args(args=argv)
 
    if args.quiet:
        log_level = logging.WARN
    else:
        log_level = logging.DEBUG
    logging.basicConfig(level=log_level, format='%(message)s')
 
    log.debug('Args: %s', args)
 
    platform = guess_platform(args.blender_dist)
 
    if not args.mainfile.endswith('.blend'):
        raise ValueError('mainfile must be a .blend file')
 
    if args.name is None:
        name = os.path.basename(args.mainfile)
        name = name[:-6]
    else:
        name = args.name
 
    suffix_list = []
    if args.version is not None:
        suffix_list = [args.version]
    dir_suffix = '-'.join(suffix_list)
    suffix_list.extend(platform)
    zip_suffix = '-'.join(suffix_list)
 
    if args.docs is not None:
        docs = args.docs
    else:
        docs = []
 
    game_meta = GameMeta(name, dir_suffix, zip_suffix, args.mainfile, args.assets, docs, args.strip)
 
    if args.exclude is None:
        exclude = ExGlobber()
    else:
        exclude = ExGlobber.from_file(args.exclude)
 
    arcadapter = get_adapter(args.blender_dist)
    mapper = MAPPERS[platform](game_meta, exclude)
 
    archive, executable = translate(game_meta, args.blender_dist, mapper, arcadapter)
 
    print('Game packaged as {}'.format(archive))
    print('To play the game, extract the archive and run `{}`'.format(executable))
 
 
if __name__ == '__main__':
    run(sys.argv[1:])