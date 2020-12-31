import asyncio
import json

from . import utils


class FhemModule:
    def __init__(self, logger):
        self.logger = logger
        self.loop = asyncio.get_event_loop()
        self._tasks = []
        self._conf_set = {}
        self._conf_attr = {}

    def set_attr_config(self, attr_config):
        self._conf_attr = attr_config

    def set_set_config(self, set_config):
        self._conf_set = set_config

    # FHEM FUNCTION
    async def FW_detailFn(self, hash, args, argsh):
        (FW_wname, d, room, pageHash) = args
        ret = """<script type="text/javascript">
        $(document).ready(function() {
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
        });
        </script>"""
        js_set_conf = {}
        for key in self._conf_set:
            if "help" in self._conf_set[key]:
                js_set_conf[key] = {}
                js_set_conf[key]["help"] = self._conf_set[key]["help"]
        ret = ret.replace(
            "###SET_CMD_CONFIG_STRING###",
            json.dumps(js_set_conf),
        )
        js_attr_conf = {}
        for key in self._conf_attr:
            if "help" in self._conf_attr[key]:
                js_attr_conf[key] = {}
                js_attr_conf[key]["help"] = self._conf_attr[key]["help"]
        ret = ret.replace(
            "###ATTR_CONFIG_STRING###",
            json.dumps(js_attr_conf),
        )
        return ret

    # FHEM FUNCTION
    async def Define(self, hash, args, argsh):
        self.hash = hash
        await utils.handle_define_attr(self._conf_attr, self, hash)

    # FHEM FUNCTION
    async def Attr(self, hash, args, argsh):
        return await utils.handle_attr(self._conf_attr, self, hash, args, argsh)

    # FHEM FUNCTION
    async def Set(self, hash, args, argsh):
        return await utils.handle_set(self._conf_set, self, hash, args, argsh)

    def create_async_task(self, coro):
        task = asyncio.create_task(coro)
        self._tasks.append(task)
        return task

    def cancel_async_task(self, task):
        self._tasks.remove(task)
        task.cancel()

    # FHEM FUNCTION
    async def Undefine(self, hash):
        # cancel all tasks
        for task in self._tasks:
            task.cancel()
