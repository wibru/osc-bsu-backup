import argparse
import logging
import osc_bsu_backup.bsu_backup as bsu_backup
from osc_bsu_backup.utils import setup_logging

from osc_bsu_backup import __version__

logger = setup_logging(__name__)


def backup(args):
    conn = bsu_backup.auth(args.profile, args.region, args.endpoint)

    if args.instance_id:
        res = bsu_backup.find_instance_by_id(conn, args.instance_id)
    elif args.instances_tags:
        res = bsu_backup.find_instances_by_tags(conn, args.instances_tags)
    elif args.volume_id:
        res = bsu_backup.find_volume_by_id(conn, args.volume_id)
    elif args.volumes_tags:
        res = bsu_backup.find_volumes_by_tags(conn, args.volumes_tags)

    if res:
        bsu_backup.rotate_snapshots(conn, res, args.rotate)
        bsu_backup.create_snapshots(conn, res)

    return True


def main():
    logger.info("osc_bsu_backup: %s", __version__)

    parser = argparse.ArgumentParser(
        description="osc-ebs-backup: {}".format(__version__)
    )
    parser.add_argument(
        "--instance-by-id",
        dest="instance_id",
        action="store",
        help="instance to backup",
    )
    parser.add_argument(
        "--instances-by-tags",
        dest="instances_tags",
        action="store",
        help="instances tags to look for, use the format Key:Value",
    )
    parser.add_argument(
        "--volume-by-id", dest="volume_id", action="store", help="volume to backup",
    )
    parser.add_argument(
        "--volumes-by-tags",
        dest="volumes_tags",
        action="store",
        help="volumes tags to look for, use the format Key:Value",
    )
    parser.add_argument(
        "--rotate",
        dest="rotate",
        type=int,
        action="store",
        default=10,
        help="retention for snapshot",
    )
    parser.add_argument(
        "--region", dest="region", action="store", default="eu-west-2", help="region"
    )
    parser.add_argument(
        "--endpoint", dest="endpoint", default=None, action="store", help="endpoint"
    )
    parser.add_argument(
        "--profile",
        dest="profile",
        action="store",
        default="default",
        help="aws profile to use, ~/.aws/credentials",
    )
    parser.add_argument(
        "--debug", dest="debug", action="store_true", default=False, help="enable debug"
    )
    args = parser.parse_args()

    if args.instances_tags and len(args.instances_tags.split(":")) != 2:
        parser.error(
            "please use the format Key:Value for tags: --instances-by-tags Name:vm-1"
        )
    elif args.volumes_tags and len(args.volumes_tags.split(":")) != 2:
        parser.error(
            "please use the format Key:Value for tags: --volumes-by-tags Name:vm-1"
        )
    elif (
        not args.instance_id
        and not args.instances_tags
        and not args.volume_id
        and not args.volumes_tags
    ):
        parser.error(
            "please use --instance-by-id or --instances-by-tags or --volume-by-id or --volumes-by-tags"
        )

    if args.debug:
        setup_logging(level=logging.DEBUG)

    return backup(args)


if __name__ == "__main__":
    main()
