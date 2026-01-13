import os
import tkinter as tk
import datetime
import shutil
import time
import sys
import traceback
from datetime import datetime as dt
from tkinter import messagebox, ttk
from pathlib import Path
import logging

# Setup logging
logging.basicConfig(
    filename='backup_tool.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class BackupTool:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title('LothianGaming Save Backup Tool')
        self.root.geometry('600x400')
        self.root.configure(bg='#1e1e1e')
        
        # Platform-specific paths
        self.main_dir = Path.home()
        self.backup_base = self.main_dir / "AppData" / "LocalLow" / "semiwork" / "Repo"
        self.save_dir = self.backup_base / "saves"
        
        # Create backup directory with timestamp
        self.backup_dir = self.backup_base / "LothianGaming_SaveBackups" / f"Backup_{dt.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Settings defaults
        self.auto_backup_var = tk.BooleanVar(value=False)
        self.compression_var = tk.BooleanVar(value=False)
        self.retention_var = tk.IntVar(value=30)
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the user interface"""
        # Main frame
        main_frame = tk.Frame(self.root, bg='#1e1e1e', padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header
        header = tk.Label(main_frame, 
                         text="LothianGaming Save Backup Tool",
                         font=("Arial", 16, "bold"),
                         bg='#1e1e1e',
                         fg="#ff0000")
        header.pack(pady=(0, 20))
        
        # Status display
        self.status_var = tk.StringVar(value="Ready to backup saves")
        status_label = tk.Label(main_frame, 
                               textvariable=self.status_var,
                               font=("Arial", 10),
                               bg='#1e1e1e',
                               fg='white')
        status_label.pack(pady=(0, 10))
        
        # Progress bar
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.pack(fill=tk.X, pady=(0, 20))
        
        # Info frame
        info_frame = tk.LabelFrame(main_frame, 
                                  text="Backup Information",
                                  font=("Arial", 10, "bold"),
                                  bg='#2d2d2d',
                                  fg='white',
                                  padx=10,
                                  pady=10)
        info_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Source and destination info
        tk.Label(info_frame, 
                text=f"Source: {self.save_dir}",
                bg='#2d2d2d',
                fg='#cccccc',
                anchor='w').pack(fill=tk.X, pady=(0, 5))
        tk.Label(info_frame, 
                text=f"Destination: {self.backup_dir}",
                bg='#2d2d2d',
                fg='#cccccc',
                anchor='w').pack(fill=tk.X, pady=(0, 5))
        
        # Stats display
        self.stats_var = tk.StringVar(value="No backup performed yet")
        stats_label = tk.Label(info_frame, 
                              textvariable=self.stats_var,
                              bg='#2d2d2d',
                              fg='#00ff00',
                              anchor='w')
        stats_label.pack(fill=tk.X, pady=(5, 0))
        
        # Button frame
        button_frame = tk.Frame(main_frame, bg='#1e1e1e')
        button_frame.pack()
        
        # Buttons
        tk.Button(button_frame, 
                 text="Backup Now",
                 command=self.backup_saves,
                 bg='#007acc',
                 fg='white',
                 padx=20,
                 pady=5).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, 
                 text="Open Backup Folder",
                 command=self.open_backup_folder,
                 bg='#555555',
                 fg='white',
                 padx=20,
                 pady=5).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, 
                 text="Settings",
                 command=self.open_settings,
                 bg='#555555',
                 fg='white',
                 padx=20,
                 pady=5).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, 
                 text="Exit",
                 command=self.root.quit,
                 bg='#cc0000',
                 fg='white',
                 padx=20,
                 pady=5).pack(side=tk.LEFT, padx=5)
        
    def get_directory_size(self, directory_path):
        """Calculate total size of a directory in bytes"""
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(directory_path):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                if os.path.isfile(filepath):
                    total_size += os.path.getsize(filepath)
        return total_size
    
    def format_size(self, size_bytes):
        """Convert bytes to human-readable format"""
        if size_bytes == 0:
            return "0 bytes"
        
        size_names = ["bytes", "KB", "MB", "GB", "TB"]
        i = 0
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1
        
        return f"{size_bytes:.2f} {size_names[i]}"
    
    def copy_directory(self, source, destination):
        """Recursively copy directory with progress tracking"""
        files_copied = 0
        
        for root_dir, dirs, files in os.walk(source):
            # Create corresponding directories in destination
            rel_path = os.path.relpath(root_dir, source)
            dest_dir = os.path.join(destination, rel_path)
            os.makedirs(dest_dir, exist_ok=True)
            
            for file in files:
                src_file = os.path.join(root_dir, file)
                dest_file = os.path.join(dest_dir, file)
                
                # Skip if file already exists and is identical
                if os.path.exists(dest_file):
                    if self.files_identical(src_file, dest_file):
                        continue
                
                shutil.copy2(src_file, dest_file)  # copy2 preserves metadata
                files_copied += 1
                
                # Update status periodically
                if files_copied % 10 == 0:
                    self.status_var.set(f"Copying... {files_copied} files processed")
                    self.root.update()
        
        return files_copied
    
    def files_identical(self, file1, file2):
        """Check if two files are identical"""
        try:
            return os.path.getmtime(file1) == os.path.getmtime(file2) and \
                   os.path.getsize(file1) == os.path.getsize(file2)
        except:
            return False
    
    def create_backup_report(self, files_copied):
        """Create a detailed backup report"""
        total_size_bytes = self.get_directory_size(self.backup_dir)
        total_size_human = self.format_size(total_size_bytes)
        
        report = {
            "backup_date": dt.now().isoformat(),
            "source": str(self.save_dir),
            "destination": str(self.backup_dir),
            "files_copied": files_copied,
            "total_size_bytes": total_size_bytes,
            "total_size_human": total_size_human,
            "system_info": {
                "platform": sys.platform,
                "python_version": sys.version
            }
        }
        
        report_path = self.backup_dir / "backup_report.json"
        import json
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        return total_size_human
    
    def create_compressed_backup(self):
        """Create a compressed ZIP backup"""
        try:
            from zipfile import ZipFile, ZIP_DEFLATED
            
            zip_path = self.backup_dir.with_suffix('.zip')
            
            with ZipFile(zip_path, 'w', ZIP_DEFLATED) as zipf:
                for root_dir, dirs, files in os.walk(self.save_dir):
                    for file in files:
                        file_path = os.path.join(root_dir, file)
                        arcname = os.path.relpath(file_path, self.save_dir)
                        zipf.write(file_path, arcname)
            
            # Remove uncompressed directory after successful compression
            shutil.rmtree(self.backup_dir)
            return zip_path
            
        except Exception as e:
            logging.error(f"Compression failed: {str(e)}")
            return None
    
    def cleanup_old_backups(self):
        """Remove backups older than retention period"""
        try:
            backup_root = self.backup_base / "LothianGaming_SaveBackups"
            if not backup_root.exists():
                return
            
            cutoff_date = dt.now() - datetime.timedelta(days=self.retention_var.get())
            backups_removed = 0
            
            for backup_dir in backup_root.iterdir():
                if backup_dir.is_dir():
                    try:
                        # Extract date from directory name
                        dir_name = backup_dir.name
                        if dir_name.startswith("Backup_"):
                            date_str = dir_name.replace("Backup_", "")
                            dir_date = dt.strptime(date_str, '%Y%m%d_%H%M%S')
                            if dir_date < cutoff_date:
                                shutil.rmtree(backup_dir)
                                backups_removed += 1
                                logging.info(f"Removed old backup: {backup_dir}")
                    except ValueError:
                        continue
            
            if backups_removed > 0:
                self.status_var.set(f"Cleaned up {backups_removed} old backup(s)")
                
        except Exception as e:
            logging.warning(f"Failed to cleanup old backups: {str(e)}")
    
    def backup_saves(self):
        """Main backup function"""
        try:
            self.progress.start()
            self.status_var.set("Starting backup...")
            self.root.update()
            
            # Validate source directory exists
            if not self.save_dir.exists():
                messagebox.showerror("Error", f"Save directory not found:\n{self.save_dir}")
                return
            
            # Create backup directory
            self.backup_dir.mkdir(parents=True, exist_ok=True)
            
            # Clean up old backups
            self.cleanup_old_backups()
            
            # Backup files
            files_copied = self.copy_directory(self.save_dir, self.backup_dir)
            
            # Create compressed backup if enabled
            if self.compression_var.get():
                self.status_var.set("Compressing backup...")
                self.root.update()
                zip_path = self.create_compressed_backup()
                if zip_path:
                    self.backup_dir = zip_path
            
            # Create backup report
            total_size = self.create_backup_report(files_copied)
            
            self.status_var.set(f"Backup completed! {files_copied} files ({total_size})")
            self.stats_var.set(f"Last backup: {dt.now().strftime('%Y-%m-%d %H:%M:%S')} | Files: {files_copied} | Size: {total_size}")
            
            logging.info(f"Backup completed: {files_copied} files ({total_size}) to {self.backup_dir}")
            
            # Show success message
            messagebox.showinfo("Success", 
                              f"Backup completed successfully!\n\n"
                              f"Files: {files_copied}\n"
                              f"Size: {total_size}\n"
                              f"Location: {self.backup_dir}")
            
        except Exception as e:
            error_msg = f"An error occurred:\n{str(e)}"
            logging.error(f"Backup failed: {str(e)}")
            messagebox.showerror("Backup Error", error_msg)
            self.status_var.set("Backup failed - see log for details")
        finally:
            self.progress.stop()
    
    def open_backup_folder(self):
        """Open the backup folder in file explorer"""
        try:
            folder_path = self.backup_base / "LothianGaming_SaveBackups"
            folder_path.mkdir(exist_ok=True)  # Create if doesn't exist
            
            if sys.platform == 'win32':
                os.startfile(folder_path)
            elif sys.platform == 'darwin':
                import subprocess
                subprocess.run(['open', folder_path])
            else:
                import subprocess
                subprocess.run(['xdg-open', folder_path])
        except Exception as e:
            messagebox.showwarning("Warning", f"Could not open folder:\n{str(e)}")
    
    def open_settings(self):
        """Open settings window"""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Settings")
        settings_window.geometry("400x300")
        settings_window.configure(bg='#2d2d2d')
        
        # Add settings options
        tk.Label(settings_window, 
                text="Backup Settings",
                font=("Arial", 14, "bold"),
                bg='#2d2d2d',
                fg='white').pack(pady=10)
        
        # Auto-backup option
        tk.Checkbutton(settings_window, 
                      text="Enable auto-backup on game launch",
                      variable=self.auto_backup_var,
                      bg='#2d2d2d',
                      fg='white',
                      selectcolor='#2d2d2d',
                      activebackground='#2d2d2d',
                      activeforeground='white').pack(pady=5, anchor='w', padx=20)
        
        # Compression option
        tk.Checkbutton(settings_window,
                      text="Compress backups (ZIP format)",
                      variable=self.compression_var,
                      bg='#2d2d2d',
                      fg='white',
                      selectcolor='#2d2d2d',
                      activebackground='#2d2d2d',
                      activeforeground='white').pack(pady=5, anchor='w', padx=20)
        
        # Retention policy
        tk.Label(settings_window, 
                text="Keep backups for:",
                bg='#2d2d2d',
                fg='white').pack(pady=(10, 0), anchor='w', padx=20)
        
        spin_frame = tk.Frame(settings_window, bg='#2d2d2d')
        spin_frame.pack(pady=5, anchor='w', padx=20)
        
        tk.Spinbox(spin_frame, 
                  from_=1, to=365,
                  textvariable=self.retention_var,
                  width=5,
                  bg='#3d3d3d',
                  fg='white').pack(side=tk.LEFT)
        tk.Label(spin_frame, 
                text="days",
                bg='#2d2d2d',
                fg='white').pack(side=tk.LEFT, padx=5)
        
        # Save button
        tk.Button(settings_window, 
                 text="Save Settings",
                 command=lambda: self.save_settings(settings_window),
                 bg='#007acc',
                 fg='white',
                 padx=20,
                 pady=5).pack(pady=20)
    
    def save_settings(self, window):
        """Save settings to config file"""
        settings = {
            'auto_backup': self.auto_backup_var.get(),
            'compress_backups': self.compression_var.get(),
            'retention_days': self.retention_var.get()
        }
        
        config_dir = self.main_dir / ".lothiangaming_backup"
        config_dir.mkdir(exist_ok=True)
        config_file = config_dir / "settings.json"
        
        import json
        try:
            with open(config_file, 'w') as f:
                json.dump(settings, f, indent=2)
            
            window.destroy()
            messagebox.showinfo("Settings", "Settings saved successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save settings:\n{str(e)}")
    
    def load_settings(self):
        """Load settings from config file"""
        config_file = self.main_dir / ".lothiangaming_backup" / "settings.json"
        if config_file.exists():
            try:
                import json
                with open(config_file, 'r') as f:
                    settings = json.load(f)
                    self.auto_backup_var.set(settings.get('auto_backup', False))
                    self.compression_var.set(settings.get('compress_backups', False))
                    self.retention_var.set(settings.get('retention_days', 30))
            except Exception as e:
                logging.warning(f"Failed to load settings: {str(e)}")


def main():
    """Main entry point"""
    try:
        app = BackupTool()
        app.load_settings()  # Load saved settings
        
        # Center the window on screen
        app.root.update_idletasks()
        width = app.root.winfo_width()
        height = app.root.winfo_height()
        x = (app.root.winfo_screenwidth() // 2) - (width // 2)
        y = (app.root.winfo_screenheight() // 2) - (height // 2)
        app.root.geometry(f'{width}x{height}+{x}+{y}')
        
        app.root.mainloop()
    except Exception as e:
        logging.critical(f"Application failed to start: {str(e)}")
        messagebox.showerror("Critical Error", 
                           f"The application encountered a critical error:\n{str(e)}\n\n"
                           f"Please check the log file for details.")
        sys.exit(1)


if __name__ == "__main__":
    main()
