import pytest
import os

import pandas as pd

from great_expectations.data_context.store import (
    NamespacedReadWriteStore,
    NamespacedReadWriteStoreConfig,
    BasicInMemoryStore,
    BasicInMemoryStoreConfig,
    FileSystemWriteOnlyStoreConfig,
    FileSystemWriteOnlyStore,
    DelimitedFileSystemWriteOnlyStoreConfig,
    DelimitedFileSystemWriteOnlyStore,
)
from great_expectations.data_context.types import (
    DataAssetIdentifier,
    ValidationResultIdentifier,
)
from great_expectations.util import (
    gen_directory_tree_str,
)

# NOTE : Abe 2019/08/30 : Keeping this for now, since we'll likely do some work on standardizing config-init patterns soon.
# def test_store_config(tmp_path_factory):
#     path = str(tmp_path_factory.mktemp('test_store_config__dir'))

#     config = {
#         "module_name": "great_expectations.data_context.store",
#         "class_name": "InMemoryStore",
#         "store_config": {
#             "serialization_type": "json"
#         },
#     }
#     typed_config = StoreMetaConfig(
#         coerce_types=True,
#         **config
#     )
#     print(typed_config)

#     loaded_module = importlib.import_module(typed_config.module_name)
#     loaded_class = getattr(loaded_module, typed_config.class_name)

#     typed_sub_config = loaded_class.get_config_class()(
#         coerce_types=True,
#         **typed_config.store_config
#     )

#     data_asset_snapshot_store = loaded_class(
#         root_directory=os.path.abspath(path),
#         config=typed_sub_config,
#     )

def test_NamespacedReadWriteStore_with_InMemoryStoreBackend():

    my_store = NamespacedReadWriteStore(
        config=NamespacedReadWriteStoreConfig(**{
            "resource_identifier_class_name": "ValidationResultIdentifier",
            "serialization_type" : None,
            "store_backend" : {
                "module_name" : "great_expectations.data_context.store",
                "class_name" : "InMemoryStoreBackend",
                "separator" : ".",
            }
        }),
        root_directory=None,#"dummy/path/",
    )

    with pytest.raises(TypeError):
        my_store.get("not_a_ValidationResultIdentifier")

    with pytest.raises(KeyError):
        my_store.get(ValidationResultIdentifier(**{}))
    
    ns_1 = ValidationResultIdentifier(
        from_string="ValidationResultIdentifier.a.b.c.quarantine.prod-100"
    )
    my_store.set(ns_1,"aaa")
    assert my_store.get(ns_1) == "aaa"

    ns_2 = ValidationResultIdentifier(
        from_string="ValidationResultIdentifier.a.b.c.quarantine.prod-200"
    )
    my_store.set(ns_2, "bbb")
    assert my_store.get(ns_2) == "bbb"

    # Verify that internals are working as expected
    assert my_store.store_backend.store == {
        'a.b.c.quarantine.prod-100': 'aaa',
        'a.b.c.quarantine.prod-200': 'bbb',
    }

    print(my_store.list_keys())
    assert set(my_store.list_keys()) == set([
        ns_1,
        ns_2,
    ])

def test_NamespacedReadWriteStore__convert_resource_identifier_to_list():

    my_store = NamespacedReadWriteStore(
        config=NamespacedReadWriteStoreConfig(**{
            "resource_identifier_class_name": "ValidationResultIdentifier",
            "serialization_type" : None,
            "store_backend" : {
                "module_name" : "great_expectations.data_context.store",
                "class_name" : "InMemoryStoreBackend",
                "separator" : ".",
            }
        }),
        root_directory=None,#"dummy/path/",
    )

    ns_1 = ValidationResultIdentifier(
        from_string="ValidationResultIdentifier.a.b.c.quarantine.prod-100"
    )
    assert my_store._convert_resource_identifier_to_tuple(ns_1) == ('a', 'b', 'c', 'quarantine', 'prod-100')
    
def test_NamespacedReadWriteStore_with_FileSystemStoreBackend(tmp_path_factory):
    path = str(tmp_path_factory.mktemp('test_test_NamespacedReadWriteStore_with_FileSystemStoreBackend__dir'))
    project_path = str(tmp_path_factory.mktemp('my_dir'))

    my_store = NamespacedReadWriteStore(
        config=NamespacedReadWriteStoreConfig(**{
            "resource_identifier_class_name": "ValidationResultIdentifier",
            "serialization_type" : None,
            "store_backend" : {
                "module_name" : "great_expectations.data_context.store",
                "class_name" : "FilesystemStoreBackend",
                "base_directory" : "my_store/",
                "file_extension" : "txt",
                "filepath_template" : "{4}/{0}/{1}/{2}/validation-results-{2}-{3}.{file_extension}",
                "replaced_substring" : "/",
                "replacement_string" : "__",
            }
        }),
        root_directory = path,
    )

    with pytest.raises(TypeError):
        my_store.get("not_a_ValidationResultIdentifier")

    with pytest.raises(KeyError):
        my_store.get(ValidationResultIdentifier(**{}))
    
    ns_1 = ValidationResultIdentifier(
        from_string="ValidationResultIdentifier.a.b.c.quarantine.prod-100"
    )
    my_store.set(ns_1,"aaa")
    assert my_store.get(ns_1) == "aaa"

    ns_2 = ValidationResultIdentifier(
        from_string="ValidationResultIdentifier.a.b.c.quarantine.prod-200"
    )
    my_store.set(ns_2, "bbb")
    assert my_store.get(ns_2) == "bbb"

    print(my_store.list_keys())
    assert set(my_store.list_keys()) == set([
        ns_1,
        ns_2,
    ])

    print(gen_directory_tree_str(path))
    assert gen_directory_tree_str(path) == """\
test_test_NamespacedReadWriteStore_with_FileSystemStoreBackend__dir0/
    my_store/
        prod-100/
            a/
                b/
                    c/
                        validation-results-c-quarantine.txt
        prod-200/
            a/
                b/
                    c/
                        validation-results-c-quarantine.txt
"""

def test_NamespacedReadWriteStore_pandas_csv_serialization(tmp_path_factory):
    #TODO: We should consider using this trick everywhere, as a way to avoid directory name collisions
    path = str(tmp_path_factory.mktemp('test_test_NamespacedReadWriteStore_pandas_csv_serialization__dir'))

    my_store = NamespacedReadWriteStore(
        config=NamespacedReadWriteStoreConfig(**{
            "resource_identifier_class_name": "ValidationResultIdentifier",
            "serialization_type" : "pandas_csv",
            "store_backend" : {
                "module_name" : "great_expectations.data_context.store",
                "class_name" : "FilesystemStoreBackend",
                "base_directory" : "my_store/",
                "file_extension" : "csv",
                "filepath_template" : "{4}/{0}/{1}/{2}/quarantined-rows-{2}-{3}.{file_extension}",
                "replaced_substring" : "/",
                "replacement_string" : "__",
            }
        }),
        root_directory = path,
    )

    key1 = ValidationResultIdentifier(
        from_string="ValidationResultIdentifier.a.b.c.quarantine.prod-20190801"
    )
    with pytest.raises(AssertionError):
        my_store.set(key1, "hi")

    my_df = pd.DataFrame({"x": [1,2,3], "y": ["a", "b", "c"]})
    my_store.set(key1, my_df)

    print(gen_directory_tree_str(path))
    assert gen_directory_tree_str(path) == """\
test_test_NamespacedReadWriteStore_pandas_csv_serialization__dir0/
    my_store/
        prod-20190801/
            a/
                b/
                    c/
                        quarantined-rows-c-quarantine.csv
"""

    with open(os.path.join(path, "my_store/prod-20190801/a/b/c/quarantined-rows-c-quarantine.csv")) as f_:
        assert f_.read() == """\
x,y
1,a
2,b
3,c
"""

    with pytest.raises(NotImplementedError):
        my_store.get(key1)


def test_BasicInMemoryStore():
    my_store = BasicInMemoryStore()

    my_key = "A"
    with pytest.raises(KeyError):
        my_store.get(my_key)
    
    my_store.set(my_key, "aaa")
    assert my_store.get(my_key) == "aaa"

    #??? Putting a non-string object into a store triggers an error.
    # TODO: Allow bytes as well.
    with pytest.raises(TypeError):
        my_store.set("B", {"x":1})

    assert my_store.has_key(my_key) == True
    assert my_store.has_key("B") == False
    assert my_store.has_key("A") == True
    assert my_store.list_keys() == ["A"]


# TODO : Call this TemplatedFileSystemWriteOnlyStore
def test_FileSystemWriteOnlyStore(tmp_path_factory):
    path = str(tmp_path_factory.mktemp('test_FileSystemWriteOnlyStore__dir'))

    my_store = FileSystemWriteOnlyStore(
        FileSystemWriteOnlyStoreConfig(**{
            "base_directory" : "my_store/",
        }),
        root_directory = path,
    )

    my_store.set("a/b/index.txt", "hello!")

    print( gen_directory_tree_str(path) )
    assert gen_directory_tree_str(path) == """\
test_FileSystemWriteOnlyStore__dir0/
    my_store/
        a/
            b/
                index.txt
"""

    with open(os.path.join(path, "my_store", "a/b/index.txt")) as file_:
        assert file_.read() == "hello!"


def test_DelimitedFileSystemWriteOnlyStore(tmp_path_factory):
    path = str(tmp_path_factory.mktemp('test_DelimitedFileSystemWriteOnlyStore__dir'))

    my_store = DelimitedFileSystemWriteOnlyStore(
        DelimitedFileSystemWriteOnlyStoreConfig(**{
            "base_directory" : "my_store/",
        }),
        root_directory = path,
    )

    my_store.set( ("a", "b", "index.txt"), "hello!")

    print( gen_directory_tree_str(path) )
    assert gen_directory_tree_str(path) == """\
test_DelimitedFileSystemWriteOnlyStore__dir0/
    my_store/
        a/
            b/
                index.txt
"""

    with open(os.path.join(path, "my_store", "a/b/index.txt")) as file_:
        assert file_.read() == "hello!"