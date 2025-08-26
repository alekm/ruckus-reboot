#!/usr/bin/env python3
"""
Ruckus Access Point Reboot Tool

This application provides functionality to SSH into Ruckus access points
and reboot them using pexpect for interactive command execution.
Supports both single device and batch processing from CSV file.
"""

import os
import sys
import time
import logging
import csv
import ipaddress
from typing import Optional, Tuple, List, Dict
import pexpect
from dotenv import load_dotenv
import click
from rich.console import Console
from rich.logging import RichHandler
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True)]
)

logger = logging.getLogger("ruckus_reboot")
console = Console()


class RuckusRebootTool:
    """Main class for handling Ruckus access point reboot operations."""
    
    def __init__(self, host: str, username: str, password: str, port: int = 22):
        """
        Initialize the Ruckus reboot tool.
        
        Args:
            host: IP address or hostname of the Ruckus access point
            username: SSH username
            password: SSH password
            port: SSH port (default: 22)
        """
        self.host = host
        self.username = username
        self.password = password
        self.port = port
        self.child = None
        
    def connect(self) -> bool:
        """
        Establish SSH connection to the Ruckus access point.
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                task = progress.add_task(f"Connecting to {self.host}...", total=None)
                
                # Construct SSH command
                ssh_cmd = f"ssh -p {self.port} {self.username}@{self.host}"
                
                # Start pexpect process
                self.child = pexpect.spawn(ssh_cmd, timeout=30)
                
                # Handle different SSH prompts
                i = self.child.expect([
                    'Please login:',
                    'password:',
                    'Password:',
                    'Are you sure you want to continue connecting',
                    pexpect.EOF,
                    pexpect.TIMEOUT
                ])
                
                logger.debug(f"SSH prompt detected: index {i}")
                
                if i == 0:  # Ruckus login prompt
                    self.child.sendline(self.username)
                    self.child.expect(['password :'])
                    self.child.sendline(self.password)
                elif i == 1 or i == 2:  # Standard password prompt
                    self.child.sendline(self.password)
                elif i == 3:  # SSH key verification
                    self.child.sendline('yes')
                    self.child.expect(['password:', 'Password:', 'Please login:'])
                    if self.child.after == b'Please login:':
                        self.child.sendline(self.username)
                        self.child.expect(['password :'])
                        self.child.sendline(self.password)
                    else:
                        self.child.sendline(self.password)
                elif i == 4:  # EOF
                    logger.error(f"SSH connection failed to {self.host} - EOF received")
                    return False
                elif i == 5:  # Timeout
                    logger.error(f"SSH connection to {self.host} timed out")
                    return False
                
                # Wait for Ruckus CLI prompt
                try:
                    self.child.expect('rkscli:', timeout=10)
                    logger.info(f"Successfully connected to {self.host} (Ruckus CLI)")
                    return True
                        
                except pexpect.TIMEOUT:
                    logger.error(f"Timeout waiting for Ruckus CLI prompt from {self.host}")
                    return False
                    
        except Exception as e:
            logger.error(f"Connection error to {self.host}: {str(e)}")
            return False
    
    def execute_command(self, command: str, timeout: int = 30) -> Tuple[bool, str]:
        """
        Execute a command on the Ruckus access point.
        
        Args:
            command: Command to execute
            timeout: Command timeout in seconds
            
        Returns:
            Tuple[bool, str]: (success, output)
        """
        if not self.child:
            return False, "Not connected"
        
        try:
            self.child.sendline(command)
            
            # Wait for response (expect OK for reboot command)
            if command == "reboot":
                i = self.child.expect(['OK', 'rkscli:', pexpect.EOF, pexpect.TIMEOUT], timeout=timeout)
                output = self.child.before.decode('utf-8', errors='ignore').strip()
                
                if i == 0:  # OK response
                    return True, "OK"
                else:
                    return False, f"Reboot command failed: {output}"
            else:
                # For other commands, wait for CLI prompt
                i = self.child.expect(['rkscli:', pexpect.EOF, pexpect.TIMEOUT], timeout=timeout)
                output = self.child.before.decode('utf-8', errors='ignore').strip()
                
                if i == 0:  # rkscli prompt
                    return True, output
                else:
                    return False, f"Command failed: {output}"
                
        except Exception as e:
            return False, f"Command execution error: {str(e)}"
    
    def reboot(self, confirm: bool = True) -> bool:
        """
        Reboot the Ruckus access point.
        
        Args:
            confirm: Whether to require confirmation before reboot
            
        Returns:
            bool: True if reboot initiated successfully
        """
        if not self.child:
            logger.error(f"Not connected to {self.host}")
            return False
        
        try:
            # For Ruckus CLI, we can proceed directly with reboot
            # The whoami command may not be available in Ruckus CLI
            logger.info(f"Initiating reboot on {self.host}...")
            
            # Execute reboot command
            logger.info(f"Initiating reboot on {self.host}...")
            
            if confirm:
                console.print(Panel(
                    f"[red]WARNING: This will reboot the access point at {self.host}[/red]\n"
                    "This action will disconnect all connected devices temporarily.",
                    title="Reboot Confirmation",
                    border_style="red"
                ))
                
                if not click.confirm("Do you want to continue?"):
                    logger.info(f"Reboot cancelled by user for {self.host}")
                    return False
            
            # Try reboot command (Ruckus uses 'reboot')
            reboot_commands = [
                "reboot"
            ]
            
            for cmd in reboot_commands:
                            success, output = self.execute_command(cmd, timeout=60)
            if success:
                logger.info(f"Reboot command '{cmd}' executed successfully on {self.host}")
                logger.info(f"Command output: '{output}'")
                logger.info(f"Access point {self.host} is rebooting...")
                return True
            else:
                logger.error(f"Command '{cmd}' failed on {self.host}: {output}")
            
            logger.error(f"All reboot commands failed on {self.host}")
            return False
            
        except Exception as e:
            logger.error(f"Reboot error on {self.host}: {str(e)}")
            return False
    
    def get_system_info(self) -> dict:
        """
        Get system information from the access point.
        
        Returns:
            dict: System information
        """
        info = {}
        
        commands = {
            "version": "get version",
            "uptime": "get uptime"
        }
        
        for key, cmd in commands.items():
            success, output = self.execute_command(cmd)
            if success:
                # Clean up the output
                if key == "version":
                    # Remove "get version" command from the output first
                    clean_output = output.replace('get version', '').strip()
                    lines = clean_output.split('\n')
                    if len(lines) >= 2:
                        model = lines[0].strip()
                        version = lines[1].replace('Version:', '').strip()
                        info[key] = f"{model} - {version}"
                    else:
                        info[key] = clean_output
                elif key == "uptime":
                    # Extract just the uptime info
                    if 'Uptime:' in output:
                        uptime = output.split('Uptime:')[1].split('OK')[0].strip()
                        info[key] = uptime
                    else:
                        info[key] = output.strip()
                else:
                    info[key] = output.strip()
            else:
                info[key] = "Not available"
        
        return info
    
    def disconnect(self):
        """Disconnect from the access point."""
        if self.child:
            try:
                self.child.sendline("exit")
                self.child.close()
                logger.info(f"Disconnected from {self.host}")
            except:
                pass
            finally:
                self.child = None


def read_csv_file(csv_file: str) -> List[str]:
    """
    Read IP addresses from a CSV file.
    
    Args:
        csv_file: Path to the CSV file
        
    Returns:
        List[str]: List of valid IP addresses
    """
    ip_addresses = []
    invalid_ips = []
    
    try:
        with open(csv_file, 'r', newline='') as file:
            reader = csv.reader(file)
            for row_num, row in enumerate(reader, 1):
                if row:  # Skip empty rows
                    ip = row[0].strip()
                    if ip and not ip.startswith('#'):  # Skip comments
                        # Validate IP address
                        try:
                            ipaddress.ip_address(ip)
                            ip_addresses.append(ip)
                        except ValueError:
                            invalid_ips.append((row_num, ip))
        
        # Report invalid IP addresses
        if invalid_ips:
            console.print(f"[red]Warning: Found {len(invalid_ips)} invalid IP addresses in {csv_file}:[/red]")
            for row_num, ip in invalid_ips:
                console.print(f"[red]  Row {row_num}: '{ip}' is not a valid IP address[/red]")
            
            if not ip_addresses:
                console.print(f"[red]Error: No valid IP addresses found in {csv_file}[/red]")
                sys.exit(1)
            else:
                console.print(f"[yellow]Continuing with {len(ip_addresses)} valid IP addresses...[/yellow]")
        
        console.print(f"[green]Loaded {len(ip_addresses)} valid IP addresses from {csv_file}[/green]")
        return ip_addresses
        
    except FileNotFoundError:
        console.print(f"[red]Error: CSV file '{csv_file}' not found[/red]")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]Error reading CSV file: {str(e)}[/red]")
        sys.exit(1)


def process_single_device(host: str, username: str, password: str, port: int, 
                         no_confirm: bool, info: bool, no_reboot: bool = False, verbose: bool = False) -> Dict[str, str]:
    """
    Process a single device.
    
    Returns:
        Dict[str, str]: Result information
    """
    tool = RuckusRebootTool(host, username, password, port)
    result = {
        'host': host,
        'status': 'Failed',
        'message': 'Unknown error'
    }
    
    try:
        # Connect to access point
        if not tool.connect():
            result['message'] = 'Connection failed'
            return result
        
        # Get system information if requested
        if info:
            sys_info = tool.get_system_info()
            # Add system info to result for table display
            result.update(sys_info)
        
        # Perform reboot (unless --no-reboot is specified)
        if no_reboot:
            result['status'] = 'Success'
            result['message'] = 'System information retrieved successfully (no reboot performed)'
        else:
            if tool.reboot(confirm=not no_confirm):
                result['status'] = 'Success'
                result['message'] = 'Reboot initiated successfully'
            else:
                result['message'] = 'Failed to initiate reboot'
            
    except Exception as e:
        result['message'] = f'Error: {str(e)}'
    finally:
        tool.disconnect()
    
    return result


def process_batch_devices(ip_addresses: List[str], username: str, password: str, 
                         port: int, no_confirm: bool, info: bool, no_reboot: bool = False, verbose: bool = False) -> List[Dict[str, str]]:
    """
    Process multiple devices in batch.
    
    Returns:
        List[Dict[str, str]]: List of results for each device
    """
    results = []
    
    if verbose:
        console.print(f"\n[bold blue]Processing {len(ip_addresses)} devices...[/bold blue]")
        
        for i, host in enumerate(ip_addresses):
            console.print(f"\n[bold]Processing {host} ({i+1}/{len(ip_addresses)})...[/bold]")
            
            result = process_single_device(host, username, password, port, no_confirm, info, no_reboot, verbose)
            results.append(result)
            
            # Add delay between devices to avoid overwhelming the network
            if i < len(ip_addresses) - 1:
                time.sleep(2)
    else:
        # Simple output mode
        for i, host in enumerate(ip_addresses):
            if not info:  # Only show reboot progress if not getting system info
                console.print(f"Rebooting {host}...", end="")
            
            result = process_single_device(host, username, password, port, no_confirm, info, no_reboot, verbose)
            results.append(result)
            
            if not info:  # Only show status if not getting system info
                if result['status'] == 'Success':
                    console.print("OK!")
                else:
                    console.print(f"FAILED: {result['message']}")
            
            # Add delay between devices to avoid overwhelming the network
            if i < len(ip_addresses) - 1:
                time.sleep(2)
    
    return results


def display_results(results: List[Dict[str, str]], verbose: bool = False, info_mode: bool = False):
    """Display results in a formatted table."""
    if info_mode:
        # Always show system information table when --info is used
        table = Table(title="System Information Results")
        table.add_column("Host", style="cyan")
        table.add_column("Version", style="blue")
        table.add_column("Uptime", style="green")
        table.add_column("Status", style="yellow")
        
        for result in results:
            status_style = "green" if result['status'] == 'Success' else "red"
            version = result.get('version', 'N/A')
            uptime = result.get('uptime', 'N/A')
            table.add_row(
                result['host'],
                version,
                uptime,
                f"[{status_style}]{result['status']}[/{status_style}]"
            )
        
        console.print(table)
    elif verbose:
        # Reboot results table (only in verbose mode)
        table = Table(title="Reboot Results")
        table.add_column("Host", style="cyan")
        table.add_column("Status", style="green")
        table.add_column("Message", style="white")
        
        for result in results:
            status_style = "green" if result['status'] == 'Success' else "red"
            table.add_row(
                result['host'],
                f"[{status_style}]{result['status']}[/{status_style}]",
                result['message']
            )
        
        console.print(table)
    
    # Summary
    success_count = sum(1 for r in results if r['status'] == 'Success')
    total_count = len(results)
    
    if info_mode:
        if verbose:
            console.print(f"\n[bold]Summary:[/bold] {success_count}/{total_count} devices queried successfully")
        else:
            console.print(f"\n{success_count}/{total_count} devices queried successfully")
    else:
        if verbose:
            console.print(f"\n[bold]Summary:[/bold] {success_count}/{total_count} devices rebooted successfully")
        else:
            console.print(f"\n{success_count}/{total_count} devices rebooted successfully")


@click.command()
@click.option('--host', '-h', help='IP address or hostname of the Ruckus access point (single device mode)')
@click.option('--csv-file', '-f', help='CSV file containing list of IP addresses (batch mode)')
@click.option('--username', '-u', help='SSH username (will prompt if not provided)')
@click.option('--password', '-p', help='SSH password (will prompt if not provided)')
@click.option('--port', default=22, help='SSH port (default: 22)')
@click.option('--no-confirm', is_flag=True, help='Skip reboot confirmation')
@click.option('--info', is_flag=True, help='Show system information before reboot')
@click.option('--no-reboot', is_flag=True, help='Only show system information, do not reboot')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose logging')
def main(host, csv_file, username, password, port, no_confirm, info, no_reboot, verbose):
    """Ruckus Access Point Reboot Tool - Single device or batch processing"""
    
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    else:
        logging.getLogger().setLevel(logging.WARNING)
    
    # Validate input parameters
    if not host and not csv_file:
        console.print("[red]Error: Either --host or --csv-file must be specified[/red]")
        sys.exit(1)
    
    if host and csv_file:
        console.print("[red]Error: Cannot specify both --host and --csv-file[/red]")
        sys.exit(1)
    
    # Get username and password if not provided
    if not username:
        username = click.prompt('SSH Username')
    if not password:
        password = click.prompt('SSH Password', hide_input=True)
    
    try:
        if host:
            # Single device mode
            if verbose:
                console.print(Panel(
                    f"[bold blue]Single Device Mode[/bold blue]\n"
                    f"Host: {host}\n"
                    f"Username: {username}\n"
                    f"Port: {port}",
                    title="Reboot Operation",
                    border_style="blue"
                ))
            
            result = process_single_device(host, username, password, port, no_confirm, info, no_reboot, verbose)
            display_results([result], verbose, info_mode=info)
            
        else:
            # Batch mode
            if verbose:
                console.print(Panel(
                    f"[bold blue]Batch Processing Mode[/bold blue]\n"
                    f"CSV File: {csv_file}\n"
                    f"Username: {username}\n"
                    f"Port: {port}",
                    title="Batch Reboot Operation",
                    border_style="blue"
                ))
            
            ip_addresses = read_csv_file(csv_file)
            if not ip_addresses:
                console.print("[red]No valid IP addresses found in CSV file[/red]")
                sys.exit(1)
            
            # Confirm batch operation (only if actually rebooting)
            if not no_confirm and not no_reboot:
                if verbose:
                    console.print(Panel(
                        f"[red]WARNING: This will reboot {len(ip_addresses)} access points[/red]\n"
                        "This action will disconnect all connected devices temporarily.",
                        title="Batch Reboot Confirmation",
                        border_style="red"
                    ))
                else:
                    console.print(f"About to reboot {len(ip_addresses)} access points...")
                
                if not click.confirm("Do you want to continue?"):
                    console.print("[yellow]Batch operation cancelled by user[/yellow]")
                    sys.exit(0)
            
            results = process_batch_devices(ip_addresses, username, password, port, no_confirm, info, no_reboot, verbose)
            display_results(results, verbose, info_mode=info)
            
    except KeyboardInterrupt:
        console.print("\n[yellow]Operation cancelled by user[/yellow]")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]Unexpected error: {str(e)}[/red]")
        sys.exit(1)


if __name__ == "__main__":
    main()
