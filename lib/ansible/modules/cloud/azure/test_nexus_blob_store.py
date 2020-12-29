
from nexus_blob_store_core import checkRequiredAction
from nexus_blob_store_core import performAction
import unittest

class TestNexusBlobStore(unittest.TestCase):
    def test_checkRequiredAction(self):
        self.assertEqual(checkRequiredAction(dict(changed=False,store=''), False, False), 'NoOp')
        self.assertEqual(checkRequiredAction(dict(changed=False,store=''), False, False), 'NoOp')
        self.assertEqual(checkRequiredAction(dict(changed=False,store=''), False, True ), 'Create')
        self.assertEqual(checkRequiredAction(dict(changed=False,store=''), False, True ), 'Create')
        self.assertEqual(checkRequiredAction(dict(changed=False,store=''), True,  False), 'Delete')
        self.assertEqual(checkRequiredAction(dict(changed=False,store=''), True,  False), 'Delete')
        self.assertEqual(checkRequiredAction(dict(changed=False,store=''), True,  True ), 'NoOp')
        self.assertEqual(checkRequiredAction(dict(changed=False,store=''), True,  True ), 'NoOp')

    def test_performAction(self):
        self.assertEqual(performAction(dict(changed=False,store=''), 'NoOp', True), 'Nothing')
        self.assertEqual(performAction(dict(changed=False,store=''), 'NoOp', False), 'Nothing')
        self.assertEqual(performAction(dict(changed=False,store=''), 'Create', False), 'Created')
        self.assertEqual(performAction(dict(changed=False,store=''), 'Create', True), 'Nothing')
        self.assertEqual(performAction(dict(changed=False,store=''), 'Delete', False), 'Deleted')
        self.assertEqual(performAction(dict(changed=False,store=''), 'Delete', True), 'Nothing')

if __name__ == '__main__':
    unittest.main()

