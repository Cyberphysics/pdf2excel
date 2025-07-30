/**
 * 规格表格式指南组件
 * 提供详细的列名映射和格式要求信息
 */

// 格式指南组件类
class FormatGuideComponent {
    constructor() {
        this.modalId = 'format-guide-modal';
        this.initialized = false;
        this.columnMappings = null;
    }

    // 初始化组件
    async initialize() {
        if (this.initialized) return;

        // 创建模态框
        this.createModal();
        
        // 加载列名映射配置
        await this.loadColumnMappings();
        
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
            <div class="modal-content">
                <div class="modal-header">
                    <h3><i class="fas fa-info-circle"></i> 规格表格式指南</h3>
                    <span class="close">&times;</span>
                </div>
                <div class="modal-body">
                    <div class="format-guide-tabs">
                        <button class="tab-button active" data-tab="overview">概述</button>
                        <button class="tab-button" data-tab="columns">列名映射</button>
                        <button class="tab-button" data-tab="examples">示例</button>
                        <button class="tab-button" data-tab="tips">常见问题</button>
                    </div>
                    
                    <div class="format-guide-content">
                        <!-- 概述标签页 -->
                        <div id="overview-tab" class="format-guide-tab active">
                            <h4>规格表格式要求</h4>
                            <p>规格表是用于订单核对的基准数据，包含产品的标准信息。系统支持灵活的列名映射，可以自动识别常见的列名变体。</p>
                            
                            <div class="format-info">
                                <h5><i class="fas fa-exclamation-circle"></i> 必需列</h5>
                                <p>规格表必须包含以下必需列（系统支持多种列名格式）：</p>
                                <div class="required-columns" id="required-columns-list">
                                    <!-- 将通过JavaScript动态加载 -->
                                </div>
                            </div>
                            
                            <div class="format-info">
                                <h5><i class="fas fa-check-circle"></i> 可选列</h5>
                                <p>以下列是可选的，但建议包含以提高核对准确性：</p>
                                <div class="required-columns" id="optional-columns-list">
                                    <!-- 将通过JavaScript动态加载 -->
                                </div>
                            </div>
                            
                            <div class="format-info">
                                <h5><i class="fas fa-file-excel"></i> 文件格式</h5>
                                <p>规格表必须是Excel格式（.xlsx或.xls）。</p>
                                <p>第一行必须是列标题行，系统将根据列标题进行映射。</p>
                                <p>数据从第二行开始，每行代表一个产品。</p>
                            </div>
                        </div>
                        
                        <!-- 列名映射标签页 -->
                        <div id="columns-tab" class="format-guide-tab">
                            <h4>列名映射详情</h4>
                            <p>系统支持多种列名格式，以下是系统可以识别的列名映射关系：</p>
                            
                            <div class="mapping-container" id="mapping-container">
                                <!-- 将通过JavaScript动态加载 -->
                            </div>
                            
                            <div class="format-info">
                                <h5><i class="fas fa-lightbulb"></i> 提示</h5>
                                <p>如果您的Excel文件使用了不同的列名，系统会尝试自动映射。如果映射失败，您可以：</p>
                                <ul>
                                    <li>修改Excel文件的列名为系统支持的名称</li>
                                    <li>使用自定义映射功能手动指定列映射关系</li>
                                    <li>联系管理员添加新的列名映射规则</li>
                                </ul>
                            </div>
                        </div>
                        
                        <!-- 示例标签页 -->
                        <div id="examples-tab" class="format-guide-tab">
                            <h4>规格表示例</h4>
                            <p>以下是一个符合要求的规格表示例：</p>
                            
                            <div class="example-table-container" id="example-table-container">
                                <!-- 将通过JavaScript动态加载 -->
                            </div>
                            
                            <div class="example-notes">
                                <h5><i class="fas fa-sticky-note"></i> 说明</h5>
                                <ul>
                                    <li><strong>item_id</strong>：产品唯一标识符，不能为空</li>
                                    <li><strong>product_name</strong>：产品名称，建议不要为空</li>
                                    <li><strong>standard_unit_price</strong>：标准单价，必须是数字</li>
                                    <li><strong>size</strong>和<strong>color</strong>：可选，但建议提供以便更准确地核对</li>
                                </ul>
                                <p class="tip">提示：您可以下载此示例作为模板使用。</p>
                            </div>
                            
                            <div class="format-actions">
                                <button class="btn btn-info btn-small" id="download-template-btn-modal">
                                    <i class="fas fa-download"></i> 下载模板文件
                                </button>
                            </div>
                        </div>
                        
                        <!-- 常见问题标签页 -->
                        <div id="tips-tab" class="format-guide-tab">
                            <h4>常见问题与解决方法</h4>
                            
                            <div class="faq-item">
                                <h5><i class="fas fa-question-circle"></i> 我的Excel文件列名与系统不匹配怎么办？</h5>
                                <p>系统支持多种常见的列名变体，会尝试自动映射。如果自动映射失败，您可以：</p>
                                <ul>
                                    <li>修改Excel文件的列名</li>
                                    <li>使用自定义映射功能手动指定列映射关系</li>
                                    <li>联系管理员添加新的列名映射规则</li>
                                </ul>
                            </div>
                            
                            <div class="faq-item">
                                <h5><i class="fas fa-question-circle"></i> 为什么我的规格表上传失败？</h5>
                                <p>常见的上传失败原因包括：</p>
                                <ul>
                                    <li>缺少必需列（item_id、product_name）</li>
                                    <li>item_id列存在空值</li>
                                    <li>standard_unit_price列包含非数字值</li>
                                    <li>Excel文件格式不正确或损坏</li>
                                </ul>
                            </div>
                            
                            <div class="faq-item">
                                <h5><i class="fas fa-question-circle"></i> 如何处理警告信息？</h5>
                                <p>上传过程中可能出现警告，这些警告不会阻止上传，但可能影响后续的订单核对：</p>
                                <ul>
                                    <li>item_id重复：可能导致订单核对时匹配到错误的产品</li>
                                    <li>product_name为空：建议填写以便更好地识别产品</li>
                                    <li>standard_unit_price为负值：请确认价格是否正确</li>
                                </ul>
                            </div>
                            
                            <div class="faq-item">
                                <h5><i class="fas fa-question-circle"></i> 如何获取更多帮助？</h5>
                                <p>如果您遇到其他问题，请联系系统管理员或查阅详细的用户手册。</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        // 添加到文档中
        document.body.appendChild(modal);
    }

    // 加载列名映射配置
    async loadColumnMappings() {
        try {
            const response = await fetch('/api/config/column_mappings');
            const result = await response.json();
            
            if (response.ok && result.success) {
                this.columnMappings = result.config;
                this.updateColumnMappingsUI();
            } else {
                console.error('加载列名映射配置失败:', result.error || '未知错误');
            }
        } catch (error) {
            console.error('加载列名映射配置失败:', error);
        }
    }

    // 更新列名映射UI
    updateColumnMappingsUI() {
        if (!this.columnMappings) return;
        
        // 更新必需列列表
        const requiredColumnsList = document.getElementById('required-columns-list');
        if (requiredColumnsList) {
            requiredColumnsList.innerHTML = '';
            this.columnMappings.required_columns.forEach(column => {
                const tag = document.createElement('span');
                tag.className = 'column-tag';
                tag.textContent = column;
                requiredColumnsList.appendChild(tag);
            });
        }
        
        // 更新可选列列表
        const optionalColumnsList = document.getElementById('optional-columns-list');
        if (optionalColumnsList) {
            optionalColumnsList.innerHTML = '';
            this.columnMappings.optional_columns.forEach(column => {
                const tag = document.createElement('span');
                tag.className = 'column-tag';
                tag.style.backgroundColor = '#6c757d'; // 使用灰色区分可选列
                tag.textContent = column;
                optionalColumnsList.appendChild(tag);
            });
        }
        
        // 更新列名映射详情
        const mappingContainer = document.getElementById('mapping-container');
        if (mappingContainer) {
            mappingContainer.innerHTML = '';
            
            // 先处理必需列
            this.columnMappings.required_columns.forEach(column => {
                this.addMappingItem(mappingContainer, column, true);
            });
            
            // 再处理可选列
            this.columnMappings.optional_columns.forEach(column => {
                this.addMappingItem(mappingContainer, column, false);
            });
        }
        
        // 更新示例表格
        this.updateExampleTable();
    }

    // 添加映射项
    addMappingItem(container, column, isRequired) {
        const aliases = this.columnMappings.column_mappings[column] || [];
        
        const item = document.createElement('div');
        item.className = 'mapping-item';
        
        const standardColumn = document.createElement('div');
        standardColumn.className = `standard-column ${isRequired ? 'required' : 'optional'}`;
        standardColumn.innerHTML = `
            ${column}
            <span class="${isRequired ? 'required-badge' : 'optional-badge'}">
                ${isRequired ? '必需' : '可选'}
            </span>
        `;
        
        const columnAliases = document.createElement('div');
        columnAliases.className = 'column-aliases';
        columnAliases.innerHTML = '<strong>可接受的列名：</strong> ';
        
        if (aliases.length > 0) {
            aliases.forEach(alias => {
                const aliasTag = document.createElement('span');
                aliasTag.className = 'alias-tag';
                aliasTag.textContent = alias;
                columnAliases.appendChild(aliasTag);
            });
        } else {
            columnAliases.innerHTML += '<em>无别名</em>';
        }
        
        item.appendChild(standardColumn);
        item.appendChild(columnAliases);
        container.appendChild(item);
    }

    // 更新示例表格
    updateExampleTable() {
        const exampleTableContainer = document.getElementById('example-table-container');
        if (!exampleTableContainer) return;
        
        // 创建示例表格
        const table = document.createElement('table');
        table.className = 'data-table';
        
        // 表头
        const thead = document.createElement('thead');
        const headerRow = document.createElement('tr');
        
        // 添加所有列（必需列和可选列）
        const allColumns = [
            ...this.columnMappings.required_columns,
            ...this.columnMappings.optional_columns
        ];
        
        allColumns.forEach(column => {
            const th = document.createElement('th');
            const isRequired = this.columnMappings.required_columns.includes(column);
            th.innerHTML = `
                ${column}
                <span class="${isRequired ? 'required-badge-inline' : 'optional-badge-inline'}">
                    ${isRequired ? '必需' : '可选'}
                </span>
            `;
            headerRow.appendChild(th);
        });
        
        thead.appendChild(headerRow);
        table.appendChild(thead);
        
        // 表体（示例数据）
        const tbody = document.createElement('tbody');
        
        // 示例数据
        const exampleData = [
            {
                item_id: 'PROD001',
                product_name: '办公椅',
                size: '标准',
                color: '黑色',
                standard_unit_price: 299.99
            },
            {
                item_id: 'PROD002',
                product_name: '办公桌',
                size: '120x60cm',
                color: '原木色',
                standard_unit_price: 599.00
            },
            {
                item_id: 'PROD003',
                product_name: '文件柜',
                size: '三层',
                color: '灰色',
                standard_unit_price: 450.00
            }
        ];
        
        // 添加示例数据行
        exampleData.forEach(item => {
            const row = document.createElement('tr');
            
            allColumns.forEach(column => {
                const td = document.createElement('td');
                td.textContent = item[column] !== undefined ? item[column] : '';
                row.appendChild(td);
            });
            
            tbody.appendChild(row);
        });
        
        table.appendChild(tbody);
        exampleTableContainer.innerHTML = '';
        exampleTableContainer.appendChild(table);
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
        
        // 下载模板按钮
        const downloadTemplateBtn = document.getElementById('download-template-btn-modal');
        if (downloadTemplateBtn) {
            downloadTemplateBtn.addEventListener('click', () => this.downloadTemplate());
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
        const tabContents = document.querySelectorAll(`#${this.modalId} .format-guide-tab`);
        tabContents.forEach(content => {
            content.classList.toggle('active', content.id === `${tabName}-tab`);
        });
    }

    // 显示模态框
    showModal() {
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

    // 下载模板
    downloadTemplate() {
        window.open('/api/download_spec_template?rows=5', '_blank');
    }
}

// 创建格式指南组件实例
const formatGuide = new FormatGuideComponent();

// 导出组件
window.formatGuide = formatGuide;