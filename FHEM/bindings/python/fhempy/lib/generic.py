import asyncio
import functools
import inspect
import json
import os

from fhempy.lib import fhem

from . import utils

_README_CACHE = {}


class FhemModule:
    def __init__(self, logger):
        self.logger = logger
        try:
            self.loop = asyncio.get_running_loop()
        except RuntimeError:
            self.loop = None
        self._tasks = []
        self._conf_set = {}
        self._conf_attr = {}

    async def set_attr_config(self, attr_config):
        self._conf_attr = attr_config
        await utils.handle_define_attr(self._conf_attr, self, self.hash)

    async def set_set_config(self, set_config):
        self._conf_set = set_config
        await fhem.send_default_response(
            self.hash,
            await utils.handle_set(self._conf_set, self, self.hash, ["?"], {}),
        )

    async def set_icon(self, icon_name):
        curr_icon = await fhem.AttrVal(self.hash["NAME"], "icon", "")
        if curr_icon == "":
            await fhem.CommandAttr(self.hash, f"{self.hash['NAME']} icon {icon_name}")

    # FHEM FUNCTION
    async def FW_detailFn(self, hash, args, argsh):
        """Read current module help for each detail page, preserving Markdown."""
        FW_wname, d, room, pageHash = args

        if not hasattr(self, "hash"):
            return (
                "This device is disabled, set disable attribute "
                "to 0 or delete it to enable the device<br>"
            )

        ret = """<script type="text/javascript">
        function displayHelp() {
          var x = document.getElementById("fhempyReadme");
          if (x.style.display === "none") {
            x.style.display = "block";
          } else {
            x.style.display = "none";
          }
          var off = $("#fhempyReadme").position().top-20;
          $('body, html').animate({scrollTop:off}, 500);
        }
        
        $(document).ready(function() {
          $("#content").append('<div class="makeTable help" id="fhempyReadme"></div>');
          $("#fhempyReadme").html(###README_HELP_STRING###);
          document.getElementById("fhempyReadme").style.display = "none";

          var helpCmdStr = '###SET_CMD_CONFIG_STRING###';
          var helpCmdJson = JSON.parse(helpCmdStr);
          $("select.set").change(helpSetAction);
          function
          helpSetAction(){
            var cmd = $("select.set").val()
            if(helpCmdJson[cmd] && helpCmdJson[cmd].help) {
              if (document.getElementById("idCmdHelp")===null) {
                $('<div id="idCmdHelp" class="makeTable help"></div>')
                      .insertBefore("div.makeTable.internals");
              }
              $("div#idCmdHelp").html(helpCmdJson[cmd].help + "<br>");
            } else {
              $("div#idCmdHelp").remove();
            }
          }
          helpSetAction();

          var helpAttrStr = '###ATTR_CONFIG_STRING###';
          var helpAttrJson = JSON.parse(helpAttrStr);
          $("select.attr").change(helpAttrAction);
          function
          helpAttrAction(){
            var cmd = $("select.attr").val()
            if(helpAttrJson[cmd] && helpAttrJson[cmd].help) {
              if (document.getElementById("idAttrHelp")===null) {
                $('<div id="idAttrHelp" class="makeTable help"></div>')
                      .insertBefore("div.makeTable.attributes");
              }
              $("div#idAttrHelp").html(helpAttrJson[cmd].help + "<br>");
            } else {
              $("div#idAttrHelp").remove();
            }
          }
          helpAttrAction();

          var helpLink = document.getElementById("content")
            .getElementsByClassName("detLink");
          if (helpLink.length == 0) {
            helpLink = document.getElementById("content")
              .getElementsByClassName("detLink devSpecHelp");
            helpLink[0].innerHTML = '<div class="detLink devSpecHelp"><a href="#" onclick="displayHelp();return false;">Device specific help</a></div>';
          } else {
            helpLink[0].innerHTML = '<div class="detLink"><a href="#" onclick="displayHelp();return false;">Help for fhempy device ###DEVICETYPE###</a></div>';
          }
        });
        </script>"""
        js_set_conf = {}
        for key in self._conf_set:
            if "help" in self._conf_set[key]:
                js_set_conf[key] = {}
                js_set_conf[key]["help"] = (
                    self._conf_set[key]["help"]
                    .replace("\n", "<br>")
                    .replace("'", '"')
                    .replace('"', '\\"')
                )
        ret = ret.replace(
            "###SET_CMD_CONFIG_STRING###",
            json.dumps(js_set_conf),
        )
        js_attr_conf = {}
        for key in self._conf_attr:
            if "help" in self._conf_attr[key]:
                js_attr_conf[key] = {}
                js_attr_conf[key]["help"] = (
                    self._conf_attr[key]["help"]
                    .replace("\n", "<br>")
                    .replace("'", '"')
                    .replace('"', '\\"')
                )
        ret = ret.replace(
            "###ATTR_CONFIG_STRING###",
            json.dumps(js_attr_conf),
        )

        ret = ret.replace(
            "###DEVICETYPE###",
            self.hash["FHEMPYTYPE"],
        )

        # Reload on each detail page request so README edits need no restart.
        readme_str = await utils.run_blocking(
            functools.partial(self._get_readme_content)
        )
        ret = ret.replace(
            "###README_HELP_STRING###",
            json.dumps(readme_str).replace("<", "\\u003c"),
        )

        return ret

    def _get_readme_content(self):
        """Read and convert the module's Markdown, including fenced code blocks.

        Caches the rendered HTML keyed by file modification time (mtime) so
        that subsequent views avoid disk I/O and markdown parsing while edits
        to the README are still detected automatically without a restart.
        """
        import markdown2
        from fhempy import lib

        initfile = inspect.getfile(lib)
        fhempy_root = os.path.dirname(initfile)
        fhempy_type = self.hash["FHEMPYTYPE"]
        readme_path = os.path.join(fhempy_root, fhempy_type, "README.md")
        try:
            mtime = os.path.getmtime(readme_path)
            cached = _README_CACHE.get(fhempy_type)
            if cached and cached[0] == mtime:
                return cached[1]

            with open(readme_path, "r", encoding="utf-8") as f:
                readme_md = f.read()

            readme_str = markdown2.markdown(readme_md, extras=["fenced-code-blocks"])
            _README_CACHE[fhempy_type] = (mtime, readme_str)
            return readme_str
        except FileNotFoundError:
            _README_CACHE.pop(fhempy_type, None)
            return f"No README.md file found for {fhempy_type}."

    @staticmethod
    def validate_define(args, argsh):
        """Optionally return an error/usage string, or None for valid arguments.

        This must be a quick, synchronous argument check without I/O or state
        changes. The binding calls it before replacing an initialized device
        of the same type, and after loading a module for a new device. First
        loads are already acknowledged; their errors are reported in state.

        Keep validation rules and usage text in the module. Define may reuse
        this hook, including when running with an older binding. Modules that
        do not override it retain their existing behaviour.
        """
        return None

    # FHEM FUNCTION
    async def Define(self, hash, args, argsh):
        self.hash = hash
        self._defargs = args
        self._defargsh = argsh

        # send set to fhem if set_set_config wasn't used before
        if self._conf_set == {}:
            await self.set_set_config(self._conf_set)

        info = await utils.handle_define_attr(
            self._conf_attr, self, self.hash, {"room": "", "group": ""}
        )
        if info["init_done"] == 1:
            if info["attr"]["room"] == "":
                await fhem.CommandAttr(self.hash, f"{self.hash['NAME']} room fhempy")
            if info["attr"]["group"] == "":
                await fhem.CommandAttr(
                    self.hash,
                    (f"{self.hash['NAME']} group " f"{self.hash['FHEMPYTYPE']}"),
                )

    # FHEM FUNCTION
    async def Attr(self, hash, args, argsh):
        return await utils.handle_attr(self._conf_attr, self, hash, args, argsh)

    # FHEM FUNCTION
    async def Set(self, hash, args, argsh):
        return await utils.handle_set(self._conf_set, self, hash, args, argsh)

    def create_async_task(self, coro):
        task = asyncio.create_task(
            self._run_coro(coro), name=getattr(coro, "__qualname__", None)
        )
        task.add_done_callback(self._handle_task_result)
        self._tasks.append(task)
        return task

    async def _run_coro(self, coro):
        try:
            await coro
        except asyncio.CancelledError:
            pass

    def _handle_task_result(self, task):
        if task in self._tasks:
            self._tasks.remove(task)
        try:
            task.result()
        except asyncio.CancelledError:
            pass
        except Exception:
            self.logger.exception(
                f"Background task {task.get_name()} stopped because of an error"
            )

    def track_async_task(self, task):
        """Cancel an already running task on Undefine, e.g. a Set which
        continues in the background."""
        self._tasks.append(task)
        task.add_done_callback(self._untrack_task)

    def _untrack_task(self, task):
        if task in self._tasks:
            self._tasks.remove(task)

    def cancel_async_task(self, task):
        if task in self._tasks:
            self._tasks.remove(task)
        task.cancel()

    # FHEM FUNCTION
    async def Undefine(self, hash):
        # cancel all tasks, Define might be called again (attr disable 0)
        tasks = self._tasks
        self._tasks = []
        for task in tasks:
            task.cancel()
