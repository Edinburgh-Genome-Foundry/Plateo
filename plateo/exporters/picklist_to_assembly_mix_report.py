from .reports import report_writer, template_path
from ..tools import find_best_volume_unit, human_volume
from .AssemblyPicklistGenerator import AssemblyPicklistGenerator

def picklist_to_assembly_mix_report(picklist, target, data=None,
                                    volume_unit='auto'):
    html = report_writer.pug_to_html(
        path=template_path("assembly_mix_picklist_report.pug"),
        picklist=picklist,
        data=data or {},
        get_part_from_well=AssemblyPicklistGenerator.get_part_from_well,
        get_construct_from_well=lambda w: w.data.get("construct", ""),
        well_sorter=lambda w: w.coordinates[::-1],
        human_volume=human_volume
    )
    report_writer.write_report(html, target)
