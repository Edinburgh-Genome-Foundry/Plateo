from .picklist_from_labcyte_echo_logfile import \
    picklist_from_labcyte_echo_logfile
from .plate_from_tables import plate_from_platemap_spreadsheet

def plate_volumes_from_labcyte_echo_logfile(logfile=None, logcontent=None,
                                            plates_dict=None,
                                            data_field="volume_left"):
    """Return a plate with the volume left in each well after dispenses.

    Parameters
    ----------

    Parameters
    ----------

    logfile
      The path to the echo logfile.

    logcontent
      Echo logfile content, can be provided instead of filename

    plates_dict
      A dictionary of the form {'Plate name': Plate()} linking the plate names
      found in the Echo logs to Plateo Plate objects. If None is provided,
      plates are infered from the Echo logs (a bit experimental).

    data_field
      The well data field that will contain the "volume left" at the end.

    """
    picklist = picklist_from_labcyte_echo_logfile(logfile=logfile,
                                                  logcontent=logcontent)
    source_plates = set([t.source_plate for t in picklist.transfers_list])
    source_plate = list(source_plates)[0]
    for transfer in picklist.transfers_list:
        volume = transfer.data['Current Fluid Volume']*1e-6
        source_plate[transfer.source_well.name].data[data_field] = volume
    return source_plate


def plate_volumes_from_labcyte_echo_survey(filepath=None):
    plate = plate_from_platemap_spreadsheet(filepath, data_field='volume_muL',
                                            skiprows=3)
    def volume(well):
        if 'volume_muL' in well.data:
            return 1e-6 * well.data["volume_muL"]
        else:
            return None

    plate.compute_data_field("volume", volume)
    return plate
