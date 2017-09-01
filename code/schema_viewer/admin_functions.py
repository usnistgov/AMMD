from os import path, listdir, remove, makedirs
from shutil import rmtree
from zipfile import ZipFile
from re import findall, DOTALL, sub

from mgi.settings import SITE_ROOT


def unzip_oxygen_files(zip_file):
    """
    Unzip a file (zip_file), extract the contained files, and clean the useful files name.

    Extract the files and clean their names following the rules:
    _Is not a MAC OS file (name beginning with __MACOSX),
    _The JPEG diagrams name are saved into a list of images name,
    _The left menu file name (ending with .indexList.html) is saved,
    _The main content file name (ending with _xsd.html) is saved.

    :param zip_file: Zip file to be extracted
    :return:
    _files_unzipped: list of files unzipped
    _name_left_menu: left menu file name
    _name_main_content: main content file name
    _list_img_files_to_save: list of diagram name
    """
    name_main_content = None
    name_left_menu = None
    list_img_files_to_save = list()

    files_unzipped = ZipFile(zip_file)
    for file_unzipped_name in files_unzipped.namelist():
        if not file_unzipped_name.startswith('__MACOSX'):
            if file_unzipped_name.endswith(".jpeg"):
                list_img_files_to_save.append(file_unzipped_name)
            elif file_unzipped_name.endswith(".indexList.html"):
                name_left_menu = file_unzipped_name
            elif file_unzipped_name.endswith("_xsd.html"):
                name_main_content = file_unzipped_name

    return files_unzipped, name_left_menu, name_main_content, list_img_files_to_save


def get_body(html_file_content):
    """
    Return the body part of HTML files.

    :param html_file_content: HTML file to be truncated.
    :return: HTML body part
    """
    return findall("<body>(.*?)</body>", html_file_content, DOTALL)[0].decode("utf-8")


def correct_img_links(body_main_content, schema_name, list_name_image):
    """
    Correct the diagram links into the main content body.

    :param body_main_content: Main content body,
    :param schema_name: Schema name related to the oxygen files,
    :param list_name_image: List of image names.
    :return: New body content with images link solved.
    """
    for name_image in list_name_image:
        body_main_content = body_main_content.replace(
            "src=\"" + name_image + "\"",
            "src=\"{% static \"schema_viewer/oxygen/" + schema_name + "/" + name_image + "\" %}\""
        )
    return body_main_content


def correct_links(html_file, schema_name):
    """
    Correct the links to an element with a specified id within a page.

    :param html_file: HTML file to be transformed,
    :param schema_name: Schema name related to the oxygen files.
    :return: HTML body
    """
    return html_file.replace(schema_name.replace(".", "_") + "_xsd.html#", "#").replace("target=\"mainFrame\"", "")


def create_html_file(body_left_menu, body_main_content):
    """
    Create the final HTML oxygen files, with the common header, a specific left menu and the main body.

    :param body_left_menu: Left menu body.
    :param body_main_content: Main content body.
    :return: Content of the new HTML file.
    """

    # Get the header fie and get it contents
    path_header = path.join(
        SITE_ROOT,
        'schema_viewer',
        'templates',
        'schema_viewer',
        'oxygen',
        'header_oxygen_template.html'
    )
    file_header = open(path_header, 'r')
    header = file_header.read()
    file_header.close()

    # Create the final file
    final_file = \
        header \
        + "\n{% block oxygen_menu %}\n" \
        + body_left_menu \
        + "{% endblock %}\n{% block oxygen_content %}" \
        + body_main_content \
        + "{% endblock %}"

    return final_file


def delete_previous_files(schema_name, path_template, path_static):
    """
    Delete the previous version of the oxygen files in case of an update.

    :param schema_name: Schema name
    :param path_template: Template path
    :param path_static: Static files path
    """
    list_file_static = listdir(path_static)
    list_file_template = listdir(path_template)
    if schema_name in list_file_static:
        tree_path = path.join(path_static, schema_name)
        rmtree(tree_path, ignore_errors=True)
    html_file_name = "wrap_" + schema_name + ".html"
    if html_file_name in list_file_template:
        html_file_path = path.join(path_template, html_file_name)
        remove(html_file_path)


def save_file(schema_name, unzipped_file, list_name_img, html_file_content):
    """
    Save the oxygen treated files.

    :param schema_name: Schema name
    :param unzipped_file: List of all the unzipped files.
    :param list_name_img: List of diagram names.
    :param html_file_content: Content of the final HTML file.
    :return:
    """

    # Create the different paths
    base_path = path.join(SITE_ROOT, 'schema_viewer')
    path_template = path.join(base_path, 'templates', 'schema_viewer', 'oxygen')
    path_static = path.join(base_path, 'static', 'schema_viewer', 'oxygen')
    path_images = path.join(path_static, schema_name)

    # Delete the previous version
    delete_previous_files(schema_name, path_template, path_static)

    # Create the directory for the diagrams and save them
    makedirs(path.join(path_images, "img"))
    for name_image in list_name_img:
        path_img = path.join(path_images, name_image)
        img_file = open(path_img, 'w')
        img_file.write(unzipped_file.read(name_image))
        img_file.close()

    # Create the html file
    path_html = path.join(path_template, "wrap_" + schema_name + ".html")
    html_file = open(path_html, 'w')
    html_file.write(html_file_content.encode('utf-8'))
    html_file.close()


def delete_menu(body_left_menu):
    """
    Delete the drop list on the left menu.

    :param body_left_menu: Left menu HTML body.
    :return: Left menu HTML without the drop list.
    """
    return sub("<form (.*?) </form>", "", body_left_menu, flags=DOTALL)


def is_correct_name(name_left_menu, name_main_content, schema_name):
    """
    Check if the files are name the right way.

    :param name_left_menu: Name of the left menu file.
    :param name_main_content: Name of the main content file.
    :param schema_name: Schema exact name
    :return: True if the name files correspond to the schema name, False else.
    """
    return name_main_content.startswith(schema_name.replace(".", "_")) and name_left_menu.startswith(schema_name)


def del_global_control(body_main_content):
    """
    Delete the floating global control on the main content.

    :param body_main_content: Main content body
    :return: Main content body without the floating global control.
    """
    return sub("<div id=\"global_controls\" (.*?) </div>", "", body_main_content, flags=DOTALL)
