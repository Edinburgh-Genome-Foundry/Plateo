import pandas as pd
from ..PlateLayout import PlateLayout

def plate_from_aati_fragment_analyzer_peaktable(filename):
    df = pd.read_csv(filename)
    df = df[pd.notnull(df["% (Conc.)"])]
    wells = {
        name: {"bands": {
            peak_id: row.to_dict()
            for peak_id, row in d.set_index("Peak ID").iterrows()
        }}
        for name, d in df.groupby(["Well"])
    }
    from plate_converter import PlateLayout
    return PlateLayout(96, wells_metadata=wells)




def parse_fragment_analyzer_peaktable(filename):
    # legacy

    def _find_fa_output_blocks(filename):
        with open(filename, "r") as f:
            lines = [line.strip().split(",") for line in f.readlines()]
        blocs_beginnings = [0] + [
            i
            for i in range(2, len(lines))
            if (lines[i - 1][0] == '') and (lines[i][0] != '')
        ] + [len(lines)]
        blocks = [
            lines[a:b]
            for a, b in zip(blocs_beginnings, blocs_beginnings[1:])
        ]
        return blocks


    def _treat_fa_output_block(lines):
        block = {
            "well_name": lines[0][0].strip(":"),
            "label": lines[0][1],
            "peaks": {},
            "attributes": {}
        }
        labels = ("id", "size", "%concentration", "nmole/L", "ng/ul", "RFU")
        for line in lines[2:]:
            if line[0] != '':
                peak = dict(zip(labels, line))
                if " " in peak["size"]:
                    peak["size"], peak["label"] = peak["size"].split()
                else:
                    peak["label"] = ""
                if peak["%concentration"] == '':
                    peak["%concentration"] = 0

                types = {
                    "id": int,
                    "size": int,
                    "%concentration": float,
                    "nmole/L": float,
                    "ng/ul": float,
                    "RFU": int
                }
                for field, ftype in types.items():
                    peak[field] = ftype(peak[field])
                block["peaks"][peak["id"]] = peak

            if line[1].startswith(("TIM", "TIC", "Total Conc.")):
                field, quantity, unit = line[1][:-1], float(line[2]), line[3]
                block["attributes"][field] = {
                    "field": field,
                    "quantity": quantity,
                    "unit": unit
                }
        return block

    blocks = [
        _treat_fa_output_block(block)
        for block in _find_fa_output_blocks(filename)
    ]

    return {
        block["well_name"]: block
        for block in blocks
    }
