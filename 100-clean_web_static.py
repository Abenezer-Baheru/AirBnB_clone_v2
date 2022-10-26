#!/usr/bin/python3
"""A fabric script that generate a .tgz archive from the contents of
the web_static folder ofr your AirBnB clone repo"""
from fabric.api import *


env.hosts = ['3.236.115.124', '3.227.233.5']


def do_pack():
    """Generate the .tgz archive"""
    from datetime import datetime
    import os.path

    d = datetime.now()

    file_path = 'versions/web_static_{}{}{}{}{}{}.tgz'.format(
            d.year, d.month, d.day, d.hour, d.minute, d.second)

    if not os.path.exists('versions'):
        os.mkdir('versions')

    print('Packing web_static to ' + file_path)
    r = local('tar  -cvzf {} {}'.format(file_path, 'web_static'))

    if r.stderr:
        return None

    file_stats = os.stat(file_path)

    print('web_static packed: {} -> {}Bytes'.format(
        file_path, file_stats.st_size))

    return os.path.realpath(file_path) if not r.stderr else None


def do_deploy(archive_path):
    """Deploy web_static archive on servers"""
    import os.path

    if not os.path.exists(archive_path):
        return None

    # env.usernmae =
    # env.password =
    # env.key_filename =

    remote_archive = '/tmp/' + os.path.basename(archive_path)

    remote_to_xfolder = '/data/web_static/releases/'
    remote_to_xfolder += os.path.splitext(os.path.basename(archive_path))[0]

    # extract archive file to '/data/web_static/releases/<arch. file no ext.>
    put(local_path=archive_path, remote_path=remote_archive)

    r = sudo('mkdir -p {} && tar -xvf {} -C {}'.format(
                remote_to_xfolder, remote_archive, remote_to_xfolder))
    if r.stderr:
        return False

    # remote archive file
    r = sudo('rm ' + remote_archive)
    if r.stderr:
        return False

    # update deploy symbolink link

    sudo('rm -f /data/web_static/current')
    sudo('ln -sf {} {}'.format(
        remote_to_xfolder + '/web_static', '/data/web_static/current'))

    return True


def deploy():
    """Create and distributes an archive to your web servers"""
    archive_path = do_pack()

    if not archive_path:
        return False

    return do_deploy(archive_path)


def do_clean(number=0):
    """Deletes out-of-date archives, using the function do_clean"""
    import os

    # files to delete
    number = int(number)
    if number <= 0:
        number = 1

    dirpath = os.path.realpath('versions')

    # read file names
    filenames = [s for s in os.listdir(dirpath)
                 if os.path.isfile(os.path.join(dirpath, s))]
    filenames = sorted(filenames, reverse=True)

    # cleaup local filers
    for filename in filenames[number:]:
        os.remove('versions/' + filename)

    # clean update remote server
    remote_dirpaths = run('ls /data/web_static/releases/').split()
    remote_dirpaths = sorted(remote_dirpaths, reverse=True)

    for remote_dirpath in remote_dirpaths[number:]:
        sudo('rm -r /data/web_static/releases/' + remote_dirpath)
