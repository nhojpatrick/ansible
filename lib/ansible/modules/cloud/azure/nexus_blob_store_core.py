#!/usr/bin/python

from ansible.module_utils.basic import *
from ansible.module_utils.urls import *

def checkRequiredAction(result, already_exists, exists):

    changed=already_exists != exists

    result['changed'] = changed

    if changed:
        if exists:
            return 'Create'
        else:
            return 'Delete'
    else:
        return 'NoOp'

def performAction(result, action, checkMode):

    if 'Create' == action and not checkMode:
        return 'Created'

    elif 'Delete' == action and not checkMode:
        return 'Deleted'

    return 'Nothing'

def create_blob_store(url, nexus_username, nexus_password, store_name, store_type, store_path):
    '''
    Deletes 'blob store' by name
    Valid http responses and return values are;
    204 True
    404 False
    All other response codes will trigger fail_json
    '''

    if 'File' == store_type:
        url  = url + '/file'
    else:
        module.fail_json(changed=False, msg='Create Blob Store Error!', reason='Unsupported store_type \'' + store_type + '\'.')

    try:
        response_obj = open_url(url,
            method='POST',
            url_username=nexus_username,
            url_password=nexus_password,
            force_basic_auth=True,
            headers={'Accept':'application/json','Content-Type':'application/json'},
            data=json.dumps({"name":store_name,"path":store_path})
        )
        if response_obj.code == 204:
            return True
        module.fail_json(changed=False, msg='Create Api Call Unexpected Response!.', reason=str(response_obj.code) + ' ' + response_obj.msg)
    except Exception as e:
        raise e;
        #if e.code == 404:
        #    return False
        #module.fail_json(changed=False, msg='Create Api Call Failed! store_name \'' + store_name + '\'.', reason=str(e))



def run_module():
    result = dict(
        changed=False,
        store=''
    )

    create_blob_store('', 'http://192.168.0.50:8081/service/rest/v1/blobstores', 'admin', 'L0cked4$', 'alpha2', 'File', '/opt/sonatype/sonatype-work/nexus3/blobs/alpha2')



def main():
    run_module()

if __name__ == '__main__':
    main()
