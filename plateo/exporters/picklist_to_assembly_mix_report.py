from .reports import report_writer, template_path

def picklist_to_assembly_mix_report(picklist, target, data=None):
    html = report_writer.pug_to_html(
        path=template_path("assembly_mix_picklist_report.pug"),
        picklist=picklist,
        data=data or {},
        get_part_from_well=lambda w: w.content.components_as_string(),
        get_construct_from_well=lambda w: w.data.get("construct", "")
    )
    report_writer.write_report(html, target)
