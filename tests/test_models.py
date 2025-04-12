from mkdocstrings_handlers.graphql._internal.models import Node, Schema


class TestSchema:
    def test_glob(self) -> None:
        member_1 = Node(name="name1", path="path1")
        member_2 = Node(name="name2", path="path2")
        member_3 = Node(name="name3", path="path3")
        members = {"include.member1": member_1, "include.member2": member_2, "exclude.member3": member_3}

        schema = Schema(members=members)
        globbed = list(schema.glob("include.*"))

        assert len(globbed) == 2
        assert globbed == [member_1, member_2]
