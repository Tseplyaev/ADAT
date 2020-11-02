from aiida.plugins import DataFactory
from aiida.engine import calcfunction as cf
from aiida.engine import submit

from aiida_fleur.workflows.create_magnetic_film import FleurCreateMagneticWorkChain

StructureData = DataFactory('structure')

@cf
def generate_labeled_structure(structure_input, label='451'):
    '''
    Adds the label name to the last site in the structure
    '''

    structure = StructureData(cell=structure_input.cell)
    sites = structure_input.sites

    for i, site in enumerate(sites):
        if i + 1 == len(sites):
            structure.append_atom(position=site.position, symbols=site.kind_name, name=(site.kind_name + label))
        else:
            structure.append_atom(position=site.position, symbols=site.kind_name, name=site.kind_name)

    structure.pbc = (True, True, False)

    return structure

def redo_create_magnetic(optimized_structure, total_number_layers=13, num_relaxed_layers=6):
    ''' Submits another CreateMagnetic workchain to generate a structure with the same relaxations '''

    wf_para = {
        'total_number_layers': total_number_layers,
        'num_relaxed_layers': num_relaxed_layers
    }
    wf_para = Dict(dict=wf_para)

    inputs = {
        'wf_parameters': wf_para,
        'optimized_structure': optimized_structure
    }

    res = submit(FleurCreateMagneticWorkChain, **inputs)
    film_name = optimized_structure.get_formula()
    res.label = film_name
    return (res.uuid)

