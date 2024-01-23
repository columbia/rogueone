signature_lists = {
        'os_command': [
            "sink_hqbpillvul_execFile",
            'sink_hqbpillvul_exec',
            'sink_hqbpillvul_execSync',
            'sink_hqbpillvul_spawn',
            'sink_hqbpillvul_spawnSync'
            ],
        'xss': [
            'sink_hqbpillvul_http_write',
            'sink_hqbpillvul_http_setHeader'
            ],
        'proto_pollution': [
            'merge', 'extend', 'clone', 'parse'
            ],
        'code_exec': [
            'Function',
            'eval',
            # "sink_hqbpillvul_execFile",
            # 'sink_hqbpillvul_exec',
            # 'sink_hqbpillvul_execSync',
            'sink_hqbpillvul_eval'
            ],
        'nosql': [
            'sink_hqbpillvul_nosql'
            ],
        'sanitation': [
            'parseInt'
            ],
        'path_traversal': [
            'pipe',
            'sink_hqbpillvul_http_write'
            ],
        'data_flow': ['sink_hqbpillvul_http_write', 'sink_hqbpillvul_db', 'sink_hqbpillvul_exec', 'sink_hqbpillvul_execFileSync', 'sink_hqbpillvul_execSync', 'extend', 'sink_hqbpillvul_spawnSync', 'Function', 'sink_hqbpillvul_execFile', 'eval', 'sink_hqbpillvul_pp', 'sink_hqbpillvul_code_execution', 'merge', 'pipe', 'sink_hqbpillvul_eval',  'sink_hqbpillvul_http_setHeader', 'sink_hqbpillvul_http_sendFile', 'sink_hqbpillvul_spawn']
}
signature_type_map = {
'sink_hqbpillvul_http_write': 'sys:backend:net:write',
'sink_hqbpillvul_exec': 'sys:backend:process:exec',
'sink_hqbpillvul_execFileSync': 'sys:backend:process:execFileSync',
'sink_hqbpillvul_execSync': 'sys:backend:process:execSync',
'extend': 'sys:lang:proto:extend',
'sink_hqbpillvul_spawnSync': 'sys:backend:process:spawnSync',
'Function': 'sys:lang:core:Function',
'sink_hqbpillvul_execFile': 'sys:backend:process:execFile',
'eval': 'sys:lang:core:eval',
'merge': 'sys:lang:proto:merge',
'pipe': 'sys:lang:proto:pipe',
'sink_hqbpillvul_eval': 'sys:lang:core:evalSink',
 'sink_hqbpillvul_http_setHeader': 'sys:backend:net:setHeader',
'sink_hqbpillvul_http_sendFile': 'sys:backend:net:sendFile',
'sink_hqbpillvul_spawn':'sys:backend:process:spawn',
}

def get_all_sign_list():
    """
    return a list of all the signature functions
    """
    res = []
    for key in signature_lists:
        res += signature_lists[key]

    return res

