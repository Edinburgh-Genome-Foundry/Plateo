"""Design of Experiments."""

import pandas
from ..parsers.picklist_from_tables import columnnames


def volumetable_from_valuetable(valuetable, source_plate):
    # 1 microliter = 1e-6 L
    pass


def valuetable_from_csv(filename):
    valuetable = pandas.read_csv(filename, index_col=0)

    return valuetable


def dataframe_from_volume_table(volumetable, source_plate, dest_plate):
    """Convert a volume-based transfer table into an action-based format."""

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

    transfer_list = []
    volumetable_columns = volumetable.columns.tolist()
    for expunit, row in volumetable.iterrows():
        for factor in volumetable_columns:
            transfer_volume = row[factor]
            # Action-based specification:
            transfer = [
                source_plate.name,
                factor_wells_dict[factor].name,
                transfer_volume,
                dest_plate.name,
                expunit_dest_well_dict[expunit].name,
            ]
            transfer_list += [transfer]

    dataframe = pandas.DataFrame(columns=columnnames, data=transfer_list)

    return dataframe


def volumetable_from_csv_file(filename, unit=1e-6):
    # 1 microliter = 1e-6 L
    volumetable = pandas.read_csv(filename, index_col=0)
    volumetable = volumetable * unit

    return volumetable
