/**
 * 列映射确认对话框组件
 * 允许用户预览和确认列映射关系
 */

// 列映射确认对话框类
class MappingConfirmationDialog {
    constructor() {
        this.modalId = 'mapping-confirmation-modal';
        this.initialized = false;
        this.fileId = null;
        this.originalFilename = null;
        this.mappingResult = null;
        this.columnMappings = null;
        this.customMapping = {};
        this.previewData = [];
    }

    // 初始化组件
    initialize() {
        if (this.initialized) return;

        // 创建模态框
        this.createModal();
        
        // 添加事件监听器
        this.addEventListeners();
        
        this.initialized = true;
    }

    // 创建模态框
    createModal() {
        // 检查模态框是否已存在
        if (document.getElementById(this.modalId)) return;
        
        // 创建模态框元素
        const modal = document.createElement('div');
        modal.id = this.modalId;
        modal.className = 'modal';
        
        // 设置模态框内容
        modal.innerHTML = `
            <div class="modal-content mapping-modal">
                <div class="modal-header">
                    <h3><i class="fas fa-columns"></i> 列映射确认</h3>
                    <span class="close">&times;</span>
                </div>
                <div class="modal-body">
                    <div class="mapping-status" id="mapping-status">
                        <!-- 映射状态将通过JavaScript动态加载 -->
                    </div>
                    
                    <div class="mapping-tabs">
                        <button class="tab-button active" data-tab="auto">自动映射</button>
                        <button class="tab-button" data-tab="custom">自定义映射</button>
                    </div>
                    
                    <div class="mapping-content">
                        <!-- 自动映射标签页 -->
                        <div id="auto-tab" class="mapping-tab active">
                            <div class="auto-mapping-result" id="auto-mapping-result">
                                <!-- 自动映射结果将通过JavaScript动态加载 -->
                            </div>
                        </div>
                        
                        <!-- 自定义映射标签页 -->
                        <div id="custom-tab" class="mapping-tab">
                            <div class="custom-mapping-form" id="custom-mapping-form">
                                <!-- 自定义映射表单将通过JavaScript动态加载 -->
                            </div>
                        </div>
                    </div>
                    
                    <div class="preview-section">
                        <h4>数据预览</h4>
                        <div class="preview-container" id="mapping-preview-container">
                            <!-- 预览数据将通过JavaScript动态加载 -->
                        </div>
                    </div>
                    
                    <div class="mapping-actions">
                        <button class="btn btn-secondary" id="cancel-mapping-btn">
                            <i class="fas fa-times"></i> 取消
                        </button>
                        <button class="btn btn-primary" id="confirm-mapping-btn">
                            <i class="fas fa-check"></i> 确认并上传
                        </button>
                    </div>
                </div>
            </div>
        `;
        
        // 添加到文档中
        document.body.appendChild(modal);
    }

    // 添加事件监听器
    addEventListeners() {
        // 关闭按钮
        const closeBtn = document.querySelector(`#${this.modalId} .close`);
        if (closeBtn) {
            closeBtn.addEventListener('click', () => this.hideModal());
        }
        
        // 点击模态框外部关闭
        const modal = document.getElementById(this.modalId);
        if (modal) {
            modal.addEventListener('click', (event) => {
                if (event.target === modal) {
                    this.hideModal();
                }
            });
        }
        
        // 标签页切换
        const tabButtons = document.querySelectorAll(`#${this.modalId} .tab-button`);
        tabButtons.forEach(button => {
            button.addEventListener('click', () => {
                const tabName = button.getAttribute('data-tab');
                this.switchTab(tabName);
            });
        });
        
        // 取消按钮
        const cancelBtn = document.getElementById('cancel-mapping-btn');
        if (cancelBtn) {
            cancelBtn.addEventListener('click', () => this.hideModal());
        }
        
        // 确认按钮
        const confirmBtn = document.getElementById('confirm-mapping-btn');
        if (confirmBtn) {
            confirmBtn.addEventListener('click', () => this.confirmMapping());
        }
    }

    // 切换标签页
    switchTab(tabName) {
        // 更新标签按钮状态
        const tabButtons = document.querySelectorAll(`#${this.modalId} .tab-button`);
        tabButtons.forEach(button => {
            button.classList.toggle('active', button.getAttribute('data-tab') === tabName);
        });
        
        // 更新标签内容状态
        const tabContents = document.querySelectorAll(`#${this.modalId} .mapping-tab`);
        tabContents.forEach(content => {
            content.classList.toggle('active', content.id === `${tabName}-tab`);
        });
        
        // 更新预览数据
        if (tabName === 'auto') {
            this.updatePreview('auto');
        } else if (tabName === 'custom') {
            this.updatePreview('custom');
        }
    }

    // 显示模态框
    async showModal(fileId, originalFilename) {
        this.initialize();
        
        this.fileId = fileId;
        this.originalFilename = originalFilename;
        
        // 显示模态框
        const modal = document.getElementById(this.modalId);
        if (modal) {
            modal.style.display = 'block';
        }
        
        // 显示加载状态
        this.showLoadingState();
        
        // 加载列映射配置
        await this.loadColumnMappings();
        
        // 加载映射预览
        await this.loadMappingPreview();
    }

    // 隐藏模态框
    hideModal() {
        const modal = document.getElementById(this.modalId);
        if (modal) {
            modal.style.display = 'none';
        }
        
        // 重置状态
        this.fileId = null;
        this.originalFilename = null;
        this.mappingResult = null;
        this.customMapping = {};
        this.previewData = [];
    }

    // 显示加载状态
    showLoadingState() {
        const statusElement = document.getElementById('mapping-status');
        if (statusElement) {
            statusElement.innerHTML = `
                <div class="loading-indicator">
                    <div class="spinner"></div>
                    <p>正在分析文件并生成列映射...</p>
                </div>
            `;
        }
        
        const autoMappingResult = document.getElementById('auto-mapping-result');
        if (autoMappingResult) {
            autoMappingResult.innerHTML = '';
        }
        
        const customMappingForm = document.getElementById('custom-mapping-form');
        if (customMappingForm) {
            customMappingForm.innerHTML = '';
        }
        
        const previewContainer = document.getElementById('mapping-preview-container');
        if (previewContainer) {
            previewContainer.innerHTML = '';
        }
    }

    // 加载列映射配置
    async loadColumnMappings() {
        try {
            const response = await fetch('/api/config/column_mappings');
            const result = await response.json();
            
            if (response.ok && result.success) {
                this.columnMappings = result.config;
                return true;
            } else {
                console.error('加载列名映射配置失败:', result.error || '未知错误');
                return false;
            }
        } catch (error) {
            console.error('加载列名映射配置失败:', error);
            return false;
        }
    }

    // 加载映射预览
    async loadMappingPreview() {
        if (!this.fileId) return;
        
        try {
            const response = await fetch('/api/preview_mapping', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    file_id: this.fileId
                })
            });
            
            const result = await response.json();
            
            if (response.ok) {
                this.mappingResult = result;
                this.previewData = result.preview_data;
                
                // 初始化自定义映射
                if (result.mapped_columns) {
                    this.customMapping = { ...result.mapped_columns };
                }
                
                // 更新UI
                this.updateMappingStatus();
                this.updateAutoMappingResult();
                this.updateCustomMappingForm();
                this.updatePreview('auto');
                
                return true;
            } else {
                this.showMappingError(result.error || '预览映射失败');
                return false;
            }
        } catch (error) {
            this.showMappingError(error.message || '预览映射失败');
            return false;
        }
    }

    // 更新映射状态
    updateMappingStatus() {
        const statusElement = document.getElementById('mapping-status');
        if (!statusElement || !this.mappingResult) return;
        
        const mappingSuccess = this.mappingResult.mapping_success;
        const missingRequired = this.mappingResult.missing_required || [];
        const unmappedColumns = this.mappingResult.unmapped_columns || [];
        
        let statusHtml = '';
        
        if (mappingSuccess) {
            statusHtml = `
                <div class="status-success">
                    <i class="fas fa-check-circle"></i>
                    <div class="status-message">
                        <h4>自动映射成功</h4>
                        <p>系统已成功识别所有必需的列。您可以直接确认或自定义映射关系。</p>
                    </div>
                </div>
            `;
        } else {
            statusHtml = `
                <div class="status-warning">
                    <i class="fas fa-exclamation-triangle"></i>
                    <div class="status-message">
                        <h4>自动映射不完整</h4>
                        <p>系统无法识别所有必需的列。请使用自定义映射功能手动指定列映射关系。</p>
                        ${missingRequired.length > 0 ? `<p><strong>缺少必需列:</strong> ${missingRequired.join(', ')}</p>` : ''}
                    </div>
                </div>
            `;
        }
        
        statusElement.innerHTML = statusHtml;
    }

    // 更新自动映射结果
    updateAutoMappingResult() {
        const resultElement = document.getElementById('auto-mapping-result');
        if (!resultElement || !this.mappingResult) return;
        
        const mappedColumns = this.mappingResult.mapped_columns || {};
        const unmappedColumns = this.mappingResult.unmapped_columns || [];
        const suggestions = this.mappingResult.suggestions || {};
        
        let resultHtml = '';
        
        // 已映射的列
        if (Object.keys(mappedColumns).length > 0) {
            resultHtml += `
                <div class="mapping-section">
                    <h4>已识别的列映射</h4>
                    <div class="mapping-list">
            `;
            
            for (const [originalCol, standardCol] of Object.entries(mappedColumns)) {
                const isRequired = this.columnMappings && this.columnMappings.required_columns.includes(standardCol);
                
                resultHtml += `
                    <div class="mapping-item">
                        <div class="mapping-from">${originalCol}</div>
                        <div class="mapping-arrow"><i class="fas fa-arrow-right"></i></div>
                        <div class="mapping-to ${isRequired ? 'required' : 'optional'}">
                            ${standardCol}
                            ${isRequired ? '<span class="required-badge-inline">必需</span>' : '<span class="optional-badge-inline">可选</span>'}
                        </div>
                    </div>
                `;
            }
            
            resultHtml += `
                    </div>
                </div>
            `;
        }
        
        // 未映射的列
        if (unmappedColumns.length > 0) {
            resultHtml += `
                <div class="mapping-section">
                    <h4>未识别的列</h4>
                    <div class="mapping-list">
            `;
            
            for (const col of unmappedColumns) {
                let suggestionHtml = '';
                
                if (suggestions[col]) {
                    const colSuggestions = suggestions[col].suggestions || [];
                    if (colSuggestions.length > 0) {
                        suggestionHtml = `
                            <div class="mapping-suggestion">
                                <span>建议映射为: </span>
                                ${colSuggestions.map(s => `<span class="suggestion-tag">${s}</span>`).join(' ')}
                            </div>
                        `;
                    }
                }
                
                resultHtml += `
                    <div class="mapping-item unmapped">
                        <div class="mapping-from">${col}</div>
                        <div class="mapping-arrow"><i class="fas fa-times"></i></div>
                        <div class="mapping-to">未映射</div>
                        ${suggestionHtml}
                    </div>
                `;
            }
            
            resultHtml += `
                    </div>
                </div>
            `;
        }
        
        // 缺少的必需列
        const missingRequired = this.mappingResult.missing_required || [];
        if (missingRequired.length > 0) {
            resultHtml += `
                <div class="mapping-section">
                    <h4>缺少的必需列</h4>
                    <div class="mapping-list">
            `;
            
            for (const col of missingRequired) {
                resultHtml += `
                    <div class="mapping-item missing">
                        <div class="mapping-from"><i class="fas fa-exclamation-circle"></i></div>
                        <div class="mapping-arrow"><i class="fas fa-times"></i></div>
                        <div class="mapping-to required">
                            ${col}
                            <span class="required-badge-inline">必需</span>
                        </div>
                    </div>
                `;
            }
            
            resultHtml += `
                    </div>
                </div>
            `;
        }
        
        resultElement.innerHTML = resultHtml;
    }

    // 更新自定义映射表单
    updateCustomMappingForm() {
        const formElement = document.getElementById('custom-mapping-form');
        if (!formElement || !this.mappingResult || !this.columnMappings) return;
        
        const originalColumns = this.mappingResult.original_columns || [];
        const requiredColumns = this.columnMappings.required_columns || [];
        const optionalColumns = this.columnMappings.optional_columns || [];
        
        let formHtml = `
            <p>请为每个标准列选择对应的原始列：</p>
            <div class="custom-mapping-list">
        `;
        
        // 必需列
        for (const standardCol of requiredColumns) {
            const currentMapping = this.customMapping[standardCol] || '';
            
            formHtml += `
                <div class="custom-mapping-item">
                    <div class="mapping-label required">
                        ${standardCol}
                        <span class="required-badge-inline">必需</span>
                    </div>
                    <div class="mapping-select">
                        <select class="column-select" data-standard="${standardCol}">
                            <option value="">-- 请选择 --</option>
                            ${originalColumns.map(col => `
                                <option value="${col}" ${currentMapping === col ? 'selected' : ''}>${col}</option>
                            `).join('')}
                        </select>
                    </div>
                </div>
            `;
        }
        
        // 可选列
        for (const standardCol of optionalColumns) {
            const currentMapping = this.customMapping[standardCol] || '';
            
            formHtml += `
                <div class="custom-mapping-item">
                    <div class="mapping-label optional">
                        ${standardCol}
                        <span class="optional-badge-inline">可选</span>
                    </div>
                    <div class="mapping-select">
                        <select class="column-select" data-standard="${standardCol}">
                            <option value="">-- 不映射 --</option>
                            ${originalColumns.map(col => `
                                <option value="${col}" ${currentMapping === col ? 'selected' : ''}>${col}</option>
                            `).join('')}
                        </select>
                    </div>
                </div>
            `;
        }
        
        formHtml += `
            </div>
        `;
        
        formElement.innerHTML = formHtml;
        
        // 添加选择框事件监听器
        const selects = formElement.querySelectorAll('.column-select');
        selects.forEach(select => {
            select.addEventListener('change', () => {
                const standardCol = select.getAttribute('data-standard');
                const originalCol = select.value;
                
                if (originalCol) {
                    this.customMapping[standardCol] = originalCol;
                } else {
                    delete this.customMapping[standardCol];
                }
                
                // 更新预览
                this.updatePreview('custom');
            });
        });
    }

    // 更新预览
    updatePreview(mappingType) {
        const previewContainer = document.getElementById('mapping-preview-container');
        if (!previewContainer || !this.previewData || this.previewData.length === 0) return;
        
        let previewHtml = `
            <div class="preview-table-container">
                <table class="data-table">
                    <thead>
                        <tr>
                            <th>行号</th>
                            <th colspan="999">原始数据</th>
                        </tr>
                        <tr>
                            <th></th>
                            ${this.mappingResult.original_columns.map(col => `<th>${col}</th>`).join('')}
                        </tr>
                    </thead>
                    <tbody>
        `;
        
        // 添加原始数据行
        for (const row of this.previewData) {
            previewHtml += `
                <tr>
                    <td>${row.row_index}</td>
                    ${this.mappingResult.original_columns.map(col => `<td>${row.original[col] !== undefined ? row.original[col] : ''}</td>`).join('')}
                </tr>
            `;
        }
        
        previewHtml += `
                    </tbody>
                </table>
            </div>
            
            <div class="preview-table-container">
                <table class="data-table">
                    <thead>
                        <tr>
                            <th>行号</th>
                            <th colspan="999">映射后数据</th>
                        </tr>
                        <tr>
                            <th></th>
        `;
        
        // 获取映射后的列
        let mappedColumns = [];
        if (mappingType === 'auto') {
            // 使用自动映射
            const standardColumns = [
                ...this.columnMappings.required_columns,
                ...this.columnMappings.optional_columns
            ];
            
            // 过滤出已映射的列
            mappedColumns = standardColumns.filter(col => {
                // 检查是否有映射
                for (const [origCol, stdCol] of Object.entries(this.mappingResult.mapped_columns || {})) {
                    if (stdCol === col) return true;
                }
                return false;
            });
        } else {
            // 使用自定义映射
            mappedColumns = Object.keys(this.customMapping);
        }
        
        // 添加映射后的列标题
        for (const col of mappedColumns) {
            const isRequired = this.columnMappings.required_columns.includes(col);
            previewHtml += `
                <th class="${isRequired ? 'required-column' : ''}">
                    ${col}
                    ${isRequired ? '<span class="required-badge-inline">必需</span>' : ''}
                </th>
            `;
        }
        
        previewHtml += `
                        </tr>
                    </thead>
                    <tbody>
        `;
        
        // 添加映射后的数据行
        for (const row of this.previewData) {
            previewHtml += `<tr><td>${row.row_index}</td>`;
            
            for (const col of mappedColumns) {
                let value = '';
                
                if (mappingType === 'auto') {
                    // 使用自动映射
                    for (const [origCol, stdCol] of Object.entries(this.mappingResult.mapped_columns || {})) {
                        if (stdCol === col && row.original[origCol] !== undefined) {
                            value = row.original[origCol];
                            break;
                        }
                    }
                } else {
                    // 使用自定义映射
                    const origCol = this.customMapping[col];
                    if (origCol && row.original[origCol] !== undefined) {
                        value = row.original[origCol];
                    }
                }
                
                previewHtml += `<td>${value}</td>`;
            }
            
            previewHtml += `</tr>`;
        }
        
        previewHtml += `
                    </tbody>
                </table>
            </div>
        `;
        
        previewContainer.innerHTML = previewHtml;
    }

    // 显示映射错误
    showMappingError(errorMessage) {
        const statusElement = document.getElementById('mapping-status');
        if (statusElement) {
            statusElement.innerHTML = `
                <div class="status-error">
                    <i class="fas fa-times-circle"></i>
                    <div class="status-message">
                        <h4>映射失败</h4>
                        <p>${errorMessage}</p>
                    </div>
                </div>
            `;
        }
    }

    // 确认映射
    async confirmMapping() {
        if (!this.fileId) return;
        
        // 获取当前活动的标签页
        const activeTab = document.querySelector(`#${this.modalId} .tab-button.active`);
        if (!activeTab) return;
        
        const mappingType = activeTab.getAttribute('data-tab');
        
        // 验证映射
        if (mappingType === 'custom') {
            // 检查必需列是否都已映射
            const missingRequired = this.columnMappings.required_columns.filter(col => !this.customMapping[col]);
            
            if (missingRequired.length > 0) {
                alert(`请为以下必需列选择映射: ${missingRequired.join(', ')}`);
                return;
            }
        } else if (mappingType === 'auto' && !this.mappingResult.mapping_success) {
            // 自动映射不成功，提示用户使用自定义映射
            alert('自动映射不完整，请使用自定义映射功能手动指定列映射关系。');
            this.switchTab('custom');
            return;
        }
        
        try {
            // 显示加载状态
            showLoading();
            
            // 构建请求数据
            const requestData = {
                file_id: this.fileId,
                mapping_type: mappingType,
                original_filename: this.originalFilename
            };
            
            // 如果是自定义映射，添加映射数据
            if (mappingType === 'custom') {
                requestData.column_mapping = this.customMapping;
            }
            
            // 发送确认请求
            const response = await fetch('/api/confirm_mapping', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(requestData)
            });
            
            const result = await response.json();
            
            // 隐藏加载状态
            hideLoading();
            
            if (response.ok && result.success) {
                // 显示成功消息
                showSuccessMessage('规格表上传成功！');
                
                // 隐藏模态框
                this.hideModal();
                
                // 刷新规格表列表
                if (typeof loadSpecList === 'function') {
                    loadSpecList();
                }
                
                // 刷新订单核对页面的规格表列表
                if (typeof loadSpecFiles === 'function') {
                    loadSpecFiles();
                }
                
                // 重置规格表上传区域
                if (typeof resetSpecUpload === 'function') {
                    resetSpecUpload();
                }
                
                return true;
            } else {
                // 显示错误消息
                showErrorMessage(result.message || result.error || '确认映射失败');
                return false;
            }
        } catch (error) {
            // 隐藏加载状态
            hideLoading();
            
            // 显示错误消息
            showErrorMessage(error.message || '确认映射失败');
            return false;
        }
    }
}

// 创建映射确认对话框实例
const mappingDialog = new MappingConfirmationDialog();

// 导出组件
window.mappingDialog = mappingDialog;