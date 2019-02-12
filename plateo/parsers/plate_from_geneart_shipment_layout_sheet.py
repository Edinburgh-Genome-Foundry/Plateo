import pandas
import flametree
from ..containers import Plate96

def parts_ids_from_geneart_records_dir(folder):
    records_root = flametree.file_tree(folder)
    return {
        dir_._name.split("_")[0]: "_".join(dir_._name.split("_")[1:])
        for dir_ in records_root._dirs
    }

def plates_from_geneart_shipment_layout_sheet(filepath, parts_ids_dict=None,
                                              geneart_parts_dir=None):
    """Return a list of all plates (Plate96) in the shipment layout sheet.
    
    Example
    -------

    >>> plates = plates_from_geneart_shipment_layout_spreadsheet(
    >>>     filepath="2018AAMOBC_layout_shipment.xlsx",
    >>>     geneart_parts_dir="./tfcdownload(4).zip")
    >>> # Write the plates in reformatted format:
    >>> for plate in plates:
    >>>     plate_to_content_spreadsheet(plate, "./%s.xlsx" % plate.name)
    Parameters
    ----------
    
    filepath
      Path to the Geneart excel spreadsheet or a filelike.
    
    parts_ids_dict
      Optional. dictionnary {geneart_id: part_name}. If provided, the content
      of the wells will be indicated using your custom part_name, if not
      provided, the genart_id will be used.
    
    geneart_parts_dir
      Optional path to a folder, zip file, or Flametree-compatible dir, from
      which to read filenames like "18AFY2AC_p9_EGFP" from which the
      association between geneart IDs(here, 18AFY2AC) and your part names
      (p9_EGFP) will be read.

    
    """
    if geneart_parts_dir is not None:
        parts_ids_dict = parts_ids_from_geneart_records_dir(geneart_parts_dir)
    plates_data = pandas.read_excel(filepath, skiprows=2)
    plates_indices = sorted(set(plates_data.Plate))
    plates = {index: Plate96(name="Plate %d" % index)
              for index in plates_indices}
    for index, plate in plates.items():
        subdata = plates_data[plates_data.Plate == index]
        for i, row in subdata.iterrows():
            well = plate.wells[row.Pos]
            well.data = {
                k: row[k]
                for k in ('OC_Number', 'IDAuftrag', 'IDConstruct')
            }
            volume_microl = row['Volume shiped [µl]']
            volume_in_l = volume_microl * 1e-6
            quantity = volume_microl * row['Conzentration [µg/µl]'] * 1e-6
            part_label = row.IDAuftrag
            if parts_ids_dict is not None:
                part_label = parts_ids_dict[row.IDConstruct]
            else:
                part_label = row.IDConstruct
            well.add_content({part_label: quantity}, volume=volume_in_l)
    return [plate for i, plate in sorted(plates.items())]