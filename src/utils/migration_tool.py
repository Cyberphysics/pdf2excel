#!/usr/bin/env python3
"""
目录结构迁移工具 - 自动化迁移现有数据到新的目录结构
"""
import os
import shutil
import logging
import json
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from pathlib import Path

from .path_manager import PathManager

logger = logging.getLogger(__name__)

@dataclass
class MigrationStatus:
    """迁移状态数据类"""
    uploads_migrated: bool = False
    outputs_migrated: bool = False
    database_migrated: bool = False
    code_updated: bool = False
    config_updated: bool = False
    migration_time: Optional[datetime] = None
    errors: List[str] = field(default_factory=list)
    migrated_files: Dict[str, List[str]] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'uploads_migrated': self.uploads_migrated,
            'outputs_migrated': self.outputs_migrated,
            'database_migrated': self.database_migrated,
            'code_updated': self.code_updated,
            'config_updated': self.config_updated,
            'migration_time': self.migration_time.isoformat() if self.migration_time else None,
            'errors': self.errors,
            'migrated_files': self.migrated_files
        }

class MigrationError(Exception):
    """迁移过程中的基础异常"""
    pass

class DirectoryMigrationError(MigrationError):
    """目录迁移异常"""
    pass

class MigrationTool:
    """目录结构迁移工具"""
    
    def __init__(self, path_manager: PathManager):
        """
        初始化迁移工具
        
        Args:
            path_manager: 路径管理器实例
        """
        self.path_manager = path_manager
        self.old_paths = self._detect_old_structure()
        self.status = MigrationStatus()
        
        logger.info("MigrationTool initialized")
    
    def _detect_old_structure(self) -> Dict[str, str]:
        """
        检测旧的目录结构
        
        Returns:
            旧目录路径字典
        """
        project_root = self.path_manager.project_root
        old_paths = {
            'uploads': os.path.join(project_root, 'src', 'uploads'),
            'outputs': os.path.join(project_root, 'src', 'outputs'),
            'database': os.path.join(project_root, 'src', 'database.db'),
            'logs': os.path.join(project_root, 'src', 'logs'),
            'config': os.path.join(project_root, 'src', 'config')
        }
        
        # 检查哪些旧路径实际存在
        existing_old_paths = {}
        for name, path in old_paths.items():
            if os.path.exists(path):
                existing_old_paths[name] = path
                logger.info(f"Found old structure: {name} at {path}")
        
        return existing_old_paths
    
    def check_migration_needed(self) -> bool:
        """
        检查是否需要迁移
        
        Returns:
            如果需要迁移返回True
        """
        return len(self.old_paths) > 0
    
    def migrate_uploads(self) -> bool:
        """
        迁移uploads目录
        
        Returns:
            迁移是否成功
        """
        if 'uploads' not in self.old_paths:
            logger.info("No old uploads directory found, skipping migration")
            self.status.uploads_migrated = True
            return True
        
        old_uploads = self.old_paths['uploads']
        new_uploads = self.path_manager.config.uploads_dir
        
        try:
            migrated_files = self._migrate_directory(old_uploads, new_uploads)
            self.status.uploads_migrated = True
            self.status.migrated_files['uploads'] = migrated_files
            logger.info(f"Successfully migrated uploads directory: {len(migrated_files)} files")
            return True
        except Exception as e:
            error_msg = f"Failed to migrate uploads directory: {e}"
            logger.error(error_msg)
            self.status.errors.append(error_msg)
            return False
    
    def migrate_outputs(self) -> bool:
        """
        迁移outputs目录
        
        Returns:
            迁移是否成功
        """
        if 'outputs' not in self.old_paths:
            logger.info("No old outputs directory found, skipping migration")
            self.status.outputs_migrated = True
            return True
        
        old_outputs = self.old_paths['outputs']
        new_outputs = self.path_manager.config.outputs_dir
        
        try:
            migrated_files = self._migrate_directory(old_outputs, new_outputs)
            self.status.outputs_migrated = True
            self.status.migrated_files['outputs'] = migrated_files
            logger.info(f"Successfully migrated outputs directory: {len(migrated_files)} files")
            return True
        except Exception as e:
            error_msg = f"Failed to migrate outputs directory: {e}"
            logger.error(error_msg)
            self.status.errors.append(error_msg)
            return False
    
    def migrate_database(self) -> bool:
        """
        迁移数据库文件
        
        Returns:
            迁移是否成功
        """
        if 'database' not in self.old_paths:
            logger.info("No old database file found, skipping migration")
            self.status.database_migrated = True
            return True
        
        old_db_path = self.old_paths['database']
        new_db_path = self.path_manager.get_database_path()
        
        try:
            # 确保目标目录存在
            os.makedirs(os.path.dirname(new_db_path), exist_ok=True)
            
            # 复制数据库文件
            shutil.copy2(old_db_path, new_db_path)
            
            # 验证复制结果
            if self._verify_file_copy(old_db_path, new_db_path):
                self.status.database_migrated = True
                self.status.migrated_files['database'] = [os.path.basename(new_db_path)]
                logger.info(f"Successfully migrated database: {old_db_path} -> {new_db_path}")
                return True
            else:
                raise MigrationError("Database file verification failed")
                
        except Exception as e:
            error_msg = f"Failed to migrate database: {e}"
            logger.error(error_msg)
            self.status.errors.append(error_msg)
            return False
    
    def _migrate_directory(self, source_dir: str, target_dir: str) -> List[str]:
        """
        安全的目录迁移
        
        Args:
            source_dir: 源目录
            target_dir: 目标目录
            
        Returns:
            迁移的文件列表
            
        Raises:
            DirectoryMigrationError: 迁移失败时抛出
        """
        if not os.path.exists(source_dir):
            raise DirectoryMigrationError(f"Source directory does not exist: {source_dir}")
        
        if not os.path.isdir(source_dir):
            raise DirectoryMigrationError(f"Source is not a directory: {source_dir}")
        
        # 创建目标目录
        os.makedirs(target_dir, exist_ok=True)
        
        migrated_files = []
        
        try:
            # 遍历源目录中的所有文件
            for root, dirs, files in os.walk(source_dir):
                for file in files:
                    source_file = os.path.join(root, file)
                    
                    # 计算相对路径
                    relative_path = os.path.relpath(source_file, source_dir)
                    target_file = os.path.join(target_dir, relative_path)
                    
                    # 确保目标文件的目录存在
                    os.makedirs(os.path.dirname(target_file), exist_ok=True)
                    
                    # 复制文件
                    shutil.copy2(source_file, target_file)
                    
                    # 验证复制结果
                    if self._verify_file_copy(source_file, target_file):
                        migrated_files.append(relative_path)
                        logger.debug(f"Migrated file: {relative_path}")
                    else:
                        raise DirectoryMigrationError(f"File verification failed: {relative_path}")
            
            return migrated_files
            
        except Exception as e:
            # 如果迁移失败，尝试清理已创建的文件
            self._cleanup_partial_migration(target_dir, migrated_files)
            raise DirectoryMigrationError(f"Directory migration failed: {e}")
    
    def _verify_file_copy(self, source_file: str, target_file: str) -> bool:
        """
        验证文件复制的完整性
        
        Args:
            source_file: 源文件路径
            target_file: 目标文件路径
            
        Returns:
            验证是否通过
        """
        try:
            # 检查目标文件是否存在
            if not os.path.exists(target_file):
                return False
            
            # 比较文件大小
            source_size = os.path.getsize(source_file)
            target_size = os.path.getsize(target_file)
            
            if source_size != target_size:
                logger.warning(f"File size mismatch: {source_file} ({source_size}) vs {target_file} ({target_size})")
                return False
            
            # 比较修改时间
            source_mtime = os.path.getmtime(source_file)
            target_mtime = os.path.getmtime(target_file)
            
            # 允许1秒的时间差异（考虑到文件系统的精度）
            if abs(source_mtime - target_mtime) > 1:
                logger.warning(f"File mtime mismatch: {source_file} vs {target_file}")
                # 注意：这里不返回False，因为mtime差异不一定表示文件损坏
            
            return True
            
        except Exception as e:
            logger.error(f"File verification error: {e}")
            return False
    
    def _cleanup_partial_migration(self, target_dir: str, migrated_files: List[str]):
        """
        清理部分迁移的文件
        
        Args:
            target_dir: 目标目录
            migrated_files: 已迁移的文件列表
        """
        try:
            for file_path in migrated_files:
                full_path = os.path.join(target_dir, file_path)
                if os.path.exists(full_path):
                    os.remove(full_path)
                    logger.debug(f"Cleaned up partial migration file: {file_path}")
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
    
    def create_backup(self) -> Optional[str]:
        """
        创建旧结构的备份
        
        Returns:
            备份目录路径，如果备份失败返回None
        """
        if not self.old_paths:
            logger.info("No old structure to backup")
            return None
        
        # 创建备份目录
        backup_dir = os.path.join(self.path_manager.project_root, 'backup_old_structure')
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_dir = f"{backup_dir}_{timestamp}"
        
        try:
            os.makedirs(backup_dir, exist_ok=True)
            
            # 备份每个旧目录/文件
            for name, old_path in self.old_paths.items():
                backup_path = os.path.join(backup_dir, name)
                
                if os.path.isdir(old_path):
                    shutil.copytree(old_path, backup_path)
                else:
                    shutil.copy2(old_path, backup_path)
                
                logger.info(f"Backed up {name}: {old_path} -> {backup_path}")
            
            # 创建备份信息文件
            backup_info = {
                'backup_time': datetime.now().isoformat(),
                'original_paths': self.old_paths,
                'backup_dir': backup_dir
            }
            
            info_file = os.path.join(backup_dir, 'backup_info.json')
            with open(info_file, 'w', encoding='utf-8') as f:
                json.dump(backup_info, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Backup created successfully: {backup_dir}")
            return backup_dir
            
        except Exception as e:
            error_msg = f"Failed to create backup: {e}"
            logger.error(error_msg)
            self.status.errors.append(error_msg)
            return None
    
    def remove_old_structure(self) -> bool:
        """
        移除旧的目录结构（在成功迁移后）
        
        Returns:
            移除是否成功
        """
        if not self._is_migration_complete():
            logger.warning("Migration not complete, skipping old structure removal")
            return False
        
        success = True
        
        for name, old_path in self.old_paths.items():
            try:
                if os.path.isdir(old_path):
                    shutil.rmtree(old_path)
                else:
                    os.remove(old_path)
                
                logger.info(f"Removed old {name}: {old_path}")
                
            except Exception as e:
                error_msg = f"Failed to remove old {name} at {old_path}: {e}"
                logger.error(error_msg)
                self.status.errors.append(error_msg)
                success = False
        
        return success
    
    def _is_migration_complete(self) -> bool:
        """检查迁移是否完成"""
        return (self.status.uploads_migrated and 
                self.status.outputs_migrated and 
                self.status.database_migrated)
    
    def create_migration_report(self) -> Dict[str, Any]:
        """
        创建迁移报告
        
        Returns:
            迁移报告字典
        """
        # 统计迁移的文件数量
        total_files = sum(len(files) for files in self.status.migrated_files.values())
        
        report = {
            'migration_summary': {
                'migration_needed': self.check_migration_needed(),
                'migration_complete': self._is_migration_complete(),
                'total_files_migrated': total_files,
                'migration_time': self.status.migration_time.isoformat() if self.status.migration_time else None
            },
            'directory_status': {
                'uploads': self.status.uploads_migrated,
                'outputs': self.status.outputs_migrated,
                'database': self.status.database_migrated
            },
            'migrated_files': self.status.migrated_files,
            'errors': self.status.errors,
            'old_paths_detected': self.old_paths,
            'new_paths': {
                'uploads': self.path_manager.config.uploads_dir,
                'outputs': self.path_manager.config.outputs_dir,
                'data': self.path_manager.config.data_dir,
                'logs': self.path_manager.config.logs_dir,
                'config': self.path_manager.config.config_dir
            }
        }
        
        return report
    
    def save_migration_report(self, report_path: Optional[str] = None) -> str:
        """
        保存迁移报告到文件
        
        Args:
            report_path: 报告文件路径，如果为None则使用默认路径
            
        Returns:
            报告文件的实际路径
        """
        if report_path is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            report_filename = f"migration_report_{timestamp}.json"
            report_path = self.path_manager.get_log_path(report_filename)
        
        report = self.create_migration_report()
        
        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(report_path), exist_ok=True)
            
            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Migration report saved: {report_path}")
            return report_path
            
        except Exception as e:
            logger.error(f"Failed to save migration report: {e}")
            raise MigrationError(f"Failed to save migration report: {e}")
    
    def perform_full_migration(self, create_backup: bool = True, remove_old: bool = False) -> bool:
        """
        执行完整的迁移过程
        
        Args:
            create_backup: 是否创建备份
            remove_old: 是否移除旧结构
            
        Returns:
            迁移是否成功
        """
        logger.info("Starting full migration process")
        self.status.migration_time = datetime.now()
        
        try:
            # 1. 检查是否需要迁移
            if not self.check_migration_needed():
                logger.info("No migration needed")
                return True
            
            # 2. 创建备份（如果需要）
            backup_dir = None
            if create_backup:
                backup_dir = self.create_backup()
                if backup_dir is None:
                    logger.warning("Backup creation failed, continuing with migration")
            
            # 3. 执行迁移
            migration_success = True
            
            if not self.migrate_uploads():
                migration_success = False
            
            if not self.migrate_outputs():
                migration_success = False
            
            if not self.migrate_database():
                migration_success = False
            
            # 4. 移除旧结构（如果需要且迁移成功）
            if remove_old and migration_success:
                if not self.remove_old_structure():
                    logger.warning("Failed to remove old structure, but migration was successful")
            
            # 5. 保存迁移报告
            try:
                report_path = self.save_migration_report()
                logger.info(f"Migration report saved to: {report_path}")
            except Exception as e:
                logger.error(f"Failed to save migration report: {e}")
            
            if migration_success:
                logger.info("Full migration completed successfully")
            else:
                logger.error("Migration completed with errors")
            
            return migration_success
            
        except Exception as e:
            error_msg = f"Full migration failed: {e}"
            logger.error(error_msg)
            self.status.errors.append(error_msg)
            return False