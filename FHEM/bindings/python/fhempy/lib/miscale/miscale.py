from datetime import datetime
from fhempy.lib import fhem
from fhempy.lib.ble_monitor.blemonitor import BLEmonitor
from fhempy.lib.ble_monitor.bt_helpers import BT_INTERFACES
from fhempy.lib.miscale.body_metrics import bodyMetrics
from fhempy.lib.miscale.body_score import bodyScore
from .. import generic


class miscale(generic.FhemModule):
    def __init__(self, logger):
        super().__init__(logger)

        self.blemonitor = None

        attr_config = {
            "hci_interface": {
                "default": "0",
                "options": ",".join(list(map(str, BT_INTERFACES))),
                "format": "int",
                "help": f"{BT_INTERFACES}",
            },
            "birthday": {
                "default": "",
                "help": "Format: %Y-%m-%d",
            },
            "gender": {
                "default": "",
                "options": "male,female",
            },
            "height": {
                "default": "0",
                "format": "int",
                "help": "In centimeters",
            },
        }
        self.set_attr_config(attr_config)

    # FHEM FUNCTION
    async def Define(self, hash, args, argsh):
        await super().Define(hash, args, argsh)
        if len(args) != 4:
            return "Usage: define my_miscale fhempy miscale 11:22:33:44:55:66"

        self.mac_addr = args[3]

        self.blemonitor = BLEmonitor.getInstance(self.logger)
        self.blemonitor.register_device(self)

        await fhem.readingsSingleUpdateIfChanged(self.hash, "state", "ready", 1)

    def mac(self):
        return self.mac_addr

    def hci(self):
        return self._attr_hci_interface

    def encryption_key(self):
        return None

    async def received_data(self, data):
        try:
            if "type" in data and data["type"][0:8] != "Mi Scale":
                await fhem.readingsSingleUpdateIfChanged(
                    self.hash,
                    "state",
                    f"detected type {data['type']} is not miscale",
                    1,
                )
                return

            await fhem.readingsBeginUpdate(self.hash)
            for reading in data:
                if reading in ["packet"]:
                    continue
                await fhem.readingsBulkUpdateIfChanged(
                    self.hash, reading.replace(" ", "_"), data[reading]
                )

            if "stabilized" in data and data["stabilized"] == 1 and "weight" in data:
                await self.update_scores(data)

            await fhem.readingsEndUpdate(self.hash, 1)
        except Exception:
            self.logger.exception("Failed to update readings")

    async def update_scores(self, data):
        if (
            self._attr_height == 0
            or self._attr_birthday == ""
            or self._attr_gender == ""
        ):
            await fhem.readingsBulkUpdate(
                self.hash, "state", "attr weight/birthday/gender missing"
            )
            return

        weight = data["weight"]
        height = self._attr_height
        age = self.get_age(self._attr_birthday)
        gender = self._attr_gender

        readings = {}
        if data["type"] == "Mi Scale V2":
            if "impedance" not in data:
                return
            impedance = data["impedance"]
            lib = bodyMetrics(weight, height, age, gender, impedance)
            bodyscale = [
                "Obese",
                "Overweight",
                "Thick-set",
                "Lack-exercise",
                "Balanced",
                "Balanced-muscular",
                "Skinny",
                "Balanced-skinny",
                "Skinny-muscular",
            ]
            bmi = lib.getBMI()
            bodyfat = lib.getFatPercentage()
            muscle = lib.getMuscleMass()
            water = lib.getWaterPercentage()
            visceral_fat = lib.getVisceralFat()
            bone = lib.getBoneMass()
            basal_metabolism = lib.getBMR()
            protein = lib.getProteinPercentage()

            readings["bmi"] = "{:.1f}".format(bmi)
            readings["bmr"] = "{:.0f}".format(basal_metabolism)
            readings["visceral_fat"] = "{:.0f}".format(visceral_fat)
            readings["weight_ideal"] = "{:.2f}".format(lib.getIdealWeight())
            readings["bmi_label"] = lib.getBmiLabel()
            readings["lbm_coefficient"] = "{:.1f}".format(lib.getLBMCoefficient())
            readings["bodyfat"] = "{:.1f}".format(bodyfat)
            readings["water"] = "{:.1f}".format(water)
            readings["bone"] = "{:.2f}".format(bone)
            readings["muscle"] = "{:.2f}".format(muscle)
            readings["fat_mass_to_lose_or_gain"] = "{:.2f}".format(
                lib.getFatMassToIdeal()["mass"]
            )
            readings["protein"] = "{:.1f}".format(protein)
            readings["body_type"] = bodyscale[lib.getBodyType()]
            readings["metabolic_age"] = "{:.0f}".format(lib.getMetabolicAge())
            bs = bodyScore(
                age,
                gender,
                height,
                weight,
                bmi,
                bodyfat,
                muscle,
                water,
                visceral_fat,
                bone,
                basal_metabolism,
                protein,
            )
            readings["bodyscore"] = "{:.0f}".format(bs.getBodyScore())
        else:
            lib = bodyMetrics(weight, height, age, gender, 0)
            bmi = lib.getBMI()
            visceral_fat = lib.getVisceralFat()
            basal_metabolism = lib.getBMR()
            readings["bmi"] = "{:.1f}".format(bmi)
            readings["bmr"] = "{:.0f}".format(basal_metabolism)
            readings["visceral_fat"] = "{:.0f}".format(visceral_fat)
            readings["weight_ideal"] = "{:.2f}".format(lib.getIdealWeight())
            readings["bmi_label"] = lib.getBmiLabel()

        for reading_name in readings:
            await fhem.readingsBulkUpdateIfChanged(
                self.hash, reading_name.replace(" ", "_"), readings[reading_name]
            )

    def get_age(self, birthday):
        born = datetime.strptime(birthday, "%Y-%m-%d")
        today = datetime.today()
        return (
            today.year - born.year - ((today.month, today.day) < (born.month, born.day))
        )

    async def set_attr_hci_interface(self, hash):
        self.blemonitor.unregister_device(self)
        self.blemonitor.register_device(self)

    async def Undefine(self, hash):
        if self.blemonitor:
            self.blemonitor.unregister_device(self)
        return await super().Undefine(hash)
