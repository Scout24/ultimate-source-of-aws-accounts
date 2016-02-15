from pybuilder.core import use_plugin, init

use_plugin("python.core")
use_plugin("python.unittest")
use_plugin("python.install_dependencies")
use_plugin("python.flake8")
use_plugin("python.coverage")
use_plugin("python.distutils")
use_plugin('copy_resources')
use_plugin("filter_resources")
use_plugin('python.cram')


name = "ultimate-source-of-accounts"
description = "Upload information about your AWS accounts to an S3 bucket"
default_task = ["clean", "analyze", "run_cram_tests"]
version = '1.1'


@init
def set_properties(project):
    project.set_property('install_dependencies_upgrade', True)
    project.build_depends_on("unittest2")
    project.build_depends_on("moto")
    project.build_depends_on("mock")
    project.depends_on("yamlreader")
    project.depends_on("pyyaml")
    project.depends_on("boto")
    project.depends_on("boto3")
    project.depends_on("docopt")
    project.depends_on("six")
    # unittest-xml-reporting version 2.0 dropped support for Python 2.6. Use
    # an older version to make the build work on RHEL 6.
    project.depends_on("unittest-xml-reporting<2.0.0")

    project.set_property('distutils_console_scripts', ['ultimate-source-of-accounts=ultimate_source_of_accounts.cli:main'])
    project.set_property('flake8_break_build', True)


@init(environments='teamcity')
def set_properties_for_teamcity_builds(project):
    import os
    project.set_property('teamcity_output', True)
    project.version = '%s-%s' % (project.version,
                                 os.environ.get('BUILD_NUMBER', 0))
    project.default_task = ['clean', 'install_build_dependencies', 'publish']
    project.set_property('install_dependencies_index_url',
                         os.environ.get('PYPIPROXY_URL'))
    project.rpm_release = os.environ.get('RPM_RELEASE', 0)
    project.set_property('copy_resources_target', '$dir_dist')
    project.get_property('copy_resources_glob').extend(['setup.cfg'])
    project.get_property('filter_resources_glob').extend(['**/setup.cfg'])
