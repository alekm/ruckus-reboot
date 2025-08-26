# Ruckus Access Point Reboot Tool

A Python application that can SSH into a Ruckus access point and reboot it using `pexpect` for interactive command execution.

## Features

- 🔐 Secure SSH connection to Ruckus access points
- 🔄 Automated reboot functionality with confirmation
- 📊 System information gathering (version, uptime)
- 🎨 Beautiful CLI interface with progress indicators and tables
- 🛡️ Error handling and timeout management
- 🔒 Password prompt for secure credential input
- 📋 Batch processing from CSV files
- 📋 Information-only mode (no reboot)
- 📊 Clean table output for batch operations

## Installation

1. **Clone or download this repository**
   ```bash
   git clone https://github.com/alekm/ruckus-reboot.git
   cd ruckus-reboot
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Ready to use!**
   
   The tool is now ready to use. You can provide credentials via command line arguments or interactive prompts.

## Usage

### Single Device Mode

```bash
# Reboot with interactive password prompt
python ruckus_reboot.py --host 192.168.1.1 --username admin

# Reboot with password provided
python ruckus_reboot.py --host 192.168.1.1 --username admin --password your_password

# Skip confirmation prompt
python ruckus_reboot.py --host 192.168.1.1 --username admin --no-confirm
```

### Batch Processing Mode

```bash
# Reboot multiple devices from CSV file
python ruckus_reboot.py --csv-file example_ips.csv --username admin

# Skip confirmation for batch operations
python ruckus_reboot.py --csv-file example_ips.csv --username admin --no-confirm

# Show system information for each device
python ruckus_reboot.py --csv-file example_ips.csv --username admin --info

# Show system information without rebooting (information-only mode)
python ruckus_reboot.py --csv-file example_ips.csv --username admin --info --no-reboot
```

### Advanced Usage

```bash
# Show system information before reboot
python ruckus_reboot.py --host 192.168.1.1 --username admin --info

# Show system information without rebooting (information-only mode)
python ruckus_reboot.py --host 192.168.1.1 --username admin --info --no-reboot

# Use custom SSH port
python ruckus_reboot.py --host 192.168.1.1 --username admin --port 2222

# Enable verbose logging
python ruckus_reboot.py --host 192.168.1.1 --username admin --verbose
```

### Command Line Options

| Option | Short | Description | Required |
|--------|-------|-------------|----------|
| `--host` | `-h` | IP address or hostname of the Ruckus AP (single device mode) | No* |
| `--csv-file` | `-f` | CSV file containing list of IP addresses (batch mode) | No* |
| `--username` | `-u` | SSH username | Yes |
| `--password` | `-p` | SSH password (prompts if not provided) | No |
| `--port` | | SSH port (default: 22) | No |
| `--no-confirm` | | Skip reboot confirmation | No |
| `--info` | | Show system information before reboot | No |
| `--no-reboot` | | Information-only mode (no reboot) | No |
| `--verbose` | `-v` | Enable verbose logging | No |

*Either `--host` or `--csv-file` must be specified

## CSV File Format

For batch processing, create a CSV file with one IP address per line:

```csv
# Sample CSV file with Ruckus Access Point IP addresses
# Lines starting with # are comments and will be ignored
# Each IP address should be on its own line

192.168.1.1
192.168.1.2
192.168.1.3
10.0.0.1
10.0.0.2
172.16.1.1
172.16.1.2
```



## How It Works

### Single Device Mode
1. **Connection**: The tool establishes an SSH connection using `pexpect` to handle interactive prompts
2. **Authentication**: Handles Ruckus-specific login flow (`Please login:` → `password :`) and standard SSH authentication
3. **System Information** (if `--info`): Retrieves version and uptime information
4. **Reboot Execution** (unless `--no-reboot`): Executes the `reboot` command on the Ruckus CLI
5. **Cleanup**: Properly disconnects from the access point

### Batch Processing Mode
1. **CSV Parsing**: Reads IP addresses from the specified CSV file
2. **Progress Tracking**: Shows progress indicators and status for each device
3. **Sequential Processing**: Processes devices one by one with delays to avoid network overload
4. **Result Collection**: Collects results from all devices
5. **Summary Report**: Displays formatted table with results and summary statistics

## System Information Commands

The tool uses standard Ruckus commands to gather system information:
- `get version` - Retrieves model and firmware version
- `get uptime` - Retrieves system uptime

## Reboot Command

The tool uses the standard Ruckus reboot command:
- `reboot`

**Note**: The tool is specifically optimized for Ruckus access points and handles their custom CLI prompt (`rkscli:`) and authentication flow.

## Troubleshooting

### Common Issues

1. **Connection Timeout**
   - Verify the IP address is correct
   - Check if SSH is enabled on the access point
   - Ensure network connectivity

2. **Authentication Failed**
   - Verify username and password
   - Check if the user has reboot privileges
   - Some Ruckus models require specific user roles

3. **Reboot Command Not Found**
   - Verify the user has sufficient privileges to execute the `reboot` command
   - Check if the Ruckus CLI is accessible
   - Some models may require different commands

4. **Permission Denied**
   - Ensure the user has administrative privileges
   - Verify the user has reboot permissions on the Ruckus access point

### Debug Mode

Enable verbose logging to see detailed information:

```bash
python ruckus_reboot.py --host 192.168.1.1 --username admin --verbose
```

### Information-Only Mode

Get system information without rebooting:

```bash
# Single device
python ruckus_reboot.py --host 192.168.1.1 --username admin --info --no-reboot

# Multiple devices with table output
python ruckus_reboot.py --csv-file example_ips.csv --username admin --info --no-reboot --verbose
```

#### Sample System Information Table

When using `--info` with batch processing, the tool displays a clean table with system information:

```
                                         System Information Results                                          
┏━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━┓
┃ Host           ┃ Version                                              ┃ Uptime                  ┃ Status  ┃
┡━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━┩
│ 172.16.250.121 │ Ruckus R350 Multimedia Hotzone Wireless AP -         │ 4 hrs 27 mins 43 secs   │ Success │
│                │ 7.1.1.520.830                                        │                         │         │
│ 172.16.250.122 │ Ruckus R670 Multimedia Hotzone Wireless AP -         │ 1 hr 51 mins 1 sec      │ Success │
│                │ 7.1.1.520.830                                        │                         │         │
│ 172.16.250.123 │ Ruckus R670 Multimedia Hotzone Wireless AP -         │ 13 days 37 mins 56 secs │ Success │
│                │ 7.1.1.520.830                                        │                         │         │
└────────────────┴──────────────────────────────────────────────────────┴─────────────────────────┴─────────┘
```

## Security Considerations

- **Password Security**: Passwords are not logged and are hidden during input
- **SSH Key Verification**: The tool handles SSH key verification prompts automatically
- **Connection Cleanup**: Proper disconnection ensures no lingering sessions
- **Confirmation**: Reboot requires user confirmation by default
- **Information-Only Mode**: Use `--no-reboot` for safe system information gathering

## Requirements

- Python 3.7+
- SSH access to the Ruckus access point
- Valid credentials with reboot privileges
- Network connectivity to the access points

## Dependencies

The following Python packages are required (see `requirements.txt`):

- `pexpect`: Interactive command execution
- `paramiko`: SSH protocol implementation (backup)

- `click`: Command line interface
- `rich`: Rich terminal output

Install with: `pip install -r requirements.txt`

## Quick Start

```bash
# Clone the repository
git clone https://github.com/alekm/ruckus-reboot.git
cd ruckus-reboot

# Install dependencies
pip install -r requirements.txt

# Reboot a single access point
python ruckus_reboot.py --host 192.168.1.1 --username admin

# Reboot multiple access points from CSV
python ruckus_reboot.py --csv-file example_ips.csv --username admin
```

## License

This project is open source. Please ensure you have proper authorization before rebooting any network equipment.

## Disclaimer

⚠️ **Warning**: This tool will reboot your access point, which will temporarily disconnect all connected devices. Use with caution and ensure you have proper authorization before rebooting network equipment.

## Contributing

Feel free to submit issues and enhancement requests!
