import os
import sys
import requests

def setup(target):
    '''Create skeleton Osgeo4W folders and setup database environment'''
    if not bits:
        sys.stderr.write('\n*** CPU Architecture not defined. Please use `--arch [x86 | x86_64]`\n')
        sys.exit(2)    
    if not os.path.isdir(root):
        sys.stderr.write('Root dir not found, creating %s\n' % root)
        os.makedirs(root)
    if not os.path.isdir(config):
        sys.stderr.write('creating %s\n' % config)
        os.makedirs(config)
    if not os.path.isfile(installed_db):
        sys.stderr.write('creating %s\n' % installed_db)
        global installed
        installed = {0:{}}
        write_installed()
    if not os.path.isfile(setup_ini):
        sys.stderr.write('getting %s\n' % setup_ini)
        update()
    print '''
    Osgeo4w folders and setup config exist; skeleton environment is complete.

    You might try `apt available` and `apt install` next.
    '''
def update():
    '''Fetch updated package list from mirror.

        apt update

    Specify mirror (web server, windows file share, local disk):

        apt --mirror=http://example.com/...  update
        apt --mirror=file:////server/share/...  update
        apt --mirror=file://D:/downloads/cache/...  update
    '''
    if not os.path.exists(downloads):
        os.makedirs(downloads)

    # AMR66: bits now is an option
    # bits = 'x86'
    # bits = 'x86_64'
    ##print 'CPU Architecture:', bits

    if not command == 'setup':
        bits = get_setup_arch(setup_ini)
    
    # AMR66: changed to uncompressed ini
    filename =  '%s/%s'%(bits, 'setup.ini')
    source = '%s/%s' % (mirror, filename)
    archive = os.path.join(downloads, filename)

    # backup cached ini archive
    if os.path.exists(archive):
        shutil.copy(archive, archive + '.bak')

    print('Fetching %s' % source)
    dodo_download(source, archive)
##    print('')
##
##    try:
##        uncompressedData = bz2.BZ2File(archive).read()
##    except:
##       raise IOError('\n*** Error decompressing: %s' % archive)
##
    # backup existing setup config
    if os.path.exists(setup_ini):
        shutil.copy(setup_ini, setup_bak)

    shutil.copy(archive, setup_ini)
##
##    # save uncompressed ini to setup dir
##    ini = open(setup_ini, 'w')
##    ini.write(uncompressedData)
##    ini.close

    save_config('last-mirror', mirror)
def get_mirror():
    if last_mirror == None:
        mirror = 'http://download.osgeo.org/osgeo4w/'
    else:
        mirror = last_mirror
    return mirror

def get_cache_dir():
    '''Return path to use for saving downloads.

    Precedence order:
        - command line option (-c, --cache)
        - last used cache (read from setup.rc)
        - Public Downloads folder
        - Osgeo default (%osgeo4w_root%/var/...)
    '''
    if 'cache_dir' in globals() and globals()['cache_dir'] is not None:
        return globals()['cache_dir']
    if 'last_cache' in globals() and globals()['last_cache'] is not None:
        return globals()['last_cache']
    # AMR66: changed, because an exception should be cought
    try:
        pubdown = knownpaths.get_path(getattr(knownpaths.FOLDERID, 'PublicDownloads'))
    except knownpaths.PathNotFoundException:
        # AMR66: try to use default tmp from environment,
        #        this is pretty close to osgeo4w_setup?
        pubdown = os.environ["TEMP"]

    if not os.path.exists(pubdown):
        if debug: print 'Public downloads "%s" not found, using ./var/cache instead'
        cache_dir = '%s/var/cache/setup' % (root)
    else:
        # cache_dir = os.path.join(pubdown, 'OSGeo4W-setup-cache')
        # AMR66: changed, pubdown on its own is ok
        cache_dir = pubdown
    return cache_dir
def write_installed ():
    ''' Record installed packages in install.db '''
    file = open (installed_db, 'w')
    file.write (installed_db_magic)
    file.writelines (map (lambda x: '%s %s 0\n' % (x, installed[0][x]),
                  installed[0].keys ()))
    if file.close ():
        raise TypeError('urg')

root_dir = sys.argv[1]
bits = sys.argv[2]

root = root_dir
config = root + '/etc/setup/'
setup_ini = config + '/setup.ini'
setup_bak = config + '/setup.bak'
installed_db = config + '/installed.db'
installed_db_magic = 'INSTALLED.DB 2\n'

last_mirror = ''
if not 'mirror' in globals():
    mirror = get_mirror()
# convert mirror url into acceptable folder name
mirror_dir = requests.utils.quote(mirror, '').lower()

cache_dir = get_cache_dir()

downloads = '%s/%s' % (cache_dir, mirror_dir)

if __name__ == '__main__':
    setup(root)
