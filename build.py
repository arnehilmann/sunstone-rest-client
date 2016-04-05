from pybuilder.core import use_plugin, init, Author, task

use_plugin("python.core")
use_plugin("python.unittest")
use_plugin("python.install_dependencies")
use_plugin("python.flake8")
use_plugin("python.coverage")
use_plugin("python.distutils")
use_plugin('copy_resources')
use_plugin('filter_resources')

name = "sunstone-rest-client"
version = '0.1.0'

default_task = ["clean", "analyze", "publish"]

authors = [Author('Arne Hilmann', 'arne.hilmann@gmail.com')]
summary = 'sunstone rest client | an opennebula client in python, using the sunstone ReST API'
description = """sunstone rest client

an opennebula client in python, using the sunstone ReST API
instead of the XML-RPC
"""
url = 'https://github.com/arnehilmann/sunstone-rest-client'
license = 'Apache License v2.0'


@task
def gittag(project, logger):
    logger.info("The following commands create a new release, triggering all the fun stuff:")
    logger.info("git tag -a v{0} -m v{0}".format(project.version))
    logger.info("git push --tags")


@init
def set_properties(project):
    project.build_depends_on('mock')
    project.build_depends_on('testfixtures')

    project.depends_on("requests")
    project.depends_on("bs4")

    project.set_property('coverage_threshold_warn', 75)
    project.set_property('coverage_break_build', True)

    project.set_property('flake8_verbose_output', True)
    project.set_property('flake8_include_test_sources', True)
    project.set_property('flake8_ignore', 'E501,E402,E731')
    project.set_property('flake8_break_build', True)

    project.set_property('copy_resources_target', '$dir_dist')
    project.get_property('copy_resources_glob').append('setup*.cfg')
    project.get_property('filter_resources_glob').extend(['**/setup*.cfg'])
