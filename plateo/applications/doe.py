"""Design of Experiments."""

import pandas
from ..parsers.picklist_from_tables import columnnames


def convert_valuetable_to_volumetable(valuetable, source_plate=None):
    # If all values are volumes, then a source plate is not required.

    factor_wells_dict = {}
    if source_plate is not None:
        source_wells = list(source_plate.iter_wells())
        for well in source_wells:
            # assumed there is only 1 component in each source well:
            factor_wells_dict[well.content.components_as_string()] = well

    # 1 microliter = 1e-6 L
    # 'units' is the default name for a special line in the valuetable
    unit_line = "units"
    unit_dict = {index: value for index, value in valuetable.loc[unit_line].items()}
    # SI unit: (multiplier, type)
    unit_interpreter = {
        "L": (1, "volume"),
        "mL": (1e-3, "volume"),
        "uL": (1e-6, "volume"),
        "nL": (1e-9, "volume"),
        "g": (1, "mass"),
        "mg": (1e-3, "mass"),
        "ug": (1e-6, "mass"),
        "ng": (1e-9, "mass"),
        "g-L": (1, "concentration"),
        "ng-uL": (1e-3, "concentration"),
    }
    # we use "-" as the division sign; see plate_to_content_spreadsheet()

    volume_list = []  # collect "series" to construct the final dataframe

    # Get rows to subset df to actual values (factor levels):
    # 'final_volume' and 'complement' are special columns in the valuetable
    # 'final_volume' is in uL
    factor_columns = [
        factor
        for factor in valuetable.columns
        if factor not in ["complement", "final_volume"]
    ]
    expunit_rows = [
        expunit for expunit in valuetable.index if expunit not in [unit_line]
    ]
    for index, row in valuetable.loc[expunit_rows, factor_columns].iterrows():
        if index == unit_line:
            continue
        volumes = []  # collect calculated volumes for an experimental unit
        for factor in factor_columns:
            # VOLUME
            unit_type = unit_interpreter[unit_dict[factor]][1]
            if unit_type == "volume":
                multiplier = unit_interpreter[unit_dict[factor]][0]
                volumes += [float(row[factor]) * multiplier]
            # MASS
            elif unit_type == "mass":
                multiplier = unit_interpreter[unit_dict[factor]][0]
                mass = float(row[factor]) * multiplier
                concentration = factor_wells_dict[factor].content.concentration()
                volume = mass / concentration
                volumes += [volume]
            # CONCENTRATION
            elif unit_type == "concentration":
                multiplier = unit_interpreter[unit_dict[factor]][0]
                final_concentration = float(row[factor]) * multiplier
                mass = final_concentration * unit_dict["final_volume"] * 1e-6
                concentration = factor_wells_dict[factor].content.concentration()
                volume = mass / concentration
                volumes += [volume]

        complement_volume = unit_dict["final_volume"] * 1e-6 - sum(volumes)
        # 'final_volume' is in uL, need to convert to L

        volumes += [complement_volume]

        volume_list += [volumes]

    columnnames = factor_columns + [unit_dict["complement"]]
    volumetable = pandas.DataFrame(
        columns=columnnames, index=expunit_rows, data=volume_list
    )

    return volumetable


def import_valuetable_from_csv(filename):
    valuetable = pandas.read_csv(filename, index_col=0)

    return valuetable


def convert_volumetable_to_actiontable(volumetable, source_plate, dest_plate):
    """Convert a volume-based transfer table into an action-based format."""
    # This also labels the destination plate wells with the experimental unit names.

    factor_wells_dict = {}
    source_wells = list(source_plate.iter_wells())
    for well in source_wells:
        # assumed there is only 1 component in each source well:
        factor_wells_dict[well.content.components_as_string()] = well

    # Sanity check volumes:
    for column in volumetable.columns:
        source_well_content_volume = factor_wells_dict[column].volume
        if sum(volumetable[column]) > source_well_content_volume:
            raise Exception("Not enough material in source plate: %s" % column)

    # Check if we have enough destination wells:
    number_of_expunits = volumetable.shape[0]  # Shape = N_rows, N_columns
    if number_of_expunits > len(dest_plate.wells):
        raise Exception(
            "Not enough wells in destination plate: %d > %d"
            % (number_of_expunits, len(dest_plate.wells))
        )

    expunit_dest_well_dict = {}
    iterator = zip(volumetable.index, dest_plate.iter_wells(direction="column"))
    for expunit, destination_well in iterator:
        expunit_dest_well_dict[expunit] = destination_well
        destination_well.data["expunit"] = expunit  # for exporting the plate

    transfer_list = []
    volumetable_columns = volumetable.columns.tolist()
    for expunit, row in volumetable.iterrows():
        for factor in volumetable_columns:
            transfer_volume = row[factor]
            # Action-based specification:
            transfer = [
                source_plate.name,
                factor_wells_dict[factor].name,
                dest_plate.name,
                expunit_dest_well_dict[expunit].name,
                transfer_volume,
            ]
            transfer_list += [transfer]

    actiontable = pandas.DataFrame(columns=columnnames, data=transfer_list)

    return actiontable


def import_volumetable_from_csv_file(filename, unit=1e-6):
    # 1 microliter = 1e-6 L
    volumetable = pandas.read_csv(filename, index_col=0)
    volumetable = volumetable * unit

    return volumetable
