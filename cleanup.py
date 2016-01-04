#!/usr/bin/python

import click
import os
import sys

@click.command()
@click.option('--cluster-id', default='demo', show_default=True,
              help='cluster identifier')
@click.option('--region', default='us-east-1', help='ec2 region',
              show_default=True)
@click.option('--r53-zone', prompt=True,
              help='route53 hosted zone')
@click.option('--app-dns-prefix', default='apps', help='application dns prefix',
              show_default=True)
@click.option('--rhsm-user', prompt=True, help='Red Hat Subscription Management User')
@click.option('--rhsm-pass', prompt=True, hide_input=True,
              help='Red Hat Subscription Management Password')
@click.option('--no-confirm', is_flag=True,
              help='Skip confirmation prompt')
@click.help_option('--help', '-h')
@click.option('-v', '--verbose', count=True)
def cleanup(region=None, r53_zone=None, cluster_id=None, app_dns_prefix=None,
            rhsm_user=None, rhsm_pass=None, no_confirm=False, verbose=0):
    click.echo("This script will cleanup the following items for the "
               "{0} environment in {1}:".format(cluster_id, region))
    click.echo('\tVPC')
    click.echo('\tSecurity Groups')
    click.echo('\tElastic Load Balancers')
    click.echo('\tLaunch Configs')
    click.echo('\tAuto Scaling Groups')
    click.echo('\tDNS entries in the following r53_zone: %s' % r53_zone)

    click.echo('\trhsm_user: %s' % rhsm_user)
    click.echo('\trhsm_pass: *******')

    host_zone="%s.%s" % (cluster_id, r53_zone)
    wildcard_zone="%s.%s.%s" % (app_dns_prefix, cluster_id, r53_zone)

    click.echo('Host DNS entries will be created under the %s domain' % host_zone)
    click.echo('Application wildcard zone for this env will be %s' % wildcard_zone)

    if not no_confirm and not click.confirm('Continue using these values?'):
        sys.exit(0)

    # refresh the inventory cache to prevent stale hosts from
    # interferring with re-running
    command='inventory/aws/hosts/ec2.py --refresh-cache'
    os.system(command)

    # remove any cached facts to prevent stale data during a re-run
    command='rm -rf .ansible/cached_facts'
    os.system(command)

    command='ansible-playbook -i inventory/aws/hosts -e \'cluster_id=%s ec2_region=%s r53_zone=%s r53_host_zone=%s r53_wildcard_zone=%s rhsm_user=%s rhsm_pass=%s\' playbooks/cleanup.yml' % (cluster_id, region, r53_zone, host_zone, wildcard_zone, rhsm_user, rhsm_pass)

    if verbose > 0:
        command += " -" + "".join(['v']*verbose)

    status = os.system(command)
    if os.WIFEXITED(status) and os.WEXITSTATUS(status) != 0:
        return os.WEXITSTATUS(status)

if __name__ == '__main__':
    cleanup(auto_envvar_prefix='OSE_DEMO')
