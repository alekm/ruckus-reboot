#!/usr/bin/env python3
"""
Test script for Ruckus Access Point connectivity

This script tests SSH connectivity and basic functionality without rebooting.
Supports both single device and batch testing from CSV file.
"""

import sys
import csv
import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from ruckus_reboot import RuckusRebootTool

console = Console()


def read_csv_file(csv_file: str) -> list:
    """Read IP addresses from a CSV file."""
    ip_addresses = []
    
    try:
        with open(csv_file, 'r', newline='') as file:
            reader = csv.reader(file)
            for row in reader:
                if row:  # Skip empty rows
                    ip = row[0].strip()
                    if ip and not ip.startswith('#'):  # Skip comments
                        ip_addresses.append(ip)
        
        console.print(f"[green]Loaded {len(ip_addresses)} IP addresses from {csv_file}[/green]")
        return ip_addresses
        
    except FileNotFoundError:
        console.print(f"[red]Error: CSV file '{csv_file}' not found[/red]")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]Error reading CSV file: {str(e)}[/red]")
        sys.exit(1)


def test_single_device(host: str, username: str, password: str, port: int) -> dict:
    """Test a single device and return results."""
    tool = RuckusRebootTool(host, username, password, port)
    result = {
        'host': host,
        'connection': 'Failed',
        'privileges': 'Unknown',
        'reboot_commands': 'Unknown',
        'message': 'Unknown error'
    }
    
    try:
        # Test connection
        if tool.connect():
            result['connection'] = 'Success'
        else:
            result['message'] = 'Connection failed'
            return result
        
        # Test system information
        sys_info = tool.get_system_info()
        
        # Test privilege level
        success, output = tool.execute_command("whoami")
        if success:
            user = output.strip()
            if "admin" in user.lower() or "root" in user.lower():
                result['privileges'] = 'Admin'
            else:
                result['privileges'] = 'User'
        else:
            result['privileges'] = 'Failed'
        
        # Test reboot command availability (Ruckus uses 'reboot')
        reboot_commands = ["reboot"]
        available_commands = []
        
        for cmd in reboot_commands:
            # Try both 'which' command and direct command test
            success, output = tool.execute_command(f"which {cmd}")
            if success and output.strip():
                available_commands.append(cmd)
            else:
                # For Ruckus CLI, try the command directly
                success, output = tool.execute_command(f"{cmd} --help")
                if success or "usage" in output.lower() or "help" in output.lower():
                    available_commands.append(cmd)
        
        if available_commands:
            result['reboot_commands'] = f"{len(available_commands)} available"
        else:
            result['reboot_commands'] = 'None found'
        
        result['message'] = 'Test completed successfully'
        
    except Exception as e:
        result['message'] = f'Error: {str(e)}'
    finally:
        tool.disconnect()
    
    return result


def test_batch_devices(ip_addresses: list, username: str, password: str, port: int) -> list:
    """Test multiple devices and return results."""
    results = []
    
    console.print(f"\n[bold blue]Testing {len(ip_addresses)} devices...[/bold blue]")
    
    for i, host in enumerate(ip_addresses):
        console.print(f"\n[bold]Testing {host} ({i+1}/{len(ip_addresses)})...[/bold]")
        result = test_single_device(host, username, password, port)
        results.append(result)
    
    return results


def display_test_results(results: list):
    """Display test results in a formatted table."""
    table = Table(title="Connection Test Results")
    table.add_column("Host", style="cyan")
    table.add_column("Connection", style="green")
    table.add_column("Privileges", style="yellow")
    table.add_column("Reboot Commands", style="blue")
    table.add_column("Message", style="white")
    
    for result in results:
        # Color coding for connection status
        conn_style = "green" if result['connection'] == 'Success' else "red"
        priv_style = "green" if result['privileges'] == 'Admin' else "yellow"
        
        table.add_row(
            result['host'],
            f"[{conn_style}]{result['connection']}[/{conn_style}]",
            f"[{priv_style}]{result['privileges']}[/{priv_style}]",
            result['reboot_commands'],
            result['message']
        )
    
    console.print(table)
    
    # Summary
    success_count = sum(1 for r in results if r['connection'] == 'Success')
    admin_count = sum(1 for r in results if r['privileges'] == 'Admin')
    total_count = len(results)
    
    console.print(f"\n[bold]Summary:[/bold]")
    console.print(f"  • {success_count}/{total_count} devices connected successfully")
    console.print(f"  • {admin_count}/{total_count} devices have admin privileges")
    console.print(f"  • {total_count - success_count} devices failed to connect")


@click.command()
@click.option('--host', '-h', help='IP address or hostname of the Ruckus access point (single device mode)')
@click.option('--csv-file', '-f', help='CSV file containing list of IP addresses (batch mode)')
@click.option('--username', '-u', help='SSH username (will prompt if not provided)')
@click.option('--password', '-p', help='SSH password (will prompt if not provided)')
@click.option('--port', default=22, help='SSH port (default: 22)')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
def test_connection(host, csv_file, username, password, port, verbose):
    """Test SSH connectivity to Ruckus access point(s)"""
    
    # Validate input parameters
    if not host and not csv_file:
        console.print("[red]Error: Either --host or --csv-file must be specified[/red]")
        sys.exit(1)
    
    if host and csv_file:
        console.print("[red]Error: Cannot specify both --host and --csv-file[/red]")
        sys.exit(1)
    
    if not username:
        username = click.prompt('SSH Username')
    if not password:
        password = click.prompt('SSH Password', hide_input=True)
    
    try:
        if host:
            # Single device mode
            console.print(Panel(
                f"[bold blue]Testing Single Device[/bold blue]\n"
                f"Host: {host}\n"
                f"Username: {username}\n"
                f"Port: {port}",
                title="Connection Test",
                border_style="blue"
            ))
            
            result = test_single_device(host, username, password, port)
            display_test_results([result])
            
        else:
            # Batch mode
            console.print(Panel(
                f"[bold blue]Batch Testing Mode[/bold blue]\n"
                f"CSV File: {csv_file}\n"
                f"Username: {username}\n"
                f"Port: {port}",
                title="Batch Connection Test",
                border_style="blue"
            ))
            
            ip_addresses = read_csv_file(csv_file)
            if not ip_addresses:
                console.print("[red]No valid IP addresses found in CSV file[/red]")
                sys.exit(1)
            
            results = test_batch_devices(ip_addresses, username, password, port)
            display_test_results(results)
            
    except KeyboardInterrupt:
        console.print("\n[yellow]Test cancelled by user[/yellow]")
        sys.exit(1)
    except Exception as e:
        console.print(f"\n[red]Test failed with error: {str(e)}[/red]")
        sys.exit(1)


if __name__ == "__main__":
    test_connection()
