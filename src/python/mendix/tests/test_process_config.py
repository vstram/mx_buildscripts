import unittest

from mendix.process_config import ProcessConfig

class TestProcessConfig(unittest.TestCase):

    def test_split(self):
        pc = ProcessConfig(
            config_filepath = "H:\\work\\vstram\\mx_buildscripts\\src\\mendix\\template_config.json", 
            app_identifier = "myapp.nativeapp02", 
            app_name = "NativeApp02", 
            app_version = "1.0.0", 
            build_number = 1, 
            runtime_url = "http://192.168.0.42:8080"
        )
        
        output_config_file = "H:\\work\\vstram\\mx_buildscripts\\src\\python\\mendix\\tests\\data\\config.json"
        pc.write(output_filepath=output_config_file)
        
        # TODO: do the assert!

if __name__ == '__main__':
    unittest.main()