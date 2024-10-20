from lib import Lineage, Person


lin = Lineage()

child = Person(1,'Elias','2005-07-31',True,'White Other')

lin.add_person(child)

print(child.name)