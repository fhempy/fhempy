/*
 * fhempy module installer for FHEMWEB.
 * Opened by the "Install modules" button of the local fhempy device
 * (devStateIcon of BindingsIo): fhempyModules()
 *
 * Every module of the catalog below has a tile. "Set up" defines the device
 * right away, modules needing more parameters ask for them first.
 */
(function () {
  "use strict";

  var base = (typeof FW_root !== "undefined" ? FW_root : "/fhem") + "/fhempy/";
  var docs = "https://github.com/fhempy/fhempy/tree/master/FHEM/bindings/python/fhempy/lib/";

  var categories = [
    { id: "popular", title: "Popular", icon: "⭐" },
    { id: "home", title: "Smart home", icon: "🏠" },
    { id: "energy", title: "Energy & solar", icon: "☀️" },
    { id: "cars", title: "Cars", icon: "🚗" },
    { id: "bt", title: "Bluetooth", icon: "📶" },
    { id: "media", title: "Media", icon: "🎵" },
    { id: "presence", title: "Presence & discovery", icon: "🔍" },
    { id: "tools", title: "Information & tools", icon: "🧰" }
  ];
  var popular = ["matter", "matter_bridge", "zigbee2mqtt", "mcp_server",
                 "tuya_smartlife", "googlecast", "esphome", "openmeteo_weather"];

  /* parameter helpers */
  function p(label, placeholder, help, extra) {
    var r = { label: label, placeholder: placeholder || "", help: help || "" };
    for (var k in extra || {}) r[k] = extra[k];
    return r;
  }
  function opt(label, placeholder, help, extra) {
    return p(label, placeholder, help, $.extend({ optional: true }, extra));
  }
  function secret(label, help) { return p(label, "", help, { secret: true }); }
  var MAC_HELP = "Bluetooth address, e.g. A4:C1:38:12:34:56. The module discover_ble lists the devices nearby.";
  var mac = p("Bluetooth address (MAC)", "AA:BB:CC:DD:EE:FF", MAC_HELP);
  var user = p("Username / e-mail", "me@example.com");
  var pw = secret("Password");
  var ip = p("IP address", "192.168.1.50");

  /*
   * id: fhempy module, name: suggested device name, single: only one device needed,
   * params: define arguments, modes: alternative argument sets (args are fixed values)
   */
  var modules = [
    { id: "matter", cat: "home", title: "Matter", name: "matter", single: true, logo: "matter.png",
      desc: "Control Matter devices: lights, plugs, sensors, thermostats, locks and blinds, also behind Hue, IKEA or Aqara bridges" },
    { id: "matter_bridge", cat: "home", title: "Matter Bridge", name: "matterbridge", single: true, logo: "matter.png", badge: "⇄",
      desc: "Use your FHEM devices in Apple Home, Google Home, Alexa and SmartThings, including voice control" },
    { id: "zigbee2mqtt", cat: "home", title: "Zigbee2MQTT", name: "z2m", single: true, logo: "zigbee2mqtt.png",
      desc: "Installs and runs a Zigbee2MQTT server: Zigbee devices without a vendor hub" },
    { id: "mcp_server", cat: "tools", title: "AI (MCP server)", name: "AI", single: true, logo: "mcp_server.png",
      desc: "Control FHEM in plain language with AI apps (Claude, LM Studio...), the AI can also create automations" },
    { id: "esphome", cat: "home", title: "ESPHome", name: "esphome", single: true, logo: "esphome.png",
      desc: "Installs and starts the ESPHome dashboard for easy ESPHome device management" },
    { id: "tuya_smartlife", cat: "home", title: "Tuya Smart Life", name: "tuya_smartlife", logo: "tuya.png",
      desc: "Recommended for Tuya: all devices of the Smart Life app incl. real-time updates (WiFi & ZigBee)",
      args: ["setup"], params: [p("User code", "", "Smart Life app: Me > Settings (gear) > Account and Security > User Code")] },
    { id: "tuya", cat: "home", title: "Tuya local", name: "tuya_local", logo: "tuya.png",
      desc: "Control Tuya WiFi devices locally incl. real-time updates",
      modes: [
        { label: "Find all devices (Tuya IoT account)", args: ["setup"],
          params: [p("API key", "", "Access ID of your project on iot.tuya.com"), secret("API secret", "Access Secret of your project on iot.tuya.com"),
                   p("Device ID", "", "ID of any of your devices, see iot.tuya.com"), opt("Region", "eu", "", { options: ["eu", "us", "cn", "in"] })] },
        { label: "Single device with local key", args: [],
          params: [p("Product ID"), p("Device ID"), ip, opt("Protocol version", "3.3", "", { options: ["3.1", "3.3", "3.4", "3.5"] }),
                   opt("API key"), opt("API secret", "", "", { secret: true })] }
      ] },
    { id: "tuya_cloud", cat: "home", title: "Tuya cloud", name: "tuya_cloud", logo: "tuya.png",
      desc: "Control Tuya devices via the Tuya IoT cloud incl. real-time updates (WiFi & ZigBee)",
      args: ["setup"], params: [p("API key", "", "Access ID of your project on iot.tuya.com"), secret("API secret"), user, pw,
                                opt("App", "smartlife", "", { options: ["smartlife", "tuyaSmart"] })] },
    { id: "googlecast", cat: "media", title: "Google Cast", name: "cast", logo: "googlecast.png",
      desc: "Control Chromecast and Google/Nest speakers, text to speech and Spotify",
      params: [opt("Cast device name", "Living Room", "Name of the speaker or TV as shown in the Google Home app")] },
    { id: "openmeteo_weather", cat: "tools", title: "Weather", name: "weather", logo: "openmeteo_weather.png",
      desc: "Weather and forecast from Open-Meteo, no account needed",
      params: [p("Location", "Berlin", "City name")] },

    { id: "homekit", cat: "home", title: "HomeKit devices", name: "homekit", logo: "homekit.png",
      desc: "Control HomeKit accessories and bridges (e.g. Velux) directly",
      params: [p("HomeKit ID", "", "Device ID shown by the module discover_mdns"), p("Setup code", "123-45-678", "Pairing code printed on the device")] },
    { id: "miio", cat: "home", title: "Xiaomi WiFi", name: "xiaomi", logo: "miio.png",
      desc: "Control Xiaomi WiFi devices: vacuums, air purifiers, fans, lamps...",
      params: [p("Device type", "", "", { options: ["vacuum", "viomivacuum", "airpurifier", "airpurifiermiot", "airhumidifier", "airhumidifiermiot",
        "airdehumidifier", "airfresh", "airqualitymonitor", "fan", "fanp5", "fansa1", "fanv2", "fanza1", "fanza3", "fanza4", "heater",
        "ceil", "philipsbulb", "philipseyecare", "philipsmoonlight", "philipswhitebulb", "yeelight", "plug", "plugv1", "plugv3",
        "chuangmiplug", "powerstrip", "pwznrelay", "waterpurifier", "cooker", "toiletlid", "wifirepeater", "wifispeaker", "chuangmiir",
        "chuangmicamera", "aqaracamera", "alarmclock", "airconditioningcompanion", "airconditioningcompanionv3", "airfresht2017",
        "airhumidifierca1", "airhumidifiercb1", "airhumidifierjsq", "airhumidifiermjjsq", "gateway", "miotdevice", "device"] }),
        ip, p("Token", "", "32 characters, the module Xiaomi tokens gets all tokens from the cloud")] },
    { id: "xiaomi_tokens", cat: "home", title: "Xiaomi tokens", name: "xiaomi_tokens", single: true, logo: "miio.png",
      desc: "Retrieve the tokens of all your Xiaomi devices from the cloud" },
    { id: "xiaomi_gateway3", cat: "home", title: "Xiaomi Gateway 3", name: "xiaomi_gw3", logo: "xiaomi_gateway3.png",
      desc: "Xiaomi Gateway V3 (only V3!) with its Zigbee and BLE devices",
      params: [ip, p("Token", "", "32 characters, the module Xiaomi tokens gets all tokens from the cloud")] },
    { id: "meross", cat: "home", title: "Meross", name: "meross", logo: "meross.png",
      desc: "Control Meross plugs, lights and garage doors",
      args: ["setup"], params: [user, pw] },
    { id: "gree_climate", cat: "home", title: "Gree air conditioner", name: "gree", logo: "gree_climate.png",
      desc: "Control Gree HVAC devices",
      modes: [
        { label: "Search all air conditioners", args: ["scan"], params: [] },
        { label: "Single device", args: [], params: [p("Device name", "", "Name of the air conditioner in the app")] }
      ] },
    { id: "mqtt_ha_discovery", cat: "home", title: "MQTT discovery", name: "mqtt_ha", single: true, logo: "mqtt_ha_discovery.png",
      desc: "Creates FHEM devices for MQTT devices using Home Assistant MQTT discovery",
      params: [opt("MQTT server", "127.0.0.1"), opt("Port", "1883"), opt("Username"), opt("Password", "", "", { secret: true })] },
    { id: "nefit", cat: "home", title: "Nefit / Bosch", name: "nefit", logo: "nefit.png",
      desc: "Control Nefit Easy thermostats",
      params: [p("Serial number")] },
    { id: "pyit600", cat: "home", title: "Salus iT600", name: "salus", logo: "pyit600.png",
      desc: "Control Salus iT600 thermostats",
      params: [p("Gateway IP address", "192.168.1.50"), p("EUID", "", "First 16 characters printed on the bottom of the gateway")] },
    { id: "erelax_vaillant", cat: "home", title: "Vaillant eRelax", name: "vaillant", logo: "erelax_vaillant.png",
      desc: "Control Vaillant eRelax thermostats", params: [user, pw] },
    { id: "ring", cat: "home", title: "Ring", name: "ring", logo: "ring.png",
      desc: "Ring doorbells, chimes and cameras",
      params: [user, p("Ring device name", "Front Door", "Name of the device in the Ring app"), opt("Identifier")] },
    { id: "warema", cat: "home", title: "Warema", name: "warema", icon: "🪟",
      desc: "Control Warema blinds via the WMS WebControl gateway",
      params: [p("Gateway IP address", "192.168.1.50"), p("Channel", "1")] },

    { id: "tibber", cat: "energy", title: "Tibber", name: "tibber", logo: "tibber.png",
      desc: "Prices and consumption data from Tibber",
      params: [p("Access token", "", "developer.tibber.com > Access Token", { secret: true })] },
    { id: "fusionsolar", cat: "energy", title: "Huawei FusionSolar", name: "solar", logo: "fusionsolar.png",
      desc: "Data of your Huawei solar system from FusionSolar",
      params: [user, pw, opt("Region", "eu5", "Subdomain of your FusionSolar login, e.g. eu5 for eu5.fusionsolar.huawei.com")] },
    { id: "huawei_modbus", cat: "energy", title: "Huawei inverter (Modbus)", name: "inverter", logo: "huawei_modbus.png",
      desc: "Read Huawei inverters locally via Modbus TCP",
      params: [ip, opt("Port", "502"), opt("Slave ID", "0")] },
    { id: "goodwe", cat: "energy", title: "GoodWe", name: "goodwe", logo: "goodwe.png",
      desc: "Get data from GoodWe inverters", params: [ip] },
    { id: "rct_power", cat: "energy", title: "RCT Power", name: "rct", logo: "rct_power.png",
      desc: "RCT Power inverter", params: [ip, opt("Port", "8899")] },
    { id: "alphaesscloud", cat: "energy", title: "Alpha ESS", name: "alphaess", logo: "alphaesscloud.png",
      desc: "Alpha ESS inverter via the Alpha ESS cloud",
      params: [p("App ID", "", "open.alphaess.com > Developer"), secret("App secret"), p("Serial number of the system")] },
    { id: "zappi", cat: "energy", title: "myenergi zappi", name: "zappi", logo: "zappi.png",
      desc: "Zappi wallbox and harvi sensors",
      params: [p("Hub serial number"), secret("API key"), opt("harvi serial numbers", "", "Separate several with spaces", { multi: true })] },
    { id: "wienernetze_smartmeter", cat: "energy", title: "Wiener Netze Smart Meter", name: "smartmeter", logo: "wienernetze_smartmeter.png",
      desc: "Consumption of your Wiener Netze smart meter", params: [user, pw] },
    { id: "energie_gv_at", cat: "energy", title: "Energy Austria", name: "energy_austria", single: true, icon: "⚡",
      desc: "Current status of the Austrian power grid" },

    { id: "bmw", cat: "cars", title: "BMW & MINI", name: "my_bmw", logo: "bmw.png",
      desc: "BMW and MINI via official BMW CarData: battery, range, charging, doors, position",
      params: [opt("Client ID", "", "Created in the BMW portal, the device asks for it otherwise")] },
    { id: "kia_hyundai", cat: "cars", title: "Kia / Hyundai / Genesis", name: "my_car", logo: "kia_hyundai.png",
      desc: "Kia, Hyundai and Genesis cars",
      modes: [
        { label: "Official Pleos API (Europe)", args: [], params: [] },
        { label: "App login", args: [], params: [user, pw, p("PIN", "", "", { secret: true }),
          p("Brand", "", "", { options: ["Kia", "Hyundai", "Genesis"] }),
          p("Region", "", "", { options: ["Europe", "USA", "Canada", "Australia", "India", "China", "Brazil"] })] }
      ] },
    { id: "volvo", cat: "cars", title: "Volvo", name: "my_volvo", logo: "volvo.png",
      desc: "Infos from your Volvo car (new API)",
      params: [p("VCC API key", "", "developer.volvocars.com"), user, pw] },
    { id: "volvo_software_update", cat: "cars", title: "Volvo software update", name: "volvo_update", logo: "volvo.png",
      desc: "Get notified about Volvo software updates", params: [p("URL", "https://")] },
    { id: "seatconnect", cat: "cars", title: "Seat / Cupra", name: "my_seat", logo: "seatconnect.png",
      desc: "Control your Seat or Cupra car", params: [user, pw, p("S-PIN", "", "", { secret: true })] },
    { id: "skodaconnect", cat: "cars", title: "Skoda", name: "my_skoda", logo: "skodaconnect.png",
      desc: "Control your Skoda car", params: [user, pw, p("S-PIN", "", "", { secret: true })] },

    { id: "scooter", cat: "bt", title: "Xiaomi / Ninebot scooter", name: "my_scooter", logo: "xiaomi.png",
      desc: "E-scooters: battery, range, mileage. Finds the nearest scooter on its own",
      params: [opt("Bluetooth address (MAC)", "AA:BB:CC:DD:EE:FF", "Empty: the nearest scooter is used")] },
    { id: "eq3bt", cat: "bt", title: "eQ-3 thermostat", name: "thermostat", logo: "eq3bt.png",
      desc: "Control EQ3 Bluetooth radiator thermostats", params: [mac, opt("PIN", "", "Only for eqiva thermostats with pairing PIN")] },
    { id: "ble_monitor", cat: "bt", title: "BLE monitor", name: "ble_sensor", logo: "ble_monitor.png",
      desc: "Supports a lot of Bluetooth sensors (Xiaomi, Govee, Inkbird...)", params: [mac] },
    { id: "mitemp", cat: "bt", title: "Xiaomi temperature sensor", name: "mi_temp", logo: "xiaomi.png",
      desc: "Xiaomi BLE temperature/humidity sensor", params: [mac] },
    { id: "miflora", cat: "bt", title: "Xiaomi plant sensor", name: "mi_plant", logo: "xiaomi.png",
      desc: "Xiaomi Mi Flora plant sensor", params: [mac] },
    { id: "miscale", cat: "bt", title: "Xiaomi scale", name: "mi_scale", logo: "xiaomi.png",
      desc: "Xiaomi Mi Scale V1/V2", params: [mac] },
    { id: "ble_presence", cat: "bt", title: "BLE presence", name: "ble_tag", logo: "bluetooth.svg",
      desc: "Presence detection incl. RSSI for Bluetooth Low Energy tags", params: [mac] },
    { id: "bt_presence", cat: "bt", title: "Bluetooth presence", name: "bt_phone", logo: "bluetooth.svg",
      desc: "Presence detection incl. RSSI for classic Bluetooth (e.g. smartphones)", params: [mac] },
    { id: "blue_connect", cat: "bt", title: "Blue Connect", name: "pool", logo: "bluetooth.svg",
      desc: "Blue Connect pool sensor", params: [mac] },
    { id: "gfprobt", cat: "bt", title: "GF Pro irrigation", name: "irrigation", logo: "bluetooth.svg",
      desc: "Control GF Pro Bluetooth irrigation control", params: [mac] },
    { id: "nespresso_ble", cat: "bt", title: "Nespresso", name: "nespresso", logo: "nespresso_ble.png",
      desc: "Nespresso Bluetooth coffee machine", params: [mac, opt("Auth code")] },
    { id: "mantra_ble", cat: "bt", title: "mAntra ceiling fan", name: "fan", logo: "bluetooth.svg",
      desc: "mAntra ceiling fan lamps", params: [p("Lamp ID", "1F42", "4 hex digits")] },
    { id: "ble_reset", cat: "bt", title: "Bluetooth reset", name: "ble_reset", single: true, logo: "bluetooth.svg",
      desc: "Resets all Bluetooth interfaces every few hours" },

    { id: "spotify", cat: "media", title: "Spotify", name: "spotify", logo: "spotify.png",
      desc: "Control Spotify Connect and use FHEM as Spotify Connect player" },
    { id: "dlna_dmr", cat: "media", title: "DLNA renderer", name: "dlna", logo: "dlna_dmr.svg",
      desc: "Control DLNA MediaRenderer devices, discover_upnp creates them on its own",
      params: [p("UDN", "uuid:...", "Unique device name, shown by discover_upnp")] },

    { id: "arp_presence", cat: "presence", title: "ARP presence", name: "presence_phone", icon: "📱",
      desc: "Presence detection in your network, works also for iOS",
      params: [p("IP or MAC address", "192.168.1.23")] },
    { id: "discover_ble", cat: "presence", title: "Discover Bluetooth", name: "discover_ble", single: true, logo: "bluetooth.svg",
      desc: "Lists the Bluetooth LE devices nearby" },
    { id: "discover_mdns", cat: "presence", title: "Discover mDNS", name: "discover_mdns", single: true, icon: "🔎",
      desc: "Finds mDNS devices (e.g. Google Cast) in your network" },
    { id: "discover_upnp", cat: "presence", title: "Discover UPnP", name: "discover_upnp", single: true, logo: "discover_upnp.png",
      desc: "Finds UPnP devices in your network" },

    { id: "github_backup", cat: "tools", title: "GitHub backup", name: "backup", single: true, logo: "github.png",
      desc: "Backup of the FHEM configuration to a private GitHub repository",
      params: [p("Repository URL", "https://github.com/USER/fhem_backup", "Use a private repository"),
               p("Backup directory", "fhem_raspi", "Directory in the repository, one per FHEM installation")] },
    { id: "github_restore", cat: "tools", title: "GitHub restore", name: "restore", single: true, logo: "github.png",
      desc: "Restore the FHEM configuration from GitHub",
      params: [p("Repository URL", "https://github.com/USER/fhem_backup"), p("Backup directory", "fhem_raspi")] },
    { id: "prusalink", cat: "tools", title: "Prusa 3D printer", name: "prusa", logo: "prusalink.png",
      desc: "Prusa 3D printer via PrusaLink",
      params: [p("Printer URL", "http://192.168.1.50"), p("Username", "maker"), pw] },
    { id: "object_detection", cat: "tools", title: "Object detection", name: "object_detection", logo: "object_detection.svg",
      desc: "TensorFlow Lite object detection in camera streams or images",
      modes: [
        { label: "Video stream", args: ["stream"], params: [p("Stream URL", "rtsp://...")] },
        { label: "Image", args: ["image"], params: [p("Image file", "www/snapshot.jpg")] }
      ] },
    { id: "piclock", cat: "tools", title: "LED clock", name: "piclock", single: true, logo: "piclock.png",
      desc: "LED clock with MAX7219 on a Raspberry Pi",
      params: [opt("Temperature", "device:reading"), opt("Weather", "device:reading"), opt("Button GPIOs", "4,17,27,22,18")] },
    { id: "wienerlinien", cat: "tools", title: "Wiener Linien", name: "departures", logo: "wienerlinien.png",
      desc: "Wiener Linien departure times", params: [p("Stop ID", "4118", "RBL number of the stop")] },
    { id: "geizhals", cat: "tools", title: "Geizhals", name: "price", icon: "💶",
      desc: "Watch prices on geizhals", params: [p("Product URL", "https://geizhals.at/...")] },
    { id: "aktionsfinder", cat: "tools", title: "Aktionsfinder", name: "offers", icon: "🏷️",
      desc: "Keep informed about product promotions", params: [p("Product", "Mineralwasser")] },
    { id: "ikos", cat: "tools", title: "Ikos resorts", name: "holiday", icon: "🏖️",
      desc: "Check prices for Ikos resorts",
      params: [p("From", "2026-07-01", "YYYY-MM-DD"), p("To", "2026-07-14", "YYYY-MM-DD")] },
    { id: "ddnssde", cat: "tools", title: "ddnss.de", name: "ddnss", single: true, icon: "🌐",
      desc: "Dynamic DNS updater for the free ddnss.de service", params: [user, pw] },
    { id: "websitetests", cat: "tools", title: "Website tests", name: "webtest", icon: "🧪",
      desc: "Basic checks of a website", params: [p("URL", "https://")] },
    { id: "helloworld", cat: "tools", title: "Hello World", name: "hello", icon: "👋",
      desc: "Example for developers to start writing their own module" }
  ];

  var byId = {};
  modules.forEach(function (m) { byId[m.id] = m; });

  /* device name -> fhempy module of the defined fhempy devices */
  var defined = {};
  var allNames = {};
  var view = { cat: "all", search: "" };

  function esc(t) { return $("<div>").text(t === undefined ? "" : String(t)).html(); }

  function css() {
    if ($("#fhempyModulesCss").length) return;
    $("head").append('<style id="fhempyModulesCss">' +
      "#fhempyModules{max-height:calc(100vh - 170px)!important;overflow-y:auto;font-family:'Segoe UI','Helvetica Neue',Helvetica,Arial,sans-serif;line-height:1.35}" +
      "#fhempyModules .fmTop{display:flex;align-items:center;gap:12px;margin-bottom:10px}" +
      "#fhempyModules .fmSearch{flex:1;padding:8px 12px;border-radius:18px;border:1px solid rgba(128,128,128,0.45);font-size:14px;background:transparent;color:inherit}" +
      "#fhempyModules .fmChips{display:flex;flex-wrap:wrap;gap:6px;margin-bottom:10px}" +
      "#fhempyModules .fmChip{padding:4px 11px;border-radius:14px;border:1px solid rgba(128,128,128,0.4);cursor:pointer;font-size:13px;user-select:none;white-space:nowrap}" +
      "#fhempyModules .fmChip.fmActive{background:#4B8BBE;border-color:#4B8BBE;color:#fff}" +
      "#fhempyModules .fmList{max-height:calc(100vh - 330px);overflow-y:auto;padding:2px 4px 4px 2px}" +
      "#fhempyModules .fmCat{font-weight:600;margin:14px 0 8px;font-size:15px}" +
      "#fhempyModules .fmCat:first-child{margin-top:2px}" +
      "#fhempyModules .fmGrid{display:grid;grid-template-columns:repeat(auto-fill,minmax(215px,1fr));gap:10px}" +
      "#fhempyModules .fmTile{border:1px solid rgba(128,128,128,0.35);border-radius:12px;padding:10px;cursor:pointer;display:flex;gap:10px;align-items:flex-start;transition:transform .15s,box-shadow .15s}" +
      "#fhempyModules .fmTile:hover{transform:translateY(-2px);box-shadow:0 4px 12px rgba(0,0,0,0.15)}" +
      "#fhempyModules .fmLogo{position:relative;flex:none;width:44px;height:44px;border-radius:10px;background:#fff;display:inline-flex;align-items:center;justify-content:center;box-shadow:0 0 0 1px rgba(128,128,128,0.25);font-size:24px}" +
      "#fhempyModules .fmLogo img{width:34px;height:34px;object-fit:contain}" +
      "#fhempyModules .fmLogo.fmBig{width:64px;height:64px;border-radius:14px;font-size:36px}" +
      "#fhempyModules .fmLogo.fmBig img{width:50px;height:50px}" +
      "#fhempyModules .fmBadge{position:absolute;right:-6px;bottom:-5px;background:#4B8BBE;color:#fff;border-radius:50%;width:18px;height:18px;font-size:11px;line-height:18px;text-align:center;border:2px solid #fff}" +
      "#fhempyModules .fmTitle{font-weight:600}" +
      "#fhempyModules .fmDesc{font-size:12px;opacity:0.75;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}" +
      "#fhempyModules .fmDone{font-size:12px;color:#3fa34d;font-weight:600;margin-top:3px}" +
      "#fhempyModules .fmBtn{display:inline-block;padding:3px 14px;border-radius:12px;background:#4B8BBE;color:#fff;font-size:13px;cursor:pointer;border:none}" +
      "#fhempyModules .fmBtn.fmBig{padding:7px 22px;font-size:15px;font-weight:600}" +
      "#fhempyModules .fmBtn[disabled]{opacity:0.6;cursor:default}" +
      "#fhempyModules .fmField{margin:10px 0}" +
      "#fhempyModules .fmField label{display:block;font-weight:600;margin-bottom:3px}" +
      "#fhempyModules .fmField input[type=text],#fhempyModules .fmField input[type=password],#fhempyModules .fmField select{width:100%;margin:0;box-sizing:border-box;padding:7px 10px;border-radius:8px;border:1px solid rgba(128,128,128,0.45);font-size:14px;background:transparent;color:inherit}" +
      "#fhempyModules .fmField select option{color:#000}" +
      "#fhempyModules .fmHelp{font-size:12px;opacity:0.7;margin-top:2px}" +
      "#fhempyModules .fmMode{display:block;margin:4px 0;cursor:pointer}" +
      "#fhempyModules .fmMode input{margin:0 6px 0 0;vertical-align:-1px}" +
      "#fhempyModules .fmError{color:#d64545;margin-top:8px;white-space:pre-wrap}" +
      "#fhempyModules .fmOk{color:#3fa34d;font-weight:600;font-size:16px;margin:10px 0}" +
      "#fhempyModules .fmEmpty{opacity:0.7;margin:20px 0;text-align:center}" +
      "@keyframes fmSpin{to{transform:rotate(360deg)}}" +
      "#fhempyModules .fmSpin{display:inline-block;width:12px;height:12px;border-radius:50%;border:2px solid #fff;border-top-color:transparent;animation:fmSpin 1s linear infinite;vertical-align:-2px;margin-right:6px}" +
      "</style>");
  }

  function logo(m, big) {
    var inner = m.logo ? '<img src="' + base + m.logo + '" alt="">' : (m.icon || "🧩");
    var badge = m.badge ? '<span class="fmBadge">' + m.badge + "</span>" : "";
    return '<span class="fmLogo' + (big ? " fmBig" : "") + '">' + inner + badge + "</span>";
  }

  function devicesOf(id) {
    var r = [];
    for (var n in defined) if (defined[n] == id) r.push(n);
    return r.sort();
  }

  function matches(m) {
    var s = view.search.toLowerCase();
    if (!s) return true;
    return (m.id + " " + m.title + " " + m.desc).toLowerCase().indexOf(s) >= 0;
  }

  function tile(m) {
    var devs = devicesOf(m.id);
    var done = devs.length ? '<div class="fmDone">✓ ' +
      (devs.length == 1 ? esc(devs[0]) : devs.length + " devices") + "</div>" : "";
    return '<div class="fmTile" data-id="' + m.id + '">' + logo(m) +
      '<div style="min-width:0"><div class="fmTitle">' + esc(m.title) + "</div>" +
      '<div class="fmDesc">' + esc(m.desc) + "</div>" + done + "</div></div>";
  }

  function renderList() {
    var html = "";
    var shown = 0;
    function section(cat, list) {
      list = list.filter(matches);
      if (!list.length) return;
      shown += list.length;
      html += '<div class="fmCat">' + cat.icon + " " + esc(cat.title) + '</div><div class="fmGrid">' +
        list.map(tile).join("") + "</div>";
    }
    categories.forEach(function (c) {
      if (view.cat != "all" && view.cat != c.id) return;
      /* while searching, every module shows up once in its own category */
      if (c.id == "popular") {
        if (!view.search) section(c, popular.map(function (id) { return byId[id]; }));
        return;
      }
      section(c, modules.filter(function (m) { return m.cat == c.id; }));
    });
    if (!shown) html = '<div class="fmEmpty">No module found for “' + esc(view.search) +
      '”. <a href="https://github.com/fhempy/fhempy#-modules" target="_blank">All modules on GitHub</a></div>';
    $("#fhempyModules .fmList").html(html).scrollTop(0);
  }

  function renderMain() {
    var chips = '<span class="fmChip" data-cat="all">All</span>' + categories.map(function (c) {
      return '<span class="fmChip" data-cat="' + c.id + '">' + c.icon + " " + esc(c.title) + "</span>";
    }).join("");
    $("#fhempyModules").html(
      '<div class="fmTop"><input class="fmSearch" type="search" placeholder="🔍 Search ' +
      modules.length + ' modules, e.g. tuya, weather, car..." value="' + esc(view.search) + '"></div>' +
      '<div class="fmChips">' + chips + '</div><div class="fmList"></div>');
    $("#fhempyModules .fmChip[data-cat='" + view.cat + "']").addClass("fmActive");
    renderList();
    $("#fhempyModules .fmSearch").on("input", function () {
      view.search = $(this).val().trim();
      renderList();
    }).focus();
    $("#fhempyModules .fmChip").click(function () {
      view.cat = $(this).data("cat");
      $("#fhempyModules .fmChip").removeClass("fmActive");
      $(this).addClass("fmActive");
      renderList();
    });
    $("#fhempyModules .fmList").on("click", ".fmTile", function () {
      renderDetail(byId[$(this).data("id")]);
    });
    buttons([{ text: "Close", click: close }]);
  }

  function freeName(name) {
    var n = name, i = 2;
    while (allNames[n]) n = name + "_" + i++;
    return n;
  }

  function field(prm, i) {
    var id = "fmParam" + i;
    var label = esc(prm.label) + (prm.optional ? ' <span style="font-weight:normal;opacity:0.6">(optional)</span>' : "");
    var input;
    if (prm.options) {
      input = '<select id="' + id + '">' + (prm.optional ? '<option value=""></option>' : "") +
        prm.options.map(function (o) { return "<option>" + esc(o) + "</option>"; }).join("") + "</select>";
    } else {
      input = '<input id="' + id + '" type="' + (prm.secret ? "password" : "text") + '" placeholder="' +
        esc(prm.placeholder) + '" autocomplete="off">';
    }
    return '<div class="fmField"><label for="' + id + '">' + label + "</label>" + input +
      (prm.help ? '<div class="fmHelp">' + esc(prm.help) + "</div>" : "") + "</div>";
  }

  function modeOf(m) {
    if (!m.modes) return { args: m.args || [], params: m.params || [] };
    return m.modes[+$("input[name=fmMode]:checked").val() || 0];
  }

  function renderParams(m) {
    var mode = modeOf(m);
    $("#fhempyModules .fmParams").html(mode.params.map(field).join(""));
    center();
  }

  /* FHEM define argument: quoted if needed, ; doubled for the command line */
  function arg(v) {
    v = v.replace(/;/g, ";;");
    return /[\s"]/.test(v) ? '"' + v.replace(/"/g, '\\"') + '"' : v;
  }

  function renderDetail(m) {
    var devs = devicesOf(m.id);
    var existing = devs.length ? '<div class="fmDone" style="margin-top:6px">✓ Set up already: ' +
      devs.map(function (n) {
        return '<a href="' + FW_root + "?detail=" + encodeURIComponent(n) + '">' + esc(n) + "</a>";
      }).join(", ") + "</div>" : "";
    var modes = m.modes ? '<div class="fmField"><label>How do you want to connect?</label>' +
      m.modes.map(function (mo, i) {
        return '<label class="fmMode" style="font-weight:normal"><input type="radio" name="fmMode" value="' + i + '"' +
          (i ? "" : " checked") + "> " + esc(mo.label) + "</label>";
      }).join("") + "</div>" : "";
    $("#fhempyModules").html(
      '<div><a href="#" class="fmBack">← All modules</a></div>' +
      '<div style="display:flex;gap:14px;align-items:center;margin:12px 0">' + logo(m, true) +
      '<div><div class="fmTitle" style="font-size:18px">' + esc(m.title) + "</div>" +
      '<div style="font-size:13px;opacity:0.8">' + esc(m.desc) + "</div>" +
      '<div style="font-size:12px;margin-top:3px"><a href="' + docs + m.id + '" target="_blank">Documentation</a> · module ' +
      esc(m.id) + "</div>" + existing + "</div></div>" +
      '<div class="fmForm">' + modes +
      '<div class="fmField"><label for="fmName">Device name in FHEM</label><input id="fmName" type="text" value="' +
      esc(freeName(m.name)) + '"></div><div class="fmParams"></div><div class="fmError"></div></div>');
    renderParams(m);
    $("#fhempyModules input[name=fmMode]").change(function () { renderParams(m); });
    $("#fhempyModules .fmBack").click(function (e) { e.preventDefault(); renderMain(); });
    $("#fhempyModules input").keydown(function (e) { if (e.which == 13) setup(m); });
    buttons([
      { text: "Set up", "class": "fmSetupBtn", click: function () { setup(m); } },
      { text: "Back", click: renderMain }
    ]);
    var first = $("#fhempyModules .fmParams input, #fhempyModules .fmParams select").first();
    (first.length ? first : $("#fmName")).focus();
  }

  function setup(m) {
    var btn = $(".fmSetupBtn");
    if (btn.prop("disabled")) return;
    var err = $("#fhempyModules .fmError");
    var name = $("#fmName").val().trim();
    if (!/^[A-Za-z0-9._]+$/.test(name)) {
      err.text("The device name may only contain letters, digits, . and _");
      return;
    }
    if (allNames[name]) {
      err.text("A device named " + name + " exists already, please choose another name.");
      return;
    }
    var mode = modeOf(m);
    var args = mode.args.slice();
    var missing = [];
    var empty = null;
    mode.params.forEach(function (prm, i) {
      var v = ($("#fmParam" + i).val() || "").trim();
      if (v === "") {
        if (!prm.optional) missing.push(prm.label);
        else if (!empty) empty = prm.label;
        return;
      }
      /* optional arguments are positional, a later one needs the earlier ones */
      if (empty) {
        missing.push(empty);
        empty = null;
      }
      if (prm.multi) v.split(/\s+/).forEach(function (x) { args.push(arg(x)); });
      else args.push(arg(v));
    });
    if (missing.length) {
      err.text("Please fill in: " + missing.join(", "));
      return;
    }
    err.text("");
    btn.prop("disabled", true).html('<span class="fmSpin"></span>Setting up...');
    /* new fhempy devices use the local fhempy on their own */
    var cmd = "define " + name + " fhempy " + m.id + (args.length ? " " + args.join(" ") : "");
    FW_cmd(FW_root + "?cmd=" + encodeURIComponent(cmd) + "&XHR=1", function (r) {
      r = (r || "").replace(/[\r\n]+$/, "");
      if (r !== "") {
        btn.prop("disabled", false).text("Set up");
        err.text(r.replace(/<br>/g, "\n").replace(/<[^>]+>/g, ""));
        return;
      }
      defined[name] = m.id;
      allNames[name] = 1;
      done(m, name);
    });
  }

  function done(m, name) {
    $("#fhempyModules").html(
      '<div style="text-align:center;padding:10px 0">' + logo(m, true) +
      '<div class="fmOk">✓ ' + esc(m.title) + " is set up</div>" +
      "<div>The device <b>" + esc(name) + "</b> was created" + (m.cat == "bt" || m.id == "matter" || m.id == "zigbee2mqtt" ?
        ". The first start installs everything it needs, this can take a few minutes." : ".") + "</div>" +
      '<div style="margin-top:6px;font-size:13px"><a href="' + docs + m.id + '" target="_blank">What can ' + esc(m.title) + " do?</a></div></div>");
    buttons([
      { text: "Open " + name, click: function () { location.href = FW_root + "?detail=" + encodeURIComponent(name); } },
      { text: "Set up another module", click: renderMain },
      { text: "Close", click: close }
    ]);
  }

  function buttons(list) {
    var d = $("#fhempyModules");
    if (!d.dialog("instance")) return;
    d.dialog("option", "buttons", list);
    center();
  }

  /* the content changed, keep the dialog on the screen */
  function center() {
    var d = $("#fhempyModules");
    if (d.dialog("instance")) d.dialog("option", "position", { my: "center", at: "center", of: window });
  }

  function close() {
    $("#fhempyModules").dialog("close");
  }

  function loadDefined(cb) {
    var cmd = '{join(",", map {$_.":".InternalVal($_,"FHEMPYTYPE","")} devspec2array("TYPE=fhempy"))."|".join(",", devspec2array(".*"))}';
    FW_cmd(FW_root + "?cmd=" + encodeURIComponent(cmd) + "&XHR=1", function (r) {
      var parts = (r || "").replace(/[\r\n]+$/, "").split("|");
      defined = {};
      allNames = {};
      (parts[0] || "").split(",").forEach(function (d) {
        var x = d.split(":");
        if (x[0] && x[1]) defined[x[0]] = x[1];
      });
      (parts[1] || "").split(",").forEach(function (n) { if (n) allNames[n] = 1; });
      cb();
    });
  }

  window.fhempyModules = function (search) {
    css();
    $("#fhempyModules").remove();
    view = { cat: "all", search: search || "" };
    var div = $('<div id="fhempyModules"></div>');
    $("body").append(div);
    div.html('<div class="fmEmpty">Loading modules...</div>');
    div.dialog({
      modal: true,
      title: "Install fhempy modules",
      width: Math.min(820, $(window).width() - 20),
      close: function () { $(this).remove(); }
    });
    loadDefined(renderMain);
  };
})();
