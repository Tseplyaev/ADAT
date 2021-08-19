from aiida.orm import CalcJobNode, load_node
from aiida.orm.querybuilder import QueryBuilder
from aiida.common.exceptions import NotExistent

from aiida_fleur.calculation.fleur import FleurCalculation


def find_nested_process(wc_node, p_class):
    '''
    This function finds all nested child FleurCalculations of the workchain
    '''
    child_fleurcalcs = []
    lower = wc_node.get_outgoing().all()
    for i in lower:
	try:
        if 'CALL' in i.link_label:
                if i.node.process_class is p_class:
                    child_fleurcalcs.append(i.node)
                else:
                    child_fleurcalcs.extend(find_nested_process(i.node, p_class))
	except AttributeError:
            pass
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
    pk_last = max(find_nested_process(wc_node, FleurCalculation))
    last_calcjob = load_node(pk_last)
    if 'relax_parameters' not in last_calcjob.outputs:
        return None
    total_energies = last_calcjob.outputs.relax_parameters.get_dict()['energies']
    return len(total_energies)

def get_remote_by_node(node, check_if_successfull=True):
    ''' Finds the remote folder of the last FleurCalculation'''
    if not node.is_finished_ok and check_if_successfull:
        return None

    calcjob_pks = [x.pk for x in find_nested_process(node, FleurCalculation)]
    last_fleur = load_node(max(calcjob_pks))

    try:
        remote = last_fleur.get_outgoing().get_node_by_label('remote_folder')
    except NotExistent:
        return None

    return remote
