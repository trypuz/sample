from oblib import taxonomy
from dataclasses import dataclass
from typing import List
import sys


@dataclass
class Child(object):
    pass


@dataclass
class Table(object):

    name: str
    pks: List[str]
    pk_values_enum: List[List[str]]
    members: List[str]
    children: List[Child]


@dataclass
class Abstract(Child):

    name: str
    members: List[str]
    tables: List[Table]
    children: List[Child]


@dataclass
class OB(object):

    abstracts: List[Abstract]
    tables: List[Table]


tax = taxonomy.Taxonomy()

def abstract_relationships(entrypoint, abstracts):

    relationships = tax.semantic.get_entrypoint_relationships(entrypoint)
    if relationships is None:
        print("Entry Point command line argument does not exist in Taxonomy.")
        return []

    for r in relationships:
        f = r.from_.split(":")[1]
        t = r.to.split(":")[1]
        if f.endswith("Abstract") and t.endswith("Abstract"):
            parent = None
            child = None
            for item in abstracts.items():
                if item[1].name == f.replace("Abstract", ""):
                    parent = item[1]
                if item[1].name == t.replace("Abstract", ""):
                    child = item[1]
            if parent.children:
                parent.children.append(child)
            else:
                parent.children = [child]


def table_relationships(entrypoint, abstracts):

    relationships = tax.semantic.get_entrypoint_relationships(entrypoint)
    if relationships is None:
        print("Entry Point command line argument does not exist in Taxonomy.")
        return []

    for r in relationships:
        f = r.from_.split(":")[1]
        t = r.to.split(":")[1]
        if f.endswith("LineItems") and t.endswith("Abstract"):
            parent = None
            child = None
            for item in abstracts.items():
                if item[1].tables:
                    for table in item[1].tables:
                        # TODO: Fix brittle code which assumes that LineItems and Table name is always identically prefixed
                        # This is the cause of the warning: "Warning - parent/child relationship not found"
                        if table.name == f.replace("LineItems", ""):
                            parent = table
                            break

                        # for member in table.members:
                        #     if member == f.replace("LineItems", ""):
                        #         parent = table
                        #         break
            for item in abstracts.items():
                if item[1].name == t.replace("Abstract", ""):
                    child = item[1]

            if not parent or not child:
                print("  Warning - parent/child relationship not found", parent, child)
            else:
                if parent.children:
                    parent.children.append(child)
                else:
                    parent.children = [child]


def create_abstracts(entrypoint):

    relationships = tax.semantic.get_entrypoint_relationships(entrypoint)
    if relationships is None:
        print("Entry Point command line argument does not exist in Taxonomy.")
        return []

    abstracts = {}
    last_abstract = None
    last_table = None
    pk_count = -1
    for r in relationships:
        f = r.from_.split(":")[1]
        t = r.to.split(":")[1]
        if r.role.value == "domain-member" and f.endswith("Abstract"):
            name = f.replace("Abstract", "")
            if name in abstracts:
                if not t.endswith("LineItems"):
                    abstracts[name].members.append(t)
                last_abstract = abstracts[name]
            else:
                if t.endswith("LineItems"):
                    abstracts[name] = Abstract(name, [], None, None)
                else:
                    abstracts[name] = Abstract(name, [t], None, None)
                last_abstract = abstracts[name]
        elif r.role.value == "domain-member" and f.endswith("LineItems"):
            last_table.members.append(t.replace("Abstract", "(A)"))
        elif r.role.value == "domain-member" and f.endswith("Domain"):
            if last_table.pk_values_enum == None:
                last_table.pk_values_enum = [[]]
                for i in range(1, pk_count+1):
                    last_table.pk_values_enum.append([])
            last_table.pk_values_enum[pk_count].append(t.replace("Member", ""))
        elif r.role.value == "all":
            if last_abstract.tables == None:
                last_abstract.tables = []
            last_table = Table(t.replace("Table", ""), [], None, [], None)
            last_abstract.tables.append(last_table)
            pk_count = -1
        elif r.role.value == "dimension-domain":
            pass
        elif r.role.value == "hypercube-dimension":
            last_table.pks.append(t.replace("Axis", ""))
            pk_count += 1
            if last_table.pk_values_enum:
                last_table.pk_values_enum.append([])

    abstract_relationships(entrypoint, abstracts)
    table_relationships(entrypoint, abstracts)

    return abstracts


if __name__ == "__main__":

    if len(sys.argv) != 2:
        print("Incorrect number of arguments - 2 required")
        print("  Entrypoint")
        sys.exit(1)

    entrypoint = sys.argv[1]
    abstracts = create_abstracts(entrypoint)
    for item in abstracts.items():
        print(item[1])
    print()

