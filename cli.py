print("cli")
import lib

lin1 = lib.Lineage()


exporter = lib.ImExPorter()
lineages = exporter.importProgress("family_tree_2024-10-21_17-31-27.xml")

for i in lineages:
    print(i)
# Call saveProgress using the instance
