from fhempy.lib.generic import FhemModule

from .controller import matter_controller
from .device import matter_device


class matter(FhemModule):
    """Matter controller (define matter fhempy matter) or Matter device
    (created automatically: define matter_5 fhempy matter <controller> 5)"""

    def __init__(self, logger):
        super().__init__(logger)
        self.impl = None

    # FHEM FUNCTION
    async def Define(self, hash, args, argsh):
        if len(args) > 4:
            self.impl = matter_device(self.logger, self)
        else:
            self.impl = matter_controller(self.logger, self)
        await super().Define(hash, args, argsh)
        return await self.impl.Define(hash, args, argsh)

    # FHEM FUNCTION
    async def Undefine(self, hash):
        if self.impl is not None:
            await self.impl.Undefine(hash)
        return await super().Undefine(hash)

    def __getattr__(self, name):
        # set_* functions are implemented by the controller or device
        if name.startswith("set_") and name not in (
            "set_attr_config",
            "set_set_config",
        ):
            impl = self.__dict__.get("impl")
            if impl is not None and hasattr(impl, name):
                return getattr(impl, name)
        raise AttributeError(name)
