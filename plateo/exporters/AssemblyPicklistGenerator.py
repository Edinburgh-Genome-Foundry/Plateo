from ..PickList import PickList
from ..Well import TransferError
from ..tools import round_at, did_you_mean


class AssemblyPicklistGenerator:

    def __init__(self, part_mol=None, part_l=None, part_g=None,
                 complement_to=None, buffer_volume=0, volume_rounding=None,
                 minimal_dispense_volume=0):

        self.part_mol = part_mol
        self.part_l = part_l
        self.part_g = part_g
        self.buffer_volume = buffer_volume
        self.complement_to = complement_to
        self.volume_rounding = volume_rounding
        self.minimal_dispense_volume = minimal_dispense_volume

    def make_picklist(self, assembly_plan, source_wells, destination_wells,
                      buffer_well=None, complement_well=None):
        source_wells = list(source_wells)
        destination_wells = list(destination_wells)
        destination_wells = destination_wells[:len(assembly_plan.assemblies)]

        part_wells = {}
        duplicates = {}
        for well in source_wells:
            well_part = self.get_part_from_well(well)
            if well_part in part_wells:
                if well_part not in duplicates:
                    duplicates[well_part] = []
                duplicates[well_part].append(well.name)
                previous_well = part_wells[well_part]
                previous_concentration = previous_well.content.concentration()
                if well.content.concentration() > previous_concentration:
                    part_wells[well_part] = well
            else:
                part_wells[well_part] = well

        required_parts = set(assembly_plan.all_parts_used())
        missing_parts = required_parts.difference(set(part_wells))
        if missing_parts:
            return None, {'missing_parts': {
                part: {
                    'featured_in': assembly_plan.assemblies_featuring(part),
                    'did_you_mean': [
                        (name, str(part_wells[name]))
                        for name in did_you_mean(
                            part, part_wells, min_score=50)
                    ]
                }
                for part in missing_parts
            }}

        picklist = PickList()
        iterator = zip(assembly_plan.assemblies.items(), destination_wells)
        for ((construct_name, parts), destination_well) in iterator:
            destination_well.data.construct = construct_name
            for part in parts:
                source_well = part_wells[part]
                volume = self.volume_from_well(source_well,
                                               assembly_plan.parts_data)
                volume = round_at(volume, self.volume_rounding)
                volume = max(volume, self.minimal_dispense_volume)
                picklist.add_transfer(source_well, destination_well,
                                      volume=volume)

        wells_over_desired_volume = []
        if self.complement_to is not None:
            if complement_well is None:
                for label in 'COMPLEMENT', 'WATER':
                    complement_well = part_wells.get(label, None)
                if complement_well is None:
                    raise ValueError("Could not identify the complement well.")
            if complement_well.is_empty:
                raise TransferError("Empty complement well: %s."
                                    % (complement_well))
            for well in destination_wells:
                to_well = picklist.restricted_to(destination_well=well)
                total_transfer_volume = to_well.total_transfered_volume()
                complement_volume = (self.complement_to -
                                     total_transfer_volume -
                                     self.buffer_volume)
                if complement_volume < 0:
                    wells_over_desired_volume.append(well)
                else:
                    picklist.add_transfer(source_well=complement_well,
                                          destination_well=well,
                                          volume=complement_volume)
        if self.buffer_volume:
            if buffer_well is None:
                buffer_well = part_wells.get('BUFFER', None)
            if buffer_well.is_empty:
                raise TransferError("Empty buffer well: %s." % (buffer_well))
            buffer_volume = round_at(self.buffer_volume, self.volume_rounding)
            for well in destination_wells:
                picklist.add_transfer(buffer_well, well, volume=buffer_volume)

        return picklist, {
            'wells_over_desired_volume': wells_over_desired_volume,
            'duplicates': {
                part_name: {
                    'wells': wells,
                    'selected': part_wells[part_name]
                }
                for part_name, wells in duplicates.items()
            }
        }

    @staticmethod
    def get_part_from_well(well):
        if 'part' in well.data:
            return well.data['part']
        else:
            return well.content.components_as_string()

    def get_part_molar_weight(self, part_data):
        """Returns the molar weight of the sequence in g/m.
        http://cels.uri.edu/gsc/cndna.html
        """
        if 'size' in part_data:
            size = part_data['size']
        else:
            size = len(part_data['record'])
        return 650 * size

    def volume_from_well(self, well, parts_data):
        part_mol = self.part_mol
        part_g = self.part_g
        part_l = self.part_l
        if part_mol is not None:
            part = self.get_part_from_well(well)
            molar_weight = self.get_part_molar_weight(parts_data[part])
            part_g = molar_weight * part_mol
        if part_g is not None:
            part_l = part_g / well.content.concentration()
        return part_l
