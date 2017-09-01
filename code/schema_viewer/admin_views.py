from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from django.contrib.messages import add_message, INFO, ERROR, SUCCESS
from django.forms import formset_factory
from mongoengine import DoesNotExist

from mgi.models import Template
from schema_viewer.models import TemplateSchemaViewer
from schema_viewer.admin_forms import FormUnzip, FormManageVisibilityDefault
from schema_viewer.admin_functions import unzip_oxygen_files, get_body, create_html_file, save_file, \
    correct_links, correct_img_links, delete_menu, is_correct_name, del_global_control

from zipfile import BadZipfile


@staff_member_required
def upload_oxygen(request):
    """
    View to create/populate/validate form to upload a doxygen zip files associate with a schema.

    If the request in POST, the form is validated, the file contained :
    _ Exists,
    _ Has to be at the right extension (.zip),
    _ Has to be a correct zip file,
    _ Has the correct files (.jpeg files into img folders, and html for the left menu/main content),
    _ Has the files beginning with the exact associated schema.
    Once validated, the files are transformed and saved in the server side.

    In all the case, the form containing all the visible schemas, and by default, the default schema, w
    ith a field to upload a file is produced.

    If there is no template available, an INFO message is produced, in the error case an error message is produced.

    :param request: Django request object.
    :return: HTML rendered page
    """
    if request.method == 'POST':
        zip_file = request.POST.get('zip_file', None)
        if zip_file != '':
            form = FormUnzip(request.POST, request.FILES)
            if form.is_valid():
                zip_file = form.cleaned_data['zip_file']
                if zip_file.name.endswith(".zip"):
                    schema_name = str(form.cleaned_data['schema'])
                    try:
                        # Unzip the files
                        files_unzipped, name_left_menu, name_main_content, list_img_files_to_save, \
                         = unzip_oxygen_files(zip_file=zip_file)
                        if name_main_content \
                                and name_left_menu \
                                and len(list_img_files_to_save) != 0:
                            if is_correct_name(name_left_menu, name_main_content, schema_name):
                                # get the files content
                                content_left_menu = files_unzipped.read(name=name_left_menu)
                                content_main_content = files_unzipped.read(name=name_main_content)
                                body_left_menu = get_body(content_left_menu)
                                # Transform left menu
                                body_left_menu = delete_menu(body_left_menu)
                                body_main_content = get_body(content_main_content)
                                # Transform main content
                                body_main_content = correct_img_links(body_main_content,
                                                                      schema_name,
                                                                      list_img_files_to_save)
                                body_main_content = del_global_control(body_main_content)
                                # Create the final HTML file
                                html_file = create_html_file(body_left_menu, body_main_content)
                                html_file = correct_links(html_file, schema_name)
                                # Save the images and the html page
                                save_file(schema_name, files_unzipped, list_img_files_to_save, html_file)
                                message = "The files are successfully imported."
                                add_message(request, SUCCESS, message)
                            else:
                                message = "The file names do not correspond to the selected schema."
                                add_message(request, ERROR, message)
                        else:
                            message = "The files in the archive are not the ones expected, please verify the archive."
                            add_message(request, ERROR, message)
                    except BadZipfile:
                        message = "The given file can't be processed, upload an other."
                        add_message(request, ERROR, message)
                else:
                    message = "The file has to be a zip file."
                    add_message(request, ERROR, message)
        else:
            message = "You have to select a file."
            add_message(request, ERROR, message)

    not_visible_templates_id = TemplateSchemaViewer.get_id_not_visible_template()
    if Template.objects.filter(pk__nin=not_visible_templates_id).count() != 0:
        form = FormUnzip()
        form.set_default()
    else:
        message = "No template available, please upload one first."
        add_message(request, INFO, message)

    return render(request, "schema_viewer/admin/upload_oxygen.html", locals())


@staff_member_required
def manage_visible_default(request):
    """
        View to create/populate/validate form to define visible and default schemas.

        If the request in POST, the form is validated :
        _ If a new default template is defined, it is set to visible and the old one is set to non-default.
        _ If a template is set to visible it is deleted from the database or it is not created.
        _ If a template is set to not visible it is saved to the database


        In all the case, the form containing all the schemas and the different options is produced.

        If there is no template available, an INFO message is produced, in the error case an error message is produced.

        :param request: Django request object.
        :return: HTML rendered page
    """
    if request.method == 'POST':
        # Get all the data
        number_forms = int(request.POST['form-TOTAL_FORMS'])
        manage_formset = formset_factory(FormManageVisibilityDefault, extra=number_forms)
        formset = manage_formset(request.POST, request.FILES)
        if formset.is_valid():
            for form in formset:
                data = form.cleaned_data
                schema_name = data["schema_name"]

                is_default = data["is_default"]
                if is_default:
                    is_visible = True
                else:
                    is_visible = data["is_visible"]
                template = Template.objects.get(title=schema_name)

                try:
                    object_schema = TemplateSchemaViewer.objects.get(template=template)
                    already_exist = True
                except DoesNotExist:
                    object_schema = TemplateSchemaViewer()
                    already_exist = False

                # The schema is the new default
                if is_default:
                    try:
                        temp = TemplateSchemaViewer.objects.get(is_default=True)
                        # An other default schema already exist
                        if object_schema != temp:
                            if temp.is_visible:
                                temp.delete()
                            else:
                                temp.update(is_default=False)
                    except DoesNotExist:
                        pass
                    if already_exist:
                        object_schema.update(is_default=is_default)
                        object_schema.update(is_visible=True)
                    else:
                        object_schema.is_visible = True
                        object_schema.is_default = is_default
                        object_schema.template = template
                        object_schema.save()
                # The schema is not the new default
                else:
                    if is_visible:
                        if already_exist:
                            object_schema.delete()
                    else:
                        if already_exist:
                            object_schema.update(is_visible=is_visible)
                        else:
                            object_schema.is_visible = is_visible
                            object_schema.is_default = is_default
                            object_schema.template = template
                            object_schema.save()
            message = "All changes has been applied."
            add_message(request, INFO, message)

    if Template.objects.count() != 0:
        manage_formset = formset_factory(FormManageVisibilityDefault, extra=0)
        object_all_template = Template.objects
        object_template_viewer = TemplateSchemaViewer.objects

        initial_data = list()
        for template in object_all_template.all():
            dict_template = dict()
            dict_template['schema_name'] = template.title
            try:
                modification_template = object_template_viewer.get(template=template)
                dict_template["is_default"] = modification_template.is_default
                dict_template["is_visible"] = modification_template.is_visible
            except DoesNotExist:
                pass
            initial_data.append(dict_template)

        formset = manage_formset(initial=initial_data)
    else:
        message = "No template available, please upload one first."
        add_message(request, INFO, message)

    return render(request, "schema_viewer/admin/manage_visible_default.html", locals())
