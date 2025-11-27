#!/usr/bin/env python3
"""
Task Scheduler Integration - Windows Task Scheduler Helper (v1.3.0+)
Creates and manages scheduled tasks for unattended generation
"""

import os
import subprocess
from pathlib import Path
from typing import Optional, List
from datetime import datetime, timedelta

from .logger import Logger


class TaskSchedulerHelper:
    """
    Windows Task Scheduler integration
    
    Features:
    - Create scheduled tasks
    - Delete scheduled tasks
    - List existing tasks
    - Configure triggers (time, daily, weekly)
    - Configure actions (which seasons to generate)
    """
    
    def __init__(self):
        self.logger = Logger("TaskScheduler")
        self.task_name_prefix = "NGIO_Automation"
    
    def create_task(self, 
                   task_name: str,
                   script_path: str,
                   arguments: str = "",
                   trigger_time: str = "02:00",
                   frequency: str = "ONCE",
                   description: str = "NGIO Grass Cache Generation"
                   ) -> bool:
        """
        Create a scheduled task
        
        Args:
            task_name: Name for the task
            script_path: Path to ngio_automation_runner.py or .bat
            arguments: CLI arguments (e.g., "--season winter --unattended")
            trigger_time: Time to run (HH:MM format)
            frequency: ONCE, DAILY, WEEKLY
            description: Task description
            
        Returns:
            True if successful
        """
        try:
            full_task_name = f"{self.task_name_prefix}_{task_name}"
            
            # Build schtasks command
            cmd = [
                "schtasks",
                "/Create",
                "/TN", full_task_name,
                "/TR", f'"{script_path}" {arguments}',
                "/SC", frequency,
                "/ST", trigger_time,
                "/F"  # Force create (overwrites if exists)
            ]
            
            if description:
                cmd.extend(["/RU", "SYSTEM"])  # Run as SYSTEM for reliability
            
            self.logger.info(f"Creating scheduled task: {full_task_name}")
            self.logger.debug(f"Command: {' '.join(cmd)}")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                shell=True
            )
            
            if result.returncode == 0:
                self.logger.success(f"✅ Task created: {full_task_name}")
                self.logger.info(f"   Trigger: {frequency} at {trigger_time}")
                self.logger.info(f"   Command: {script_path} {arguments}")
                return True
            else:
                self.logger.error(f"❌ Failed to create task: {result.stderr}")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to create scheduled task: {e}")
            return False
    
    def delete_task(self, task_name: str) -> bool:
        """
        Delete a scheduled task
        
        Args:
            task_name: Name of task to delete
            
        Returns:
            True if successful
        """
        try:
            full_task_name = f"{self.task_name_prefix}_{task_name}"
            
            cmd = [
                "schtasks",
                "/Delete",
                "/TN", full_task_name,
                "/F"  # Force without confirmation
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                shell=True
            )
            
            if result.returncode == 0:
                self.logger.success(f"✅ Task deleted: {full_task_name}")
                return True
            else:
                self.logger.warning(f"Task not found or already deleted: {full_task_name}")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to delete task: {e}")
            return False
    
    def list_tasks(self) -> List[str]:
        """
        List all NGIO automation tasks
        
        Returns:
            List of task names
        """
        try:
            cmd = [
                "schtasks",
                "/Query",
                "/FO", "LIST",
                "/V"
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                shell=True
            )
            
            if result.returncode != 0:
                return []
            
            # Parse output for NGIO tasks
            tasks = []
            for line in result.stdout.split('\n'):
                if self.task_name_prefix in line and "TaskName" in line:
                    task_name = line.split(':')[-1].strip()
                    tasks.append(task_name)
            
            return tasks
            
        except Exception as e:
            self.logger.error(f"Failed to list tasks: {e}")
            return []
    
    def create_overnight_task(self, 
                            season: str = "all",
                            time: str = "02:00") -> bool:
        """
        Quick helper: Create task to run overnight
        
        Args:
            season: Season to generate (winter, spring, summer, autumn, all)
            time: Time to run (HH:MM)
            
        Returns:
            True if successful
        """
        script_path = Path(__file__).parent.parent.parent / "ngio_automation_runner.py"
        
        if not script_path.exists():
            # Try .bat file
            script_path = script_path.parent / "start_ngio_automation.bat"
        
        if not script_path.exists():
            self.logger.error("Cannot find automation runner script")
            return False
        
        arguments = f"--season {season} --unattended --no-banner"
        task_name = f"Overnight_{season}"
        
        return self.create_task(
            task_name=task_name,
            script_path=str(script_path),
            arguments=arguments,
            trigger_time=time,
            frequency="ONCE",
            description=f"NGIO {season} grass cache generation"
        )
    
    def create_weekly_task(self, 
                          season: str = "all",
                          day: str = "SAT",
                          time: str = "20:00") -> bool:
        """
        Quick helper: Create weekly recurring task
        
        Args:
            season: Season to generate
            day: Day of week (MON, TUE, WED, THU, FRI, SAT, SUN)
            time: Time to run (HH:MM)
            
        Returns:
            True if successful
        """
        script_path = Path(__file__).parent.parent.parent / "ngio_automation_runner.py"
        
        if not script_path.exists():
            script_path = script_path.parent / "start_ngio_automation.bat"
        
        if not script_path.exists():
            self.logger.error("Cannot find automation runner script")
            return False
        
        arguments = f"--season {season} --unattended --no-banner"
        task_name = f"Weekly_{day}_{season}"
        
        # For weekly tasks, need to use /D parameter
        try:
            full_task_name = f"{self.task_name_prefix}_{task_name}"
            
            cmd = [
                "schtasks",
                "/Create",
                "/TN", full_task_name,
                "/TR", f'"{script_path}" {arguments}',
                "/SC", "WEEKLY",
                "/D", day,
                "/ST", time,
                "/F"
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                shell=True
            )
            
            if result.returncode == 0:
                self.logger.success(f"✅ Weekly task created: {full_task_name}")
                self.logger.info(f"   Runs every {day} at {time}")
                return True
            else:
                self.logger.error(f"Failed to create weekly task: {result.stderr}")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to create weekly task: {e}")
            return False
    
    def generate_task_xml(self,
                         task_name: str,
                         script_path: str,
                         arguments: str,
                         trigger_time: str,
                         description: str = "") -> str:
        """
        Generate Task Scheduler XML for advanced configuration
        
        Args:
            task_name: Task name
            script_path: Script to run
            arguments: Arguments to pass
            trigger_time: When to trigger
            description: Task description
            
        Returns:
            XML string
        """
        xml_template = f"""<?xml version="1.0" encoding="UTF-16"?>
<Task version="1.4" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
  <RegistrationInfo>
    <Description>{description}</Description>
    <Author>NGIO Automation Suite</Author>
  </RegistrationInfo>
  <Triggers>
    <TimeTrigger>
      <StartBoundary>{datetime.now().date()}T{trigger_time}:00</StartBoundary>
      <Enabled>true</Enabled>
    </TimeTrigger>
  </Triggers>
  <Principals>
    <Principal>
      <LogonType>InteractiveToken</LogonType>
      <RunLevel>HighestAvailable</RunLevel>
    </Principal>
  </Principals>
  <Settings>
    <MultipleInstancesPolicy>IgnoreNew</MultipleInstancesPolicy>
    <DisallowStartIfOnBatteries>false</DisallowStartIfOnBatteries>
    <StopIfGoingOnBatteries>false</StopIfGoingOnBatteries>
    <AllowHardTerminate>true</AllowHardTerminate>
    <StartWhenAvailable>true</StartWhenAvailable>
    <RunOnlyIfNetworkAvailable>false</RunOnlyIfNetworkAvailable>
    <AllowStartOnDemand>true</AllowStartOnDemand>
    <Enabled>true</Enabled>
    <Hidden>false</Hidden>
    <RunOnlyIfIdle>false</RunOnlyIfIdle>
    <WakeToRun>false</WakeToRun>
    <ExecutionTimeLimit>PT72H</ExecutionTimeLimit>
    <Priority>7</Priority>
  </Settings>
  <Actions Context="Author">
    <Exec>
      <Command>{script_path}</Command>
      <Arguments>{arguments}</Arguments>
    </Exec>
  </Actions>
</Task>"""
        return xml_template
    
    def print_setup_guide(self):
        """Print user-friendly setup guide for Task Scheduler"""
        self.logger.info("=" * 60)
        self.logger.info("📅 TASK SCHEDULER SETUP GUIDE")
        self.logger.info("=" * 60)
        
        self.logger.info("\n✨ Quick Setup Options:")
        self.logger.info("\n1. OVERNIGHT GENERATION (One-time)")
        self.logger.info("   Run tonight at 2 AM:")
        self.logger.info("   python -m src.utils.task_scheduler overnight --season all --time 02:00")
        
        self.logger.info("\n2. WEEKLY GENERATION (Recurring)")
        self.logger.info("   Run every Saturday at 8 PM:")
        self.logger.info("   python -m src.utils.task_scheduler weekly --season all --day SAT --time 20:00")
        
        self.logger.info("\n3. CUSTOM TASK")
        self.logger.info("   Full control over schedule:")
        self.logger.info("   python -m src.utils.task_scheduler create \\")
        self.logger.info("       --name MyTask --season winter --time 03:00 --frequency DAILY")
        
        self.logger.info("\n📋 MANAGE TASKS:")
        self.logger.info("   List tasks:   python -m src.utils.task_scheduler list")
        self.logger.info("   Delete task:  python -m src.utils.task_scheduler delete --name TaskName")
        
        self.logger.info("\n💡 TIPS:")
        self.logger.info("   • Tasks run even if you're logged out")
        self.logger.info("   • PC must be powered on at scheduled time")
        self.logger.info("   • Generation takes 30-60 min per season")
        self.logger.info("   • Check Windows Event Viewer if task doesn't run")
        
        self.logger.info("\n" + "=" * 60)


# === CLI INTERFACE ===

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="NGIO Task Scheduler Helper")
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # overnight command
    overnight_parser = subparsers.add_parser('overnight', help='Create overnight task')
    overnight_parser.add_argument('--season', default='all', help='Season to generate')
    overnight_parser.add_argument('--time', default='02:00', help='Time to run (HH:MM)')
    
    # weekly command
    weekly_parser = subparsers.add_parser('weekly', help='Create weekly task')
    weekly_parser.add_argument('--season', default='all', help='Season to generate')
    weekly_parser.add_argument('--day', default='SAT', help='Day of week')
    weekly_parser.add_argument('--time', default='20:00', help='Time to run (HH:MM)')
    
    # create command
    create_parser = subparsers.add_parser('create', help='Create custom task')
    create_parser.add_argument('--name', required=True, help='Task name')
    create_parser.add_argument('--season', required=True, help='Season to generate')
    create_parser.add_argument('--time', required=True, help='Time to run (HH:MM)')
    create_parser.add_argument('--frequency', default='ONCE', help='ONCE, DAILY, WEEKLY')
    
    # delete command
    delete_parser = subparsers.add_parser('delete', help='Delete task')
    delete_parser.add_argument('--name', required=True, help='Task name to delete')
    
    # list command
    list_parser = subparsers.add_parser('list', help='List all NGIO tasks')
    
    # guide command
    guide_parser = subparsers.add_parser('guide', help='Show setup guide')
    
    args = parser.parse_args()
    
    scheduler = TaskSchedulerHelper()
    
    if args.command == 'overnight':
        scheduler.create_overnight_task(args.season, args.time)
    
    elif args.command == 'weekly':
        scheduler.create_weekly_task(args.season, args.day, args.time)
    
    elif args.command == 'create':
        script_path = Path(__file__).parent.parent.parent / "ngio_automation_runner.py"
        arguments = f"--season {args.season} --unattended --no-banner"
        scheduler.create_task(args.name, str(script_path), arguments, args.time, args.frequency)
    
    elif args.command == 'delete':
        scheduler.delete_task(args.name)
    
    elif args.command == 'list':
        tasks = scheduler.list_tasks()
        if tasks:
            print(f"\nFound {len(tasks)} NGIO tasks:")
            for task in tasks:
                print(f"  • {task}")
        else:
            print("\nNo NGIO tasks found")
    
    elif args.command == 'guide':
        scheduler.print_setup_guide()
    
    else:
        parser.print_help()
        print("\nQuick start: python -m src.utils.task_scheduler guide")

