# -*- coding: utf-8 -*-

# Import Python libs
from __future__ import absolute_import
import textwrap

# Import Salt Testing Libs
from tests.support.mixins import LoaderModuleMockMixin
from tests.support.unit import skipIf, TestCase
from tests.support.mock import (
    NO_MOCK,
    NO_MOCK_REASON,
    MagicMock,
    patch)

# Import Salt Libs
import salt.modules.pkgng as pkgng


@skipIf(NO_MOCK, NO_MOCK_REASON)
class PkgNgTestCase(TestCase, LoaderModuleMockMixin):
    '''
    Test cases for salt.modules.pkgng
    '''

    @classmethod
    def setup_loader_modules(cls):
        return {
            pkgng: {
                '__salt__': {}
            }
        }

    def test_lock(self):
        '''
        Test pkgng.lock
        '''
        lock_cmd = MagicMock(return_value={
            'stdout': ('pkga-1.0\n'
                       'pkgb-2.0\n'),
            'retcode': 0
        })
        with patch.dict(pkgng.__salt__, {'cmd.run_all': lock_cmd}):

            result = pkgng.lock('pkga')
            self.assertTrue(result)
            lock_cmd.assert_called_with(
                ['pkg', 'lock', '-y', '--quiet', '--show-locked', 'pkga'],
                output_loglevel='trace', python_shell=False
            )

            result = pkgng.lock('dummy')
            self.assertFalse(result)
            lock_cmd.assert_called_with(
                ['pkg', 'lock', '-y', '--quiet', '--show-locked', 'dummy'],
                output_loglevel='trace', python_shell=False
            )

    def test_unlock(self):
        '''
        Test pkgng.unlock
        '''
        unlock_cmd = MagicMock(return_value={
            'stdout': ('pkga-1.0\n'
                       'pkgb-2.0\n'),
            'retcode': 0
        })
        with patch.dict(pkgng.__salt__, {'cmd.run_all': unlock_cmd}):

            result = pkgng.unlock('pkga')
            self.assertFalse(result)
            unlock_cmd.assert_called_with(
                ['pkg', 'unlock', '-y', '--quiet', '--show-locked', 'pkga'],
                output_loglevel='trace', python_shell=False
            )

            result = pkgng.unlock('dummy')
            self.assertTrue(result)
            unlock_cmd.assert_called_with(
                ['pkg', 'unlock', '-y', '--quiet', '--show-locked', 'dummy'],
                output_loglevel='trace', python_shell=False
            )

    def test_locked(self):
        '''
        Test pkgng.unlock
        '''
        lock_cmd = MagicMock(return_value={
            'stdout': ('pkga-1.0\n'
                       'pkgb-2.0\n'),
            'retcode': 0
        })
        with patch.dict(pkgng.__salt__, {'cmd.run_all': lock_cmd}):

            result = pkgng.locked('pkga')
            self.assertTrue(result)
            lock_cmd.assert_called_with(
                ['pkg', 'lock', '-y', '--quiet', '--show-locked'],
                output_loglevel='trace', python_shell=False
            )

            result = pkgng.locked('dummy')
            self.assertFalse(result)
            lock_cmd.assert_called_with(
                ['pkg', 'lock', '-y', '--quiet', '--show-locked'],
                output_loglevel='trace', python_shell=False
            )

    def test_list_upgrades_present(self):
        '''
        Test pkgng.list_upgrades with upgrades available
        '''
        pkg_cmd = MagicMock(return_value=textwrap.dedent(
            """
            The following 6 package(s) will be affected (of 0 checked):

            New packages to be INSTALLED:
                    pkge: 5.0 [FreeBSD]
                    pkgf: 6.0 [FreeBSD]

            Installed packages to be UPGRADED:
                    pkga: 1.0 -> 1.1 [FreeBSD]
                    pkgb: 2.0 -> 2.1 [FreeBSD]

            Installed packages to be REINSTALLED:
                    pkgc-3.0 [FreeBSD] (direct dependency changed: pkga)
                    pkgd-4.0 [FreeBSD] (direct dependency changed: pkgb)

            Number of packages to be upgraded: 2
            Number of packages to be reinstalled: 2

            The process will require 14 MiB more space.
            22 MiB to be downloaded.
            """
        ))

        with patch.dict(pkgng.__salt__, {'cmd.run_stdout': pkg_cmd}):

            result = pkgng.list_upgrades(refresh=False)
            self.assertDictEqual(result, {'pkga': '1.1', 'pkgb': '2.1'})
            pkg_cmd.assert_called_with(
                ['pkg', 'upgrade', '--dry-run', '--quiet', '--no-repo-update'],
                output_loglevel='trace', python_shell=False, ignore_retcode=True
            )

    def test_list_upgrades_absent(self):
        '''
        Test pkgng.list_upgrades with no upgrades available
        '''
        pkg_cmd = MagicMock(return_value='')

        with patch.dict(pkgng.__salt__, {'cmd.run_stdout': pkg_cmd}):
            result = pkgng.list_upgrades(refresh=False)
            self.assertDictEqual(result, {})
            pkg_cmd.assert_called_with(
                ['pkg', 'upgrade', '--dry-run', '--quiet', '--no-repo-update'],
                output_loglevel='trace', python_shell=False, ignore_retcode=True
            )
