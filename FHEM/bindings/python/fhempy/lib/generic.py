import asyncio
import functools
import inspect
import json
import os

import markdown2
from fhempy.lib import fhem

from . import utils


class FhemModule:
    def __init__(self, logger):
        self.logger = logger
        self.loop = asyncio.get_event_loop()
        self._tasks = []
        self._conf_set = {}
        self._conf_attr = {}
        self.readme_str = None

    def set_attr_config(self, attr_config):
        self._conf_attr = attr_config

    def set_set_config(self, set_config):
        self._conf_set = set_config

    # FHEM FUNCTION
    async def FW_detailFn(self, hash, args, argsh):
        (FW_wname, d, room, pageHash) = args
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
          $("#fhempyReadme").html(`###README_HELP_STRING###`);
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
            .getElementsByClassName("detLink devSpecHelp");
          helpLink[0].innerHTML = '<div class="detLink devSpecHelp"><a href="#" onclick="displayHelp();return false;">Device specific help</a></div>';
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

        # add readme as help
        if False and self.readme_str is not None:
            ret = ret.replace(
                "###README_HELP_STRING###",
                self.readme_str.replace("\n", "<br>")
                .replace("\\", "\\\\")
                .replace("`", "\\`"),
            )

        return ret

    def _get_readme_content(self):
        from fhempy import lib

        initfile = inspect.getfile(lib)
        fhempy_root = os.path.dirname(initfile)
        try:
            readme_md = ""
            with open(
                fhempy_root + "/" + self.hash["FHEMPYTYPE"] + "/README.md", "r"
            ) as f:
                readme_md = f.read()

            readme_str = markdown2.markdown(readme_md)
            return readme_str
            # make_html_images_inline(
            #    readme_str, fhempy_root + "/" + self.hash["FHEMPYTYPE"] + "/"
            # )

        except FileNotFoundError:
            return f"No README.md file found for {self.hash['FHEMPYTYPE']}."

    # FHEM FUNCTION
    async def Define(self, hash, args, argsh):
        self.hash = hash
        self._defargs = args
        self._defargsh = argsh
        check_init_done = await fhem.init_done(self.hash)
        if check_init_done == 1:
            if await fhem.AttrVal(self.hash["NAME"], "room", "") == "":
                await fhem.CommandAttr(self.hash, f"{self.hash['NAME']} room fhempy")
            if await fhem.AttrVal(self.hash["NAME"], "group", "") == "":
                await fhem.CommandAttr(
                    self.hash,
                    (f"{self.hash['NAME']} group " f"{self.hash['FHEMPYTYPE']}"),
                )
        self.readme_str = await utils.run_blocking(
            functools.partial(self._get_readme_content)
        )
        await utils.handle_define_attr(self._conf_attr, self, hash)

    # FHEM FUNCTION
    async def Attr(self, hash, args, argsh):
        return await utils.handle_attr(self._conf_attr, self, hash, args, argsh)

    # FHEM FUNCTION
    async def Set(self, hash, args, argsh):
        return await utils.handle_set(self._conf_set, self, hash, args, argsh)

    def create_async_task(self, coro):
        task = asyncio.create_task(self._run_coro(coro))
        task.add_done_callback(self._handle_task_result)
        self._tasks.append(task)
        return task

    async def _run_coro(self, coro):
        try:
            await coro
        except asyncio.CancelledError:
            pass

    def _handle_task_result(self, task):
        try:
            task.result()
        except asyncio.CancelledError:
            pass
        except Exception:
            self.logger.exception("Exception raised by task: %r", task)

    def cancel_async_task(self, task):
        self._tasks.remove(task)
        task.cancel()

    # FHEM FUNCTION
    async def Undefine(self, hash):
        # cancel all tasks
        for task in self._tasks:
            task.cancel()
