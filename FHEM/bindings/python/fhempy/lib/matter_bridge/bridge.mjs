// Matter bridge for fhempy: makes FHEM devices available as Matter devices
// (Apple Home, Google Home, Alexa, SmartThings...).
//
// fhempy starts this script with node and talks to it with one JSON object
// per line, fhempy -> bridge on stdin, bridge -> fhempy on stdout.
// All logs go to stderr.
//
// fhempy -> bridge
//   {"cmd": "devices", "devices": [{"id", "type", "name", "state", "parts"}]}
//     parts: additional sensors of the same FHEM device, e.g. ["humidity"],
//     the apps show them in one device
//   {"cmd": "state", "id", "state": {...}}
//   {"cmd": "reachable", "id", "reachable": true|false}
//   {"cmd": "pairing_mode"}  (allows pairing with one more app for 15 min)
// bridge -> fhempy
//   {"event": "status", "commissioned", "qr", "manual", "fabrics": [...]}
//   {"event": "command", "id", "command": {...}}
//   {"event": "pairing_mode", "minutes"}
//   {"event": "error", "id", "message"}
//
// state and command use the same keys per type:
//   switch/outlet/light: on (bool); dimmer: on, level (0-100)
//   blind: position (0-100, 100 = open), command also stop (true)
//   thermostat: current, target (°C); lock: locked (bool)
//   contact: closed (bool); motion: occupied (bool)
//   temperature: temperature (°C); humidity: humidity (%)

import { Endpoint, ServerNode, VendorId } from "@matter/main";
import { BridgedDeviceBasicInformationServer } from "@matter/main/behaviors/bridged-device-basic-information";
import { WindowCoveringServer } from "@matter/main/behaviors/window-covering";
import { OccupancySensingServer } from "@matter/main/behaviors/occupancy-sensing";
import { ThermostatServer } from "@matter/main/behaviors/thermostat";
import { ContactSensorDevice } from "@matter/main/devices/contact-sensor";
import { DimmableLightDevice } from "@matter/main/devices/dimmable-light";
import { DoorLockDevice } from "@matter/main/devices/door-lock";
import { HumiditySensorDevice } from "@matter/main/devices/humidity-sensor";
import { OccupancySensorDevice } from "@matter/main/devices/occupancy-sensor";
import { OnOffLightDevice } from "@matter/main/devices/on-off-light";
import { OnOffPlugInUnitDevice } from "@matter/main/devices/on-off-plug-in-unit";
import { TemperatureSensorDevice } from "@matter/main/devices/temperature-sensor";
import { ThermostatDevice } from "@matter/main/devices/thermostat";
import { WindowCoveringDevice } from "@matter/main/devices/window-covering";
import { AggregatorEndpoint } from "@matter/main/endpoints/aggregator";
import { BridgedNodeEndpoint } from "@matter/main/endpoints/bridged-node";
import { DoorLock, OccupancySensing, Thermostat, WindowCovering } from "@matter/main/clusters";
import { DeviceCommissioner } from "@matter/main/protocol";
import { createInterface } from "node:readline";

// stdout is reserved for messages to fhempy
console.log = console.info = console.debug = (...args) => console.error(...args);

// settings come from fhempy as JSON in an environment variable, matter.js
// itself interprets command line arguments
const options = JSON.parse(process.env.FHEMPY_BRIDGE ?? "{}");


// Commands from the controller are collected for a short time, a slider
// in Apple/Google Home or a level transition sends many changes.
const COMMAND_DELAY_MS = 300;

function send(message) {
    process.stdout.write(JSON.stringify(message) + "\n");
}

const devices = new Map(); // id -> {type, name, parts, endpoint, state, pending, timer}
// Matter endpoint -> id of the FHEM device (endpoints of parts have own ids)
const deviceIds = new WeakMap();
const deviceId = endpoint => deviceIds.get(endpoint) ?? endpoint.id;

function emitCommand(id, command) {
    const device = devices.get(id);
    if (device === undefined) return;
    // the last of stop and position wins
    if ("stop" in command) delete device.pending.position;
    if ("position" in command) delete device.pending.stop;
    device.pending = { ...device.pending, ...command };
    clearTimeout(device.timer);
    device.timer = setTimeout(() => {
        const pending = device.pending;
        device.pending = {};
        send({ event: "command", id, command: pending });
    }, COMMAND_DELAY_MS);
}

// changes caused by fhempy (state messages) are not sent back
function changedByController(id, key, value) {
    const device = devices.get(id);
    return device !== undefined && device.state[key] !== value;
}

const levelToPct = level => (level === null ? 0 : Math.round((level / 254) * 100));
const pctToLevel = pct => Math.min(254, Math.max(1, Math.round((pct / 100) * 254)));
// Matter: 0 = open, 10000 = closed; FHEM side: 100 = open
const positionToMatter = position => Math.round((100 - position) * 100);
const matterToPosition = value => (value === null ? null : 100 - Math.round(value / 100));
const toHundredths = value => Math.round(value * 100);

class FhemWindowCoveringServer extends WindowCoveringServer.with(
    WindowCovering.Feature.Lift,
    WindowCovering.Feature.PositionAwareLift,
) {
    // the blind moves in FHEM, the position is updated by fhempy
    handleMovement(type, reversed, direction, targetPercent100ths) {
        if (targetPercent100ths !== undefined) {
            emitCommand(deviceId(this.endpoint), { position: matterToPosition(targetPercent100ths) });
        }
    }

    handleStopMovement() {
        emitCommand(deviceId(this.endpoint), { stop: true });
        return super.handleStopMovement();
    }
}

const FhemThermostatServer = ThermostatServer.with(Thermostat.Feature.Heating);

const TYPES = {
    switch: { device: OnOffPlugInUnitDevice },
    outlet: { device: OnOffPlugInUnitDevice },
    light: { device: OnOffLightDevice },
    dimmer: { device: DimmableLightDevice },
    blind: { device: WindowCoveringDevice.with(FhemWindowCoveringServer) },
    thermostat: { device: ThermostatDevice.with(FhemThermostatServer) },
    lock: { device: DoorLockDevice },
    contact: { device: ContactSensorDevice },
    motion: {
        device: OccupancySensorDevice.with(
            OccupancySensingServer.with(OccupancySensing.Feature.PassiveInfrared),
        ),
    },
    temperature: { device: TemperatureSensorDevice },
    humidity: { device: HumiditySensorDevice },
};

function initialState(type) {
    switch (type) {
        case "blind":
            return {
                windowCovering: {
                    type: WindowCovering.WindowCoveringType.Rollershade,
                    endProductType: WindowCovering.EndProductType.RollerShade,
                },
            };
        case "thermostat":
            return {
                thermostat: {
                    controlSequenceOfOperation: Thermostat.ControlSequenceOfOperation.HeatingOnly,
                    systemMode: Thermostat.SystemMode.Heat,
                    absMinHeatSetpointLimit: 400,
                    minHeatSetpointLimit: 400,
                    absMaxHeatSetpointLimit: 3200,
                    maxHeatSetpointLimit: 3200,
                },
            };
        case "lock":
            return {
                doorLock: {
                    lockType: DoorLock.LockType.DeadBolt,
                    actuatorEnabled: true,
                    lockState: DoorLock.LockState.Locked,
                    operatingMode: DoorLock.OperatingMode.Normal,
                    // bits are inverted: 0 = supported
                    supportedOperatingModes: {
                        normal: false,
                        vacation: true,
                        privacy: true,
                        noRemoteLockUnlock: true,
                        passage: true,
                        alwaysSet: 2047,
                    },
                    wrongCodeEntryLimit: 3,
                    userCodeTemporaryDisableTime: 10,
                },
            };
        case "motion":
            return {
                occupancySensing: {
                    occupancySensorType: OccupancySensing.OccupancySensorType.Pir,
                    occupancySensorTypeBitmap: { pir: true },
                },
            };
        default:
            return {};
    }
}

// FHEM state -> Matter attributes
function matterState(type, state) {
    const result = {};
    const has = key => state[key] !== undefined && state[key] !== null;
    switch (type) {
        case "switch":
        case "outlet":
        case "light":
            if (has("on")) result.onOff = { onOff: state.on };
            break;
        case "dimmer":
            if (has("on")) result.onOff = { onOff: state.on };
            if (has("level") && state.level > 0) result.levelControl = { currentLevel: pctToLevel(state.level) };
            break;
        case "blind":
            if (has("position")) {
                const value = positionToMatter(state.position);
                result.windowCovering = {
                    currentPositionLiftPercent100ths: value,
                    targetPositionLiftPercent100ths: value,
                };
            }
            break;
        case "thermostat":
            result.thermostat = {};
            if (has("current")) result.thermostat.localTemperature = toHundredths(state.current);
            if (has("target")) {
                result.thermostat.occupiedHeatingSetpoint = Math.min(3200, Math.max(400, toHundredths(state.target)));
            }
            break;
        case "lock":
            if (has("locked")) {
                result.doorLock = { lockState: state.locked ? DoorLock.LockState.Locked : DoorLock.LockState.Unlocked };
            }
            break;
        case "contact":
            if (has("closed")) result.booleanState = { stateValue: state.closed };
            break;
        case "motion":
            if (has("occupied")) result.occupancySensing = { occupancy: { occupied: state.occupied } };
            break;
        case "temperature":
            if (has("temperature")) result.temperatureMeasurement = { measuredValue: toHundredths(state.temperature) };
            break;
        case "humidity":
            if (has("humidity")) {
                result.relativeHumidityMeasurement = { measuredValue: toHundredths(state.humidity) };
            }
            break;
    }
    return result;
}

// Matter attribute changes made by a controller -> commands for FHEM
function listen(id, type, endpoint) {
    const events = endpoint.events;
    if (events.onOff !== undefined) {
        events.onOff.onOff$Changed.on(value => {
            if (changedByController(id, "on", value)) emitCommand(id, { on: value });
        });
    }
    if (type === "dimmer") {
        events.levelControl.currentLevel$Changed.on(value => {
            const level = levelToPct(value);
            if (changedByController(id, "level", level)) emitCommand(id, { level });
        });
    }
    if (type === "thermostat") {
        events.thermostat.occupiedHeatingSetpoint$Changed.on(value => {
            const target = value / 100;
            if (changedByController(id, "target", target)) emitCommand(id, { target });
        });
    }
    if (type === "lock") {
        events.doorLock.lockState$Changed.on(value => {
            const locked = value === DoorLock.LockState.Locked;
            if (changedByController(id, "locked", locked)) emitCommand(id, { locked });
        });
    }
}

let server;
let aggregator;

function basicInformation(id, name) {
    const label = name.slice(0, 32);
    return {
        nodeLabel: label,
        productName: label,
        productLabel: label,
        vendorName: "FHEM",
        serialNumber: id.slice(0, 32),
        uniqueId: `fhem-${id}`.slice(0, 32),
        reachable: true,
    };
}

function deviceEndpoint(type, options) {
    return new Endpoint(TYPES[type].device, options);
}

function typeOptions(type, state) {
    return mergeState(initialState(type), matterState(type, state ?? {}));
}

async function addDevice({ id, type, name, state, parts }) {
    if (TYPES[type] === undefined || (parts ?? []).some(part => TYPES[part] === undefined)) {
        send({ event: "error", id, message: `unknown type ${[type, ...(parts ?? [])].join(", ")}` });
        return;
    }
    let endpoint;
    let main;
    const partEndpoints = new Map();
    if (!parts?.length) {
        endpoint = main = new Endpoint(TYPES[type].device.with(BridgedDeviceBasicInformationServer), {
            id,
            bridgedDeviceBasicInformation: basicInformation(id, name),
            ...typeOptions(type, state),
        });
    } else {
        // one bridged device with an endpoint per function, the apps show
        // it as one device like in FHEM
        for (const part of [type, ...parts]) {
            const partEndpoint = deviceEndpoint(part, { id: part, ...typeOptions(part, state) });
            deviceIds.set(partEndpoint, id);
            partEndpoints.set(part, partEndpoint);
        }
        main = partEndpoints.get(type);
        endpoint = new Endpoint(BridgedNodeEndpoint, {
            id,
            bridgedDeviceBasicInformation: basicInformation(id, name),
            parts: [...partEndpoints.values()],
        });
    }
    deviceIds.set(endpoint, id);
    await aggregator.add(endpoint);
    devices.set(id, {
        type,
        name,
        parts: parts ?? [],
        endpoint,
        partEndpoints,
        state: { ...state },
        pending: {},
    });
    listen(id, type, main);
}

function mergeState(a, b) {
    const result = { ...a };
    for (const [key, value] of Object.entries(b)) {
        result[key] = { ...(result[key] ?? {}), ...value };
    }
    return result;
}

async function setDevices(list) {
    const wanted = new Map(list.map(device => [device.id, device]));
    for (const [id, device] of devices) {
        const update = wanted.get(id);
        if (
            update === undefined ||
            update.type !== device.type ||
            update.name !== device.name ||
            (update.parts ?? []).join() !== device.parts.join()
        ) {
            // removed, or changed in a way Matter controllers only see on a new endpoint
            devices.delete(id);
            clearTimeout(device.timer);
            await device.endpoint.delete();
        }
    }
    for (const device of list) {
        try {
            if (!devices.has(device.id)) {
                await addDevice(device);
            } else if (device.state !== undefined) {
                await setState(device.id, device.state);
            }
        } catch (error) {
            send({ event: "error", id: device.id, message: String(error?.message ?? error) });
        }
    }
}

async function setState(id, state) {
    const device = devices.get(id);
    if (device === undefined) return;
    Object.assign(device.state, state);
    if (device.partEndpoints.size) {
        for (const [part, endpoint] of device.partEndpoints) {
            const values = matterState(part, state);
            if (Object.keys(values).length) await endpoint.set(values);
        }
        return;
    }
    const values = matterState(device.type, state);
    if (Object.keys(values).length) await device.endpoint.set(values);
}

async function setReachable(id, reachable) {
    const device = devices.get(id);
    if (device === undefined) return;
    await device.endpoint.set({ bridgedDeviceBasicInformation: { reachable } });
}

function sendStatus() {
    const commissioning = server.state.commissioning;
    send({
        event: "status",
        commissioned: commissioning.commissioned,
        qr: commissioning.pairingCodes.qrPairingCode,
        manual: commissioning.pairingCodes.manualPairingCode,
        fabrics: Object.values(commissioning.fabrics ?? {}).map(fabric => ({
            label: fabric.label,
            vendor: fabric.rootVendorId,
        })),
    });
}

const PAIRING_MODE_MINUTES = 15;

let pairingModeTimer;

async function openPairingMode() {
    if (!server.state.commissioning.commissioned) {
        // a new bridge can be paired anyway
        sendStatus();
        return;
    }
    // like "Turn on pairing mode" in an app, with the code of the bridge
    const commissioner = server.env.get(DeviceCommissioner);
    await commissioner.allowBasicCommissioning(() => {
        clearTimeout(pairingModeTimer);
        send({ event: "pairing_mode", minutes: 0 });
    });
    clearTimeout(pairingModeTimer);
    pairingModeTimer = setTimeout(() => commissioner.endCommissioning(), PAIRING_MODE_MINUTES * 60_000);
    send({ event: "pairing_mode", minutes: PAIRING_MODE_MINUTES });
}

async function handle(message) {
    switch (message.cmd) {
        case "devices":
            await setDevices(message.devices);
            break;
        case "state":
            await setState(message.id, message.state);
            break;
        case "reachable":
            await setReachable(message.id, message.reachable);
            break;
        case "status":
            sendStatus();
            break;
        case "pairing_mode":
            await openPairingMode();
            break;
    }
}

async function main() {
    const serial = `fhem-${options.discriminator}-${options.port}`;
    server = await ServerNode.create({
        id: "fhem-bridge",
        network: { port: options.port },
        commissioning: {
            passcode: options.passcode,
            discriminator: options.discriminator,
        },
        productDescription: {
            name: options.name,
            deviceType: AggregatorEndpoint.deviceType,
        },
        basicInformation: {
            vendorName: "FHEM",
            // test vendor/product id, the bridge isn't certified
            vendorId: VendorId(0xfff1),
            productId: 0x8000,
            productName: "FHEM Matter Bridge",
            productLabel: "Matter Bridge",
            nodeLabel: options.name.slice(0, 32),
            serialNumber: serial,
            uniqueId: `${serial}-bridge`,
        },
    });
    aggregator = new Endpoint(AggregatorEndpoint, { id: "aggregator" });
    await server.add(aggregator);

    // all messages are handled one after the other
    let queue = Promise.resolve();
    const lines = createInterface({ input: process.stdin });
    lines.on("line", line => {
        if (!line.trim()) return;
        queue = queue.then(async () => {
            try {
                await handle(JSON.parse(line));
            } catch (error) {
                send({ event: "error", message: String(error?.message ?? error) });
            }
        });
    });
    // fhempy stopped
    lines.on("close", async () => {
        await queue;
        await server.close();
        process.exit(0);
    });

    server.lifecycle.commissioned.on(() => sendStatus());
    server.lifecycle.decommissioned.on(() => sendStatus());
    server.events.commissioning.fabricsChanged.on(() => sendStatus());

    await server.start();
    sendStatus();
}

process.on("SIGTERM", async () => {
    await server?.close();
    process.exit(0);
});

await main();
