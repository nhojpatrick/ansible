#!/usr/bin/python

# Copyright: (c) 2018, Terry Jones <terry.jones@example.org>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'community'
}

DOCUMENTATION = '''
---
module: nexus_blob_store

short_description: Create pr Delete Nexus Blob Store

version_added: "2.9"

description:
    - "Create or Delete Nexus Blob Store, only supports \'File\' type at the moment"

options:
    store_name:
        description:
            - This name of blob store
        type: str
        required: true
    store_type:
        description:
            - This type of blob store, e.g. File or S3.
              Currently only File is supported
        type: str
        default: File
        required: false
        choices: [ File ]
    exists:
        description:
            - This state of blob store, i.e. absent or present
        type: bool
        default: True
        required: false
    host:
        description:
            - Nexus Repository host
        type: str
        required: true
    api_endpoint:
        description:
            - Nexus Repository API endpoint
        type: str
        default: /service/rest/v1/blobstores
        required: false
    nexus_username:
        description:
            - Nexus Username
        type: str
        required: true
    nexus_password:
        description:
            - Nexus Password
        type: str
        required: true
    file_store_path:
        description:
            - File blob store path, store_name automatically appended
              Required if store_type is File
        type: str
        default: /opt/sonatype/sonatype-work/nexus3/blobs
        required: false

extends_documentation_fragment:
    - azure

author:
    - Your Name (@yourhandle)
'''



  #- name: Delete new Blob Store
  #  nexus_blob_store:
  #    store_name: 'alpha'
  #    host: 'http://192.168.0.50:8081'
  #    nexus_username: 'admin'
  #    nexus_password: 'L0cked4$'
  #    exists: False
  #  register: testout

EXAMPLES = '''
# Create new Blob Store
- name: Create new Blob Store
  nexus_blob_store:
    store_name: 'my-store'
    store_type: 'File'
    host: 'http://nexus.example.tld:8081'
    nexus_username: 'username'
    nexus_password: 'password'

# Delete new Blob Store
- name: Delete a Blob Store
  nexus_blob_store:
    store_name: 'my-store'
    host: 'http://nexus.example.tld:8081'
    nexus_username: 'username'
    nexus_password: 'password'
    exists: False
'''

RETURN = '''
original_message:
    description: The original name param that was passed in
    type: str
    returned: always
message:
    description: The output message that the test module generates
    type: str
    returned: always
'''

from ansible.module_utils.basic import *
from ansible.module_utils.urls import *

def checkRequiredAction(result, already_exists, expected_exists):
    '''
    Check Action required, i.e.
    Create
    Delete
    NoOp
    '''
    changed=already_exists != expected_exists

    result['changed'] = changed

    if changed:
        if expected_exists:
            return 'Create'
        else:
            return 'Delete'
    else:
        return 'NoOp'

def performAction(result, module, action, url, store_name, store_type):
    '''
    Perform Action
    '''
    if 'Create' == action:
        return create_blob_store(result, module, url, store_name, store_type)

    elif 'Delete' == action:
        return delete_blob_store(result, module, url, store_name, store_type)

    return 'Nothing'

def create_blob_store(result, module, url, store_name, store_type):
    '''
    Create 'blob store' by name and type
    Valid http responses and return values are;
    204 True
    404 False
    All other response codes will trigger fail_json
    '''
    if 'File' == store_type:
        url  = url + '/file'
    else:
        module.fail_json(changed=False, msg='Create Blob Store Error!', reason='Unsupported store_type \'' + store_type + '\'.')


    store_path=module.params['file_store_path'] + store_name

    result['store']['type'] = store_type
    result['store']['path'] = store_path

    try:
        response_obj = open_url(url,
            method='POST',
            url_username=module.params['nexus_username'],
            url_password=module.params['nexus_password'],
            force_basic_auth=True,
            headers={'Accept':'application/json','Content-Type':'application/json'},
            data=json.dumps({"name":store_name,"path":store_path})
        )

        if response_obj.code == 204:
            return True

        module.fail_json(changed=False, msg='Create Api Call Unexpected Response!.', reason=str(response_obj.code) + ' ' + response_obj.msg)

    except Exception as e:
        module.fail_json(changed=False, msg='Create Api Call Failed! store_name \'' + store_name + '\'.', reason=str(e))

def delete_blob_store(result, module, url, store_name, store_type):
    '''
    Deletes 'blob store' by name
    Valid http responses and return values are;
    204 True
    404 False
    All other response codes will trigger fail_json
    '''
    try:
        response_obj = open_url(url + '/' + store_name,
            method='DELETE',
            url_username=module.params['nexus_username'],
            url_password=module.params['nexus_password'],
            force_basic_auth=True,
            headers={'Accept':'application/json'}
        )

        if response_obj.code == 204:
            return True

        module.fail_json(changed=False, msg='Delete Api Call Unexpected Response!.', reason=str(response_obj.code) + ' ' + response_obj.msg)

    except Exception as e:

        if e.code == 404:
            return False

        module.fail_json(changed=False, msg='Delete Api Call Failed! store_name \'' + store_name + '\'.', reason=str(e))

def get_blob_store(result, module, url, store_name, store_type):
    '''
    Get 'blob store' detail by name
    Valid http responses and return values are;
    204 True
    All other response codes will trigger fail_json
    '''
    if 'File' == store_type:
        url  = url + '/file'
    else:
        module.fail_json(changed=False, msg='Create Blob Store Error!', reason='Unsupported store_type \'' + store_type + '\'.')

    try:
        response_obj = open_url(url + '/' + store_name,
            method='GET',
            url_username=module.params['nexus_username'],
            url_password=module.params['nexus_password'],
            force_basic_auth=True,
            headers={'Accept':'application/json'}
        )

        try:
            response_json = json.loads(response_obj.read())
            result['store']['path'] = response_json['path']

        except Exception as e:
            module.fail_json(changed=False, msg='Get Api Call Response Conversion Error!.', reason=str(e))

    except Exception as e:
        module.fail_json(changed=False, msg='Get Api Call Failed!.', reason=str(e))


def list_blob_store(module, url):
    '''
    Lists of 'blob store'
    Valid http responses and return values are;
    200 json data
    All other response codes will trigger fail_json
    '''
    try:
        response_obj = open_url(url,
            method='GET',
            url_username=module.params['nexus_username'],
            url_password=module.params['nexus_password'],
            force_basic_auth=True,
            headers={'Accept':'application/json'}
        )
        try:
            return json.loads(response_obj.read())
        except Exception as e:
            module.fail_json(changed=False, msg='List Api Call Response Conversion Error!.', reason=str(e))
    except Exception as e:
        module.fail_json(changed=False, msg='List Api Call Failed!.', reason=str(e))

def run_module():
    # define available arguments/parameters a user can pass to the module
    module_args = dict(
        store_name=dict(type='str', required=True),
        store_type=dict(type='str', required=False, default='File'),
        exists=dict(type='bool', required=False, default=True),
        host=dict(type='str', required=True),
        api_endpoint=dict(type='str', required=False, default='/service/rest/v1/blobstores'),
        api_endpoint=dict(type='str', required=False, default='/service/rest/v1/blobstores'),
        nexus_username=dict(type='str', required=True),
        nexus_password=dict(type='str', required=True, no_log=True),
        file_store_path=dict(type='str', required=False, default='/opt/sonatype/sonatype-work/nexus3/blobs')
    )

    # seed the result dict in the object
    # we primarily care about changed and state
    # change is if this module effectively modified the target
    # state will include any data that you want your module to pass back
    # for consumption, for example, in a subsequent task
    result = dict(
        changed=False,
        store=''
    )

    # the AnsibleModule object will be our abstraction working with Ansible
    # this includes instantiation, a couple of common attr would be the
    # args/params passed to the execution, as well as if the module
    # supports check mode
    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    store_name=module.params['store_name']
    store_type=module.params['store_type']
    expectedExists=module.params['exists']

    url=module.params['host'] + module.params['api_endpoint']

    result['store'] = {}
    result['store']['name'] = store_name

    if store_type != 'File':
        module.fail_json(msg='Unsupported store_type \'' + store_type + '\', Only \'File\' supported.', **result)

    alreadyExists = False

    blob_stores = list_blob_store(module, url)

    # work out if blob store already exists
    for blobstore in blob_stores:
        alreadyExists = bool(alreadyExists | (blobstore['name'] == store_name))

        # found blob store with matching name
        if blobstore['name'] == store_name:
            actual_store_type = blobstore['type']
            result['store']['type'] = actual_store_type

            # can't change type
            if actual_store_type != store_type:
                module.fail_json(msg='Unable to change existing store_type \'' + actual_store_type + '\', to \'' + store_type + '\'.', **result)

            # get blob store details if it exists
            get_blob_store(result, module, url, store_name, store_type)
            break

    # work out action required, i.e. create or delete
    action = checkRequiredAction(result, alreadyExists, expectedExists)

    # perform action if not check mode
    if not module.check_mode:
        performAction(result, module, action, url, store_name, store_type)

    # return successful execution response
    module.exit_json(**result)

def main():
    run_module()

if __name__ == '__main__':
    main()
