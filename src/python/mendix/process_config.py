class ProcessConfig:
    def __init__(self, config_filepath, app_identifier, app_name, app_version, build_number, runtime_url) -> None:
        self._config_filepath = config_filepath
        
        self._replacement_dict = {
            "app_identifier" : app_identifier, 
            "app_name" : app_name,
            "app_version" : app_version,
            "build_number": build_number,
            "runtime_url": runtime_url,
        }
        
    def write(self, output_filepath):
        f_in = open(self._config_filepath, 'rt')
        f_out = open(output_filepath, 'wt')
        
        contents = f_in.read()
        
        for key, value in self._replacement_dict.items():
            contents = contents.replace(f'{key}', str(value))
            
        f_out.write(contents)
        
        f_in.close()
        f_out.close()
            
        
        
        
        
        
        
    
    
    