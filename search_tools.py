from aiida.orm import CalcJobNode, load_node
from aiida.orm.querybuilder import QueryBuilder
from aiida_fleur.calculation.fleur import FleurCalculation


def find_nested_calcjob(wc_node):
    '''
    This function finds all nested child FleurCalculations of the workchain
    '''
    child_fleurcalcs = []
    lower = wc_node.get_outgoing().all()
    for i in lower:
        if 'CALL' in i.link_label:
            if i.node.process_class is FleurCalculation:
                child_fleurcalcs.append(i.node)
            else:
                child_fleurcalcs.extend(find_nested_calcjob(i.node))
    return child_fleurcalcs

def request_calcjobs():
    '''
    Returns the total number of running CalcJobs
    '''
    qb = QueryBuilder()
    qb.append(
        CalcJobNode,                 # I am appending a CalcJobNode
        filters={                       # Specifying the filters:
            'attributes.process_state':{'in':['created', 'running', 'waiting']},  # the calculation has to be finished
        },
    )
    return len(qb.all())


def get_iterations_from_pk(wc_node):
    '''Prints out the total number of relaxation steps'''
    pk_last = max(find_nested_calcjob(wc_node))
    last_calcjob = load_node(pk_last)
    if 'relax_parameters' not in last_calcjob.outputs:
        return None
    total_energies = last_calcjob.outputs.relax_parameters.get_dict()['energies']
    return len(total_energies)