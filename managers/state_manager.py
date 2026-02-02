# state_manager.py

# 标准库模块导入
import json
import os

# 第三方模块导入
from PyQt6.QtCore import QTimer

# 项目模块导入
from utils import get_user_data_dir


class StateManager:
    """状态管理器，负责管理应用程序的状态保存、加载、撤销和重做功能

    主要职责：
    - 管理撤销/重做栈
    - 处理状态保存和加载
    - 管理自动保存功能
    - 处理新建文件操作
    """
    
    def __init__(self, parent_window):
        """初始化状态管理器
        
        Args:
            parent_window: 主窗口实例，用于访问主窗口的属性和方法
        """
        self.parent_window = parent_window
        self.debug_logger = parent_window.debug_logger
        
        # 状态管理属性
        self.undo_stack = []  # 撤销栈
        self.redo_stack = []  # 重做栈
        self.max_undo_steps = 50  # 最大撤销步骤数
        self._batch_operation = False  # 批量操作标志
        self._pending_undo_save = False  # 待保存撤销状态标志
        
        # 初始化定时器
        self._init_timers()
    
    def _init_timers(self):
        """初始化定时器"""
        # 撤销延迟保存定时器
        self._undo_save_timer = QTimer()
        self._undo_save_timer.setSingleShot(True)
        self._undo_save_timer.setInterval(500)  # 500ms延迟
        self._undo_save_timer.timeout.connect(self._delayed_save_state)

        # 自动保存定时器
        self.auto_save_timer = QTimer()
        self.auto_save_timer.setInterval(30000)  # 30秒自动保存一次
        self.auto_save_timer.timeout.connect(self.save_saved_state)
        self.auto_save_timer.start()

    def _collect_all_events_data(self):
        """收集所有事件数据 - 优化版本

        从事件表格中逐行逐列收集所有事件数据,跳过行号列。

        Returns:
            list: 所有事件数据列表,每个元素是一个事件的数据列表
        """
        table = self.parent_window.event_manager.events_table
        row_count = table.rowCount()

        # 使用列表推导式批量收集数据，避免重复调用 item() 方法
        all_events = [
            [
                (item.text() if (item := table.item(row, col)) else "")
                for col in range(1, 8)
            ]
            for row in range(row_count)
        ]

        return all_events
    
    def save_state_to_undo_stack(self):
        """保存当前状态到撤销栈

        收集当前表格中的所有事件数据，保存到撤销栈中。
        如果当前处于批量操作状态，则不保存。
        """
        if self._batch_operation:
            # 如果是批量操作，暂时不保存状态
            return

        # 添加到撤销栈
        state = {
            'events': self._collect_all_events_data()
        }

        # 限制撤销栈大小
        self.undo_stack.append(state)
        if len(self.undo_stack) > self.max_undo_steps:
            self.undo_stack.pop(0)

        # 清空重做栈
        self.redo_stack.clear()

        self.debug_logger.log_info(f"状态已保存到撤销栈，当前撤销栈大小: {len(self.undo_stack)}")

    def _delayed_save_state(self):
        """延迟保存状态到撤销栈

        如果有待保存的撤销状态标志，则调用 save_state_to_undo_stack 保存状态。
        """
        if self._pending_undo_save:
            self.save_state_to_undo_stack()
            self._pending_undo_save = False

    def mark_state_dirty(self):
        """标记状态已更改，延迟保存到撤销栈

        如果当前处于批量操作状态，则不标记。
        否则设置待保存标志，并启动延迟保存定时器。
        """
        if self._batch_operation:
            return

        # 延迟保存状态，避免频繁保存
        self._pending_undo_save = True
        self._undo_save_timer.start(500)  # 500ms后保存

    def on_undo(self):
        """撤销操作

        将当前状态保存到重做栈，然后恢复撤销栈中的上一个状态。
        如果撤销栈为空，则提示用户没有可撤销的操作。
        """
        if not self.undo_stack:
            self.parent_window.status_bar.showMessage("⚠️ 没有可撤销的操作")
            return

        # 保存当前状态到重做栈
        current_state = {
            'events': self._collect_all_events_data()
        }
        self.redo_stack.append(current_state)

        # 恢复上一个状态
        previous_state = self.undo_stack.pop()
        self._restore_state(previous_state)

        # 保存状态到文件
        self.save_saved_state()

        self.parent_window.status_bar.showMessage("✅ 已撤销操作")
        self.debug_logger.log_info("已撤销操作")

    def on_redo(self):
        """重做操作

        将当前状态保存到撤销栈，然后恢复重做栈中的下一个状态。
        如果重做栈为空，则提示用户没有可重做的操作。
        """
        if not self.redo_stack:
            self.parent_window.status_bar.showMessage("⚠️ 没有可重做的操作")
            return

        # 保存当前状态到撤销栈
        current_state = {
            'events': self._collect_all_events_data()
        }
        self.undo_stack.append(current_state)

        # 恢复下一个状态
        next_state = self.redo_stack.pop()
        self._restore_state(next_state)

        # 保存状态到文件
        self.save_saved_state()

        self.parent_window.status_bar.showMessage("✅ 已重做操作")
        self.debug_logger.log_info("已重做操作")

    def _restore_state(self, state):
        """恢复状态

        Args:
            state: 要恢复的状态字典，包含 events 列表
        """
        # 清空当前事件
        self.parent_window.event_manager.events_table.setRowCount(0)

        # 开始批量操作
        self._batch_operation = True

        try:
            # 恢复事件
            for i, event_data in enumerate(state['events']):
                # 创建行数据，包括行号
                row_data = [str(i + 1)] + event_data
                self.parent_window.event_manager.add_table_row(row_data)

            # 更新统计信息
            self.parent_window.event_manager.update_stats()

            # 立即更新预计总时间
            self.parent_window.settings_panel.on_calculate_total_time()
        finally:
            # 结束批量操作
            self._batch_operation = False

    def on_new_file(self):
        """新建文件

        清空当前事件列表，保存当前状态到撤销栈和文件。
        用户需要确认操作，未保存的更改将丢失。
        """
        # 询问用户是否确认新建
        from styles import ChineseMessageBox
        reply = ChineseMessageBox.show_question(self.parent_window, "新建文件", "确定要新建一个空的事件列表吗？当前未保存的更改将丢失。")
        if not reply:
            return

        # 清空当前事件
        self.parent_window.event_manager.events_table.setRowCount(0)

        # 保存当前状态到撤销栈
        self.save_state_to_undo_stack()

        # 保存状态到文件
        self.save_saved_state()

        # 立即更新预计总时间
        self.parent_window.settings_panel.on_calculate_total_time()

        self.parent_window.status_bar.showMessage("✅ 已新建文件")
        self.debug_logger.log_info("已新建文件")

    def load_saved_state(self):
        """加载保存的状态

        从用户数据目录的日志文件夹中加载保存的状态文件。
        恢复事件数据和设置信息。

        Returns:
            bool: 加载成功返回True，失败返回False
        """
        try:
            # 使用用户数据目录作为日志目录
            logs_dir = os.path.join(get_user_data_dir(), "logs")

            # 确保logs目录存在
            if not os.path.exists(logs_dir):
                os.makedirs(logs_dir, exist_ok=True)

            # 设置文件路径
            state_file = os.path.join(logs_dir, "BetterGI_StellTrack_state.json")
            self.debug_logger.log_info(f"尝试从 {state_file} 加载保存的状态")

            if os.path.exists(state_file):
                try:
                    with open(state_file, 'r', encoding='utf-8') as f:
                        state = json.load(f)

                    # 验证状态数据的完整性
                    if isinstance(state, dict):
                        # 恢复事件
                        if 'events' in state and isinstance(state['events'], list):
                            event_count = len(state['events'])
                            self.debug_logger.log_info(f"开始恢复 {event_count} 个事件")

                            for i, event_data in enumerate(state['events']):
                                # 创建行数据，包括行号
                                row_data = [str(i + 1)] + event_data
                                self.parent_window.event_manager.add_table_row(row_data)

                            self.debug_logger.log_info(f"已成功恢复 {event_count} 个事件")
                        else:
                            self.debug_logger.log_warning(f"状态文件中events字段缺失或格式错误，跳过事件恢复")

                        # 加载设置
                        if 'settings' in state:
                            self.parent_window.settings_panel.restore_settings(state['settings'])
                            self.debug_logger.log_info(f"已成功加载保存的设置")

                        self.debug_logger.log_info(f"已成功加载保存的状态")
                        return True
                    else:
                        self.debug_logger.log_error(f"状态文件格式不正确，不是有效的字典")
                        return False
                except json.JSONDecodeError as e:
                    self.debug_logger.log_error(f"解析状态文件失败: {e}")
                    return False
                except (OSError, ValueError) as e:
                    self.debug_logger.log_error(f"恢复事件数据失败: {e}", exc_info=True)
                    return False
            else:
                self.debug_logger.log_info(f"没有找到保存的状态文件: {state_file}")
                return False
        except (OSError, ValueError) as e:
            self.debug_logger.log_error(f"加载保存的状态失败: {e}", exc_info=True)
            return False

    def save_saved_state(self):
        """保存当前状态到文件

        将当前表格中的所有事件数据和设置信息保存到用户数据目录的日志文件夹中。

        Returns:
            bool: 保存成功返回True，失败返回False
        """
        try:
            # 使用用户数据目录作为日志目录
            logs_dir = os.path.join(get_user_data_dir(), "logs")

            # 确保logs目录存在
            if not os.path.exists(logs_dir):
                os.makedirs(logs_dir, exist_ok=True)

            # 设置文件路径
            state_file = os.path.join(logs_dir, "BetterGI_StellTrack_state.json")
            self.debug_logger.log_info(f"尝试将状态保存到 {state_file}")

            # 构建状态数据
            time_unit = self.parent_window.settings_panel.time_unit_combo.currentText()
            if time_unit == "ms":
                interval = self.parent_window.settings_panel.interval_input_int.value()
            else:
                interval = self.parent_window.settings_panel.interval_input_double.value()
            
            state = {
                'events': self._collect_all_events_data(),
                'settings': {
                    'loop_count': self.parent_window.settings_panel.loop_count_input.value(),
                    'interval': interval,
                    'time_unit': time_unit,
                    'width': self.parent_window.settings_panel.width_input.text(),
                    'height': self.parent_window.settings_panel.height_input.text(),
                    'scale': self.parent_window.settings_panel.scale_combo.currentText()
                }
            }

            # 验证收集的数据
            table_row_count = self.parent_window.event_manager.events_table.rowCount()
            collected_event_count = len(state['events'])
            if collected_event_count != table_row_count:
                self.debug_logger.log_error(f"收集事件数据时出现不一致: 表格中有 {table_row_count} 行，但只收集到 {collected_event_count} 个事件")
                return False

            # 确保目录存在
            state_dir = os.path.dirname(state_file)
            if not os.path.exists(state_dir):
                os.makedirs(state_dir)
                self.debug_logger.log_info(f"已创建状态文件目录: {state_dir}")

            # 保存到文件
            try:
                with open(state_file, 'w', encoding='utf-8') as f:
                    json.dump(state, f, ensure_ascii=False, indent=2)

                self.debug_logger.log_info(f"状态已成功保存到文件: {state_file}，包含 {collected_event_count} 个事件")
                return True
            except IOError as e:
                self.debug_logger.log_error(f"写入状态文件失败: {e}")
                return False
            except json.JSONDecodeError as e:
                self.debug_logger.log_error(f"序列化状态数据失败: {e}")
                return False
        except (OSError, ValueError) as e:
            self.debug_logger.log_error(f"保存状态到文件失败: {e}", exc_info=True)
            return False