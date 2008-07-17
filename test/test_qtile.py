import os, time
import libpry
import libqtile, libqtile.config
import utils

class MaxConfig(libqtile.config.Config):
    groups = ["a", "b", "c", "d"]
    layouts = [libqtile.Max()]
    keys = [
        libqtile.Key(["control"], "k", libqtile.Command("max_next")),
        libqtile.Key(["control"], "j", libqtile.Command("max_previous")),
    ]
    screens = []


class uCommon(utils.QTileTests):
    """
        We don't care if these tests run in a Xinerama or non-Xinerama X.
    """
    config = MaxConfig()
    def test_events(self):
        assert self.c.status() == "OK"

    def test_keypress(self):
        self.testWindow("one")
        self.testWindow("two")
        v = self.c.simulate_keypress(["unknown"], "j")
        assert v.startswith("Unknown modifier")
        assert self.c.groupinfo("a")["focus"] == "two"
        self.c.simulate_keypress(["control"], "j")
        assert self.c.groupinfo("a")["focus"] == "one"

    def test_spawn(self):
        assert self.c.spawn("true") == None

    def test_kill(self):
        self.testWindow("one")
        self.testwindows = []
        self.c.kill()
        self.c.sync()
        for i in range(20):
            if self.c.clientcount() == 0:
                break
            time.sleep(0.1)
        else:
            raise AssertionError("Window did not die...")


class uQTile(utils.QTileTests):
    config = MaxConfig()
    def test_mapRequest(self):
        self.testWindow("one")
        info = self.c.groupinfo("a")
        assert "one" in info["clients"]
        assert info["focus"] == "one"

        self.testWindow("two")
        info = self.c.groupinfo("a")
        assert "two" in info["clients"]
        assert info["focus"] == "two"

    def test_unmap(self):
        one = self.testWindow("one")
        two = self.testWindow("two")
        three = self.testWindow("three")
        info = self.c.groupinfo("a")
        assert info["focus"] == "three"

        assert self.c.clientcount() == 3
        self.kill(three)

        assert self.c.clientcount() == 2
        info = self.c.groupinfo("a")
        assert info["focus"] == "two"

        self.kill(two)
        assert self.c.clientcount() == 1
        info = self.c.groupinfo("a")
        assert info["focus"] == "one"

        self.kill(one)
        assert self.c.clientcount() == 0
        info = self.c.groupinfo("a")
        assert info["focus"] == None

    def test_setgroup(self):
        self.testWindow("one")
        assert self.c.pullgroup("nonexistent") == "No such group"
        self.c.pullgroup("b")
        if self.c.screencount() == 1:
            assert self.c.groupinfo("a")["screen"] == None
        else:
            assert self.c.groupinfo("a")["screen"] == 1
        assert self.c.groupinfo("b")["screen"] == 0
        self.c.pullgroup("c")
        assert self.c.groupinfo("c")["screen"] == 0

    def test_unmap_noscreen(self):
        self.testWindow("one")
        pid = self.testWindow("two")
        assert self.c.clientcount() == 2
        self.c.pullgroup("c")
        assert self.c.clientcount() == 2
        self.kill(pid)
        assert self.c.clientcount() == 1
        assert self.c.groupinfo("a")["focus"] == "one"

    def test_restart(self):
        self.testWindow("one")
        self.testWindow("two")
        self.c.restart()

        #assert self.c.clientcount() == 2


class uKey(libpry.AutoTree):
    def test_init(self):
        libpry.raises(
            "unknown key",
            libqtile.Key,
            [], "unknown", libqtile.Command("foo")
        )
        libpry.raises(
            "unknown modifier",
            libqtile.Key,
            ["unknown"], "x", libqtile.Command("foo")
        )


tests = [
    utils.XNest(xinerama=True), [
        uQTile(),
    ],
    utils.XNest(xinerama=False), [
        uCommon(),
        uQTile()
    ],
    uKey()
]
