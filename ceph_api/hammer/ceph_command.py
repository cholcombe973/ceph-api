import ceph_argparse
import json
import os
import rados
import six


class CephError(Exception):
    """Exception raised for errors with running a Ceph command

        :param cmd: cmd in which the error occurred
        :param msg: explanation of the error
    """

    def __init__(self, cmd, msg):
        self.cmd = cmd
        self.msg = msg


def run_ceph_command(conffile, cmd, inbuf):
    """Run a ceph command and return the results

    :param conffile: The ceph.conf configuration location
    :param cmd: The json command to run
    :param inbuf:
    :return: (string outbuf, string outs)
    :raise rados.Error: Raises on rados errors
    """
    cluster = rados.Rados(conffile=conffile)
    try:
        cluster.connect()
        result = cluster.mon_command(json.dumps(cmd), inbuf=inbuf)
        if result[0] is not 0:
            raise CephError(cmd=cmd, msg=os.strerror(abs(result[0])))
        return result[1], result[2]
    except rados.Error as e:
        raise e


class PlacementGroupCommand:
    def __init__(self, rados_config_file):
        self.rados_config_file = rados_config_file

    def pg_stat(self):
        """
        show placement group status.


        :return: (string outbuf, string outs)
        :raise CephError: Raises CephError on command execution errors
        :raise rados.Error: Raises on rados errors
        """

        cmd = {'prefix': 'pg stat'}
        return run_ceph_command(self.rados_config_file, cmd, inbuf='')

    def pg_getmap(self):
        """
        get binary pg map to -o/stdout


        :return: (string outbuf, string outs)
        :raise CephError: Raises CephError on command execution errors
        :raise rados.Error: Raises on rados errors
        """

        cmd = {'prefix': 'pg getmap'}
        return run_ceph_command(self.rados_config_file, cmd, inbuf='')

    def pg_send_pg_creates(self):
        """
        trigger pg creates to be issued


        :return: (string outbuf, string outs)
        :raise CephError: Raises CephError on command execution errors
        :raise rados.Error: Raises on rados errors
        """

        cmd = {'prefix': 'pg send_pg_creates'}
        return run_ceph_command(self.rados_config_file, cmd, inbuf='')

    def pg_dump(self, dumpcontents=None):
        """
        show human-readable versions of pg map (only 'all' valid 
        with plain)

        :param dumpcontents: list valid_range=["all","summary","sum","delta","pools","osds","pgs","pgs_brief"] allowed repeats=many
        :return: (string outbuf, string outs)
        :raise CephError: Raises CephError on command execution errors
        :raise rados.Error: Raises on rados errors
        """

        cmd = {'prefix': 'pg dump'}

        if dumpcontents is not None:
            dumpcontents_validator = ceph_argparse.CephChoices(
                strings="all|summary|sum|delta|pools|osds|pgs|pgs_brief")
            for s in dumpcontents:
                dumpcontents_validator.valid(s)
            cmd['dumpcontents'] = dumpcontents
        return run_ceph_command(self.rados_config_file, cmd, inbuf='')

    def pg_dump_json(self, dumpcontents=None):
        """
        show human-readable version of pg map in json only

        :param dumpcontents: list valid_range=["all","summary","sum","pools","osds","pgs"] allowed repeats=many
        :return: (string outbuf, string outs)
        :raise CephError: Raises CephError on command execution errors
        :raise rados.Error: Raises on rados errors
        """

        cmd = {'prefix': 'pg dump_json'}

        if dumpcontents is not None:
            dumpcontents_validator = ceph_argparse.CephChoices(
                strings="all|summary|sum|pools|osds|pgs")
            for s in dumpcontents:
                dumpcontents_validator.valid(s)
            cmd['dumpcontents'] = dumpcontents
        return run_ceph_command(self.rados_config_file, cmd, inbuf='')

    def pg_dump_pools_json(self):
        """
        show pg pools info in json only


        :return: (string outbuf, string outs)
        :raise CephError: Raises CephError on command execution errors
        :raise rados.Error: Raises on rados errors
        """

        cmd = {'prefix': 'pg dump_pools_json'}
        return run_ceph_command(self.rados_config_file, cmd, inbuf='')

    def pg_dump_stuck(self, stuckops=None, threshold=None):
        """
        show information about stuck pgs

        :param stuckops: list valid_range=["inactive","unclean","stale","undersized","degraded"] allowed repeats=many
        :param threshold: int
        :return: (string outbuf, string outs)
        :raise CephError: Raises CephError on command execution errors
        :raise rados.Error: Raises on rados errors
        """

        cmd = {'prefix': 'pg dump_stuck'}

        if stuckops is not None:
            stuckops_validator = ceph_argparse.CephChoices(
                strings="inactive|unclean|stale|undersized|degraded")
            for s in stuckops:
                stuckops_validator.valid(s)
            cmd['stuckops'] = stuckops

        if threshold is not None:
            threshold_validator = ceph_argparse.CephInt(range='')
            threshold_validator.valid(threshold)
            cmd['threshold'] = threshold
        return run_ceph_command(self.rados_config_file, cmd, inbuf='')

    def pg_ls_by_pool(self, poolstr, states=None):
        """
        list pg with pool = [poolname | poolid]

        :param states: list valid_range=["active","clean","down","replay","splitting","scrubbing","scrubq","degraded","inconsistent","peering","repair","recovering","backfill_wait","incomplete","stale","remapped","deep_scrub","backfill","backfill_toofull","recovery_wait","undersized"] allowed repeats=many
        :param poolstr: six.string_types allowed repeats=one
        :return: (string outbuf, string outs)
        :raise CephError: Raises CephError on command execution errors
        :raise rados.Error: Raises on rados errors
        """

        poolstr_validator = ceph_argparse.CephString(goodchars="")
        poolstr_validator.valid(poolstr)
        cmd = {'prefix': 'pg ls-by-pool', 'poolstr': poolstr}

        if states is not None:
            states_validator = ceph_argparse.CephChoices(
                strings=
                "active|clean|down|replay|splitting|scrubbing|scrubq|degraded|inconsistent|peering|repair|recovering|backfill_wait|incomplete|stale|remapped|deep_scrub|backfill|backfill_toofull|recovery_wait|undersized")
            for s in states:
                states_validator.valid(s)
            cmd['states'] = states
        return run_ceph_command(self.rados_config_file, cmd, inbuf='')

    def pg_ls_by_primary(self, osd, states=None, pool=None):
        """
        list pg with primary = [osd]

        :param states: list valid_range=["active","clean","down","replay","splitting","scrubbing","scrubq","degraded","inconsistent","peering","repair","recovering","backfill_wait","incomplete","stale","remapped","deep_scrub","backfill","backfill_toofull","recovery_wait","undersized"] allowed repeats=many
        :param osd: six.string_types
        :param pool: int
        :return: (string outbuf, string outs)
        :raise CephError: Raises CephError on command execution errors
        :raise rados.Error: Raises on rados errors
        """

        osd_validator = ceph_argparse.CephOsdName()
        osd_validator.valid(osd)
        cmd = {'prefix': 'pg ls-by-primary', 'osd': osd}

        if states is not None:
            states_validator = ceph_argparse.CephChoices(
                strings=
                "active|clean|down|replay|splitting|scrubbing|scrubq|degraded|inconsistent|peering|repair|recovering|backfill_wait|incomplete|stale|remapped|deep_scrub|backfill|backfill_toofull|recovery_wait|undersized")
            for s in states:
                states_validator.valid(s)
            cmd['states'] = states

        if pool is not None:
            pool_validator = ceph_argparse.CephInt(range='')
            pool_validator.valid(pool)
            cmd['pool'] = pool
        return run_ceph_command(self.rados_config_file, cmd, inbuf='')

    def pg_ls_by_osd(self, osd, states=None, pool=None):
        """
        list pg on osd [osd]

        :param osd: six.string_types
        :param states: list valid_range=["active","clean","down","replay","splitting","scrubbing","scrubq","degraded","inconsistent","peering","repair","recovering","backfill_wait","incomplete","stale","remapped","deep_scrub","backfill","backfill_toofull","recovery_wait","undersized"] allowed repeats=many
        :param pool: int
        :return: (string outbuf, string outs)
        :raise CephError: Raises CephError on command execution errors
        :raise rados.Error: Raises on rados errors
        """

        osd_validator = ceph_argparse.CephOsdName()
        osd_validator.valid(osd)
        cmd = {'prefix': 'pg ls-by-osd', 'osd': osd}

        if states is not None:
            states_validator = ceph_argparse.CephChoices(
                strings=
                "active|clean|down|replay|splitting|scrubbing|scrubq|degraded|inconsistent|peering|repair|recovering|backfill_wait|incomplete|stale|remapped|deep_scrub|backfill|backfill_toofull|recovery_wait|undersized")
            for s in states:
                states_validator.valid(s)
            cmd['states'] = states

        if pool is not None:
            pool_validator = ceph_argparse.CephInt(range='')
            pool_validator.valid(pool)
            cmd['pool'] = pool
        return run_ceph_command(self.rados_config_file, cmd, inbuf='')

    def pg_ls(self, states=None, pool=None):
        """
        list pg with specific pool, osd, state

        :param states: list valid_range=["active","clean","down","replay","splitting","scrubbing","scrubq","degraded","inconsistent","peering","repair","recovering","backfill_wait","incomplete","stale","remapped","deep_scrub","backfill","backfill_toofull","recovery_wait","undersized"] allowed repeats=many
        :param pool: int
        :return: (string outbuf, string outs)
        :raise CephError: Raises CephError on command execution errors
        :raise rados.Error: Raises on rados errors
        """

        cmd = {'prefix': 'pg ls'}

        if states is not None:
            states_validator = ceph_argparse.CephChoices(
                strings=
                "active|clean|down|replay|splitting|scrubbing|scrubq|degraded|inconsistent|peering|repair|recovering|backfill_wait|incomplete|stale|remapped|deep_scrub|backfill|backfill_toofull|recovery_wait|undersized")
            for s in states:
                states_validator.valid(s)
            cmd['states'] = states

        if pool is not None:
            pool_validator = ceph_argparse.CephInt(range='')
            pool_validator.valid(pool)
            cmd['pool'] = pool
        return run_ceph_command(self.rados_config_file, cmd, inbuf='')

    def pg_map(self, pgid):
        """
        show mapping of pg to osds

        :param pgid: six.string_types
        :return: (string outbuf, string outs)
        :raise CephError: Raises CephError on command execution errors
        :raise rados.Error: Raises on rados errors
        """

        pgid_validator = ceph_argparse.CephPgid()
        pgid_validator.valid(pgid)
        cmd = {'prefix': 'pg map', 'pgid': pgid}
        return run_ceph_command(self.rados_config_file, cmd, inbuf='')

    def pg_scrub(self, pgid):
        """
        start scrub on <pgid>

        :param pgid: six.string_types
        :return: (string outbuf, string outs)
        :raise CephError: Raises CephError on command execution errors
        :raise rados.Error: Raises on rados errors
        """

        pgid_validator = ceph_argparse.CephPgid()
        pgid_validator.valid(pgid)
        cmd = {'prefix': 'pg scrub', 'pgid': pgid}
        return run_ceph_command(self.rados_config_file, cmd, inbuf='')

    def pg_deep_scrub(self, pgid):
        """
        start deep-scrub on <pgid>

        :param pgid: six.string_types
        :return: (string outbuf, string outs)
        :raise CephError: Raises CephError on command execution errors
        :raise rados.Error: Raises on rados errors
        """

        pgid_validator = ceph_argparse.CephPgid()
        pgid_validator.valid(pgid)
        cmd = {'prefix': 'pg deep-scrub', 'pgid': pgid}
        return run_ceph_command(self.rados_config_file, cmd, inbuf='')

    def pg_repair(self, pgid):
        """
        start repair on <pgid>

        :param pgid: six.string_types
        :return: (string outbuf, string outs)
        :raise CephError: Raises CephError on command execution errors
        :raise rados.Error: Raises on rados errors
        """

        pgid_validator = ceph_argparse.CephPgid()
        pgid_validator.valid(pgid)
        cmd = {'prefix': 'pg repair', 'pgid': pgid}
        return run_ceph_command(self.rados_config_file, cmd, inbuf='')

    def pg_debug(self, debugop):
        """
        show debug info about pgs

        :param debugop: list valid_range=["unfound_objects_exist","degraded_pgs_exist"] allowed repeats=one
        :return: (string outbuf, string outs)
        :raise CephError: Raises CephError on command execution errors
        :raise rados.Error: Raises on rados errors
        """

        debugop_validator = ceph_argparse.CephChoices(
            strings="unfound_objects_exist|degraded_pgs_exist")
        for s in debugop:
            debugop_validator.valid(s)
        cmd = {'prefix': 'pg debug', 'debugop': debugop}
        return run_ceph_command(self.rados_config_file, cmd, inbuf='')

    def pg_force_create_pg(self, pgid):
        """
        force creation of pg <pgid>

        :param pgid: six.string_types
        :return: (string outbuf, string outs)
        :raise CephError: Raises CephError on command execution errors
        :raise rados.Error: Raises on rados errors
        """

        pgid_validator = ceph_argparse.CephPgid()
        pgid_validator.valid(pgid)
        cmd = {'prefix': 'pg force_create_pg', 'pgid': pgid}
        return run_ceph_command(self.rados_config_file, cmd, inbuf='')

    def pg_set_full_ratio(self, ratio):
        """
        set ratio at which pgs are considered full

        :param ratio: float min=0 max=1
        :return: (string outbuf, string outs)
        :raise CephError: Raises CephError on command execution errors
        :raise rados.Error: Raises on rados errors
        """

        ratio_validator = ceph_argparse.CephFloat(range='0|1')
        ratio_validator.valid(ratio)
        cmd = {'prefix': 'pg set_full_ratio', 'ratio': ratio}
        return run_ceph_command(self.rados_config_file, cmd, inbuf='')

    def pg_set_nearfull_ratio(self, ratio):
        """
        set ratio at which pgs are considered nearly full

        :param ratio: float min=0 max=1
        :return: (string outbuf, string outs)
        :raise CephError: Raises CephError on command execution errors
        :raise rados.Error: Raises on rados errors
        """

        ratio_validator = ceph_argparse.CephFloat(range='0|1')
        ratio_validator.valid(ratio)
        cmd = {'prefix': 'pg set_nearfull_ratio', 'ratio': ratio}
        return run_ceph_command(self.rados_config_file, cmd, inbuf='')


class MdsCommand:
    def __init__(self, rados_config_file):
        self.rados_config_file = rados_config_file

    def mds_stat(self):
        """
        show MDS status


        :return: (string outbuf, string outs)
        :raise CephError: Raises CephError on command execution errors
        :raise rados.Error: Raises on rados errors
        """

        cmd = {'prefix': 'mds stat'}
        return run_ceph_command(self.rados_config_file, cmd, inbuf='')

    def mds_dump(self, epoch=None):
        """
        dump info, optionally from epoch

        :param epoch: int
        :return: (string outbuf, string outs)
        :raise CephError: Raises CephError on command execution errors
        :raise rados.Error: Raises on rados errors
        """

        cmd = {'prefix': 'mds dump'}

        if epoch is not None:
            epoch_validator = ceph_argparse.CephInt(range='')
            epoch_validator.valid(epoch)
            cmd['epoch'] = epoch
        return run_ceph_command(self.rados_config_file, cmd, inbuf='')

    def mds_getmap(self, epoch=None):
        """
        get MDS map, optionally from epoch

        :param epoch: int
        :return: (string outbuf, string outs)
        :raise CephError: Raises CephError on command execution errors
        :raise rados.Error: Raises on rados errors
        """

        cmd = {'prefix': 'mds getmap'}

        if epoch is not None:
            epoch_validator = ceph_argparse.CephInt(range='')
            epoch_validator.valid(epoch)
            cmd['epoch'] = epoch
        return run_ceph_command(self.rados_config_file, cmd, inbuf='')

    def mds_tell(self, who, args):
        """
        send command to particular mds

        :param who: six.string_types allowed repeats=one
        :param args: six.string_types allowed repeats=many
        :return: (string outbuf, string outs)
        :raise CephError: Raises CephError on command execution errors
        :raise rados.Error: Raises on rados errors
        """

        who_validator = ceph_argparse.CephString(goodchars="")
        who_validator.valid(who)
        args_validator = ceph_argparse.CephString(goodchars="")
        args_validator.valid(args)
        cmd = {'prefix': 'mds tell', 'who': who, 'args': args}
        return run_ceph_command(self.rados_config_file, cmd, inbuf='')

    def mds_compat_show(self):
        """
        show mds compatibility settings


        :return: (string outbuf, string outs)
        :raise CephError: Raises CephError on command execution errors
        :raise rados.Error: Raises on rados errors
        """

        cmd = {'prefix': 'mds compat show'}
        return run_ceph_command(self.rados_config_file, cmd, inbuf='')

    def mds_stop(self, who):
        """
        stop mds

        :param who: six.string_types allowed repeats=one
        :return: (string outbuf, string outs)
        :raise CephError: Raises CephError on command execution errors
        :raise rados.Error: Raises on rados errors
        """

        who_validator = ceph_argparse.CephString(goodchars="")
        who_validator.valid(who)
        cmd = {'prefix': 'mds stop', 'who': who}
        return run_ceph_command(self.rados_config_file, cmd, inbuf='')

    def mds_deactivate(self, who):
        """
        stop mds

        :param who: six.string_types allowed repeats=one
        :return: (string outbuf, string outs)
        :raise CephError: Raises CephError on command execution errors
        :raise rados.Error: Raises on rados errors
        """

        who_validator = ceph_argparse.CephString(goodchars="")
        who_validator.valid(who)
        cmd = {'prefix': 'mds deactivate', 'who': who}
        return run_ceph_command(self.rados_config_file, cmd, inbuf='')

    def mds_set_max_mds(self, maxmds):
        """
        set max MDS index

        :param maxmds: int min=0
        :return: (string outbuf, string outs)
        :raise CephError: Raises CephError on command execution errors
        :raise rados.Error: Raises on rados errors
        """

        maxmds_validator = ceph_argparse.CephInt(range='0')
        maxmds_validator.valid(maxmds)
        cmd = {'prefix': 'mds set_max_mds', 'maxmds': maxmds}
        return run_ceph_command(self.rados_config_file, cmd, inbuf='')

    def mds_set(self, var, val, confirm=None):
        """
        set mds parameter <var> to <val>

        :param var: list valid_range=["max_mds","max_file_size","allow_new_snaps","inline_data"] allowed repeats=one
        :param val: six.string_types allowed repeats=one
        :param confirm: six.string_types allowed repeats=one
        :return: (string outbuf, string outs)
        :raise CephError: Raises CephError on command execution errors
        :raise rados.Error: Raises on rados errors
        """

        var_validator = ceph_argparse.CephChoices(
            strings="max_mds|max_file_size|allow_new_snaps|inline_data")
        for s in var:
            var_validator.valid(s)
        val_validator = ceph_argparse.CephString(goodchars="")
        val_validator.valid(val)
        cmd = {'prefix': 'mds set', 'var': var, 'val': val}

        if confirm is not None:
            confirm_validator = ceph_argparse.CephString(goodchars="")
            confirm_validator.valid(confirm)
            cmd['confirm'] = confirm
        return run_ceph_command(self.rados_config_file, cmd, inbuf='')

    def mds_setmap(self, epoch):
        """
        set mds map; must supply correct epoch number

        :param epoch: int min=0
        :return: (string outbuf, string outs)
        :raise CephError: Raises CephError on command execution errors
        :raise rados.Error: Raises on rados errors
        """

        epoch_validator = ceph_argparse.CephInt(range='0')
        epoch_validator.valid(epoch)
        cmd = {'prefix': 'mds setmap', 'epoch': epoch}
        return run_ceph_command(self.rados_config_file, cmd, inbuf='')

    def mds_set_state(self, state, gid):
        """
        set mds state of <gid> to <numeric-state>

        :param state: int min=0 max=20
        :param gid: int min=0
        :return: (string outbuf, string outs)
        :raise CephError: Raises CephError on command execution errors
        :raise rados.Error: Raises on rados errors
        """

        state_validator = ceph_argparse.CephInt(range='0|20')
        state_validator.valid(state)
        gid_validator = ceph_argparse.CephInt(range='0')
        gid_validator.valid(gid)
        cmd = {'prefix': 'mds set_state', 'state': state, 'gid': gid}
        return run_ceph_command(self.rados_config_file, cmd, inbuf='')

    def mds_fail(self, who):
        """
        force mds to status failed

        :param who: six.string_types allowed repeats=one
        :return: (string outbuf, string outs)
        :raise CephError: Raises CephError on command execution errors
        :raise rados.Error: Raises on rados errors
        """

        who_validator = ceph_argparse.CephString(goodchars="")
        who_validator.valid(who)
        cmd = {'prefix': 'mds fail', 'who': who}
        return run_ceph_command(self.rados_config_file, cmd, inbuf='')

    def mds_rm(self, who, gid):
        """
        remove nonactive mds

        :param who: six.string_types
        :param gid: int min=0
        :return: (string outbuf, string outs)
        :raise CephError: Raises CephError on command execution errors
        :raise rados.Error: Raises on rados errors
        """

        who_validator = ceph_argparse.CephName()
        who_validator.valid(who)
        gid_validator = ceph_argparse.CephInt(range='0')
        gid_validator.valid(gid)
        cmd = {'prefix': 'mds rm', 'who': who, 'gid': gid}
        return run_ceph_command(self.rados_config_file, cmd, inbuf='')

    def mds_rmfailed(self, who):
        """
        remove failed mds

        :param who: int min=0
        :return: (string outbuf, string outs)
        :raise CephError: Raises CephError on command execution errors
        :raise rados.Error: Raises on rados errors
        """

        who_validator = ceph_argparse.CephInt(range='0')
        who_validator.valid(who)
        cmd = {'prefix': 'mds rmfailed', 'who': who}
        return run_ceph_command(self.rados_config_file, cmd, inbuf='')

    def mds_cluster_down(self):
        """
        take MDS cluster down


        :return: (string outbuf, string outs)
        :raise CephError: Raises CephError on command execution errors
        :raise rados.Error: Raises on rados errors
        """

        cmd = {'prefix': 'mds cluster_down'}
        return run_ceph_command(self.rados_config_file, cmd, inbuf='')

    def mds_cluster_up(self):
        """
        bring MDS cluster up


        :return: (string outbuf, string outs)
        :raise CephError: Raises CephError on command execution errors
        :raise rados.Error: Raises on rados errors
        """

        cmd = {'prefix': 'mds cluster_up'}
        return run_ceph_command(self.rados_config_file, cmd, inbuf='')

    def mds_compat_rm_compat(self, feature):
        """
        remove compatible feature

        :param feature: int min=0
        :return: (string outbuf, string outs)
        :raise CephError: Raises CephError on command execution errors
        :raise rados.Error: Raises on rados errors
        """

        feature_validator = ceph_argparse.CephInt(range='0')
        feature_validator.valid(feature)
        cmd = {'prefix': 'mds compat rm_compat', 'feature': feature}
        return run_ceph_command(self.rados_config_file, cmd, inbuf='')

    def mds_compat_rm_incompat(self, feature):
        """
        remove incompatible feature

        :param feature: int min=0
        :return: (string outbuf, string outs)
        :raise CephError: Raises CephError on command execution errors
        :raise rados.Error: Raises on rados errors
        """

        feature_validator = ceph_argparse.CephInt(range='0')
        feature_validator.valid(feature)
        cmd = {'prefix': 'mds compat rm_incompat', 'feature': feature}
        return run_ceph_command(self.rados_config_file, cmd, inbuf='')

    def mds_add_data_pool(self, pool):
        """
        add data pool <pool>

        :param pool: six.string_types allowed repeats=one
        :return: (string outbuf, string outs)
        :raise CephError: Raises CephError on command execution errors
        :raise rados.Error: Raises on rados errors
        """

        pool_validator = ceph_argparse.CephString(goodchars="")
        pool_validator.valid(pool)
        cmd = {'prefix': 'mds add_data_pool', 'pool': pool}
        return run_ceph_command(self.rados_config_file, cmd, inbuf='')

    def mds_remove_data_pool(self, pool):
        """
        remove data pool <pool>

        :param pool: six.string_types allowed repeats=one
        :return: (string outbuf, string outs)
        :raise CephError: Raises CephError on command execution errors
        :raise rados.Error: Raises on rados errors
        """

        pool_validator = ceph_argparse.CephString(goodchars="")
        pool_validator.valid(pool)
        cmd = {'prefix': 'mds remove_data_pool', 'pool': pool}
        return run_ceph_command(self.rados_config_file, cmd, inbuf='')

    def mds_newfs(self, data, metadata, sure=None):
        """
        make new filesystem using pools <metadata> and <data>

        :param data: int min=0
        :param metadata: int min=0
        :param sure: list valid_range=["--yes-i-really-mean-it"] allowed repeats=one
        :return: (string outbuf, string outs)
        :raise CephError: Raises CephError on command execution errors
        :raise rados.Error: Raises on rados errors
        """

        data_validator = ceph_argparse.CephInt(range='0')
        data_validator.valid(data)
        metadata_validator = ceph_argparse.CephInt(range='0')
        metadata_validator.valid(metadata)
        cmd = {'prefix': 'mds newfs', 'data': data, 'metadata': metadata}

        if sure is not None:
            sure_validator = ceph_argparse.CephChoices(
                strings="--yes-i-really-mean-it")
            for s in sure:
                sure_validator.valid(s)
            cmd['sure'] = sure
        return run_ceph_command(self.rados_config_file, cmd, inbuf='')


class OsdCommand:
    def __init__(self, rados_config_file):
        self.rados_config_file = rados_config_file

    def osd_stat(self):
        """
        print summary of OSD map


        :return: (string outbuf, string outs)
        :raise CephError: Raises CephError on command execution errors
        :raise rados.Error: Raises on rados errors
        """

        cmd = {'prefix': 'osd stat'}
        return run_ceph_command(self.rados_config_file, cmd, inbuf='')

    def osd_dump(self, epoch=None):
        """
        print summary of OSD map

        :param epoch: int min=0
        :return: (string outbuf, string outs)
        :raise CephError: Raises CephError on command execution errors
        :raise rados.Error: Raises on rados errors
        """

        cmd = {'prefix': 'osd dump'}

        if epoch is not None:
            epoch_validator = ceph_argparse.CephInt(range='0')
            epoch_validator.valid(epoch)
            cmd['epoch'] = epoch
        return run_ceph_command(self.rados_config_file, cmd, inbuf='')

    def osd_tree(self, epoch=None):
        """
        print OSD tree

        :param epoch: int min=0
        :return: (string outbuf, string outs)
        :raise CephError: Raises CephError on command execution errors
        :raise rados.Error: Raises on rados errors
        """

        cmd = {'prefix': 'osd tree'}

        if epoch is not None:
            epoch_validator = ceph_argparse.CephInt(range='0')
            epoch_validator.valid(epoch)
            cmd['epoch'] = epoch
        return run_ceph_command(self.rados_config_file, cmd, inbuf='')

    def osd_ls(self, epoch=None):
        """
        show all OSD ids

        :param epoch: int min=0
        :return: (string outbuf, string outs)
        :raise CephError: Raises CephError on command execution errors
        :raise rados.Error: Raises on rados errors
        """

        cmd = {'prefix': 'osd ls'}

        if epoch is not None:
            epoch_validator = ceph_argparse.CephInt(range='0')
            epoch_validator.valid(epoch)
            cmd['epoch'] = epoch
        return run_ceph_command(self.rados_config_file, cmd, inbuf='')

    def osd_getmap(self, epoch=None):
        """
        get OSD map

        :param epoch: int min=0
        :return: (string outbuf, string outs)
        :raise CephError: Raises CephError on command execution errors
        :raise rados.Error: Raises on rados errors
        """

        cmd = {'prefix': 'osd getmap'}

        if epoch is not None:
            epoch_validator = ceph_argparse.CephInt(range='0')
            epoch_validator.valid(epoch)
            cmd['epoch'] = epoch
        return run_ceph_command(self.rados_config_file, cmd, inbuf='')

    def osd_getcrushmap(self, epoch=None):
        """
        get CRUSH map

        :param epoch: int min=0
        :return: (string outbuf, string outs)
        :raise CephError: Raises CephError on command execution errors
        :raise rados.Error: Raises on rados errors
        """

        cmd = {'prefix': 'osd getcrushmap'}

        if epoch is not None:
            epoch_validator = ceph_argparse.CephInt(range='0')
            epoch_validator.valid(epoch)
            cmd['epoch'] = epoch
        return run_ceph_command(self.rados_config_file, cmd, inbuf='')

    def osd_perf(self):
        """
        print dump of OSD perf summary stats


        :return: (string outbuf, string outs)
        :raise CephError: Raises CephError on command execution errors
        :raise rados.Error: Raises on rados errors
        """

        cmd = {'prefix': 'osd perf'}
        return run_ceph_command(self.rados_config_file, cmd, inbuf='')

    def osd_blocked_by(self):
        """
        print histogram of which OSDs are blocking their peers


        :return: (string outbuf, string outs)
        :raise CephError: Raises CephError on command execution errors
        :raise rados.Error: Raises on rados errors
        """

        cmd = {'prefix': 'osd blocked-by'}
        return run_ceph_command(self.rados_config_file, cmd, inbuf='')

    def osd_getmaxosd(self):
        """
        show largest OSD id


        :return: (string outbuf, string outs)
        :raise CephError: Raises CephError on command execution errors
        :raise rados.Error: Raises on rados errors
        """

        cmd = {'prefix': 'osd getmaxosd'}
        return run_ceph_command(self.rados_config_file, cmd, inbuf='')

    def osd_find(self, id):
        """
        find osd <id> in the CRUSH map and show its location

        :param id: int min=0
        :return: (string outbuf, string outs)
        :raise CephError: Raises CephError on command execution errors
        :raise rados.Error: Raises on rados errors
        """

        id_validator = ceph_argparse.CephInt(range='0')
        id_validator.valid(id)
        cmd = {'prefix': 'osd find', 'id': id}
        return run_ceph_command(self.rados_config_file, cmd, inbuf='')

    def osd_metadata(self, id):
        """
        fetch metadata for osd <id>

        :param id: int min=0
        :return: (string outbuf, string outs)
        :raise CephError: Raises CephError on command execution errors
        :raise rados.Error: Raises on rados errors
        """

        id_validator = ceph_argparse.CephInt(range='0')
        id_validator.valid(id)
        cmd = {'prefix': 'osd metadata', 'id': id}
        return run_ceph_command(self.rados_config_file, cmd, inbuf='')

    def osd_map(self, pool, object):
        """
        find pg for <object> in <pool>

        :param pool: six.string_types allowed repeats=one
        :param object: six.string_types
        :return: (string outbuf, string outs)
        :raise CephError: Raises CephError on command execution errors
        :raise rados.Error: Raises on rados errors
        """

        if not isinstance(pool, six.string_types):
            raise TypeError("pool is not a String")
        if not isinstance(object, six.string_types):
            raise TypeError("object is not a String")
        cmd = {'prefix': 'osd map', 'pool': pool, 'object': object}
        return run_ceph_command(self.rados_config_file, cmd, inbuf='')

    def osd_scrub(self, who):
        """
        initiate scrub on osd <who>

        :param who: six.string_types allowed repeats=one
        :return: (string outbuf, string outs)
        :raise CephError: Raises CephError on command execution errors
        :raise rados.Error: Raises on rados errors
        """

        who_validator = ceph_argparse.CephString(goodchars="")
        who_validator.valid(who)
        cmd = {'prefix': 'osd scrub', 'who': who}
        return run_ceph_command(self.rados_config_file, cmd, inbuf='')

    def osd_deep_scrub(self, who):
        """
        initiate deep scrub on osd <who>

        :param who: six.string_types allowed repeats=one
        :return: (string outbuf, string outs)
        :raise CephError: Raises CephError on command execution errors
        :raise rados.Error: Raises on rados errors
        """

        who_validator = ceph_argparse.CephString(goodchars="")
        who_validator.valid(who)
        cmd = {'prefix': 'osd deep-scrub', 'who': who}
        return run_ceph_command(self.rados_config_file, cmd, inbuf='')

    def osd_repair(self, who):
        """
        initiate repair on osd <who>

        :param who: six.string_types allowed repeats=one
        :return: (string outbuf, string outs)
        :raise CephError: Raises CephError on command execution errors
        :raise rados.Error: Raises on rados errors
        """

        who_validator = ceph_argparse.CephString(goodchars="")
        who_validator.valid(who)
        cmd = {'prefix': 'osd repair', 'who': who}
        return run_ceph_command(self.rados_config_file, cmd, inbuf='')

    def osd_lspools(self, auid=None):
        """
        list pools

        :param auid: int
        :return: (string outbuf, string outs)
        :raise CephError: Raises CephError on command execution errors
        :raise rados.Error: Raises on rados errors
        """

        cmd = {'prefix': 'osd lspools'}

        if auid is not None:
            auid_validator = ceph_argparse.CephInt(range='')
            auid_validator.valid(auid)
            cmd['auid'] = auid
        return run_ceph_command(self.rados_config_file, cmd, inbuf='')

    def osd_blacklist_ls(self):
        """
        show blacklisted clients


        :return: (string outbuf, string outs)
        :raise CephError: Raises CephError on command execution errors
        :raise rados.Error: Raises on rados errors
        """

        cmd = {'prefix': 'osd blacklist ls'}
        return run_ceph_command(self.rados_config_file, cmd, inbuf='')

    def osd_crush_rule_list(self):
        """
        list crush rules


        :return: (string outbuf, string outs)
        :raise CephError: Raises CephError on command execution errors
        :raise rados.Error: Raises on rados errors
        """

        cmd = {'prefix': 'osd crush rule list'}
        return run_ceph_command(self.rados_config_file, cmd, inbuf='')

    def osd_crush_rule_ls(self):
        """
        list crush rules


        :return: (string outbuf, string outs)
        :raise CephError: Raises CephError on command execution errors
        :raise rados.Error: Raises on rados errors
        """

        cmd = {'prefix': 'osd crush rule ls'}
        return run_ceph_command(self.rados_config_file, cmd, inbuf='')

    def osd_crush_rule_dump(self, name=None):
        """
        dump crush rule <name> (default all)

        :param name: six.string_types valid_characters=[A-Za-z0-9-_.] allowed repeats=one
        :return: (string outbuf, string outs)
        :raise CephError: Raises CephError on command execution errors
        :raise rados.Error: Raises on rados errors
        """

        cmd = {'prefix': 'osd crush rule dump'}

        if name is not None:
            name_validator = ceph_argparse.CephString(goodchars="A-Za-z0-9-_.")
            name_validator.valid(name)
            cmd['name'] = name
        return run_ceph_command(self.rados_config_file, cmd, inbuf='')

    def osd_crush_dump(self):
        """
        dump crush map


        :return: (string outbuf, string outs)
        :raise CephError: Raises CephError on command execution errors
        :raise rados.Error: Raises on rados errors
        """

        cmd = {'prefix': 'osd crush dump'}
        return run_ceph_command(self.rados_config_file, cmd, inbuf='')

    def osd_setcrushmap(self):
        """
        set crush map from input file


        :return: (string outbuf, string outs)
        :raise CephError: Raises CephError on command execution errors
        :raise rados.Error: Raises on rados errors
        """

        cmd = {'prefix': 'osd setcrushmap'}
        return run_ceph_command(self.rados_config_file, cmd, inbuf='')

    def osd_crush_set(self):
        """
        set crush map from input file


        :return: (string outbuf, string outs)
        :raise CephError: Raises CephError on command execution errors
        :raise rados.Error: Raises on rados errors
        """

        cmd = {'prefix': 'osd crush set'}
        return run_ceph_command(self.rados_config_file, cmd, inbuf='')

    def osd_crush_add_bucket(self, type, name):
        """
        add no-parent (probably root) crush bucket <name> of type 
        <type>

        :param type: six.string_types allowed repeats=one
        :param name: six.string_types valid_characters=[A-Za-z0-9-_.] allowed repeats=one
        :return: (string outbuf, string outs)
        :raise CephError: Raises CephError on command execution errors
        :raise rados.Error: Raises on rados errors
        """

        type_validator = ceph_argparse.CephString(goodchars="")
        type_validator.valid(type)
        name_validator = ceph_argparse.CephString(goodchars="A-Za-z0-9-_.")
        name_validator.valid(name)
        cmd = {'prefix': 'osd crush add-bucket', 'type': type, 'name': name}
        return run_ceph_command(self.rados_config_file, cmd, inbuf='')

    def osd_crush_rename_bucket(self, dstname, srcname):
        """
        rename bucket <srcname> to <dstname>

        :param dstname: six.string_types valid_characters=[A-Za-z0-9-_.] allowed repeats=one
        :param srcname: six.string_types valid_characters=[A-Za-z0-9-_.] allowed repeats=one
        :return: (string outbuf, string outs)
        :raise CephError: Raises CephError on command execution errors
        :raise rados.Error: Raises on rados errors
        """

        dstname_validator = ceph_argparse.CephString(goodchars="A-Za-z0-9-_.")
        dstname_validator.valid(dstname)
        srcname_validator = ceph_argparse.CephString(goodchars="A-Za-z0-9-_.")
        srcname_validator.valid(srcname)
        cmd = {'prefix': 'osd crush rename-bucket',
               'dstname': dstname,
               'srcname': srcname}
        return run_ceph_command(self.rados_config_file, cmd, inbuf='')

    def osd_crush_set_2(self, args, weight, id):
        """
        update crushmap position and weight for <name> to 
        <weight> with location <args>

        :param args: six.string_types valid_characters=[A-Za-z0-9-_.=] allowed repeats=many
        :param weight: float min=0
        :param id: six.string_types
        :return: (string outbuf, string outs)
        :raise CephError: Raises CephError on command execution errors
        :raise rados.Error: Raises on rados errors
        """

        args_validator = ceph_argparse.CephString(goodchars="A-Za-z0-9-_.=")
        args_validator.valid(args)
        weight_validator = ceph_argparse.CephFloat(range='0')
        weight_validator.valid(weight)
        id_validator = ceph_argparse.CephOsdName()
        id_validator.valid(id)
        cmd = {'prefix': 'osd crush set',
               'args': args,
               'weight': weight,
               'id': id}
        return run_ceph_command(self.rados_config_file, cmd, inbuf='')

    def osd_crush_add(self, args, weight, id):
        """
        add or update crushmap position and weight for <name> with 
        <weight> and location <args>

        :param args: six.string_types valid_characters=[A-Za-z0-9-_.=] allowed repeats=many
        :param weight: float min=0
        :param id: six.string_types
        :return: (string outbuf, string outs)
        :raise CephError: Raises CephError on command execution errors
        :raise rados.Error: Raises on rados errors
        """

        args_validator = ceph_argparse.CephString(goodchars="A-Za-z0-9-_.=")
        args_validator.valid(args)
        weight_validator = ceph_argparse.CephFloat(range='0')
        weight_validator.valid(weight)
        id_validator = ceph_argparse.CephOsdName()
        id_validator.valid(id)
        cmd = {'prefix': 'osd crush add',
               'args': args,
               'weight': weight,
               'id': id}
        return run_ceph_command(self.rados_config_file, cmd, inbuf='')

    def osd_crush_create_or_move(self, weight, id, args):
        """
        create entry or move existing entry for <name> <weight> 
        at/to location <args>

        :param weight: float min=0
        :param id: six.string_types
        :param args: six.string_types valid_characters=[A-Za-z0-9-_.=] allowed repeats=many
        :return: (string outbuf, string outs)
        :raise CephError: Raises CephError on command execution errors
        :raise rados.Error: Raises on rados errors
        """

        weight_validator = ceph_argparse.CephFloat(range='0')
        weight_validator.valid(weight)
        id_validator = ceph_argparse.CephOsdName()
        id_validator.valid(id)
        args_validator = ceph_argparse.CephString(goodchars="A-Za-z0-9-_.=")
        args_validator.valid(args)
        cmd = {'prefix': 'osd crush create-or-move',
               'weight': weight,
               'id': id,
               'args': args}
        return run_ceph_command(self.rados_config_file, cmd, inbuf='')

    def osd_crush_move(self, name, args):
        """
        move existing entry for <name> to location <args>

        :param name: six.string_types valid_characters=[A-Za-z0-9-_.] allowed repeats=one
        :param args: six.string_types valid_characters=[A-Za-z0-9-_.=] allowed repeats=many
        :return: (string outbuf, string outs)
        :raise CephError: Raises CephError on command execution errors
        :raise rados.Error: Raises on rados errors
        """

        name_validator = ceph_argparse.CephString(goodchars="A-Za-z0-9-_.")
        name_validator.valid(name)
        args_validator = ceph_argparse.CephString(goodchars="A-Za-z0-9-_.=")
        args_validator.valid(args)
        cmd = {'prefix': 'osd crush move', 'name': name, 'args': args}
        return run_ceph_command(self.rados_config_file, cmd, inbuf='')

    def osd_crush_link(self, args, name):
        """
        link existing entry for <name> under location <args>

        :param args: six.string_types valid_characters=[A-Za-z0-9-_.=] allowed repeats=many
        :param name: six.string_types allowed repeats=one
        :return: (string outbuf, string outs)
        :raise CephError: Raises CephError on command execution errors
        :raise rados.Error: Raises on rados errors
        """

        args_validator = ceph_argparse.CephString(goodchars="A-Za-z0-9-_.=")
        args_validator.valid(args)
        name_validator = ceph_argparse.CephString(goodchars="")
        name_validator.valid(name)
        cmd = {'prefix': 'osd crush link', 'args': args, 'name': name}
        return run_ceph_command(self.rados_config_file, cmd, inbuf='')

    def osd_crush_rm(self, name, ancestor=None):
        """
        remove <name> from crush map (everywhere, or just at 
        <ancestor>)

        :param name: six.string_types valid_characters=[A-Za-z0-9-_.] allowed repeats=one
        :param ancestor: six.string_types allowed repeats=one
        :return: (string outbuf, string outs)
        :raise CephError: Raises CephError on command execution errors
        :raise rados.Error: Raises on rados errors
        """

        name_validator = ceph_argparse.CephString(goodchars="A-Za-z0-9-_.")
        name_validator.valid(name)
        cmd = {'prefix': 'osd crush rm', 'name': name}

        if ancestor is not None:
            ancestor_validator = ceph_argparse.CephString(goodchars="")
            ancestor_validator.valid(ancestor)
            cmd['ancestor'] = ancestor
        return run_ceph_command(self.rados_config_file, cmd, inbuf='')

    def osd_crush_remove(self, name, ancestor=None):
        """
        remove <name> from crush map (everywhere, or just at 
        <ancestor>)

        :param name: six.string_types valid_characters=[A-Za-z0-9-_.] allowed repeats=one
        :param ancestor: six.string_types allowed repeats=one
        :return: (string outbuf, string outs)
        :raise CephError: Raises CephError on command execution errors
        :raise rados.Error: Raises on rados errors
        """

        name_validator = ceph_argparse.CephString(goodchars="A-Za-z0-9-_.")
        name_validator.valid(name)
        cmd = {'prefix': 'osd crush remove', 'name': name}

        if ancestor is not None:
            ancestor_validator = ceph_argparse.CephString(goodchars="")
            ancestor_validator.valid(ancestor)
            cmd['ancestor'] = ancestor
        return run_ceph_command(self.rados_config_file, cmd, inbuf='')

    def osd_crush_unlink(self, name, ancestor=None):
        """
        unlink <name> from crush map (everywhere, or just at 
        <ancestor>)

        :param ancestor: six.string_types allowed repeats=one
        :param name: six.string_types valid_characters=[A-Za-z0-9-_.] allowed repeats=one
        :return: (string outbuf, string outs)
        :raise CephError: Raises CephError on command execution errors
        :raise rados.Error: Raises on rados errors
        """

        name_validator = ceph_argparse.CephString(goodchars="A-Za-z0-9-_.")
        name_validator.valid(name)
        cmd = {'prefix': 'osd crush unlink', 'name': name}

        if ancestor is not None:
            ancestor_validator = ceph_argparse.CephString(goodchars="")
            ancestor_validator.valid(ancestor)
            cmd['ancestor'] = ancestor
        return run_ceph_command(self.rados_config_file, cmd, inbuf='')

    def osd_crush_reweight_all(self):
        """
        recalculate the weights for the tree to ensure they sum 
        correctly


        :return: (string outbuf, string outs)
        :raise CephError: Raises CephError on command execution errors
        :raise rados.Error: Raises on rados errors
        """

        cmd = {'prefix': 'osd crush reweight-all'}
        return run_ceph_command(self.rados_config_file, cmd, inbuf='')

    def osd_crush_reweight(self, weight, name):
        """
        change <name>'s weight to <weight> in crush map

        :param weight: float min=0
        :param name: six.string_types valid_characters=[A-Za-z0-9-_.] allowed repeats=one
        :return: (string outbuf, string outs)
        :raise CephError: Raises CephError on command execution errors
        :raise rados.Error: Raises on rados errors
        """

        weight_validator = ceph_argparse.CephFloat(range='0')
        weight_validator.valid(weight)
        name_validator = ceph_argparse.CephString(goodchars="A-Za-z0-9-_.")
        name_validator.valid(name)
        cmd = {'prefix': 'osd crush reweight', 'weight': weight, 'name': name}
        return run_ceph_command(self.rados_config_file, cmd, inbuf='')

    def osd_crush_reweight_subtree(self, weight, name):
        """
        change all leaf items beneath <name> to <weight> in crush 
        map

        :param weight: float min=0
        :param name: six.string_types valid_characters=[A-Za-z0-9-_.] allowed repeats=one
        :return: (string outbuf, string outs)
        :raise CephError: Raises CephError on command execution errors
        :raise rados.Error: Raises on rados errors
        """

        weight_validator = ceph_argparse.CephFloat(range='0')
        weight_validator.valid(weight)
        name_validator = ceph_argparse.CephString(goodchars="A-Za-z0-9-_.")
        name_validator.valid(name)
        cmd = {'prefix': 'osd crush reweight-subtree',
               'weight': weight,
               'name': name}
        return run_ceph_command(self.rados_config_file, cmd, inbuf='')

    def osd_crush_tunables(self, profile):
        """
        set crush tunables values to <profile>

        :param profile: list valid_range=["legacy","argonaut","bobtail","firefly","hammer","optimal","default"] allowed repeats=one
        :return: (string outbuf, string outs)
        :raise CephError: Raises CephError on command execution errors
        :raise rados.Error: Raises on rados errors
        """

        profile_validator = ceph_argparse.CephChoices(
            strings="legacy|argonaut|bobtail|firefly|hammer|optimal|default")
        for s in profile:
            profile_validator.valid(s)
        cmd = {'prefix': 'osd crush tunables', 'profile': profile}
        return run_ceph_command(self.rados_config_file, cmd, inbuf='')

    def osd_crush_set_tunable(self, tunable, value):
        """
        set crush tunable <tunable> to <value>

        :param tunable: list valid_range=["straw_calc_version"] allowed repeats=one
        :param value: int
        :return: (string outbuf, string outs)
        :raise CephError: Raises CephError on command execution errors
        :raise rados.Error: Raises on rados errors
        """

        tunable_validator = ceph_argparse.CephChoices(
            strings="straw_calc_version")
        for s in tunable:
            tunable_validator.valid(s)
        value_validator = ceph_argparse.CephInt(range='')
        value_validator.valid(value)
        cmd = {'prefix': 'osd crush set-tunable',
               'tunable': tunable,
               'value': value}
        return run_ceph_command(self.rados_config_file, cmd, inbuf='')

    def osd_crush_get_tunable(self, tunable):
        """
        get crush tunable <tunable>

        :param tunable: list valid_range=["straw_calc_version"] allowed repeats=one
        :return: (string outbuf, string outs)
        :raise CephError: Raises CephError on command execution errors
        :raise rados.Error: Raises on rados errors
        """

        tunable_validator = ceph_argparse.CephChoices(
            strings="straw_calc_version")
        for s in tunable:
            tunable_validator.valid(s)
        cmd = {'prefix': 'osd crush get-tunable', 'tunable': tunable}
        return run_ceph_command(self.rados_config_file, cmd, inbuf='')

    def osd_crush_show_tunables(self):
        """
        show current crush tunables


        :return: (string outbuf, string outs)
        :raise CephError: Raises CephError on command execution errors
        :raise rados.Error: Raises on rados errors
        """

        cmd = {'prefix': 'osd crush show-tunables'}
        return run_ceph_command(self.rados_config_file, cmd, inbuf='')

    def osd_crush_rule_create_simple(self, root, type, name, mode=None):
        """
        create crush rule <name> to start from <root>, replicate 
        across buckets of type <type>, using a choose mode of 
        <firstn|indep> (default firstn; indep best for erasure pools)

        :param mode: list valid_range=["firstn","indep"] allowed repeats=one
        :param root: six.string_types valid_characters=[A-Za-z0-9-_.] allowed repeats=one
        :param type: six.string_types valid_characters=[A-Za-z0-9-_.] allowed repeats=one
        :param name: six.string_types valid_characters=[A-Za-z0-9-_.] allowed repeats=one
        :return: (string outbuf, string outs)
        :raise CephError: Raises CephError on command execution errors
        :raise rados.Error: Raises on rados errors
        """

        root_validator = ceph_argparse.CephString(goodchars="A-Za-z0-9-_.")
        root_validator.valid(root)
        type_validator = ceph_argparse.CephString(goodchars="A-Za-z0-9-_.")
        type_validator.valid(type)
        name_validator = ceph_argparse.CephString(goodchars="A-Za-z0-9-_.")
        name_validator.valid(name)
        cmd = {'prefix': 'osd crush rule create-simple',
               'root': root,
               'type': type,
               'name': name}

        if mode is not None:
            mode_validator = ceph_argparse.CephChoices(strings="firstn|indep")
            for s in mode:
                mode_validator.valid(s)
            cmd['mode'] = mode
        return run_ceph_command(self.rados_config_file, cmd, inbuf='')

    def osd_crush_rule_create_erasure(self, name, profile=None):
        """
        create crush rule <name> for erasure coded pool created 
        with <profile> (default default)

        :param name: six.string_types valid_characters=[A-Za-z0-9-_.] allowed repeats=one
        :param profile: six.string_types allowed repeats=one
        :return: (string outbuf, string outs)
        :raise CephError: Raises CephError on command execution errors
        :raise rados.Error: Raises on rados errors
        """

        name_validator = ceph_argparse.CephString(goodchars="A-Za-z0-9-_.")
        name_validator.valid(name)
        cmd = {'prefix': 'osd crush rule create-erasure', 'name': name}

        if profile is not None:
            profile_validator = ceph_argparse.CephString(goodchars="")
            profile_validator.valid(profile)
            cmd['profile'] = profile
        return run_ceph_command(self.rados_config_file, cmd, inbuf='')

    def osd_crush_rule_rm(self, name):
        """
        remove crush rule <name>

        :param name: six.string_types valid_characters=[A-Za-z0-9-_.] allowed repeats=one
        :return: (string outbuf, string outs)
        :raise CephError: Raises CephError on command execution errors
        :raise rados.Error: Raises on rados errors
        """

        name_validator = ceph_argparse.CephString(goodchars="A-Za-z0-9-_.")
        name_validator.valid(name)
        cmd = {'prefix': 'osd crush rule rm', 'name': name}
        return run_ceph_command(self.rados_config_file, cmd, inbuf='')

    def osd_crush_tree(self):
        """
        dump crush buckets and items in a tree view


        :return: (string outbuf, string outs)
        :raise CephError: Raises CephError on command execution errors
        :raise rados.Error: Raises on rados errors
        """

        cmd = {'prefix': 'osd crush tree'}
        return run_ceph_command(self.rados_config_file, cmd, inbuf='')

    def osd_setmaxosd(self, newmax):
        """
        set new maximum osd value

        :param newmax: int min=0
        :return: (string outbuf, string outs)
        :raise CephError: Raises CephError on command execution errors
        :raise rados.Error: Raises on rados errors
        """

        newmax_validator = ceph_argparse.CephInt(range='0')
        newmax_validator.valid(newmax)
        cmd = {'prefix': 'osd setmaxosd', 'newmax': newmax}
        return run_ceph_command(self.rados_config_file, cmd, inbuf='')

    def osd_pause(self):
        """
        pause osd


        :return: (string outbuf, string outs)
        :raise CephError: Raises CephError on command execution errors
        :raise rados.Error: Raises on rados errors
        """

        cmd = {'prefix': 'osd pause'}
        return run_ceph_command(self.rados_config_file, cmd, inbuf='')

    def osd_unpause(self):
        """
        unpause osd


        :return: (string outbuf, string outs)
        :raise CephError: Raises CephError on command execution errors
        :raise rados.Error: Raises on rados errors
        """

        cmd = {'prefix': 'osd unpause'}
        return run_ceph_command(self.rados_config_file, cmd, inbuf='')

    def osd_erasure_code_profile_set(self, name, profile=None):
        """
        create erasure code profile <name> with [<key[=value]> 
        ...] pairs. Add a --force at the end to override an existing 
        profile (VERY DANGEROUS)

        :param name: six.string_types valid_characters=[A-Za-z0-9-_.] allowed repeats=one
        :param profile: six.string_types allowed repeats=many
        :return: (string outbuf, string outs)
        :raise CephError: Raises CephError on command execution errors
        :raise rados.Error: Raises on rados errors
        """

        name_validator = ceph_argparse.CephString(goodchars="A-Za-z0-9-_.")
        name_validator.valid(name)
        cmd = {'prefix': 'osd erasure-code-profile set', 'name': name}

        if profile is not None:
            profile_validator = ceph_argparse.CephString(goodchars="")
            profile_validator.valid(profile)
            cmd['profile'] = profile
        return run_ceph_command(self.rados_config_file, cmd, inbuf='')

    def osd_erasure_code_profile_get(self, name):
        """
        get erasure code profile <name>

        :param name: six.string_types valid_characters=[A-Za-z0-9-_.] allowed repeats=one
        :return: (string outbuf, string outs)
        :raise CephError: Raises CephError on command execution errors
        :raise rados.Error: Raises on rados errors
        """

        name_validator = ceph_argparse.CephString(goodchars="A-Za-z0-9-_.")
        name_validator.valid(name)
        cmd = {'prefix': 'osd erasure-code-profile get', 'name': name}
        return run_ceph_command(self.rados_config_file, cmd, inbuf='')

    def osd_erasure_code_profile_rm(self, name):
        """
        remove erasure code profile <name>

        :param name: six.string_types valid_characters=[A-Za-z0-9-_.] allowed repeats=one
        :return: (string outbuf, string outs)
        :raise CephError: Raises CephError on command execution errors
        :raise rados.Error: Raises on rados errors
        """

        name_validator = ceph_argparse.CephString(goodchars="A-Za-z0-9-_.")
        name_validator.valid(name)
        cmd = {'prefix': 'osd erasure-code-profile rm', 'name': name}
        return run_ceph_command(self.rados_config_file, cmd, inbuf='')

    def osd_erasure_code_profile_ls(self):
        """
        list all erasure code profiles


        :return: (string outbuf, string outs)
        :raise CephError: Raises CephError on command execution errors
        :raise rados.Error: Raises on rados errors
        """

        cmd = {'prefix': 'osd erasure-code-profile ls'}
        return run_ceph_command(self.rados_config_file, cmd, inbuf='')

    def osd_set(self, key):
        """
        set <key>

        :param key: list valid_range=["full","pause","noup","nodown","noout","noin","nobackfill","norebalance","norecover","noscrub","nodeep-scrub","notieragent"] allowed repeats=one
        :return: (string outbuf, string outs)
        :raise CephError: Raises CephError on command execution errors
        :raise rados.Error: Raises on rados errors
        """

        key_validator = ceph_argparse.CephChoices(
            strings=
            "full|pause|noup|nodown|noout|noin|nobackfill|norebalance|norecover|noscrub|nodeep-scrub|notieragent")
        for s in key:
            key_validator.valid(s)
        cmd = {'prefix': 'osd set', 'key': key}
        return run_ceph_command(self.rados_config_file, cmd, inbuf='')

    def osd_unset(self, key):
        """
        unset <key>

        :param key: list valid_range=["full","pause","noup","nodown","noout","noin","nobackfill","norebalance","norecover","noscrub","nodeep-scrub","notieragent"] allowed repeats=one
        :return: (string outbuf, string outs)
        :raise CephError: Raises CephError on command execution errors
        :raise rados.Error: Raises on rados errors
        """

        key_validator = ceph_argparse.CephChoices(
            strings=
            "full|pause|noup|nodown|noout|noin|nobackfill|norebalance|norecover|noscrub|nodeep-scrub|notieragent")
        for s in key:
            key_validator.valid(s)
        cmd = {'prefix': 'osd unset', 'key': key}
        return run_ceph_command(self.rados_config_file, cmd, inbuf='')

    def osd_cluster_snap(self):
        """
        take cluster snapshot (disabled)


        :return: (string outbuf, string outs)
        :raise CephError: Raises CephError on command execution errors
        :raise rados.Error: Raises on rados errors
        """

        cmd = {'prefix': 'osd cluster_snap'}
        return run_ceph_command(self.rados_config_file, cmd, inbuf='')

    def osd_down(self, ids):
        """
        set osd(s) <id> [<id>...] down

        :param ids: six.string_types allowed repeats=many
        :return: (string outbuf, string outs)
        :raise CephError: Raises CephError on command execution errors
        :raise rados.Error: Raises on rados errors
        """

        ids_validator = ceph_argparse.CephString(goodchars="")
        ids_validator.valid(ids)
        cmd = {'prefix': 'osd down', 'ids': ids}
        return run_ceph_command(self.rados_config_file, cmd, inbuf='')

    def osd_out(self, ids):
        """
        set osd(s) <id> [<id>...] out

        :param ids: six.string_types allowed repeats=many
        :return: (string outbuf, string outs)
        :raise CephError: Raises CephError on command execution errors
        :raise rados.Error: Raises on rados errors
        """

        ids_validator = ceph_argparse.CephString(goodchars="")
        ids_validator.valid(ids)
        cmd = {'prefix': 'osd out', 'ids': ids}
        return run_ceph_command(self.rados_config_file, cmd, inbuf='')

    def osd_in(self, ids):
        """
        set osd(s) <id> [<id>...] in

        :param ids: six.string_types allowed repeats=many
        :return: (string outbuf, string outs)
        :raise CephError: Raises CephError on command execution errors
        :raise rados.Error: Raises on rados errors
        """

        ids_validator = ceph_argparse.CephString(goodchars="")
        ids_validator.valid(ids)
        cmd = {'prefix': 'osd in', 'ids': ids}
        return run_ceph_command(self.rados_config_file, cmd, inbuf='')

    def osd_rm(self, ids):
        """
        remove osd(s) <id> [<id>...] in

        :param ids: six.string_types allowed repeats=many
        :return: (string outbuf, string outs)
        :raise CephError: Raises CephError on command execution errors
        :raise rados.Error: Raises on rados errors
        """

        ids_validator = ceph_argparse.CephString(goodchars="")
        ids_validator.valid(ids)
        cmd = {'prefix': 'osd rm', 'ids': ids}
        return run_ceph_command(self.rados_config_file, cmd, inbuf='')

    def osd_reweight(self, id, weight):
        """
        reweight osd to 0.0 < <weight> < 1.0

        :param id: int min=0
        :param weight: float min=0 max=1
        :return: (string outbuf, string outs)
        :raise CephError: Raises CephError on command execution errors
        :raise rados.Error: Raises on rados errors
        """

        id_validator = ceph_argparse.CephInt(range='0')
        id_validator.valid(id)
        weight_validator = ceph_argparse.CephFloat(range='0|1')
        weight_validator.valid(weight)
        cmd = {'prefix': 'osd reweight', 'id': id, 'weight': weight}
        return run_ceph_command(self.rados_config_file, cmd, inbuf='')

    def osd_pg_temp(self, pgid, id=None):
        """
        set pg_temp mapping pgid:[<id> [<id>...]] (developers 
        only)

        :param pgid: six.string_types
        :param id: six.string_types allowed repeats=many
        :return: (string outbuf, string outs)
        :raise CephError: Raises CephError on command execution errors
        :raise rados.Error: Raises on rados errors
        """

        pgid_validator = ceph_argparse.CephPgid()
        pgid_validator.valid(pgid)
        cmd = {'prefix': 'osd pg-temp', 'pgid': pgid}

        if id is not None:
            id_validator = ceph_argparse.CephString(goodchars="")
            id_validator.valid(id)
            cmd['id'] = id
        return run_ceph_command(self.rados_config_file, cmd, inbuf='')

    def osd_primary_temp(self, pgid, id):
        """
        set primary_temp mapping pgid:<id>|-1 (developers 
        only)

        :param pgid: six.string_types
        :param id: six.string_types allowed repeats=one
        :return: (string outbuf, string outs)
        :raise CephError: Raises CephError on command execution errors
        :raise rados.Error: Raises on rados errors
        """

        pgid_validator = ceph_argparse.CephPgid()
        pgid_validator.valid(pgid)
        id_validator = ceph_argparse.CephString(goodchars="")
        id_validator.valid(id)
        cmd = {'prefix': 'osd primary-temp', 'pgid': pgid, 'id': id}
        return run_ceph_command(self.rados_config_file, cmd, inbuf='')

    def osd_primary_affinity(self, weight, id):
        """
        adjust osd primary-affinity from 0.0 <= <weight> <= 1.0

        :param weight: float min=0 max=1
        :param id: six.string_types
        :return: (string outbuf, string outs)
        :raise CephError: Raises CephError on command execution errors
        :raise rados.Error: Raises on rados errors
        """

        weight_validator = ceph_argparse.CephFloat(range='0|1')
        weight_validator.valid(weight)
        id_validator = ceph_argparse.CephOsdName()
        id_validator.valid(id)
        cmd = {'prefix': 'osd primary-affinity', 'weight': weight, 'id': id}
        return run_ceph_command(self.rados_config_file, cmd, inbuf='')

    def osd_lost(self, id, sure=None):
        """
        mark osd as permanently lost. THIS DESTROYS DATA IF NO MORE 
        REPLICAS EXIST, BE CAREFUL

        :param id: int min=0
        :param sure: list valid_range=["--yes-i-really-mean-it"] allowed repeats=one
        :return: (string outbuf, string outs)
        :raise CephError: Raises CephError on command execution errors
        :raise rados.Error: Raises on rados errors
        """

        id_validator = ceph_argparse.CephInt(range='0')
        id_validator.valid(id)
        cmd = {'prefix': 'osd lost', 'id': id}

        if sure is not None:
            sure_validator = ceph_argparse.CephChoices(
                strings="--yes-i-really-mean-it")
            for s in sure:
                sure_validator.valid(s)
            cmd['sure'] = sure
        return run_ceph_command(self.rados_config_file, cmd, inbuf='')

    def osd_create(self, uuid=None):
        """
        create new osd (with optional UUID)

        :param uuid: uuid.UUID
        :return: (string outbuf, string outs)
        :raise CephError: Raises CephError on command execution errors
        :raise rados.Error: Raises on rados errors
        """

        cmd = {'prefix': 'osd create'}

        if uuid is not None:
            uuid_validator = ceph_argparse.CephUUID()
            uuid_validator.valid(uuid)
            cmd['uuid'] = uuid
        return run_ceph_command(self.rados_config_file, cmd, inbuf='')

    def osd_blacklist(self, addr, blacklistop, expire=None):
        """
        add (optionally until <expire> seconds from now) or 
        remove <addr> from blacklist

        :param addr: CephIPAddr + optional '/nonce'
        :param blacklistop: list valid_range=["add","rm"] allowed repeats=one
        :param expire: float min=0
        :return: (string outbuf, string outs)
        :raise CephError: Raises CephError on command execution errors
        :raise rados.Error: Raises on rados errors
        """

        addr_validator = ceph_argparse.CephEntityAddr()
        addr_validator.valid(addr)
        blacklistop_validator = ceph_argparse.CephChoices(strings="add|rm")
        for s in blacklistop:
            blacklistop_validator.valid(s)
        cmd = {'prefix': 'osd blacklist',
               'addr': addr,
               'blacklistop': blacklistop}

        if expire is not None:
            expire_validator = ceph_argparse.CephFloat(range='0')
            expire_validator.valid(expire)
            cmd['expire'] = expire
        return run_ceph_command(self.rados_config_file, cmd, inbuf='')

    def osd_pool_mksnap(self, snap, pool):
        """
        make snapshot <snap> in <pool>

        :param snap: six.string_types allowed repeats=one
        :param pool: six.string_types allowed repeats=one
        :return: (string outbuf, string outs)
        :raise CephError: Raises CephError on command execution errors
        :raise rados.Error: Raises on rados errors
        """

        snap_validator = ceph_argparse.CephString(goodchars="")
        snap_validator.valid(snap)
        if not isinstance(pool, six.string_types):
            raise TypeError("pool is not a String")
        cmd = {'prefix': 'osd pool mksnap', 'snap': snap, 'pool': pool}
        return run_ceph_command(self.rados_config_file, cmd, inbuf='')

    def osd_pool_rmsnap(self, pool, snap):
        """
        remove snapshot <snap> from <pool>

        :param pool: six.string_types allowed repeats=one
        :param snap: six.string_types allowed repeats=one
        :return: (string outbuf, string outs)
        :raise CephError: Raises CephError on command execution errors
        :raise rados.Error: Raises on rados errors
        """

        if not isinstance(pool, six.string_types):
            raise TypeError("pool is not a String")
        snap_validator = ceph_argparse.CephString(goodchars="")
        snap_validator.valid(snap)
        cmd = {'prefix': 'osd pool rmsnap', 'pool': pool, 'snap': snap}
        return run_ceph_command(self.rados_config_file, cmd, inbuf='')

    def osd_pool_ls(self, detail=None):
        """
        list pools

        :param detail: list valid_range=["detail"] allowed repeats=one
        :return: (string outbuf, string outs)
        :raise CephError: Raises CephError on command execution errors
        :raise rados.Error: Raises on rados errors
        """

        cmd = {'prefix': 'osd pool ls'}

        if detail is not None:
            detail_validator = ceph_argparse.CephChoices(strings="detail")
            for s in detail:
                detail_validator.valid(s)
            cmd['detail'] = detail
        return run_ceph_command(self.rados_config_file, cmd, inbuf='')

    def osd_pool_create(self,
                        pool,
                        pg_num,
                        ruleset=None,
                        erasure_code_profile=None,
                        pgp_num=None,
                        pool_type=None,
                        expected_num_objects=None):
        """
        create pool

        :param ruleset: six.string_types allowed repeats=one
        :param erasure_code_profile: six.string_types allowed repeats=one
        :param pgp_num: int min=0
        :param pool: six.string_types allowed repeats=one
        :param pg_num: int min=0
        :param pool_type: list valid_range=["replicated","erasure"] allowed repeats=one
        :param expected_num_objects: int
        :return: (string outbuf, string outs)
        :raise CephError: Raises CephError on command execution errors
        :raise rados.Error: Raises on rados errors
        """

        if not isinstance(pool, six.string_types):
            raise TypeError("pool is not a String")
        pg_num_validator = ceph_argparse.CephInt(range='0')
        pg_num_validator.valid(pg_num)
        cmd = {'prefix': 'osd pool create', 'pool': pool, 'pg_num': pg_num}

        if ruleset is not None:
            ruleset_validator = ceph_argparse.CephString(goodchars="")
            ruleset_validator.valid(ruleset)
            cmd['ruleset'] = ruleset

        if erasure_code_profile is not None:
            erasure_code_profile_validator = ceph_argparse.CephString(
                goodchars="")
            erasure_code_profile_validator.valid(erasure_code_profile)
            cmd['erasure_code_profile'] = erasure_code_profile

        if pgp_num is not None:
            pgp_num_validator = ceph_argparse.CephInt(range='0')
            pgp_num_validator.valid(pgp_num)
            cmd['pgp_num'] = pgp_num

        if pool_type is not None:
            pool_type_validator = ceph_argparse.CephChoices(
                strings="replicated|erasure")
            for s in pool_type:
                pool_type_validator.valid(s)
            cmd['pool_type'] = pool_type

        if expected_num_objects is not None:
            expected_num_objects_validator = ceph_argparse.CephInt(range='')
            expected_num_objects_validator.valid(expected_num_objects)
            cmd['expected_num_objects'] = expected_num_objects
        return run_ceph_command(self.rados_config_file, cmd, inbuf='')

    def osd_pool_delete(self, pool, sure=None, pool2=None):
        """
        delete pool

        :param sure: list valid_range=["--yes-i-really-really-mean-it"] allowed repeats=one
        :param pool2: six.string_types
        :param pool: six.string_types allowed repeats=one
        :return: (string outbuf, string outs)
        :raise CephError: Raises CephError on command execution errors
        :raise rados.Error: Raises on rados errors
        """

        if not isinstance(pool, six.string_types):
            raise TypeError("pool is not a String")
        cmd = {'prefix': 'osd pool delete', 'pool': pool}

        if sure is not None:
            sure_validator = ceph_argparse.CephChoices(
                strings="--yes-i-really-really-mean-it")
            for s in sure:
                sure_validator.valid(s)
            cmd['sure'] = sure

        if pool2 is not None:
            if not isinstance(pool2, six.string_types):
                raise TypeError("pool2 is not a String")
            cmd['pool2'] = pool2
        return run_ceph_command(self.rados_config_file, cmd, inbuf='')

    def osd_pool_rename(self, destpool, srcpool):
        """
        rename <srcpool> to <destpool>

        :param destpool: six.string_types allowed repeats=one
        :param srcpool: six.string_types allowed repeats=one
        :return: (string outbuf, string outs)
        :raise CephError: Raises CephError on command execution errors
        :raise rados.Error: Raises on rados errors
        """

        if not isinstance(destpool, six.string_types):
            raise TypeError("destpool is not a String")
        if not isinstance(srcpool, six.string_types):
            raise TypeError("srcpool is not a String")
        cmd = {'prefix': 'osd pool rename',
               'destpool': destpool,
               'srcpool': srcpool}
        return run_ceph_command(self.rados_config_file, cmd, inbuf='')

    def osd_pool_get(self, var, pool):
        """
        get pool parameter <var>

        :param var: list valid_range=["size","min_size","crash_replay_interval","pg_num","pgp_num","crush_ruleset","hit_set_type","hit_set_period","hit_set_count","hit_set_fpp","auid","target_max_objects","target_max_bytes","cache_target_dirty_ratio","cache_target_full_ratio","cache_min_flush_age","cache_min_evict_age","erasure_code_profile","min_read_recency_for_promote","write_fadvise_dontneed"] allowed repeats=one
        :param pool: six.string_types allowed repeats=one
        :return: (string outbuf, string outs)
        :raise CephError: Raises CephError on command execution errors
        :raise rados.Error: Raises on rados errors
        """

        var_validator = ceph_argparse.CephChoices(
            strings=
            "size|min_size|crash_replay_interval|pg_num|pgp_num|crush_ruleset|hit_set_type|hit_set_period|hit_set_count|hit_set_fpp|auid|target_max_objects|target_max_bytes|cache_target_dirty_ratio|cache_target_full_ratio|cache_min_flush_age|cache_min_evict_age|erasure_code_profile|min_read_recency_for_promote|write_fadvise_dontneed")
        for s in var:
            var_validator.valid(s)
        if not isinstance(pool, six.string_types):
            raise TypeError("pool is not a String")
        cmd = {'prefix': 'osd pool get', 'var': var, 'pool': pool}
        return run_ceph_command(self.rados_config_file, cmd, inbuf='')

    def osd_pool_set(self, var, pool, val, force=None):
        """
        set pool parameter <var> to <val>

        :param force: list valid_range=["--yes-i-really-mean-it"] allowed repeats=one
        :param var: list valid_range=["size","min_size","crash_replay_interval","pg_num","pgp_num","crush_ruleset","hashpspool","nodelete","nopgchange","nosizechange","hit_set_type","hit_set_period","hit_set_count","hit_set_fpp","use_gmt_hitset","debug_fake_ec_pool","target_max_bytes","target_max_objects","cache_target_dirty_ratio","cache_target_full_ratio","cache_min_flush_age","cache_min_evict_age","auid","min_read_recency_for_promote","write_fadvise_dontneed"] allowed repeats=one
        :param pool: six.string_types allowed repeats=one
        :param val: six.string_types allowed repeats=one
        :return: (string outbuf, string outs)
        :raise CephError: Raises CephError on command execution errors
        :raise rados.Error: Raises on rados errors
        """

        var_validator = ceph_argparse.CephChoices(
            strings=
            "size|min_size|crash_replay_interval|pg_num|pgp_num|crush_ruleset|hashpspool|nodelete|nopgchange|nosizechange|hit_set_type|hit_set_period|hit_set_count|hit_set_fpp|use_gmt_hitset|debug_fake_ec_pool|target_max_bytes|target_max_objects|cache_target_dirty_ratio|cache_target_full_ratio|cache_min_flush_age|cache_min_evict_age|auid|min_read_recency_for_promote|write_fadvise_dontneed")
        for s in var:
            var_validator.valid(s)
        if not isinstance(pool, six.string_types):
            raise TypeError("pool is not a String")
        val_validator = ceph_argparse.CephString(goodchars="")
        val_validator.valid(val)
        cmd = {'prefix': 'osd pool set', 'var': var, 'pool': pool, 'val': val}

        if force is not None:
            force_validator = ceph_argparse.CephChoices(
                strings="--yes-i-really-mean-it")
            for s in force:
                force_validator.valid(s)
            cmd['force'] = force
        return run_ceph_command(self.rados_config_file, cmd, inbuf='')

    def osd_pool_set_quota(self, field, pool, val):
        """
        set object or byte limit on pool

        :param field: list valid_range=["max_objects","max_bytes"] allowed repeats=one
        :param pool: six.string_types allowed repeats=one
        :param val: six.string_types allowed repeats=one
        :return: (string outbuf, string outs)
        :raise CephError: Raises CephError on command execution errors
        :raise rados.Error: Raises on rados errors
        """

        field_validator = ceph_argparse.CephChoices(
            strings="max_objects|max_bytes")
        for s in field:
            field_validator.valid(s)
        if not isinstance(pool, six.string_types):
            raise TypeError("pool is not a String")
        val_validator = ceph_argparse.CephString(goodchars="")
        val_validator.valid(val)
        cmd = {'prefix': 'osd pool set-quota',
               'field': field,
               'pool': pool,
               'val': val}
        return run_ceph_command(self.rados_config_file, cmd, inbuf='')

    def osd_pool_get_quota(self, pool):
        """
        obtain object or byte limits for pool

        :param pool: six.string_types allowed repeats=one
        :return: (string outbuf, string outs)
        :raise CephError: Raises CephError on command execution errors
        :raise rados.Error: Raises on rados errors
        """

        if not isinstance(pool, six.string_types):
            raise TypeError("pool is not a String")
        cmd = {'prefix': 'osd pool get-quota', 'pool': pool}
        return run_ceph_command(self.rados_config_file, cmd, inbuf='')

    def osd_pool_stats(self, name=None):
        """
        obtain stats from all pools, or from specified pool

        :param name: six.string_types allowed repeats=one
        :return: (string outbuf, string outs)
        :raise CephError: Raises CephError on command execution errors
        :raise rados.Error: Raises on rados errors
        """

        cmd = {'prefix': 'osd pool stats'}

        if name is not None:
            name_validator = ceph_argparse.CephString(goodchars="")
            name_validator.valid(name)
            cmd['name'] = name
        return run_ceph_command(self.rados_config_file, cmd, inbuf='')

    def osd_utilization(self):
        """
        get basic pg distribution stats


        :return: (string outbuf, string outs)
        :raise CephError: Raises CephError on command execution errors
        :raise rados.Error: Raises on rados errors
        """

        cmd = {'prefix': 'osd utilization'}
        return run_ceph_command(self.rados_config_file, cmd, inbuf='')

    def osd_reweight_by_utilization(self,
                                    no_increasing=None,
                                    oload=None,
                                    max_change=None,
                                    max_osds=None):
        """
        reweight OSDs by utilization 
        [overload-percentage-for-consideration, default 120]

        :param no_increasing: list valid_range=["--no-increasing"] allowed repeats=one
        :param oload: int
        :param max_change: float
        :param max_osds: int
        :return: (string outbuf, string outs)
        :raise CephError: Raises CephError on command execution errors
        :raise rados.Error: Raises on rados errors
        """

        cmd = {'prefix': 'osd reweight-by-utilization'}

        if no_increasing is not None:
            no_increasing_validator = ceph_argparse.CephChoices(
                strings="--no-increasing")
            for s in no_increasing:
                no_increasing_validator.valid(s)
            cmd['no_increasing'] = no_increasing

        if oload is not None:
            oload_validator = ceph_argparse.CephInt(range='')
            oload_validator.valid(oload)
            cmd['oload'] = oload

        if max_change is not None:
            max_change_validator = ceph_argparse.CephFloat(range='')
            max_change_validator.valid(max_change)
            cmd['max_change'] = max_change

        if max_osds is not None:
            max_osds_validator = ceph_argparse.CephInt(range='')
            max_osds_validator.valid(max_osds)
            cmd['max_osds'] = max_osds
        return run_ceph_command(self.rados_config_file, cmd, inbuf='')

    def osd_test_reweight_by_utilization(self,
                                         max_osds=None,
                                         oload=None,
                                         no_increasing=None,
                                         max_change=None):
        """
        dry run of reweight OSDs by utilization 
        [overload-percentage-for-consideration, default 120]

        :param max_osds: int
        :param oload: int
        :param no_increasing: list valid_range=["--no-increasing"] allowed repeats=one
        :param max_change: float
        :return: (string outbuf, string outs)
        :raise CephError: Raises CephError on command execution errors
        :raise rados.Error: Raises on rados errors
        """

        cmd = {'prefix': 'osd test-reweight-by-utilization'}

        if max_osds is not None:
            max_osds_validator = ceph_argparse.CephInt(range='')
            max_osds_validator.valid(max_osds)
            cmd['max_osds'] = max_osds

        if oload is not None:
            oload_validator = ceph_argparse.CephInt(range='')
            oload_validator.valid(oload)
            cmd['oload'] = oload

        if no_increasing is not None:
            no_increasing_validator = ceph_argparse.CephChoices(
                strings="--no-increasing")
            for s in no_increasing:
                no_increasing_validator.valid(s)
            cmd['no_increasing'] = no_increasing

        if max_change is not None:
            max_change_validator = ceph_argparse.CephFloat(range='')
            max_change_validator.valid(max_change)
            cmd['max_change'] = max_change
        return run_ceph_command(self.rados_config_file, cmd, inbuf='')

    def osd_reweight_by_pg(self,
                           max_osds=None,
                           pools=None,
                           max_change=None,
                           oload=None):
        """
        reweight OSDs by PG distribution 
        [overload-percentage-for-consideration, default 120]

        :param max_osds: int
        :param pools: six.string_types allowed repeats=many
        :param max_change: float
        :param oload: int
        :return: (string outbuf, string outs)
        :raise CephError: Raises CephError on command execution errors
        :raise rados.Error: Raises on rados errors
        """

        cmd = {'prefix': 'osd reweight-by-pg'}

        if max_osds is not None:
            max_osds_validator = ceph_argparse.CephInt(range='')
            max_osds_validator.valid(max_osds)
            cmd['max_osds'] = max_osds

        if pools is not None:
            if not isinstance(pools, six.string_types):
                raise TypeError("pools is not a String")
            cmd['pools'] = pools

        if max_change is not None:
            max_change_validator = ceph_argparse.CephFloat(range='')
            max_change_validator.valid(max_change)
            cmd['max_change'] = max_change

        if oload is not None:
            oload_validator = ceph_argparse.CephInt(range='')
            oload_validator.valid(oload)
            cmd['oload'] = oload
        return run_ceph_command(self.rados_config_file, cmd, inbuf='')

    def osd_test_reweight_by_pg(self,
                                pools=None,
                                max_change=None,
                                max_osds=None,
                                oload=None):
        """
        dry run of reweight OSDs by PG distribution 
        [overload-percentage-for-consideration, default 120]

        :param pools: six.string_types allowed repeats=many
        :param max_change: float
        :param max_osds: int
        :param oload: int
        :return: (string outbuf, string outs)
        :raise CephError: Raises CephError on command execution errors
        :raise rados.Error: Raises on rados errors
        """

        cmd = {'prefix': 'osd test-reweight-by-pg'}

        if pools is not None:
            if not isinstance(pools, six.string_types):
                raise TypeError("pools is not a String")
            cmd['pools'] = pools

        if max_change is not None:
            max_change_validator = ceph_argparse.CephFloat(range='')
            max_change_validator.valid(max_change)
            cmd['max_change'] = max_change

        if max_osds is not None:
            max_osds_validator = ceph_argparse.CephInt(range='')
            max_osds_validator.valid(max_osds)
            cmd['max_osds'] = max_osds

        if oload is not None:
            oload_validator = ceph_argparse.CephInt(range='')
            oload_validator.valid(oload)
            cmd['oload'] = oload
        return run_ceph_command(self.rados_config_file, cmd, inbuf='')

    def osd_thrash(self, num_epochs):
        """
        thrash OSDs for <num_epochs>

        :param num_epochs: int min=0
        :return: (string outbuf, string outs)
        :raise CephError: Raises CephError on command execution errors
        :raise rados.Error: Raises on rados errors
        """

        num_epochs_validator = ceph_argparse.CephInt(range='0')
        num_epochs_validator.valid(num_epochs)
        cmd = {'prefix': 'osd thrash', 'num_epochs': num_epochs}
        return run_ceph_command(self.rados_config_file, cmd, inbuf='')

    def osd_df(self, output_method=None):
        """
        show OSD utilization

        :param output_method: list valid_range=["plain","tree"] allowed repeats=one
        :return: (string outbuf, string outs)
        :raise CephError: Raises CephError on command execution errors
        :raise rados.Error: Raises on rados errors
        """

        cmd = {'prefix': 'osd df'}

        if output_method is not None:
            output_method_validator = ceph_argparse.CephChoices(
                strings="plain|tree")
            for s in output_method:
                output_method_validator.valid(s)
            cmd['output_method'] = output_method
        return run_ceph_command(self.rados_config_file, cmd, inbuf='')

    def osd_tier_add(self, tierpool, pool, force_nonempty=None):
        """
        add the tier <tierpool> (the second one) to base pool 
        <pool> (the first one)

        :param tierpool: six.string_types allowed repeats=one
        :param pool: six.string_types allowed repeats=one
        :param force_nonempty: list valid_range=["--force-nonempty"] allowed repeats=one
        :return: (string outbuf, string outs)
        :raise CephError: Raises CephError on command execution errors
        :raise rados.Error: Raises on rados errors
        """

        if not isinstance(tierpool, six.string_types):
            raise TypeError("tierpool is not a String")
        if not isinstance(pool, six.string_types):
            raise TypeError("pool is not a String")
        cmd = {'prefix': 'osd tier add', 'tierpool': tierpool, 'pool': pool}

        if force_nonempty is not None:
            force_nonempty_validator = ceph_argparse.CephChoices(
                strings="--force-nonempty")
            for s in force_nonempty:
                force_nonempty_validator.valid(s)
            cmd['force_nonempty'] = force_nonempty
        return run_ceph_command(self.rados_config_file, cmd, inbuf='')

    def osd_tier_remove(self, tierpool, pool):
        """
        remove the tier <tierpool> (the second one) from base pool 
        <pool> (the first one)

        :param tierpool: six.string_types allowed repeats=one
        :param pool: six.string_types allowed repeats=one
        :return: (string outbuf, string outs)
        :raise CephError: Raises CephError on command execution errors
        :raise rados.Error: Raises on rados errors
        """

        if not isinstance(tierpool, six.string_types):
            raise TypeError("tierpool is not a String")
        if not isinstance(pool, six.string_types):
            raise TypeError("pool is not a String")
        cmd = {'prefix': 'osd tier remove', 'tierpool': tierpool, 'pool': pool}
        return run_ceph_command(self.rados_config_file, cmd, inbuf='')

    def osd_tier_cache_mode(self, pool, mode):
        """
        specify the caching mode for cache tier <pool>

        :param pool: six.string_types allowed repeats=one
        :param mode: list valid_range=["none","writeback","forward","readonly","readforward","readproxy"] allowed repeats=one
        :return: (string outbuf, string outs)
        :raise CephError: Raises CephError on command execution errors
        :raise rados.Error: Raises on rados errors
        """

        if not isinstance(pool, six.string_types):
            raise TypeError("pool is not a String")
        mode_validator = ceph_argparse.CephChoices(
            strings="none|writeback|forward|readonly|readforward|readproxy")
        for s in mode:
            mode_validator.valid(s)
        cmd = {'prefix': 'osd tier cache-mode', 'pool': pool, 'mode': mode}
        return run_ceph_command(self.rados_config_file, cmd, inbuf='')

    def osd_tier_set_overlay(self, pool, overlaypool):
        """
        set the overlay pool for base pool <pool> to be 
        <overlaypool>

        :param pool: six.string_types allowed repeats=one
        :param overlaypool: six.string_types allowed repeats=one
        :return: (string outbuf, string outs)
        :raise CephError: Raises CephError on command execution errors
        :raise rados.Error: Raises on rados errors
        """

        if not isinstance(pool, six.string_types):
            raise TypeError("pool is not a String")
        if not isinstance(overlaypool, six.string_types):
            raise TypeError("overlaypool is not a String")
        cmd = {'prefix': 'osd tier set-overlay',
               'pool': pool,
               'overlaypool': overlaypool}
        return run_ceph_command(self.rados_config_file, cmd, inbuf='')

    def osd_tier_remove_overlay(self, pool):
        """
        remove the overlay pool for base pool <pool>

        :param pool: six.string_types allowed repeats=one
        :return: (string outbuf, string outs)
        :raise CephError: Raises CephError on command execution errors
        :raise rados.Error: Raises on rados errors
        """

        if not isinstance(pool, six.string_types):
            raise TypeError("pool is not a String")
        cmd = {'prefix': 'osd tier remove-overlay', 'pool': pool}
        return run_ceph_command(self.rados_config_file, cmd, inbuf='')

    def osd_tier_add_cache(self, pool, size, tierpool):
        """
        add a cache <tierpool> (the second one) of size <size> to 
        existing pool <pool> (the first one)

        :param pool: six.string_types allowed repeats=one
        :param size: int min=0
        :param tierpool: six.string_types allowed repeats=one
        :return: (string outbuf, string outs)
        :raise CephError: Raises CephError on command execution errors
        :raise rados.Error: Raises on rados errors
        """

        if not isinstance(pool, six.string_types):
            raise TypeError("pool is not a String")
        size_validator = ceph_argparse.CephInt(range='0')
        size_validator.valid(size)
        if not isinstance(tierpool, six.string_types):
            raise TypeError("tierpool is not a String")
        cmd = {'prefix': 'osd tier add-cache',
               'pool': pool,
               'size': size,
               'tierpool': tierpool}
        return run_ceph_command(self.rados_config_file, cmd, inbuf='')


class MonitorCommand:
    def __init__(self, rados_config_file):
        self.rados_config_file = rados_config_file

    def compact(self):
        """
        cause compaction of monitor's leveldb storage


        :return: (string outbuf, string outs)
        :raise CephError: Raises CephError on command execution errors
        :raise rados.Error: Raises on rados errors
        """

        cmd = {'prefix': 'compact'}
        return run_ceph_command(self.rados_config_file, cmd, inbuf='')

    def scrub(self):
        """
        scrub the monitor stores


        :return: (string outbuf, string outs)
        :raise CephError: Raises CephError on command execution errors
        :raise rados.Error: Raises on rados errors
        """

        cmd = {'prefix': 'scrub'}
        return run_ceph_command(self.rados_config_file, cmd, inbuf='')

    def fsid(self):
        """
        show cluster FSID/UUID


        :return: (string outbuf, string outs)
        :raise CephError: Raises CephError on command execution errors
        :raise rados.Error: Raises on rados errors
        """

        cmd = {'prefix': 'fsid'}
        return run_ceph_command(self.rados_config_file, cmd, inbuf='')

    def log(self, logtext):
        """
        log supplied text to the monitor log

        :param logtext: six.string_types allowed repeats=many
        :return: (string outbuf, string outs)
        :raise CephError: Raises CephError on command execution errors
        :raise rados.Error: Raises on rados errors
        """

        logtext_validator = ceph_argparse.CephString(goodchars="")
        logtext_validator.valid(logtext)
        cmd = {'prefix': 'log', 'logtext': logtext}
        return run_ceph_command(self.rados_config_file, cmd, inbuf='')

    def injectargs(self, injected_args):
        """
        inject config arguments into monitor

        :param injected_args: six.string_types allowed repeats=many
        :return: (string outbuf, string outs)
        :raise CephError: Raises CephError on command execution errors
        :raise rados.Error: Raises on rados errors
        """

        injected_args_validator = ceph_argparse.CephString(goodchars="")
        injected_args_validator.valid(injected_args)
        cmd = {'prefix': 'injectargs', 'injected_args': injected_args}
        return run_ceph_command(self.rados_config_file, cmd, inbuf='')

    def status(self):
        """
        show cluster status


        :return: (string outbuf, string outs)
        :raise CephError: Raises CephError on command execution errors
        :raise rados.Error: Raises on rados errors
        """

        cmd = {'prefix': 'status'}
        return run_ceph_command(self.rados_config_file, cmd, inbuf='')

    def health(self, detail=None):
        """
        show cluster health

        :param detail: list valid_range=["detail"] allowed repeats=one
        :return: (string outbuf, string outs)
        :raise CephError: Raises CephError on command execution errors
        :raise rados.Error: Raises on rados errors
        """

        cmd = {'prefix': 'health'}

        if detail is not None:
            detail_validator = ceph_argparse.CephChoices(strings="detail")
            for s in detail:
                detail_validator.valid(s)
            cmd['detail'] = detail
        return run_ceph_command(self.rados_config_file, cmd, inbuf='')

    def df(self, detail=None):
        """
        show cluster free space stats

        :param detail: list valid_range=["detail"] allowed repeats=one
        :return: (string outbuf, string outs)
        :raise CephError: Raises CephError on command execution errors
        :raise rados.Error: Raises on rados errors
        """

        cmd = {'prefix': 'df'}

        if detail is not None:
            detail_validator = ceph_argparse.CephChoices(strings="detail")
            for s in detail:
                detail_validator.valid(s)
            cmd['detail'] = detail
        return run_ceph_command(self.rados_config_file, cmd, inbuf='')

    def report(self, tags=None):
        """
        report full status of cluster, optional title tag strings

        :param tags: six.string_types allowed repeats=many
        :return: (string outbuf, string outs)
        :raise CephError: Raises CephError on command execution errors
        :raise rados.Error: Raises on rados errors
        """

        cmd = {'prefix': 'report'}

        if tags is not None:
            tags_validator = ceph_argparse.CephString(goodchars="")
            tags_validator.valid(tags)
            cmd['tags'] = tags
        return run_ceph_command(self.rados_config_file, cmd, inbuf='')

    def quorum_status(self):
        """
        report status of monitor quorum


        :return: (string outbuf, string outs)
        :raise CephError: Raises CephError on command execution errors
        :raise rados.Error: Raises on rados errors
        """

        cmd = {'prefix': 'quorum_status'}
        return run_ceph_command(self.rados_config_file, cmd, inbuf='')

    def mon_status(self):
        """
        report status of monitors


        :return: (string outbuf, string outs)
        :raise CephError: Raises CephError on command execution errors
        :raise rados.Error: Raises on rados errors
        """

        cmd = {'prefix': 'mon_status'}
        return run_ceph_command(self.rados_config_file, cmd, inbuf='')

    def sync_force(self, validate1=None, validate2=None):
        """
        force sync of and clear monitor store

        :param validate1: list valid_range=["--yes-i-really-mean-it"] allowed repeats=one
        :param validate2: list valid_range=["--i-know-what-i-am-doing"] allowed repeats=one
        :return: (string outbuf, string outs)
        :raise CephError: Raises CephError on command execution errors
        :raise rados.Error: Raises on rados errors
        """

        cmd = {'prefix': 'sync force'}

        if validate1 is not None:
            validate1_validator = ceph_argparse.CephChoices(
                strings="--yes-i-really-mean-it")
            for s in validate1:
                validate1_validator.valid(s)
            cmd['validate1'] = validate1

        if validate2 is not None:
            validate2_validator = ceph_argparse.CephChoices(
                strings="--i-know-what-i-am-doing")
            for s in validate2:
                validate2_validator.valid(s)
            cmd['validate2'] = validate2
        return run_ceph_command(self.rados_config_file, cmd, inbuf='')

    def heap(self, heapcmd):
        """
        show heap usage info (available only if compiled with 
        tcmalloc)

        :param heapcmd: list valid_range=["dump","start_profiler","stop_profiler","release","stats"] allowed repeats=one
        :return: (string outbuf, string outs)
        :raise CephError: Raises CephError on command execution errors
        :raise rados.Error: Raises on rados errors
        """

        heapcmd_validator = ceph_argparse.CephChoices(
            strings="dump|start_profiler|stop_profiler|release|stats")
        for s in heapcmd:
            heapcmd_validator.valid(s)
        cmd = {'prefix': 'heap', 'heapcmd': heapcmd}
        return run_ceph_command(self.rados_config_file, cmd, inbuf='')

    def quorum(self, quorumcmd):
        """
        enter or exit quorum

        :param quorumcmd: list valid_range=["enter","exit"] allowed repeats=one
        :return: (string outbuf, string outs)
        :raise CephError: Raises CephError on command execution errors
        :raise rados.Error: Raises on rados errors
        """

        quorumcmd_validator = ceph_argparse.CephChoices(strings="enter|exit")
        for s in quorumcmd:
            quorumcmd_validator.valid(s)
        cmd = {'prefix': 'quorum', 'quorumcmd': quorumcmd}
        return run_ceph_command(self.rados_config_file, cmd, inbuf='')

    def tell(self, args, target):
        """
        send a command to a specific daemon

        :param args: six.string_types allowed repeats=many
        :param target: six.string_types
        :return: (string outbuf, string outs)
        :raise CephError: Raises CephError on command execution errors
        :raise rados.Error: Raises on rados errors
        """

        args_validator = ceph_argparse.CephString(goodchars="")
        args_validator.valid(args)
        target_validator = ceph_argparse.CephName()
        target_validator.valid(target)
        cmd = {'prefix': 'tell', 'args': args, 'target': target}
        return run_ceph_command(self.rados_config_file, cmd, inbuf='')

    def version(self):
        """
        show mon daemon version


        :return: (string outbuf, string outs)
        :raise CephError: Raises CephError on command execution errors
        :raise rados.Error: Raises on rados errors
        """

        cmd = {'prefix': 'version'}
        return run_ceph_command(self.rados_config_file, cmd, inbuf='')

    def mon_dump(self, epoch=None):
        """
        dump formatted monmap (optionally from epoch)

        :param epoch: int min=0
        :return: (string outbuf, string outs)
        :raise CephError: Raises CephError on command execution errors
        :raise rados.Error: Raises on rados errors
        """

        cmd = {'prefix': 'mon dump'}

        if epoch is not None:
            epoch_validator = ceph_argparse.CephInt(range='0')
            epoch_validator.valid(epoch)
            cmd['epoch'] = epoch
        return run_ceph_command(self.rados_config_file, cmd, inbuf='')

    def mon_stat(self):
        """
        summarize monitor status


        :return: (string outbuf, string outs)
        :raise CephError: Raises CephError on command execution errors
        :raise rados.Error: Raises on rados errors
        """

        cmd = {'prefix': 'mon stat'}
        return run_ceph_command(self.rados_config_file, cmd, inbuf='')

    def mon_getmap(self, epoch=None):
        """
        get monmap

        :param epoch: int min=0
        :return: (string outbuf, string outs)
        :raise CephError: Raises CephError on command execution errors
        :raise rados.Error: Raises on rados errors
        """

        cmd = {'prefix': 'mon getmap'}

        if epoch is not None:
            epoch_validator = ceph_argparse.CephInt(range='0')
            epoch_validator.valid(epoch)
            cmd['epoch'] = epoch
        return run_ceph_command(self.rados_config_file, cmd, inbuf='')

    def mon_add(self, addr, name):
        """
        add new monitor named <name> at <addr>

        :param addr: v4 or v6 addr with optional port
        :param name: six.string_types allowed repeats=one
        :return: (string outbuf, string outs)
        :raise CephError: Raises CephError on command execution errors
        :raise rados.Error: Raises on rados errors
        """

        addr_validator = ceph_argparse.CephIPAddr()
        addr_validator.valid(addr)
        name_validator = ceph_argparse.CephString(goodchars="")
        name_validator.valid(name)
        cmd = {'prefix': 'mon add', 'addr': addr, 'name': name}
        return run_ceph_command(self.rados_config_file, cmd, inbuf='')

    def mon_remove(self, name):
        """
        remove monitor named <name>

        :param name: six.string_types allowed repeats=one
        :return: (string outbuf, string outs)
        :raise CephError: Raises CephError on command execution errors
        :raise rados.Error: Raises on rados errors
        """

        name_validator = ceph_argparse.CephString(goodchars="")
        name_validator.valid(name)
        cmd = {'prefix': 'mon remove', 'name': name}
        return run_ceph_command(self.rados_config_file, cmd, inbuf='')


class AuthCommand:
    def __init__(self, rados_config_file):
        self.rados_config_file = rados_config_file

    def auth_export(self, entity=None):
        """
        write keyring for requested entity, or master keyring if 
        none given

        :param entity: six.string_types allowed repeats=one
        :return: (string outbuf, string outs)
        :raise CephError: Raises CephError on command execution errors
        :raise rados.Error: Raises on rados errors
        """

        cmd = {'prefix': 'auth export'}

        if entity is not None:
            entity_validator = ceph_argparse.CephString(goodchars="")
            entity_validator.valid(entity)
            cmd['entity'] = entity
        return run_ceph_command(self.rados_config_file, cmd, inbuf='')

    def auth_get(self, entity):
        """
        write keyring file with requested key

        :param entity: six.string_types allowed repeats=one
        :return: (string outbuf, string outs)
        :raise CephError: Raises CephError on command execution errors
        :raise rados.Error: Raises on rados errors
        """

        entity_validator = ceph_argparse.CephString(goodchars="")
        entity_validator.valid(entity)
        cmd = {'prefix': 'auth get', 'entity': entity}
        return run_ceph_command(self.rados_config_file, cmd, inbuf='')

    def auth_get_key(self, entity):
        """
        display requested key

        :param entity: six.string_types allowed repeats=one
        :return: (string outbuf, string outs)
        :raise CephError: Raises CephError on command execution errors
        :raise rados.Error: Raises on rados errors
        """

        entity_validator = ceph_argparse.CephString(goodchars="")
        entity_validator.valid(entity)
        cmd = {'prefix': 'auth get-key', 'entity': entity}
        return run_ceph_command(self.rados_config_file, cmd, inbuf='')

    def auth_print_key(self, entity):
        """
        display requested key

        :param entity: six.string_types allowed repeats=one
        :return: (string outbuf, string outs)
        :raise CephError: Raises CephError on command execution errors
        :raise rados.Error: Raises on rados errors
        """

        entity_validator = ceph_argparse.CephString(goodchars="")
        entity_validator.valid(entity)
        cmd = {'prefix': 'auth print-key', 'entity': entity}
        return run_ceph_command(self.rados_config_file, cmd, inbuf='')

    def auth_print_key_2(self, entity):
        """
        display requested key

        :param entity: six.string_types allowed repeats=one
        :return: (string outbuf, string outs)
        :raise CephError: Raises CephError on command execution errors
        :raise rados.Error: Raises on rados errors
        """

        entity_validator = ceph_argparse.CephString(goodchars="")
        entity_validator.valid(entity)
        cmd = {'prefix': 'auth print_key', 'entity': entity}
        return run_ceph_command(self.rados_config_file, cmd, inbuf='')

    def auth_list(self):
        """
        list authentication state


        :return: (string outbuf, string outs)
        :raise CephError: Raises CephError on command execution errors
        :raise rados.Error: Raises on rados errors
        """

        cmd = {'prefix': 'auth list'}
        return run_ceph_command(self.rados_config_file, cmd, inbuf='')

    def auth_import(self):
        """
        auth import: read keyring file from -i <file>


        :return: (string outbuf, string outs)
        :raise CephError: Raises CephError on command execution errors
        :raise rados.Error: Raises on rados errors
        """

        cmd = {'prefix': 'auth import'}
        return run_ceph_command(self.rados_config_file, cmd, inbuf='')

    def auth_add(self, entity, caps=None):
        """
        add auth info for <entity> from input file, or random key if 
        no " \ "input is given, and/or any caps specified in the 
        command

        :param entity: six.string_types allowed repeats=one
        :param caps: six.string_types allowed repeats=many
        :return: (string outbuf, string outs)
        :raise CephError: Raises CephError on command execution errors
        :raise rados.Error: Raises on rados errors
        """

        entity_validator = ceph_argparse.CephString(goodchars="")
        entity_validator.valid(entity)
        cmd = {'prefix': 'auth add', 'entity': entity}

        if caps is not None:
            caps_validator = ceph_argparse.CephString(goodchars="")
            caps_validator.valid(caps)
            cmd['caps'] = caps
        return run_ceph_command(self.rados_config_file, cmd, inbuf='')

    def auth_get_or_create_key(self, entity, caps=None):
        """
        get, or add, key for <name> from system/caps pairs 
        specified in the command. If key already exists, any given caps must 
        match the existing caps for that key.

        :param caps: six.string_types allowed repeats=many
        :param entity: six.string_types allowed repeats=one
        :return: (string outbuf, string outs)
        :raise CephError: Raises CephError on command execution errors
        :raise rados.Error: Raises on rados errors
        """

        entity_validator = ceph_argparse.CephString(goodchars="")
        entity_validator.valid(entity)
        cmd = {'prefix': 'auth get-or-create-key', 'entity': entity}

        if caps is not None:
            caps_validator = ceph_argparse.CephString(goodchars="")
            caps_validator.valid(caps)
            cmd['caps'] = caps
        return run_ceph_command(self.rados_config_file, cmd, inbuf='')

    def auth_get_or_create(self, entity, caps=None):
        """
        add auth info for <entity> from input file, or random key if 
        no input given, and/or any caps specified in the command

        :param caps: six.string_types allowed repeats=many
        :param entity: six.string_types allowed repeats=one
        :return: (string outbuf, string outs)
        :raise CephError: Raises CephError on command execution errors
        :raise rados.Error: Raises on rados errors
        """

        entity_validator = ceph_argparse.CephString(goodchars="")
        entity_validator.valid(entity)
        cmd = {'prefix': 'auth get-or-create', 'entity': entity}

        if caps is not None:
            caps_validator = ceph_argparse.CephString(goodchars="")
            caps_validator.valid(caps)
            cmd['caps'] = caps
        return run_ceph_command(self.rados_config_file, cmd, inbuf='')

    def auth_caps(self, entity, caps):
        """
        update caps for <name> from caps specified in the command

        :param entity: six.string_types allowed repeats=one
        :param caps: six.string_types allowed repeats=many
        :return: (string outbuf, string outs)
        :raise CephError: Raises CephError on command execution errors
        :raise rados.Error: Raises on rados errors
        """

        entity_validator = ceph_argparse.CephString(goodchars="")
        entity_validator.valid(entity)
        caps_validator = ceph_argparse.CephString(goodchars="")
        caps_validator.valid(caps)
        cmd = {'prefix': 'auth caps', 'entity': entity, 'caps': caps}
        return run_ceph_command(self.rados_config_file, cmd, inbuf='')

    def auth_del(self, entity):
        """
        delete all caps for <name>

        :param entity: six.string_types allowed repeats=one
        :return: (string outbuf, string outs)
        :raise CephError: Raises CephError on command execution errors
        :raise rados.Error: Raises on rados errors
        """

        entity_validator = ceph_argparse.CephString(goodchars="")
        entity_validator.valid(entity)
        cmd = {'prefix': 'auth del', 'entity': entity}
        return run_ceph_command(self.rados_config_file, cmd, inbuf='')


class ConfigKeyCommand:
    def __init__(self, rados_config_file):
        self.rados_config_file = rados_config_file

    def config_key_get(self, key):
        """
        get <key>

        :param key: six.string_types allowed repeats=one
        :return: (string outbuf, string outs)
        :raise CephError: Raises CephError on command execution errors
        :raise rados.Error: Raises on rados errors
        """

        key_validator = ceph_argparse.CephString(goodchars="")
        key_validator.valid(key)
        cmd = {'prefix': 'config-key get', 'key': key}
        return run_ceph_command(self.rados_config_file, cmd, inbuf='')

    def config_key_put(self, key, val=None):
        """
        put <key>, value <val>

        :param key: six.string_types allowed repeats=one
        :param val: six.string_types allowed repeats=one
        :return: (string outbuf, string outs)
        :raise CephError: Raises CephError on command execution errors
        :raise rados.Error: Raises on rados errors
        """

        key_validator = ceph_argparse.CephString(goodchars="")
        key_validator.valid(key)
        cmd = {'prefix': 'config-key put', 'key': key}

        if val is not None:
            val_validator = ceph_argparse.CephString(goodchars="")
            val_validator.valid(val)
            cmd['val'] = val
        return run_ceph_command(self.rados_config_file, cmd, inbuf='')

    def config_key_del(self, key):
        """
        delete <key>

        :param key: six.string_types allowed repeats=one
        :return: (string outbuf, string outs)
        :raise CephError: Raises CephError on command execution errors
        :raise rados.Error: Raises on rados errors
        """

        key_validator = ceph_argparse.CephString(goodchars="")
        key_validator.valid(key)
        cmd = {'prefix': 'config-key del', 'key': key}
        return run_ceph_command(self.rados_config_file, cmd, inbuf='')

    def config_key_exists(self, key):
        """
        check for <key>'s existence

        :param key: six.string_types allowed repeats=one
        :return: (string outbuf, string outs)
        :raise CephError: Raises CephError on command execution errors
        :raise rados.Error: Raises on rados errors
        """

        key_validator = ceph_argparse.CephString(goodchars="")
        key_validator.valid(key)
        cmd = {'prefix': 'config-key exists', 'key': key}
        return run_ceph_command(self.rados_config_file, cmd, inbuf='')

    def config_key_list(self):
        """
        list keys


        :return: (string outbuf, string outs)
        :raise CephError: Raises CephError on command execution errors
        :raise rados.Error: Raises on rados errors
        """

        cmd = {'prefix': 'config-key list'}
        return run_ceph_command(self.rados_config_file, cmd, inbuf='')
