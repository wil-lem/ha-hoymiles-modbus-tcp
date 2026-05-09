# Hoymiles Modbus TCP Integration for Home Assistant

A custom Home Assistant integration that connects to Hoymiles DTU (Data Transfer Unit) devices via Modbus TCP to monitor solar panel production and control power output levels.

## Features

- **Real-time Power Monitoring**: View current power production from your solar panels
- **Daily Energy Production**: Track daily energy generation in kWh
- **Power Level Control**: Adjust solar panel production between 5% and 100%
- **Automatic Device Discovery**: Automatically discovers connected microinverters
- **Home Assistant Integration**: Native sensors and number entities with proper device classes

## Entities Created

### Sensors
- **Current Power**: Real-time power output in watts (kW)
- **Daily Energy**: Today's total energy production in kWh

### Controls
- **Power Level**: Adjustable slider to set production level (5-100%)

## Installation

### HACS
1. Add `https://github.com/wil-lem/ha-hoymiles-modbus-tcp/` as a custom repository to HACS
2. Install "Hoymiles Modbus TCP" in HACS
3. Follow below manual steps, from step 3

### Manual

1. Copy the `hoymiles_modbus_tcp` folder to your Home Assistant `custom_components` directory
2. Restart Home Assistant
3. Go to **Settings** > **Devices & Services** > **Add Integration**
4. Search for "Hoymiles Modbus TCP" and click to add
5. Enter your DTU's IP address and Modbus port (default: 502)

## Configuration

The integration requires:
- **DTU IP Address**: The local IP address of your Hoymiles DTU
- **DTU Port**: Modbus TCP port (typically 502)

## Requirements

- Hoymiles DTU device with Modbus TCP enabled
- DTU must be connected to your local network
- DTU must have internet connectivity
- Home Assistant with custom component support

## Dependencies

- `pymodbus`: For Modbus TCP communication
- `PyYAML`: For configuration handling

## Supported Devices

This integration communicates with Hoymiles DTU devices that support Modbus TCP protocol.

## Usage

Once configured, the integration will:
1. Automatically discover connected microinverters
2. Create sensor entities for power and energy monitoring
3. Provide a number entity for adjusting power output levels
4. Update data every 2 minutes for optimal performance

## Power Level Control

The power level control allows you to limit solar panel production:
- **Minimum**: 5% (safety limit)
- **Maximum**: 100% (full production)
- **Throttling**: Changes are limited to once every 30 seconds to prevent excessive requests

## Important Disclaimers

⚠️ **Use at Your Own Risk**: This integration is provided as-is without any warranty. Use of this software is entirely at your own risk.

⚠️ **Limited Testing**: This integration has only been tested with a **Hoymiles DTU-Pro S** device. Compatibility with other DTU models is not guaranteed.

⚠️ **Internet Requirement**: The DTU device must be connected to the internet for proper operation. Local-only configurations may not work correctly.

⚠️ **No Official Affiliation**: This project is not affiliated with, endorsed by, or officially connected to Hoymiles, Home Assistant, or any other company. All product names, logos, and brands are property of their respective owners.

⚠️ **Experimental Software**: This is experimental software that may cause unexpected behavior with your solar equipment. Always monitor your system after installation.

## Troubleshooting

### Connection Issues
- Verify DTU IP address and port
- Ensure DTU has Modbus TCP enabled
- Check that DTU is connected to your network and internet
- Verify firewall settings allow Modbus TCP traffic


## Support

This is a community-developed integration. For issues:
1. Check the Home Assistant logs for error messages
2. Verify your DTU model compatibility
3. Ensure all network connectivity requirements are met


## Contributing

Contributions are welcome! Please ensure any changes are tested with actual hardware before submitting.
