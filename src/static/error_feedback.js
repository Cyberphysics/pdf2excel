/**
 * 增强型错误反馈组件
 * 提供详细的错误信息和修改建议
 */

// 错误反馈组件类
class ErrorFeedbackComponent {
    constructor() {
        this.modalId = 'error-feedback-modal';
        this.initialized = false;
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
            <div class="modal-content error-modal">
                <div class="modal-header">
                    <h3><i class="fas fa-exclamation-triangle"></i> <span id="error-modal-title">验证错误</span></h3>
                    <span class="close">&times;</span>
                </div>
                <div class="modal-body">
                    <div class="error-summary" id="error-summary">
                        <!-- 错误摘要将通过JavaScript动态加载 -->
                    </div>
                    
                    <div class="error-tabs">
                        <button class="tab-button active" data-tab="details">详细错误</button>
                        <button class="tab-button" data-tab="suggestions">修改建议</button>
                        <button class="tab-button" data-tab="format">格式要求</button>
                    </div>
                    
                    <div class="error-content">
                        <!-- 详细错误标签页 -->
                        <div id="details-tab" class="error-tab active">
                            <div class="error-details" id="error-details">
                                <!-- 详细错误信息将通过JavaScript动态加载 -->
                            </div>
                        </div>
                        
                        <!-- 修改建议标签页 -->
                        <div id="suggestions-tab" class="error-tab">
                            <div class="error-suggestions" id="error-suggestions">
                                <!-- 修改建议将通过JavaScript动态加载 -->
                            </div>
                        </div>
                        
                        <!-- 格式要求标签页 -->
                        <div id="format-tab" class="error-tab">
                            <div class="error-format" id="error-format">
                                <!-- 格式要求将通过JavaScript动态加载 -->
                            </div>
                        </div>
                    </div>
                    
                    <div class="error-actions">
                        <button class="btn btn-secondary" id="close-error-btn">
                            <i class="fas fa-times"></i> 关闭
                        </button>
                        <button class="btn btn-primary" id="show-format-guide-btn-modal">
                            <i class="fas fa-book"></i> 查看详细格式指南
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
        
        // 关闭按钮
        const closeErrorBtn = document.getElementById('close-error-btn');
        if (closeErrorBtn) {
            closeErrorBtn.addEventListener('click', () => this.hideModal());
        }
        
        // 格式指南按钮
        const formatGuideBtn = document.getElementById('show-format-guide-btn-modal');
        if (formatGuideBtn) {
            formatGuideBtn.addEventListener('click', () => {
                this.hideModal();
                if (window.formatGuide) {
                    window.formatGuide.initialize().then(() => {
                        window.formatGuide.showModal();
                    });
                }
            });
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
        const tabContents = document.querySelectorAll(`#${this.modalId} .error-tab`);
        tabContents.forEach(content => {
            content.classList.toggle('active', content.id === `${tabName}-tab`);
        });
    }

    // 显示模态框
    showModal(errorData, title = '验证错误') {
        this.initialize();
        
        // 设置标题
        const titleElement = document.getElementById('error-modal-title');
        if (titleElement) {
            titleElement.textContent = title;
        }
        
        // 更新错误信息
        this.updateErrorContent(errorData);
        
        // 显示模态框
        const modal = document.getElementById(this.modalId);
        if (modal) {
            modal.style.display = 'block';
        }
    }

    // 隐藏模态框
    hideModal() {
        const modal = document.getElementById(this.modalId);
        if (modal) {
            modal.style.display = 'none';
        }
    }

    // 更新错误内容
    updateErrorContent(errorData) {
        if (!errorData) return;
        
        // 更新错误摘要
        this.updateErrorSummary(errorData);
        
        // 更新详细错误信息
        this.updateErrorDetails(errorData);
        
        // 更新修改建议
        this.updateErrorSuggestions(errorData);
        
        // 更新格式要求
        this.updateFormatRequirements(errorData);
    }

    // 更新错误摘要
    updateErrorSummary(errorData) {
        const summaryElement = document.getElementById('error-summary');
        if (!summaryElement) return;
        
        const errorMessage = errorData.error || errorData.message || '验证失败';
        const errorCode = errorData.error_code || '';
        
        let summaryHtml = `
            <div class="summary-icon">
                <i class="fas fa-exclamation-circle"></i>
            </div>
            <div class="summary-content">
                <h4>${errorMessage}</h4>
        `;
        
        if (errorCode) {
            summaryHtml += `<p class="error-code">错误代码: ${errorCode}</p>`;
        }
        
        if (errorData.message && errorData.message !== errorMessage) {
            summaryHtml += `<p>${errorData.message}</p>`;
        }
        
        summaryHtml += `</div>`;
        
        summaryElement.innerHTML = summaryHtml;
    }

    // 更新详细错误信息
    updateErrorDetails(errorData) {
        const detailsElement = document.getElementById('error-details');
        if (!detailsElement) return;
        
        let detailsHtml = '';
        
        // 处理警告信息
        if (errorData.warnings && errorData.warnings.length > 0) {
            detailsHtml += `
                <div class="error-section">
                    <h4><i class="fas fa-exclamation-triangle"></i> 警告</h4>
                    <ul class="error-list warning-list">
            `;
            
            errorData.warnings.forEach(warning => {
                detailsHtml += `<li>${warning}</li>`;
            });
            
            detailsHtml += `
                    </ul>
                </div>
            `;
        }
        
        // 处理数据错误
        if (errorData.data_errors && Object.keys(errorData.data_errors).length > 0) {
            detailsHtml += `
                <div class="error-section">
                    <h4><i class="fas fa-times-circle"></i> 数据错误</h4>
                    <div class="data-errors">
            `;
            
            for (const [column, error] of Object.entries(errorData.data_errors)) {
                detailsHtml += `
                    <div class="data-error-item">
                        <div class="error-column">${column}</div>
                        <div class="error-info">
                            <div class="error-type">${this.getErrorTypeName(error.type)}</div>
                            <div class="error-message">${error.message}</div>
                            ${error.rows ? `<div class="error-rows">问题行: ${error.rows.join(', ')}</div>` : ''}
                            ${error.values ? `<div class="error-values">问题值: ${error.values.join(', ')}</div>` : ''}
                        </div>
                    </div>
                `;
            }
            
            detailsHtml += `
                    </div>
                </div>
            `;
        }
        
        // 处理映射结果
        if (errorData.mapping_result) {
            const mappingResult = errorData.mapping_result;
            
            detailsHtml += `
                <div class="error-section">
                    <h4><i class="fas fa-columns"></i> 列映射结果</h4>
            `;
            
            if (mappingResult.missing_required && mappingResult.missing_required.length > 0) {
                detailsHtml += `
                    <div class="mapping-error">
                        <h5>缺少必需列</h5>
                        <ul class="error-list">
                            ${mappingResult.missing_required.map(col => `<li>${col}</li>`).join('')}
                        </ul>
                    </div>
                `;
            }
            
            if (mappingResult.unmapped_columns && mappingResult.unmapped_columns.length > 0) {
                detailsHtml += `
                    <div class="mapping-error">
                        <h5>未映射的列</h5>
                        <ul class="error-list">
                            ${mappingResult.unmapped_columns.map(col => `<li>${col}</li>`).join('')}
                        </ul>
                    </div>
                `;
            }
            
            detailsHtml += `</div>`;
        }
        
        // 如果没有详细错误信息，显示一般错误消息
        if (!detailsHtml) {
            detailsHtml = `
                <div class="error-section">
                    <p>没有可用的详细错误信息。</p>
                </div>
            `;
        }
        
        detailsElement.innerHTML = detailsHtml;
    }

    // 更新修改建议
    updateErrorSuggestions(errorData) {
        const suggestionsElement = document.getElementById('error-suggestions');
        if (!suggestionsElement) return;
        
        let suggestionsHtml = '';
        
        // 处理建议信息
        if (errorData.suggestions && Object.keys(errorData.suggestions).length > 0) {
            suggestionsHtml += `
                <div class="suggestions-intro">
                    <p>根据检测到的问题，我们提供以下修改建议：</p>
                </div>
            `;
            
            for (const [key, suggestion] of Object.entries(errorData.suggestions)) {
                suggestionsHtml += `
                    <div class="suggestion-item">
                        <h5>${suggestion.message || '修改建议'}</h5>
                `;
                
                if (key === 'column_mapping' && suggestion.suggestions) {
                    suggestionsHtml += `
                        <div class="suggestion-content">
                            <p>建议修改以下列名：</p>
                            <ul class="suggestion-list">
                                ${suggestion.suggestions.map(s => `<li>${s}</li>`).join('')}
                            </ul>
                        </div>
                    `;
                } else if (key === 'missing_columns' && suggestion.columns) {
                    suggestionsHtml += `
                        <div class="suggestion-content">
                            <p>请添加以下必需列：</p>
                            <ul class="suggestion-list">
                                ${suggestion.columns.map(col => `<li>${col}</li>`).join('')}
                            </ul>
                        </div>
                    `;
                } else if (key.endsWith('_null') && suggestion.rows) {
                    suggestionsHtml += `
                        <div class="suggestion-content">
                            <p>${suggestion.suggestion || '请填写空值'}</p>
                            <div class="suggestion-rows">问题行: ${suggestion.rows.join(', ')}</div>
                            ${suggestion.suggested_values ? `
                                <div class="suggested-values">
                                    <p>建议值:</p>
                                    <ul class="suggestion-list">
                                        ${suggestion.suggested_values.map((val, i) => `<li>行 ${suggestion.rows[i]}: ${val}</li>`).join('')}
                                    </ul>
                                </div>
                            ` : ''}
                        </div>
                    `;
                } else if (key.endsWith('_duplicate') && suggestion.rows) {
                    suggestionsHtml += `
                        <div class="suggestion-content">
                            <p>${suggestion.suggestion || '请修复重复值'}</p>
                            <div class="suggestion-rows">问题行: ${suggestion.rows.join(', ')}</div>
                            ${suggestion.values ? `<div class="suggestion-values">重复值: ${suggestion.values.join(', ')}</div>` : ''}
                            ${suggestion.suggested_values ? `
                                <div class="suggested-values">
                                    <p>建议值:</p>
                                    <ul class="suggestion-list">
                                        ${suggestion.suggested_values.map((val, i) => `<li>行 ${suggestion.rows[i]}: ${val}</li>`).join('')}
                                    </ul>
                                </div>
                            ` : ''}
                        </div>
                    `;
                } else {
                    // 通用建议处理
                    suggestionsHtml += `
                        <div class="suggestion-content">
                            <p>${suggestion.suggestion || suggestion.message || '请修复问题'}</p>
                            ${suggestion.rows ? `<div class="suggestion-rows">问题行: ${suggestion.rows.join(', ')}</div>` : ''}
                            ${suggestion.values ? `<div class="suggestion-values">问题值: ${suggestion.values.join(', ')}</div>` : ''}
                        </div>
                    `;
                }
                
                suggestionsHtml += `</div>`;
            }
        } else if (errorData.structured_suggestions) {
            // 处理结构化建议
            suggestionsHtml += `
                <div class="suggestions-intro">
                    <p>根据检测到的问题，我们提供以下修改建议：</p>
                </div>
                <div class="suggestion-item">
                    <h5>列映射建议</h5>
                    <div class="suggestion-content">
            `;
            
            for (const [col, suggestion] of Object.entries(errorData.structured_suggestions)) {
                if (suggestion.possible_mappings && suggestion.possible_mappings.length > 0) {
                    suggestionsHtml += `
                        <div class="column-suggestion">
                            <p>列 "${col}" 可能映射为: ${suggestion.possible_mappings.map(m => `<span class="suggestion-tag">${m}</span>`).join(' ')}</p>
                        </div>
                    `;
                }
            }
            
            suggestionsHtml += `
                    </div>
                </div>
            `;
        } else {
            // 如果没有建议信息，显示一般建议
            suggestionsHtml = `
                <div class="suggestions-intro">
                    <p>请检查以下常见问题：</p>
                    <ul class="general-suggestions">
                        <li>确保Excel文件包含所有必需的列</li>
                        <li>检查列名是否符合要求或可以被系统识别</li>
                        <li>确保必需列中没有空值</li>
                        <li>检查数值列是否包含非数字值</li>
                        <li>考虑使用自定义映射功能手动指定列映射关系</li>
                    </ul>
                </div>
            `;
        }
        
        suggestionsElement.innerHTML = suggestionsHtml;
    }

    // 更新格式要求
    updateFormatRequirements(errorData) {
        const formatElement = document.getElementById('error-format');
        if (!formatElement) return;
        
        // 获取列映射配置信息
        let columnMappingInfo = null;
        if (errorData.column_mapping_info) {
            columnMappingInfo = errorData.column_mapping_info;
        }
        
        let formatHtml = `
            <div class="format-section">
                <h4>规格表格式要求</h4>
                <p>规格表必须符合以下格式要求：</p>
                
                <div class="format-requirements">
                    <div class="format-item">
                        <h5><i class="fas fa-table"></i> 文件格式</h5>
                        <ul>
                            <li>Excel文件格式（.xlsx或.xls）</li>
                            <li>第一行必须是列标题行</li>
                            <li>数据从第二行开始</li>
                        </ul>
                    </div>
        `;
        
        // 必需列
        formatHtml += `
            <div class="format-item">
                <h5><i class="fas fa-exclamation-circle"></i> 必需列</h5>
        `;
        
        if (columnMappingInfo && columnMappingInfo.required_columns) {
            formatHtml += `
                <div class="required-columns">
                    ${columnMappingInfo.required_columns.map(col => `<span class="column-tag">${col}</span>`).join('')}
                </div>
            `;
            
            if (columnMappingInfo.required_columns_description) {
                formatHtml += `<ul>`;
                for (const [col, desc] of Object.entries(columnMappingInfo.required_columns_description)) {
                    formatHtml += `
                        <li>
                            <strong>${col}</strong>: ${desc.description}
                            ${desc.examples && desc.examples.length > 0 ? 
                                `<br><small>可接受的列名: ${desc.examples.map(e => `<span class="alias-tag">${e}</span>`).join(' ')}</small>` : 
                                ''}
                        </li>
                    `;
                }
                formatHtml += `</ul>`;
            }
        } else {
            formatHtml += `
                <div class="required-columns">
                    <span class="column-tag">item_id</span>
                    <span class="column-tag">product_name</span>
                </div>
                <ul>
                    <li><strong>item_id</strong>: 产品的唯一标识符，不能为空</li>
                    <li><strong>product_name</strong>: 产品的名称或描述</li>
                </ul>
            `;
        }
        
        formatHtml += `</div>`;
        
        // 可选列
        formatHtml += `
            <div class="format-item">
                <h5><i class="fas fa-check-circle"></i> 可选列</h5>
        `;
        
        if (columnMappingInfo && columnMappingInfo.optional_columns) {
            formatHtml += `
                <div class="optional-columns">
                    ${columnMappingInfo.optional_columns.map(col => `<span class="column-tag" style="background-color: #6c757d;">${col}</span>`).join('')}
                </div>
            `;
            
            if (columnMappingInfo.optional_columns_description) {
                formatHtml += `<ul>`;
                for (const [col, desc] of Object.entries(columnMappingInfo.optional_columns_description)) {
                    formatHtml += `
                        <li>
                            <strong>${col}</strong>: ${desc.description}
                            ${desc.examples && desc.examples.length > 0 ? 
                                `<br><small>可接受的列名: ${desc.examples.map(e => `<span class="alias-tag">${e}</span>`).join(' ')}</small>` : 
                                ''}
                        </li>
                    `;
                }
                formatHtml += `</ul>`;
            }
        } else {
            formatHtml += `
                <div class="optional-columns">
                    <span class="column-tag" style="background-color: #6c757d;">size</span>
                    <span class="column-tag" style="background-color: #6c757d;">color</span>
                    <span class="column-tag" style="background-color: #6c757d;">standard_unit_price</span>
                </div>
                <ul>
                    <li><strong>size</strong>: 产品的尺寸或规格</li>
                    <li><strong>color</strong>: 产品的颜色</li>
                    <li><strong>standard_unit_price</strong>: 产品的标准单价，必须是数字</li>
                </ul>
            `;
        }
        
        formatHtml += `
                </div>
            </div>
            
            <div class="format-actions">
                <button class="btn btn-info btn-small" id="download-template-btn-error">
                    <i class="fas fa-download"></i> 下载模板文件
                </button>
            </div>
        </div>
        `;
        
        formatElement.innerHTML = formatHtml;
        
        // 添加下载模板按钮事件
        const downloadTemplateBtn = document.getElementById('download-template-btn-error');
        if (downloadTemplateBtn) {
            downloadTemplateBtn.addEventListener('click', () => {
                window.open('/api/download_spec_template?rows=5', '_blank');
            });
        }
    }

    // 获取错误类型名称
    getErrorTypeName(type) {
        const errorTypes = {
            'null_values': '空值错误',
            'duplicate_values': '重复值错误',
            'invalid_type': '数据类型错误',
            'negative_values': '负值错误',
            'format_error': '格式错误',
            'range_error': '范围错误',
            'reference_error': '引用错误'
        };
        
        return errorTypes[type] || type;
    }
}

// 创建错误反馈组件实例
const errorFeedback = new ErrorFeedbackComponent();

// 导出组件
window.errorFeedback = errorFeedback;