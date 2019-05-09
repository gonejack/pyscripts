#! /usr/bin/env python
import os
import time

now = time.time()


def search_and_remove_from(search_dir=''):
    if not os.path.isdir(search_dir):
        print 'search_dir %s is not directory' % search_dir
        return
    for cur_dir, sub_dirs, filenames in os.walk(search_dir):
        for filename in filenames:
            if filename.endswith('.msg'):
                msg_file = os.path.join(cur_dir, filename)
                msg_file_mtime = os.stat(msg_file).st_mtime
                if now - msg_file_mtime > 86400 * 30:
                    print 'remove %s' % msg_file
                    os.unlink(msg_file)
        for sub_dir in sub_dirs:
            search_and_remove_from(os.path.join(cur_dir, sub_dir))


if __name__ == '__main__':
    search_and_remove_from('.')
