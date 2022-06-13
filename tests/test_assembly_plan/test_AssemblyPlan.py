import matplotlib

matplotlib.use("Agg")

from plateo import AssemblyPlan
import os

this_dir = os.path.join("tests", "test_assembly_plan")


def test_AssemblyPlan_from_xls_spreadsheet():
    asm_plan_xls = os.path.join(this_dir, "assembly_plan.xls")
    plan_xls = AssemblyPlan.from_spreadsheet(asm_plan_xls)
    assert [len(v) for v in plan_xls.assemblies.values()] == [4, 4, 5]


def test_AssemblyPlan_from_csv_spreadsheet():
    asm_plan_csv = os.path.join(this_dir, "assembly_plan.csv")
    plan_csv = AssemblyPlan.from_spreadsheet(asm_plan_csv)
    assert [len(v) for v in plan_csv.assemblies.values()] == [4, 4, 5]


def test_AssemblyPlan_from_xlsx_spreadsheet():
    asm_plan_xls = os.path.join(this_dir, "assembly_plan.xlsx")
    plan_xls = AssemblyPlan.from_spreadsheet(asm_plan_xls)
    assert [len(v) for v in plan_xls.assemblies.values()] == [4, 4, 5]
