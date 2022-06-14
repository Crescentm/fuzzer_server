import configparser


FUZZER_CONFIG = configparser.ConfigParser()
FUZZER_CONFIG.read('config.ini')

# geth settings
GETH_HTTP_URL = FUZZER_CONFIG['geth'].get('http_url', 'http://localhost:8545')


# fuzzer settings
NEW_TEST_ACCOUNT = FUZZER_CONFIG['fuzzer'].getboolean('new_test_account', False)
MYSQL_CONFIG = FUZZER_CONFIG['mysql']

NFS_PATH = FUZZER_CONFIG['fuzzer'].get('nfs_path', '/opt/faint')
JOB_SUB_PATH = FUZZER_CONFIG['fuzzer'].get('job_sub_path', 'job/')
RUN_LOCAL = FUZZER_CONFIG['fuzzer'].getboolean('run_local', True)

# job settings
ABI_PATH = FUZZER_CONFIG['job'].get('abi_path', 'src/')
BIN_PATH = FUZZER_CONFIG['job'].get('bin_path', 'src/')
