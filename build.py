from pybuilder.core import use_plugin, init

use_plugin("python.core")
use_plugin("python.unittest")
use_plugin("python.install_dependencies")
use_plugin("python.flake8")
use_plugin("python.coverage")
use_plugin("python.distutils")
use_plugin('python.cram')


name = "ultimate-source-of-accounts"
default_task = ["clean", "analyze", "run_cram_tests"]


@init
def set_properties(project):
    project.set_property('install_dependencies_upgrade', True)
    project.build_depends_on("unittest2")
    project.build_depends_on("moto")
    project.depends_on("yamlreader")
    project.depends_on("pyyaml")
    project.depends_on("mock")
    project.depends_on("boto")
    project.depends_on("docopt")

    project.set_property('distutils_console_scripts', ['usofa=ultimate-source-of-accounts.cli:main'])
