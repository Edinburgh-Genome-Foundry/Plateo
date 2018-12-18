from collections import OrderedDict
import pandas
import flametree
from sequenticon import sequenticon_batch

from .exporters.reports import template_path, report_writer
from .tools import human_seq_size, did_you_mean


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

    def parts_without_data(self):
        return {
            part_name: did_you_mean(part_name, self.parts_data)
            for part_name in self.all_parts_used()
            if part_name not in self.parts_data
        }

    def assemblies_featuring(self, part):
        return [name for (name, parts) in self.assemblies.items()
                if part in parts]

    def assemblies_with_records(self):
        return OrderedDict([
            (name, [self.get_part_data(p)['record'] for p in parts])
            for name, parts in self.assemblies.items()
        ])

    def get_part_data(self, part_name):
        if part_name not in self.parts_data:
            candidates = did_you_mean(part_name, self.parts_data)
            if len(candidates) == 0:
                suggestions = ""
            else:
                candidates = ", ".join(candidates)
                suggestions = "Did you mean one of those ? %s" % candidates
            raise ValueError("Unknown part %s. %s." % (part_name, suggestions))
        return self.parts_data[part_name]

    def rename_part(self, part_name, new_name):
        for name, parts in self.assemblies.items():
            for i, part in enumerate(parts):
                if part == part_name:
                    parts[i] = new_name
        if self.parts_data is not None:
            if part_name in self.parts_data:
                self.parts_data[new_name] = self.parts_data.pop(part_name)

    @staticmethod
    def from_spreadsheet(filepath=None, dataframe=None, sheet_name=0,
                         header=None):
        if dataframe is None:
            if filepath.lower().endswith('.csv'):
                with open(filepath, 'r') as f:
                    dataframe = pandas.DataFrame([
                        line.split(',')
                        for line in f.read().split('\n')
                    ])
            else:
                dataframe = pandas.read_excel(filepath, sheet_name=sheet_name,
                                              header=header)
        return AssemblyPlan(OrderedDict([
            (row[0], [
                str(e)
                for e in row[1:]
                if str(e) not in ['-', 'nan', 'None', '']
            ])
            for i, row in dataframe.iterrows()
            if str(row[0]).lower() not in ['nan', 'construct name',
                                           'construct', 'none', '']
        ]))

    def to_spreadsheet(self, path):
        with open(path, "w") as f:
            f.write("\n".join([("construct,parts")] + [
                ",".join([asm] + parts)
                for asm, parts in self.assemblies.items()
            ]))

    def assemblies_per_part(self):
        result = {}
        for assembly, parts in self.assemblies.items():
            for part in parts:
                if part not in result:
                    result[part] = set()
                result[part].add(assembly)
        for part, assemblies in result.items():
            result[part] = sorted(assemblies)
        return result

    def write_report(self, target):
        all_parts_used = self.all_parts_used()
        assemblies_per_part = self.assemblies_per_part()
        sequenticon_dict = None
        parts_length_dict = None
        first_part_data = list(self.parts_data.values())[0]
        if 'record' in first_part_data:
            sequenticons = sequenticon_batch([
                self.get_part_data(p)['record']
                for p in all_parts_used
            ], output_format='html_image')
            sequenticon_dict = OrderedDict([(name, icon)
                                            for (name, icon) in sequenticons])
        if (('record' in first_part_data) or ('size' in first_part_data)):
            parts_length_dict = {
                part: human_seq_size(self.get_part_length(part))
                for part in all_parts_used
            }
        html = report_writer.pug_to_html(
            path=template_path("assembly_plan_report.pug"),
            assembly_plan=self,
            sequenticon_dict=sequenticon_dict,
            parts_length_dict=parts_length_dict,
            all_parts_used=all_parts_used,
            assemblies_per_part=assemblies_per_part
        )
        report_writer.write_report(html, target)

    def get_part_length(self, part_name):
        data = self.get_part_data(part_name)
        if 'size' in data:
            return data['size']
        else:
            return len(data['record'])
