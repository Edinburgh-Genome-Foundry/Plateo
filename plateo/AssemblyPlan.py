from collections import OrderedDict

import flametree
from sequenticon import sequenticon_batch

from .exporters.reports import template_path, report_writer
from .tools import human_seq_size


class AssemblyPlan:

    def __init__(self, assemblies, parts_data=None):
        if isinstance(assemblies, (list, tuple)):
            assemblies = OrderedDict(assemblies)
        self.assemblies = assemblies
        self.parts_data = parts_data

    def all_parts_used(self):
        return sorted(set([
            part
            for assembly in self.assemblies.values()
            for part in assembly
        ]))

    def assemblies_featuring(self, part):
        return [name for (name, parts) in self.assemblies.items()
                if part in parts]

    def assemblies_with_records(self):
        return OrderedDict([
            (name, [self.parts_data[p]['record'] for p in parts])
            for name, parts in self.assemblies.items()
        ])

    def rename_part(self, part_name, new_name):
        for name, parts in self.assemblies.items():
            for i, part in enumerate(parts):
                if part == part_name:
                    parts[i] = new_name
        if self.parts_data is not None:
            if part_name in self.parts_data:
                self.parts_data[new_name] = self.parts_data.pop(part_name)

    @staticmethod
    def from_spreadsheet(path):

        if path.endswith('.csv'):
            with open(path, "r") as f:
                lines = [
                    [c.strip() for c in l.split(',') if (c.strip() != '')]
                    for l in f.read().split("\n")
                ]
            return AssemblyPlan(OrderedDict([
                (line[0], line[1:])
                for line in lines
                if line != []
            ]))
        else:
            raise NotImplementedError(
                "Assembly plan only converts from csv at the moment")

    def to_spreadsheet(self, path):
        with open(path, "w") as f:
            f.write("\n".join([
                ",".join([asm] + parts)
                for asm, parts in self.assemblies.items()
            ]))

    def write_report(self, target):
        all_parts_used = self.all_parts_used()
        sequenticon_dict = None
        parts_length_dict = None
        if 'record' in list(self.parts_data.values())[0]:
            sequenticons = sequenticon_batch([
                self.parts_data[p]['record']
                for p in all_parts_used
            ], output_format='html_image')
            sequenticon_dict = OrderedDict([(name, icon)
                                            for (name, icon) in sequenticons])
            parts_length_dict = {
                part: human_seq_size(self.get_part_length(part))
                for part in sequenticon_dict
            }
        html = report_writer.pug_to_html(
            path=template_path("assembly_plan_report.pug"),
            assembly_plan=self,
            sequenticon_dict=sequenticon_dict,
            parts_length_dict=parts_length_dict,
            all_parts_used=all_parts_used
        )
        report_writer.write_report(html, target)

    def get_part_length(self, part_name):
        data = self.parts_data[part_name]
        if 'size' in data:
            return data['size']
        else:
            return len(data['record'])
