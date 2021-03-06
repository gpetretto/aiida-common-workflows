# -*- coding: utf-8 -*-
"""Module with pre-defined options and defaults for CLI command parameters."""
import click

from aiida.cmdline.params import options, types
from aiida_common_workflows.workflows.relax import RelaxType


def get_workchain_plugins():
    """Return the registered entry point names for the ``CommonRelaxWorkChain``."""
    from aiida.plugins import entry_point
    group = 'aiida.workflows'
    entry_point_prefix = 'common_workflows.relax.'
    names = entry_point.get_entry_point_names(group)
    return {name[len(entry_point_prefix):] for name in names if name.startswith(entry_point_prefix)}


def get_relax_types():
    """Return the relaxation types available for the common relax workflow."""
    return [entry.value for entry in RelaxType]


def get_structure():
    """Return a `StructureData` representing bulk silicon.

    The database will first be queried for the existence of a bulk silicon crystal. If this is not the case, one is
    created and stored. This function should be used as a default for CLI options that require a `StructureData` node.
    This way new users can launch the command without having to construct or import a structure first. This is the
    reason that we hardcode a bulk silicon crystal to be returned. More flexibility is not required for this purpose.

    :return: a `StructureData` representing bulk silicon
    """
    from ase.spacegroup import crystal
    from aiida.orm import QueryBuilder, StructureData

    # Filters that will match any elemental Silicon structure with 2 or less sites in total
    filters = {
        'attributes.sites': {
            'of_length': 2
        },
        'attributes.kinds': {
            'of_length': 1
        },
        'attributes.kinds.0.symbols.0': 'Si'
    }

    builder = QueryBuilder().append(StructureData, filters=filters)
    results = builder.first()

    if not results:
        alat = 5.43
        ase_structure = crystal(
            'Si',
            [(0, 0, 0)],
            spacegroup=227,
            cellpar=[alat, alat, alat, 90, 90, 90],
            primitive_cell=True,
        )
        structure = StructureData(ase=ase_structure)
        structure.store()
    else:
        structure = results[0]

    return structure.uuid


STRUCTURE = options.OverridableOption(
    '-S',
    '--structure',
    type=types.DataParamType(sub_classes=('aiida.data:structure',)),
    default=get_structure,
    help='A structure data node.'
)

PROTOCOL = options.OverridableOption(
    '-p',
    '--protocol',
    type=click.Choice(['fast', 'moderate', 'precise']),
    default='fast',
    show_default=True,
    help='Select the protocol with which the inputs for the workflow should be generated.'
)

RELAXATION_TYPE = options.OverridableOption(
    '-r',
    '--relaxation-type',
    type=types.LazyChoice(get_relax_types),
    default='atoms',
    show_default=True,
    callback=lambda ctx, value: RelaxType(value),
    help='Select the relaxation type with which the workflow should be run.'
)

THRESHOLD_FORCES = options.OverridableOption(
    '--threshold-forces',
    type=click.FLOAT,
    required=False,
    help='Optional convergence threshold for the forces. Note that not all plugins may support this option.'
)

THRESHOLD_STRESS = options.OverridableOption(
    '--threshold-stress',
    type=click.FLOAT,
    required=False,
    help='Optional convergence threshold for the stress. Note that not all plugins may support this option.'
)

DAEMON = options.OverridableOption(
    '-d',
    '--daemon',
    is_flag=True,
    default=False,
    help='Submit the process to the daemon instead of running it locally.'
)

WALLCLOCK_SECONDS = options.OverridableOption(
    '-w',
    '--wallclock-seconds',
    cls=options.MultipleValueOption,
    metavar='VALUES',
    required=False,
    help='Define the wallclock seconds to request for each engine step.'
)

NUMBER_MACHINES = options.OverridableOption(
    '-m',
    '--number-machines',
    cls=options.MultipleValueOption,
    metavar='VALUES',
    required=False,
    help='Define the number of machines to request for each engine step.'
)
