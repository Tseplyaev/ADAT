from aiida_fleur.workflows.base_fleur import FleurBaseWorkChain

def clear_used_remote(node):
    '''
    Removes the content of Remote folders

    :param node: AiiDA process that
    '''
    for nested in node.get_outgoing().all():
        try:
            proc_node = nested.node
            process_class = proc_node.process_class
        except AttributeError:
            continue

        if process_class is FleurBaseWorkChain and proc_node.is_finished:
            out_remote = proc_node.outputs.remote_folder.get_outgoing().all()
            classes = [x.link_label for x in out_remote]

            if ['parent_folder', 'parent_folder', 'remote_data'] == sorted(classes):
                remote_to_clear = proc_node.outputs.remote_folder
                remote_to_clear._clean()
                print('Remote folder cleared for {}'.format(remote_to_clear.pk))
            else:
                print('{} is the last iteration or was reused by another node, I will keep it'.format(proc_node.pk))
        else:
            clear_used_remote(proc_node)
