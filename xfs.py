#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# pylint: disable=C0111,C0301,R0903

__VERSION__ = '0.1.0'

import subprocess
import re

from blackbird.plugins import base

XFS_TABLE = {
    # Extent Allocation
    'extent_alloc': [
        'xs_allocx', 'xs_allocb', 'xs_freex', 'xs_freeb'
    ],

    # Allocation Btree
    'abt': [
        'xs_abt_lookup', 'xs_abt_compare', 'xs_abt_insrec', 'xs_abt_delrec'
    ],

    # Block Mapping
    'blk_map': [
        'xs_blk_mapr', 'xs_blk_mapw', 'xs_blk_unmap', 'xs_add_exlist',
        'xs_del_exlist', 'xs_look_exlist', 'xs_cmp_exlist'
    ],

    # Block Map Btree
    'bmbt': [
        'xs_bmbt_lookup', 'xs_bmbt_compare', 'xs_bmbt_insrec', 'xs_bmbt_delrec'
    ],

    # Directory Operations
    'dir': [
        'xs_dir_lookup', 'xs_dir_create', 'xs_dir_remove', 'xs_dir_getdents'
    ],

    # Transactions
    'trans': [
        'xs_trans_sync', 'xs_trans_async', 'xs_trans_empty'
    ],

    # Inode Operations
    'ig': [
        'xs_ig_attempts', 'xs_ig_found', 'xs_ig_frecycle', 'xs_ig_missed',
        'xs_ig_dup', 'xs_ig_reclaims', 'xs_ig_attrchg'
    ],

    # Log Operations
    'log': [
        'xs_log_writes', 'xs_log_blocks', 'xs_log_noiclogs', 'xs_log_force', 'xs_log_force_sleep'
    ],

    # Tail-Pushing Stats
    'push_ail': [
        'xs_try_logspace', 'xs_sleep_logspace', 'xs_push_ail', 'xs_push_ail_success',
        'xs_push_ail_pushbuf', 'xs_push_ail_pinned', 'xs_push_ail_locked', 'xs_push_ail_flushing',
        'xs_push_ail_restarts', 'xs_push_ail_flush'
    ],

    # IoMap Write Convert
    'xstrat': [
        'xs_xstrat_quick', 'xs_xstrat_split'
    ],

    # Read/Write Stats
    'rw': [
        'xs_write_calls', 'xs_read_calls'
    ],

    # Attribute Operations
    'attr': [
        'xs_attr_get', 'xs_attr_set', 'xs_attr_remove', 'xs_attr_list'
    ],

    # Inode Clustering
    'icluster': [
        'xs_iflush_count', 'xs_icluster_flushcnt', 'xs_icluster_flushinode'
    ],

    # Vnode Statistics
    'vnodes': [
        'vn_active', 'vn_alloc', 'vn_get', 'vn_hold', 'vn_rele', 'vn_reclaim',
        'vn_remove', 'vn_free'
    ],

    # Buf Statistics
    'buf': [
        'xb_get', 'xb_create', 'xb_get_locked', 'xb_get_locked_waited', 'xb_busy_locked',
        'xb_miss_locked', 'xb_page_retries', 'xb_page_found', 'xb_get_read'
    ],

    # ABTB V2
    'abtb2': [
        'xs_abtb_2_lookup', 'xs_abtb_2_compare', 'xs_abtb_2_insrec', 'xs_abtb_2_delrec',
        'xs_abtb_2_newroot', 'xs_abtb_2_killroot', 'xs_abtb_2_increment',
        'xs_abtb_2_decrement', 'xs_abtb_2_lshift', 'xs_abtb_2_rshift', 'xs_abtb_2_split',
        'xs_abtb_2_join', 'xs_abtb_2_alloc', 'xs_abtb_2_free', 'xs_abtb_2_moves'
    ],

    # ABTC V2
    'abtc2': [
        'xs_abtc_2_lookup', 'xs_abtc_2_compare', 'xs_abtc_2_insrec', 'xs_abtc_2_delrec',
        'xs_abtc_2_newroot', 'xs_abtc_2_killroot', 'xs_abtc_2_increment',
        'xs_abtc_2_decrement', 'xs_abtc_2_lshift', 'xs_abtc_2_rshift', 'xs_abtc_2_split',
        'xs_abtc_2_join', 'xs_abtc_2_alloc', 'xs_abtc_2_free', 'xs_abtc_2_moves'
    ],

    # BMBT V2
    'bmbt2': [
        'xs_bmbt_2_lookup', 'xs_bmbt_2_compare', 'xs_bmbt_2_insrec', 'xs_bmbt_2_delrec',
        'xs_bmbt_2_newroot', 'xs_bmbt_2_killroot', 'xs_bmbt_2_increment',
        'xs_bmbt_2_decrement', 'xs_bmbt_2_lshift', 'xs_bmbt_2_rshift', 'xs_bmbt_2_split',
        'xs_bmbt_2_join', 'xs_bmbt_2_alloc', 'xs_bmbt_2_free', 'xs_bmbt_2_moves'
    ],

    # IBT V2
    'ibt2': [
        'xs_ibt_2_lookup', 'xs_ibt_2_compare', 'xs_ibt_2_insrec', 'xs_ibt_2_delrec',
        'xs_ibt_2_newroot', 'xs_ibt_2_killroot', 'xs_ibt_2_increment',
        'xs_ibt_2_decrement', 'xs_ibt_2_lshift', 'xs_ibt_2_rshift', 'xs_ibt_2_split',
        'xs_ibt_2_join', 'xs_ibt_2_alloc', 'xs_ibt_2_free', 'xs_ibt_2_moves'
    ],

    # Quota Performance
    'qm': [
        'xs_qm_dqreclaims', 'xs_qm_dqreclaim_misses', 'xs_qm_dquot_dups', 'xs_qm_dqcachemisses',
        'xs_qm_dqcachehits', 'xs_qm_dqwants', 'xs_qm_dqshake_reclaims', 'xs_qm_dqinact_reclaims'
    ],

    # eXtended Precision Counters
    'xpc': [
        'xs_xstrat_bytes', 'xs_write_bytes', 'xs_read_bytes'
    ],

    # Debug
    'debug': [
        'xs_debug'
    ]
}


class ConcreteJob(base.JobBase):
    """
    This class is Called by "Executor".
    Get xfs statistics
    and send to specified zabbix server.
    """

    def __init__(self, options, queue=None, logger=None):
        super(ConcreteJob, self).__init__(options, queue, logger)

    def build_items(self):
        """
        main loop
        """

        # ping item
        self._ping()

        # get version from xfs_info
        self._xfs_info()

        # get statistics from /proc/fs/xfs/stat
        self._xfs_proc()

    def _enqueue(self, key, value):

        item = XfsItem(
            key=key,
            value=value,
            host=self.options['hostname']
        )
        self.queue.put(item, block=False)
        self.logger.debug(
            'Inserted to queue {key}:{value}'
            ''.format(key=key, value=value)
        )

    def _ping(self):
        """
        send ping item
        """

        self._enqueue('blackbird.xfs.ping', 1)
        self._enqueue('blackbird.xfs.version', __VERSION__)

    def _xfs_info(self):
        """
        detect version from xfs_info

        $ xfs_info -V
        xfs_info version 3.2.0-alpha2
        """

        xfs_version = 'Unknown'

        try:
            output = subprocess.Popen([self.options['path'], '-V'],
                                      stdout=subprocess.PIPE).communicate()[0]
            match = re.match(r'xfs_info version (\S+)', output)
            if match:
                xfs_version = match.group(1)

        except OSError:
            self.logger.debug(
                'can not exec "{0} -V", failed to get xfs version'
                ''.format(self.options['path'])
            )

        self._enqueue('xfs.version', xfs_version)

    def _xfs_proc(self):

        with open('/proc/fs/xfs/stat') as _xs:
            for line in _xs.readlines():
                _xl = line.rstrip().split(" ")
                key = _xl[0]
                value = _xl[1:]
                zipped = zip(XFS_TABLE[key], value)
                [self._enqueue('xfs.stat[{0}]'.format(ik), iv) for ik, iv in zipped]


class XfsItem(base.ItemBase):
    """
    Enqued item.
    """

    def __init__(self, key, value, host):
        super(XfsItem, self).__init__(key, value, host)

        self._data = {}
        self._generate()

    @property
    def data(self):
        return self._data

    def _generate(self):
        self._data['key'] = self.key
        self._data['value'] = self.value
        self._data['host'] = self.host
        self._data['clock'] = self.clock


class Validator(base.ValidatorBase):
    """
    Validate configuration.
    """

    def __init__(self):
        self.__spec = None

    @property
    def spec(self):
        self.__spec = (
            "[{0}]".format(__name__),
            "path=string(default='/usr/sbin/xfs_info')",
            "hostname=string(default={0})".format(self.detect_hostname()),
        )
        return self.__spec
