import os
import shutil
import requests
import subprocess
import time

from zipfile import ZipFile
from optparse import OptionParser


C_ERROR = '\033[91m'
C_SUCCESS = '\33[32m'
C_WARNING = '\033[93m'
C_INFO = '\033[94m'
C_END = '\033[0m'


def print_section(message, cols=80):
    print('*' * cols)
    print(C_INFO + message + C_END)
    
def print_color(message, color_code = C_INFO):
    print(color_code + message + C_END)


def generate_build(project_file, mx_version, rn_template_version, config_file, release_number, output_folder):
    if not os.path.exists(project_file):
        print_color(
            f"ERROR: The given MPR project file name '{project_file}' does't not exits!", C_ERROR)
        return False

    # Checks the JAVA_HOME environment variable
    java_home = os.getenv('JAVA_HOME')
    if not java_home:
        print_color(f"ERROR: 'JAVA_HOME' environment variable is not defined!", C_ERROR)
        return False

    # Checks the NODE_HOME environment variable
    node_home = os.getenv('NODE_HOME')
    if not node_home:
        print_color(f"ERROR: 'NODE_HOME' environment variable is not defined!", C_ERROR)
        return False

    # Checks the MENDIX_HOME environment variable
    mendix_home = os.getenv('MENDIX_HOME')
    if not mendix_home:
        print_color(f"ERROR: 'MENDIX_HOME' environment variable is not defined!", C_ERROR)
        return False

    if not os.path.exists(config_file):
        print_color(
            f"ERROR: The given Config Json file '{config_file}' does't not exit!", C_ERROR)
        return False

    # Checks the working directory. It's a sub-directory under project directory called 'build'. If already exists, deletes if necessary.
    project_path = os.path.dirname(project_file)
    working_directory = os.path.join(project_path, 'build')
    deployment_directory = os.path.join(project_path, 'deployment')

    # Checks the output folder
    if output_folder == None:
        output_folder = project_path
    else:
        if not os.path.exists(output_folder):
            print_color(
                f"ERROR: The given output folder '{output_folder}' does't not exist", C_ERROR)
            return False
    print_color(
        f'The output (APK and AAB) will be saved on the project folder: {output_folder}')

    # Defines the RN template folder
    # Note: removes the 'v' at the beginning
    rn_mx_template_folder = os.path.join(
        working_directory, f"native-template-{rn_template_version.lstrip('v')}")

    if os.path.exists(working_directory):
        print_section(f'Removing the working directory: {working_directory}')
        shutil.rmtree(working_directory, ignore_errors=True)
        
    if os.path.exists(deployment_directory):
        print_section(f'Removing the deployment directory: {deployment_directory}')
        shutil.rmtree(working_directory, ignore_errors=True)

    # Recreates the working directory
    print_section('Recreating the working directory ...')
    if not os.path.exists(working_directory):
        os.mkdir(working_directory)

    # Changes the current working dir to 'working_directory'
    print_section(f'Current working directory: {working_directory}')
    os.chdir(working_directory)

    # Downloads the react native template to the current directory
    print_section(
        'Downloads the react native template to the current directory')
    rn_mx_url_template = f"https://github.com/mendix/native-template/archive/refs/tags/{rn_template_version}.zip"
    request_file = requests.get(rn_mx_url_template, allow_redirects=True)
    rn_mx_template_zipfile = os.path.join(
        working_directory, f'{rn_template_version}.zip')
    open(rn_mx_template_zipfile, 'wb').write(request_file.content)

    # Extracts the contents of the react native template
    print_section('Extracts the contents of the react native template')
    with ZipFile(rn_mx_template_zipfile, 'r') as zip:
        print('Extracting all the React Native Project template files now...')
        zip.extractall(working_directory)
        print_color('Done!', C_SUCCESS)

    # Defines the required executables
    java_exe = os.path.join(java_home, 'bin\\java.exe')
    mxbuild_exe = os.path.join(mendix_home, mx_version, 'modeler\\mxbuild.exe')

    # Runs the command line that generates the build. As final result, we'll get the bundle
    print_section('Runs the command line that generates the build.')
    mxbuild_full_command = f'{mxbuild_exe} --java-home="{java_home}" --java-exe-path="{java_exe}" --target=deploy --native-packager --loose-version-check {project_file}'
    print_color(f'Running now the MxBuild command:\n{mxbuild_full_command}', C_INFO)
    try:
        res = subprocess.run(mxbuild_full_command, capture_output=False, text=True, check=True)
    except:
        print_color(res.stderr, C_ERROR)
        return False

    # Copies the bundle to the correct template sub-folder - only for Android
    print_section('Copies the bundle to the correct template sub-folder')
    android_assets_path = os.path.join(
        project_path, "deployment\\native\\bundle\\android")
    rn_mx_template_bundle_folder = os.path.join(
        rn_mx_template_folder, "android\\app\\src\\main")
    shutil.copytree(android_assets_path,
                    rn_mx_template_bundle_folder, dirs_exist_ok=True)

    # Changes the current working dir to 'rn_mx_template_folder'
    os.chdir(rn_mx_template_folder)
    print_color(f'Current working directory: {rn_mx_template_folder}')

    # Copies the config.json file
    print_section('Copies the config.json file')
    print_color(
        f'Copying the Config Json from: "{config_file}" to "{rn_mx_template_folder}"')
    copied_file = shutil.copy(config_file, rn_mx_template_folder)

    # Ensures that the Config Json file has the name 'config.json'
    os.rename(copied_file, os.path.join(rn_mx_template_folder, 'config.json'))

    # Executes the NodeJS commands in the RN template folder
    print_section("Executes the NodeJS commands in the RN template folder")
    node_exe = f'{node_home}\\node.exe'
    npm_install_cli = f'{node_exe} D:\\bin\\nodejs\\node_modules\\npm\\bin\\npm-cli.js'
    npm_install_command = f'{npm_install_cli} install'
    try:
        print_color(f'Executing: {npm_install_command}', C_WARNING)
        res = subprocess.run(npm_install_command, capture_output=False, text=True, check=True)
    except:
        print_color(res.stderr, C_ERROR)
        return False
    npm_install_run_configure = f'{npm_install_cli} run configure'
    try:
        print_color(f'Executing: {npm_install_run_configure}', C_WARNING)
        res = subprocess.run(npm_install_run_configure, capture_output=False, text=True, check=True)
    except:
        print_color(res.stderr, C_ERROR)
        return False

    # Executes the commands to generate the APK and AAB
    print_section("Executes the commands to generate the APK and AAB")
    rn_mx_template_android_folder = os.path.join(
        rn_mx_template_folder, 'android')
    os.chdir(rn_mx_template_android_folder)
    print_color(f'Current working directory: {rn_mx_template_android_folder}')
    assemble_build_debug_command = '.\gradlew.bat assembleAppstoreDebug'
    try:
        print_color(f'Executing: {assemble_build_debug_command}', C_WARNING)
        res = subprocess.run(assemble_build_debug_command, capture_output=False, text=True, check=True)
    except:
        print_color(res.stderr)
        return False
    print_color('Build APK: Done!', C_SUCCESS)
    assemble_build_bundle_command = '.\gradlew.bat bundleAppstoreDebug'
    try:
        res = subprocess.run(assemble_build_bundle_command, capture_output=False, text=True, check=True)
    except:
        print_color(res.stderr)
        return False
        
    print_color('Build AAB: Done!', C_SUCCESS)

    # Cleans the node_modules directory  with: npx rimraf node_modules - see https://sebhastian.com/remove-node-modules/
    print_section(
        "Cleans the node_modules directory  with: npx rimraf node_modules")
    npx_install_cli = f'{node_exe} D:\\bin\\nodejs\\node_modules\\npm\\bin\\npx-cli.js'
    npx_rimraf_command = f'{npx_install_cli} rimraf node_modules'
    os.chdir(rn_mx_template_folder)
    subprocess.run(npx_rimraf_command)
    
    # Copies the binaries to the given output folder
    print_section(f"The output are being copied now to the specified folder: {output_folder}")
    apk_filename = 'app-appstore-debug.apk'
    apk_filepath = os.path.join(
        rn_mx_template_android_folder, 'app\\build\\outputs\\apk\\appstore\\debug', apk_filename)
    if os.path.exists(apk_filepath):
        shutil.copy(apk_filepath, output_folder)
        apk_filepath_destiny = os.path.join(output_folder, f'app-appstore-debug-{release_number}.apk')
        os.replace(os.path.join(output_folder, apk_filename), apk_filepath_destiny)
        print_color(f'The APK debug is available at: {apk_filepath_destiny}')

    aab_filename = 'app-appstore-debug.aab'
    aab_filepath = os.path.join(
        rn_mx_template_android_folder, 'app\\build\\outputs\\bundle\\appstoreDebug', aab_filename)
    if os.path.exists(aab_filepath):
        shutil.copy(aab_filepath, output_folder)
        aab_filepath_destiny = os.path.join(output_folder, f'app-appstore-debug-{release_number}.aab')
        os.replace(os.path.join(output_folder, aab_filename), aab_filepath_destiny)
        print_color(f'The AAB debug is available at: {aab_filepath_destiny}')

    print_section("Script execution DONE!")
    return True


if __name__ == '__main__':
    usage = "\n\n\tBasic usage: python gen_apk_aab.py [options] mpr_project_filename"
    parser = OptionParser(usage=usage)
    parser.add_option("-n", "--release-number", dest="release_number",
                      default='1.0.0', help="Release Number")
    parser.add_option("-m", "--mx-version", dest="mx_version",
                      default='9.18.5.3736', help="Mendix Version")
    parser.add_option("-t", "--rn-template-version", dest="rn_template_version",
                      default='v6.3.5', help="React Native Template version")
    parser.add_option("-c", "--config-file", dest="config_file",
                      default=None, help="The Json Config file fullpath")
    parser.add_option("-o", "--output-folder", dest="output_folder", default=None,
                      help="The output folder in which the binaries APK and AAB should be moved to")

    (options, args) = parser.parse_args()

    try:
        mpr_project_filename = args[0]
    except IndexError:
        print_color(
            f"ERROR:\n\tMissing 'MPK project filename' argument!{usage}\n\tFor Help: python build-unsigned-debug-apk-aab -h\n", C_ERROR)
        exit()
    else:
        release_number = options.release_number
        mx_version = options.mx_version
        rn_template_version = options.rn_template_version
        config_file = options.config_file
        output_folder = options.output_folder

        # Sample usage:
        # python H:\work\vstram\mx_buildscripts\src\python\build-unsigned-debug-apk-aab.py H:\work\vstram\NativeApp01-main\NativeApp01.mpr -c H:\work\vstram\NativeApp01-main\build_scripts\sample_config.json -o H:\work\vstram\NativeApp01-main\output -m 9.18.5.3736 -t v6.3.5
        # python H:\work\vstram\mx_buildscripts\src\python\build-unsigned-debug-apk-aab.py D:\temp\NativeApp02\NativeApp02.mpr -c H:\work\vstram\mx_buildscripts\src\mendix\template_config.json -o D:\temp\NativeApp02\output -m 9.24.0.2965 -t v7.0.0

        start = time.time()
        print_section(
            "Starting the Script to generate the output for your project...")
        gen_build_result = generate_build(mpr_project_filename, mx_version,
                       rn_template_version, config_file, release_number, output_folder)
        if gen_build_result:
            print_color('BUILD SUCCESSFUL!', C_SUCCESS)
        else:
            print_color('Error on generating APK/AAB!', C_ERROR)
        
        end = time.time()
        elapsed_time = (end - start)/60.0
        print_color(f'Elapsed Time: {elapsed_time:.2f} minutes')
