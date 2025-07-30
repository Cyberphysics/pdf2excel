// 全局变量
let currentFileId = null;
let currentResultFileId = null;
let currentSpecId = null;

// DOM元素
const elements = {
    // 导航相关
    navTabs: document.querySelectorAll('.nav-tab'),
    tabContents: document.querySelectorAll('.tab-content'),

    // 调试用
    pdfConvertTab: document.getElementById('pdf-convert-tab'),
    orderCheckTab: document.getElementById('order-check-tab'),
    specManageTab: document.getElementById('spec-manage-tab'),

    // PDF转换相关
    uploadArea: document.getElementById('upload-area'),
    fileInput: document.getElementById('file-input'),
    selectFileBtn: document.getElementById('select-file-btn'),
    fileInfo: document.getElementById('file-info'),
    fileName: document.getElementById('file-name'),
    fileSize: document.getElementById('file-size'),
    changeFileBtn: document.getElementById('change-file-btn'),
    uploadBtn: document.getElementById('upload-btn'),

    // 处理相关
    uploadSection: document.getElementById('upload-section'),
    processingSection: document.getElementById('processing-section'),
    resultSection: document.getElementById('result-section'),
    progressFill: document.getElementById('progress-fill'),
    cancelBtn: document.getElementById('cancel-btn'),

    // 结果相关
    downloadBtn: document.getElementById('download-btn'),
    previewBtn: document.getElementById('preview-btn'),
    newConversionBtn: document.getElementById('new-conversion-btn'),
    previewContainer: document.getElementById('preview-container'),
    tableContainer: document.getElementById('table-container'),

    // 已转换文件相关
    convertedFilesSection: document.getElementById('converted-files-section'),
    refreshConvertedFilesBtn: document.getElementById('refresh-converted-files-btn'),
    convertedFilesBody: document.getElementById('converted-files-body'),
    convertedFilesList: document.getElementById('converted-files-list'),

    // 订单核对相关
    orderFileSelect: document.getElementById('order-file-select'),
    specFileSelect: document.getElementById('spec-file-select'),
    refreshOrdersBtn: document.getElementById('refresh-orders-btn'),
    refreshSpecsBtn: document.getElementById('refresh-specs-btn'),
    checkTotalCalc: document.getElementById('check-total-calc'),
    startCheckBtn: document.getElementById('start-check-btn'),
    checkProgress: document.getElementById('check-progress'),
    checkResults: document.getElementById('check-results'),

    // 结果统计相关
    totalRecords: document.getElementById('total-records'),
    passRecords: document.getElementById('pass-records'),
    errorRecords: document.getElementById('error-records'),
    passRate: document.getElementById('pass-rate'),
    errorList: document.getElementById('error-list'),
    downloadResultBtn: document.getElementById('download-result-btn'),
    previewResultBtn: document.getElementById('preview-result-btn'),
    resultPreview: document.getElementById('result-preview'),
    resultTableContainer: document.getElementById('result-table-container'),

    // 规格管理相关
    specUploadArea: document.getElementById('spec-upload-area'),
    specFileInput: document.getElementById('spec-file-input'),
    selectSpecBtn: document.getElementById('select-spec-btn'),
    specFileInfo: document.getElementById('spec-file-info'),
    specFileName: document.getElementById('spec-file-name'),
    specFileSize: document.getElementById('spec-file-size'),
    changeSpecBtn: document.getElementById('change-spec-btn'),
    uploadSpecBtn: document.getElementById('upload-spec-btn'),
    refreshSpecListBtn: document.getElementById('refresh-spec-list-btn'),
    specTableBody: document.getElementById('spec-table-body'),

    // 消息提示相关
    errorMessage: document.getElementById('error-message'),
    successMessage: document.getElementById('success-message'),
    warningMessage: document.getElementById('warning-message'),
    errorText: document.getElementById('error-text'),
    successText: document.getElementById('success-text'),
    warningText: document.getElementById('warning-text'),
    errorClose: document.getElementById('error-close'),
    successClose: document.getElementById('success-close'),
    warningClose: document.getElementById('warning-close'),
    loadingOverlay: document.getElementById('loading-overlay')
};

// 初始化
document.addEventListener('DOMContentLoaded', function () {
    initializeEventListeners();

    // 确保初始状态下只有 PDF 转换页面是活跃的
    switchTab('pdf-convert');

    // 加载初始数据
    loadOrderFiles();
    loadSpecFiles();
    loadSpecList();
    loadConvertedFiles();

    // 加载列名映射配置
    loadColumnMappingConfig();
});

// 初始化事件监听器
function initializeEventListeners() {
    // 导航标签页
    elements.navTabs.forEach(tab => {
        tab.addEventListener('click', () => switchTab(tab.dataset.tab));
    });

    // PDF转换功能
    elements.selectFileBtn.addEventListener('click', () => elements.fileInput.click());
    elements.fileInput.addEventListener('change', handleFileSelect);
    elements.changeFileBtn.addEventListener('click', () => elements.fileInput.click());
    elements.uploadBtn.addEventListener('click', handleFileUpload);
    elements.cancelBtn.addEventListener('click', cancelUpload);
    elements.downloadBtn.addEventListener('click', downloadFile);
    elements.previewBtn.addEventListener('click', togglePreview);
    elements.newConversionBtn.addEventListener('click', resetToUpload);

    // 已转换文件功能
    if (elements.refreshConvertedFilesBtn) {
        elements.refreshConvertedFilesBtn.addEventListener('click', loadConvertedFiles);
    }

    // 批量操作功能
    const batchPreviewBtn = document.getElementById('batch-preview-btn');
    const batchDownloadBtn = document.getElementById('batch-download-btn');
    const batchDeleteBtn = document.getElementById('batch-delete-btn');

    if (batchPreviewBtn) batchPreviewBtn.addEventListener('click', batchPreviewFiles);
    if (batchDownloadBtn) batchDownloadBtn.addEventListener('click', batchDownloadFiles);
    if (batchDeleteBtn) batchDeleteBtn.addEventListener('click', batchDeleteFiles);

    // 拖拽上传
    elements.uploadArea.addEventListener('dragover', handleDragOver);
    elements.uploadArea.addEventListener('drop', handleDrop);
    elements.uploadArea.addEventListener('dragleave', handleDragLeave);

    // 订单核对功能
    elements.refreshOrdersBtn.addEventListener('click', loadOrderFiles);
    elements.refreshSpecsBtn.addEventListener('click', loadSpecFiles);
    elements.orderFileSelect.addEventListener('change', checkCanStartCheck);
    elements.specFileSelect.addEventListener('change', checkCanStartCheck);
    elements.startCheckBtn.addEventListener('click', startOrderCheck);
    elements.downloadResultBtn.addEventListener('click', downloadCheckResult);
    elements.previewResultBtn.addEventListener('click', toggleResultPreview);

    // 规格管理功能
    elements.selectSpecBtn.addEventListener('click', () => elements.specFileInput.click());
    elements.specFileInput.addEventListener('change', handleSpecFileSelect);
    elements.changeSpecBtn.addEventListener('click', () => elements.specFileInput.click());
    elements.uploadSpecBtn.addEventListener('click', handleSpecUpload);
    elements.refreshSpecListBtn.addEventListener('click', loadSpecList);

    // 模板和格式指南功能
    const downloadTemplateBtn = document.getElementById('download-template-btn');
    const showFormatGuideBtn = document.getElementById('show-format-guide-btn');

    if (downloadTemplateBtn) {
        downloadTemplateBtn.addEventListener('click', downloadSpecTemplate);
    }

    if (showFormatGuideBtn) {
        showFormatGuideBtn.addEventListener('click', showFormatGuide);
    }

    // 规格表拖拽上传
    elements.specUploadArea.addEventListener('dragover', handleDragOver);
    elements.specUploadArea.addEventListener('drop', handleSpecDrop);
    elements.specUploadArea.addEventListener('dragleave', handleDragLeave);

    // 消息关闭
    elements.errorClose.addEventListener('click', hideErrorMessage);
    elements.successClose.addEventListener('click', hideSuccessMessage);
    if (elements.warningClose) {
        elements.warningClose.addEventListener('click', hideWarningMessage);
    }
}

// 标签页切换
function switchTab(tabName) {
    console.log('切换到标签页:', tabName);

    // 更新导航标签
    elements.navTabs.forEach(tab => {
        tab.classList.toggle('active', tab.dataset.tab === tabName);
    });

    // 更新内容区域
    elements.tabContents.forEach(content => {
        content.classList.toggle('active', content.id === `${tabName}-tab`);
    });

    // 根据标签页加载相应数据
    if (tabName === 'order-check') {
        loadOrderFiles();
        loadSpecFiles();
        console.log('订单核对页面已加载');
    } else if (tabName === 'spec-manage') {
        loadSpecList();
        console.log('规格管理页面已加载');
    }

    // 检查切换后的状态
    const status = checkTabStatus();
    console.log('切换后状态:', status);
}

// 文件选择处理
function handleFileSelect(event) {
    const file = event.target.files[0];
    if (file) {
        displayFileInfo(file);
    }
}

function displayFileInfo(file) {
    elements.fileName.textContent = file.name;
    elements.fileSize.textContent = formatFileSize(file.size);
    elements.uploadArea.style.display = 'none';
    elements.fileInfo.style.display = 'block';
}

// 拖拽处理
function handleDragOver(event) {
    event.preventDefault();
    event.currentTarget.classList.add('drag-over');
}

function handleDragLeave(event) {
    event.preventDefault();
    event.currentTarget.classList.remove('drag-over');
}

function handleDrop(event) {
    event.preventDefault();
    event.currentTarget.classList.remove('drag-over');

    const files = event.dataTransfer.files;
    if (files.length > 0) {
        const file = files[0];
        if (file.type === 'application/pdf') {
            elements.fileInput.files = files;
            displayFileInfo(file);
        } else {
            showErrorMessage('请选择PDF文件');
        }
    }
}

// 文件上传处理
async function handleFileUpload() {
    const file = elements.fileInput.files[0];
    if (!file) {
        showErrorMessage('请先选择文件');
        return;
    }

    const formData = new FormData();
    formData.append('file', file);

    try {
        showSection('processing');
        simulateProgress();

        const response = await fetch('/api/pdf/upload', {
            method: 'POST',
            body: formData
        });

        const result = await response.json();

        if (response.ok) {
            currentFileId = result.file_id;
            await convertFile(result.file_id);
        } else {
            throw new Error(result.error || '上传失败');
        }
    } catch (error) {
        showErrorMessage(error.message);
        showSection('upload');
    }
}

// 文件转换
async function convertFile(fileId) {
    try {
        // const response = await fetch('/api/pdf/convert', {
        //     method: 'POST',
        //     headers: {
        //         'Content-Type': 'application/json'
        //     },
        //     body: JSON.stringify({ file_id: fileId })
        // });
        const response = await fetch(`/api/pdf/convert/${fileId}`, {
            method: 'POST'
        });

        const result = await response.json();

        if (response.ok) {
            currentFileId = result.file_id;
            showSection('result');
            showSuccessMessage('转换完成！');
        } else {
            throw new Error(result.error || '转换失败');
        }
    } catch (error) {
        showErrorMessage(error.message);
        showSection('upload');
    }
}

// 进度模拟
function simulateProgress() {
    let progress = 0;
    const interval = setInterval(() => {
        progress += Math.random() * 15;
        if (progress > 90) {
            progress = 90;
            clearInterval(interval);
        }
        elements.progressFill.style.width = progress + '%';
    }, 500);
}

// 取消上传
function cancelUpload() {
    showSection('upload');
    elements.progressFill.style.width = '0%';
}

// 下载文件
function downloadFile() {
    if (currentFileId) {
        window.open(`/api/pdf/download/${currentFileId}`, '_blank');
    }
}

// 加载已转换文件列表
async function loadConvertedFiles() {
    try {
        showLoading();
        const response = await fetch('/api/pdf/list_converted');
        const result = await response.json();
        hideLoading();

        if (response.ok) {
            displayConvertedFiles(result.files);
            showSuccessMessage(`已加载 ${result.files.length} 个订单文件`);
        } else {
            showErrorMessage('加载已转换文件失败: ' + (result.error || '未知错误'));
            console.error('加载已转换文件失败:', result.error);
        }
    } catch (error) {
        hideLoading();
        showErrorMessage('加载已转换文件失败: ' + error.message);
        console.error('加载已转换文件失败:', error);
    }
}

// 显示已转换文件列表
function displayConvertedFiles(files) {
    if (!elements.convertedFilesList) {
        // 如果元素不存在，创建一个
        const container = document.querySelector('.converted-files-container');
        if (container) {
            const listDiv = document.createElement('div');
            listDiv.id = 'converted-files-list';
            listDiv.className = 'converted-files-list';
            container.appendChild(listDiv);
            elements.convertedFilesList = listDiv;
        } else {
            console.error('找不到已转换文件容器');
            return;
        }
    }

    // 更新文件统计信息
    updateFileStats(files);

    elements.convertedFilesList.innerHTML = '';

    if (files.length === 0) {
        elements.convertedFilesList.innerHTML = '<p class="text-muted text-center">暂无已转换文件</p>';
        hideFileStats();
        hideSelectAllContainer();
        // 即使没有文件，也显示基本的统计信息（全为0）
        updateFileStats([]);
        forceShowFileStats();
        return;
    }

    const ul = document.createElement('ul');
    ul.className = 'file-list';

    files.forEach(file => {
        const li = document.createElement('li');
        li.className = 'file-item';
        li.dataset.fileId = file.file_id;

        // 文件是否存在的状态
        const fileStatus = file.exists ? '' : 'file-missing';

        // 显示文件名，优先使用原始文件名
        const displayName = file.filename || `converted_${file.file_id}.xlsx`;
        const originalName = file.original_filename ? `(原文件: ${file.original_filename})` : '';

        li.innerHTML = `
            <input type="checkbox" class="file-checkbox" data-file-id="${file.file_id}" onchange="updateBatchButtons()">
            <div class="file-status-indicator ${file.exists ? '' : 'missing'}"></div>
            <div class="file-info with-checkbox ${fileStatus}">
                <i class="fas fa-file-excel file-icon"></i>
                <div class="file-details">
                    <div class="file-name">${displayName}</div>
                    <div class="file-meta">
                        <span><i class="fas fa-calendar"></i> ${formatDateTime(file.convert_time)}</span>
                        <span><i class="fas fa-file-alt"></i> ${formatFileSize(file.file_size)}</span>
                        ${file.record_count ? `<span><i class="fas fa-table"></i> ${file.record_count}行</span>` : ''}
                        <span class="file-id" title="文件ID">${file.file_id}</span>
                        ${!file.exists ? '<span class="file-missing-badge">文件不存在</span>' : ''}
                    </div>
                    ${originalName ? `<div class="original-filename">${originalName}</div>` : ''}
                </div>
            </div>
            <div class="file-actions">
                <button class="btn btn-info btn-small" onclick="previewOrder('${file.file_id}')" ${!file.exists ? 'disabled' : ''}>
                    <i class="fas fa-eye"></i> 预览
                </button>
                <button class="btn btn-primary btn-small" onclick="downloadOrder('${file.file_id}')" ${!file.exists ? 'disabled' : ''}>
                    <i class="fas fa-download"></i> 下载
                </button>
                <button class="btn btn-danger btn-small" onclick="deleteConvertedFile('${file.file_id}')">
                    <i class="fas fa-trash"></i> 删除
                </button>
                <button class="btn btn-secondary btn-small" onclick="checkFileExists('${file.file_id}')">
                    <i class="fas fa-sync"></i> 检查
                </button>
            </div>
        `;

        // 添加点击选择功能
        li.addEventListener('click', function (e) {
            if (e.target.type !== 'checkbox' && !e.target.closest('.file-actions')) {
                const checkbox = li.querySelector('.file-checkbox');
                checkbox.checked = !checkbox.checked;
                updateBatchButtons();
                li.classList.toggle('selected', checkbox.checked);
            }
        });

        ul.appendChild(li);
    });

    elements.convertedFilesList.appendChild(ul);
    showFileStats();
    showSelectAllContainer();
}

// 预览订单
async function previewOrder(fileId) {
    try {
        showLoading();
        const response = await fetch(`/api/pdf/preview_converted/${fileId}`);
        const result = await response.json();
        hideLoading();

        if (response.ok) {
            // 创建模态框显示预览
            const modalId = 'order-preview-modal';
            let modal = document.getElementById(modalId);

            // 如果模态框不存在，创建一个
            if (!modal) {
                modal = document.createElement('div');
                modal.id = modalId;
                modal.className = 'modal';
                document.body.appendChild(modal);
            }

            // 设置模态框内容
            modal.innerHTML = `
                <div class="modal-content">
                    <div class="modal-header">
                        <h3>订单预览 - ${result.filename}</h3>
                        <span class="close" onclick="document.getElementById('${modalId}').style.display='none'">&times;</span>
                    </div>
                    <div class="modal-body">
                        <div class="preview-info">
                            <p>转换时间: ${formatDateTime(result.convert_time)} | 文件大小: ${formatFileSize(result.file_size)}</p>
                        </div>
                        <div class="tabs">
                            ${result.sheets.map((sheet, index) =>
                `<button class="tab-button ${index === 0 ? 'active' : ''}" 
                                 onclick="switchPreviewTab('${sheet}', this, '${fileId}')">${sheet}</button>`
            ).join('')}
                        </div>
                        <div class="table-container" id="order-preview-container">
                            <!-- 表格内容将动态加载 -->
                        </div>
                    </div>
                </div>
            `;

            // 显示模态框
            modal.style.display = 'block';

            // 默认显示第一个工作表
            if (result.sheets.length > 0) {
                loadSheetData(fileId, result.sheets[0]);
            }

            // 点击模态框外部关闭
            window.onclick = function (event) {
                if (event.target === modal) {
                    modal.style.display = 'none';
                }
            };
        } else {
            throw new Error(result.error || '预览失败');
        }
    } catch (error) {
        hideLoading();
        showErrorMessage(error.message);
    }
}

// 加载工作表数据
async function loadSheetData(fileId, sheetName) {
    try {
        showLoading();
        const response = await fetch(`/api/pdf/sheet_data/${fileId}?sheet=${encodeURIComponent(sheetName)}`);
        const result = await response.json();

        if (response.ok) {
            // 使用统一的数据格式
            const formattedData = formatSheetData(result);
            displayTable(formattedData.data, formattedData.columns, document.getElementById('order-preview-container'));
        } else {
            throw new Error(result.error || '加载工作表数据失败');
        }
    } catch (error) {
        showErrorMessage(error.message);
    } finally {
        hideLoading();
    }
}

// 格式化工作表数据
function formatSheetData(result) {
    if (result.data && Array.isArray(result.data) && result.data.length > 0) {
        // 如果数据是对象数组格式，转换为displayTable期望的格式
        if (typeof result.data[0] === 'object') {
            return {
                columns: result.columns || Object.keys(result.data[0]),
                data: result.data
            };
        }
    }
    
    return {
        columns: result.columns || [],
        data: result.data || []
    };
}

// 切换预览标签
function switchPreviewTab(sheetName, button, fileId) {
    // 更新活动标签按钮
    const buttons = document.querySelectorAll('.tab-button');
    buttons.forEach(btn => btn.classList.remove('active'));
    button.classList.add('active');

    // 加载选中的工作表数据
    loadSheetData(fileId, sheetName);
}

// 下载订单
function downloadOrder(fileId) {
    window.open(`/api/pdf/download_converted/${fileId}`, '_blank');
}

// 检查文件是否存在
async function checkFileExists(fileId) {
    try {
        showLoading();
        const response = await fetch(`/api/pdf/check_file_exists/${fileId}`);
        const result = await response.json();
        hideLoading();

        if (response.ok) {
            if (result.exists) {
                showSuccessMessage(`文件 ${result.filename} 存在！`);
            } else {
                showErrorMessage(`文件 ${result.filename} 不存在，但元数据仍然保留。`);
            }
            loadConvertedFiles(); // 刷新文件列表
        } else {
            throw new Error(result.error || '检查失败');
        }
    } catch (error) {
        hideLoading();
        showErrorMessage(error.message);
    }
}

// 删除已转换文件
async function deleteConvertedFile(fileId) {
    if (!confirm('确定要删除这个文件吗？')) {
        return;
    }

    try {
        showLoading();
        const response = await fetch(`/api/pdf/delete_converted/${fileId}`, {
            method: 'DELETE'
        });
        const result = await response.json();
        hideLoading();

        if (response.ok) {
            showSuccessMessage('文件删除成功！');
            loadConvertedFiles(); // 刷新文件列表
            loadOrderFiles(); // 刷新订单核对页面的文件列表
        } else {
            throw new Error(result.error || '删除失败');
        }
    } catch (error) {
        hideLoading();
        showErrorMessage(error.message);
    }
}

// 切换预览
async function togglePreview() {
    if (elements.previewContainer.style.display === 'none') {
        await loadPreview();
        elements.previewContainer.style.display = 'block';
        elements.previewBtn.innerHTML = '<i class="fas fa-eye-slash"></i> 隐藏预览';
    } else {
        elements.previewContainer.style.display = 'none';
        elements.previewBtn.innerHTML = '<i class="fas fa-eye"></i> 预览';
    }
}

// 加载预览
async function loadPreview() {
    if (!currentFileId) return;

    try {
        const response = await fetch(`/api/pdf/preview/${currentFileId}`);
        const result = await response.json();

        if (response.ok) {
            // 处理预览数据格式
            if (result.preview_data && result.preview_data.length > 0) {
                displayMultiTablePreview(result.preview_data, elements.tableContainer);
            } else {
                elements.tableContainer.innerHTML = '<p style="text-align: center; color: #6c757d;">暂无数据</p>';
            }
        } else {
            throw new Error(result.error || '预览失败');
        }
    } catch (error) {
        showErrorMessage(error.message);
    }
}

// 重置到上传状态
function resetToUpload() {
    showSection('upload');
    elements.fileInput.value = '';
    elements.uploadArea.style.display = 'block';
    elements.fileInfo.style.display = 'none';
    elements.previewContainer.style.display = 'none';
    currentFileId = null;
}

// 显示指定区域
function showSection(sectionName) {
    const sections = ['upload', 'processing', 'result'];
    sections.forEach(section => {
        const element = document.getElementById(`${section}-section`);
        if (element) {
            element.classList.toggle('active', section === sectionName);
        }
    });
}

// 订单核对相关功能

// 加载订单文件列表
async function loadOrderFiles() {
    try {
        showLoading();
        const response = await fetch('/api/pdf/list_converted');
        const result = await response.json();
        hideLoading();

        if (response.ok) {
            console.log('加载订单文件成功:', result.files);

            // 显示所有文件，包括不存在的文件（但会在UI中标记）
            populateSelect(elements.orderFileSelect, result.files, '请选择已转换的订单文件...');

            // 统计文件状态
            const existingFiles = result.files.filter(file => file.exists).length;
            const missingFiles = result.files.filter(file => !file.exists).length;

            if (missingFiles > 0) {
                showWarningMessage(`发现 ${missingFiles} 个文件不存在，请刷新列表或检查文件状态。`);
            }
        } else {
            console.error('加载订单文件失败:', result.error);
            showErrorMessage('加载订单文件失败: ' + (result.error || '未知错误'));
        }
    } catch (error) {
        hideLoading();
        console.error('加载订单文件失败:', error);
        showErrorMessage('加载订单文件失败: ' + error.message);
    }
}

// 加载规格表文件列表
async function loadSpecFiles() {
    try {
        const response = await fetch('/api/list_specs');
        const result = await response.json();

        if (response.ok) {
            populateSelect(elements.specFileSelect, result.specs, '请选择产品规格表...', 'spec_id', 'filename');
        } else {
            console.error('加载规格表失败:', result.error);
        }
    } catch (error) {
        console.error('加载规格表失败:', error);
    }
}

// 填充下拉选择框
function populateSelect(selectElement, items, placeholder, valueKey = 'file_id', textKey = 'filename') {
    console.log('populateSelect', selectElement, items);
    selectElement.innerHTML = `<option value="">${placeholder}</option>`;

    items.forEach(item => {
        const option = document.createElement('option');
        option.value = item[valueKey];

        // 如果是订单文件，显示更多信息并标记不存在的文件
        if (valueKey === 'file_id' && 'exists' in item) {
            const fileExists = item.exists;
            const displayName = item[textKey];
            const recordCount = item.record_count ? ` (${item.record_count}行)` : '';
            const existsMarker = fileExists ? '' : ' [文件不存在]';

            option.textContent = `${displayName}${recordCount}${existsMarker}`;

            // 如果文件不存在，添加禁用属性和样式
            if (!fileExists) {
                option.disabled = true;
                option.classList.add('file-missing-option');
            }
        } else {
            option.textContent = item[textKey];
        }

        selectElement.appendChild(option);
    });
}

// 检查是否可以开始核对
function checkCanStartCheck() {
    const canStart = elements.orderFileSelect.value && elements.specFileSelect.value;
    elements.startCheckBtn.disabled = !canStart;
}

// 开始订单核对
async function startOrderCheck() {
    const orderFileId = elements.orderFileSelect.value;
    const specId = elements.specFileSelect.value;
    const checkTotalCalc = elements.checkTotalCalc.checked;

    if (!orderFileId || !specId) {
        showErrorMessage('请选择订单文件和规格表');
        return;
    }

    try {
        elements.checkProgress.style.display = 'block';
        elements.checkResults.style.display = 'none';

        const response = await fetch('/api/compare_orders', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                order_file_id: orderFileId,
                spec_id: specId,
                check_total_calc: checkTotalCalc
            })
        });

        const result = await response.json();

        if (response.ok) {
            currentResultFileId = result.result_file_id;
            displayCheckResults(result.stats);
            elements.checkProgress.style.display = 'none';
            elements.checkResults.style.display = 'block';
            showSuccessMessage('订单核对完成！');
        } else {
            throw new Error(result.error || '核对失败');
        }
    } catch (error) {
        elements.checkProgress.style.display = 'none';
        showErrorMessage(error.message);
    }
}

// 显示核对结果
function displayCheckResults(stats) {
    elements.totalRecords.textContent = stats.total_records;
    elements.passRecords.textContent = stats.total_records - stats.error_records;
    elements.errorRecords.textContent = stats.error_records;

    const passRate = stats.total_records > 0 ?
        ((stats.total_records - stats.error_records) / stats.total_records * 100).toFixed(1) : 100;
    elements.passRate.textContent = passRate + '%';

    // 显示错误类型统计
    elements.errorList.innerHTML = '';
    Object.entries(stats.error_types).forEach(([type, count]) => {
        if (count > 0) {
            const errorItem = document.createElement('div');
            errorItem.className = 'error-item';
            errorItem.innerHTML = `
                <span class="error-name">${getErrorTypeName(type)}</span>
                <span class="error-count">${count}</span>
            `;
            elements.errorList.appendChild(errorItem);
        }
    });
}

// 获取错误类型中文名称
function getErrorTypeName(type) {
    const errorNames = {
        'PRODUCT_NOT_FOUND': '产品ID不存在',
        'SIZE_MISMATCH': '尺寸不符',
        'COLOR_MISMATCH': '颜色不符',
        'PRICE_MISMATCH': '单价不符',
        'TOTAL_CALC_ERROR': '总价计算错误'
    };
    return errorNames[type] || type;
}

// 下载核对结果
function downloadCheckResult() {
    if (currentResultFileId) {
        window.open(`/api/download_comparison/${currentResultFileId}`, '_blank');
    }
}

// 切换结果预览
async function toggleResultPreview() {
    if (elements.resultPreview.style.display === 'none') {
        await loadResultPreview();
        elements.resultPreview.style.display = 'block';
        elements.previewResultBtn.innerHTML = '<i class="fas fa-eye-slash"></i> 隐藏预览';
    } else {
        elements.resultPreview.style.display = 'none';
        elements.previewResultBtn.innerHTML = '<i class="fas fa-eye"></i> 预览结果';
    }
}

// 加载结果预览
async function loadResultPreview() {
    if (!currentResultFileId) return;

    try {
        const response = await fetch(`/api/preview_comparison/${currentResultFileId}`);
        const result = await response.json();

        if (response.ok) {
            displayTable(result.data, result.columns, elements.resultTableContainer);
        } else {
            throw new Error(result.error || '预览失败');
        }
    } catch (error) {
        showErrorMessage(error.message);
    }
}

// 规格管理相关功能

// 规格表文件选择处理
function handleSpecFileSelect(event) {
    const file = event.target.files[0];
    if (file) {
        displaySpecFileInfo(file);
    }
}

function displaySpecFileInfo(file) {
    elements.specFileName.textContent = file.name;
    elements.specFileSize.textContent = formatFileSize(file.size);
    elements.specUploadArea.style.display = 'none';
    elements.specFileInfo.style.display = 'block';
}

// 规格表拖拽处理
function handleSpecDrop(event) {
    event.preventDefault();
    event.currentTarget.classList.remove('drag-over');

    const files = event.dataTransfer.files;
    if (files.length > 0) {
        const file = files[0];
        if (file.name.endsWith('.xlsx') || file.name.endsWith('.xls')) {
            elements.specFileInput.files = files;
            displaySpecFileInfo(file);
        } else {
            showErrorMessage('请选择Excel文件(.xlsx或.xls)');
        }
    }
}

// 规格表上传处理
async function handleSpecUpload() {
    const file = elements.specFileInput.files[0];
    if (!file) {
        showErrorMessage('请先选择文件');
        return;
    }

    try {
        showLoading();

        // 使用新的上传API，先上传文件获取临时ID
        const formData = new FormData();
        formData.append('file', file);

        const response = await fetch('/api/upload_for_mapping', {
            method: 'POST',
            body: formData
        });

        const result = await response.json();

        hideLoading();

        if (response.ok) {
            // 显示映射确认对话框
            if (window.mappingDialog) {
                window.mappingDialog.showModal(result.file_id, file.name);
            } else {
                // 如果映射对话框组件未加载，回退到直接上传
                await directUploadSpec(file);
            }
        } else {
            // 使用增强型错误反馈
            showErrorMessage(result.error || result.message || '上传失败', result);
        }
    } catch (error) {
        hideLoading();
        showErrorMessage(error.message);
    }
}

// 直接上传规格表（不使用映射确认对话框）
async function directUploadSpec(file) {
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    try {
        showLoading();

        const response = await fetch('/api/upload_spec', {
            method: 'POST',
            body: formData
        });

        const result = await response.json();

        hideLoading();

        if (response.ok) {
            showSuccessMessage('规格表上传成功！');
            resetSpecUpload();
            loadSpecList();
            loadSpecFiles(); // 刷新订单核对页面的规格表列表
        } else {
            // 使用增强型错误反馈
            showErrorMessage(result.error || result.message || '上传失败', result);
        }
    } catch (error) {
        hideLoading();
        showErrorMessage(error.message);
    }
}

// 重置规格表上传状态
function resetSpecUpload() {
    elements.specFileInput.value = '';
    elements.specUploadArea.style.display = 'block';
    elements.specFileInfo.style.display = 'none';
}

// 加载规格表列表
async function loadSpecList() {
    try {
        const response = await fetch('/api/list_specs');
        const result = await response.json();

        if (response.ok) {
            displaySpecList(result.specs);
        } else {
            console.error('加载规格表列表失败:', result.error);
        }
    } catch (error) {
        console.error('加载规格表列表失败:', error);
    }
}

// 显示规格表列表
function displaySpecList(specs) {
    elements.specTableBody.innerHTML = '';

    if (specs.length === 0) {
        const row = elements.specTableBody.insertRow();
        row.innerHTML = '<td colspan="5" style="text-align: center; color: #6c757d;">暂无规格表</td>';
        return;
    }

    specs.forEach(spec => {
        const row = elements.specTableBody.insertRow();
        row.innerHTML = `
            <td>${spec.filename}</td>
            <td>${spec.record_count || 0}</td>
            <td>${formatDateTime(spec.upload_time)}</td>
            <td>${formatFileSize(spec.file_size || 0)}</td>
            <td>
                <div class="action-buttons">
                    <button class="btn btn-info btn-small" onclick="previewSpec('${spec.spec_id}')">
                        <i class="fas fa-eye"></i> 预览
                    </button>
                    <button class="btn btn-primary btn-small" onclick="downloadSpec('${spec.spec_id}')">
                        <i class="fas fa-download"></i> 下载
                    </button>
                    <button class="btn btn-danger btn-small" onclick="deleteSpec('${spec.spec_id}')">
                        <i class="fas fa-trash"></i> 删除
                    </button>
                </div>
            </td>
        `;
    });
}

// 删除规格表
async function deleteSpec(specId) {
    if (!confirm('确定要删除这个规格表吗？')) {
        return;
    }

    try {
        const response = await fetch(`/api/delete_spec/${specId}`, {
            method: 'DELETE'
        });

        const result = await response.json();

        if (response.ok) {
            showSuccessMessage('规格表删除成功！');
            loadSpecList();
            loadSpecFiles(); // 刷新订单核对页面的规格表列表
        } else {
            throw new Error(result.error || '删除失败');
        }
    } catch (error) {
        showErrorMessage(error.message);
    }
}

// 预览规格表
async function previewSpec(specId) {
    try {
        showLoading();

        const response = await fetch(`/api/preview_spec/${specId}`);
        const result = await response.json();

        hideLoading();

        if (response.ok) {
            // 创建模态框显示预览
            const modalId = 'spec-preview-modal';
            let modal = document.getElementById(modalId);

            // 如果模态框不存在，创建一个
            if (!modal) {
                modal = document.createElement('div');
                modal.id = modalId;
                modal.className = 'modal';
                document.body.appendChild(modal);
            }

            // 设置模态框内容
            modal.innerHTML = `
                <div class="modal-content">
                    <div class="modal-header">
                        <h3>规格表预览</h3>
                        <span class="close" onclick="document.getElementById('${modalId}').style.display='none'">&times;</span>
                    </div>
                    <div class="modal-body">
                        <div class="preview-info">
                            <p>总记录数: ${result.total_rows} | 显示前 ${result.preview_rows} 行</p>
                        </div>
                        <div class="table-container" id="spec-preview-container">
                            <!-- 表格内容将动态加载 -->
                        </div>
                    </div>
                </div>
            `;

            // 显示模态框
            modal.style.display = 'block';

            // 显示表格数据
            displayTable(result.data, result.columns, document.getElementById('spec-preview-container'));

            // 点击模态框外部关闭
            window.onclick = function (event) {
                if (event.target === modal) {
                    modal.style.display = 'none';
                }
            };
        } else {
            throw new Error(result.error || '预览失败');
        }
    } catch (error) {
        hideLoading();
        showErrorMessage(error.message);
    }
}

// 下载规格表
function downloadSpec(specId) {
    window.open(`/api/download_spec/${specId}`, '_blank');
}

// 下载规格表模板
function downloadSpecTemplate() {
    // 尝试使用API下载，如果失败则使用静态文件
    try {
        window.open('/api/download_spec_template', '_blank');
    } catch (error) {
        // 备用方案：使用静态文件
        const link = document.createElement('a');
        link.href = '产品规格表模板.xlsx';
        link.download = '产品规格表模板.xlsx';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    }
}

// 显示规格表示例
async function showSpecExample() {
    const modalId = 'spec-example-modal';
    let modal = document.getElementById(modalId);

    // 如果模态框不存在，创建一个
    if (!modal) {
        modal = document.createElement('div');
        modal.id = modalId;
        modal.className = 'modal';
        document.body.appendChild(modal);
    }

    try {
        showLoading();

        // 获取列名映射配置
        const response = await fetch('/api/column_mapping_info');
        const mappingInfo = await response.json();

        hideLoading();

        if (!response.ok) {
            throw new Error(mappingInfo.error || '获取列名映射配置失败');
        }

        const requiredColumns = mappingInfo.required_columns || [];
        const optionalColumns = mappingInfo.optional_columns || [];
        const columnMappings = mappingInfo.column_mappings || {};

        // 构建表头
        let tableHeaders = '';
        [...requiredColumns, ...optionalColumns].forEach(col => {
            tableHeaders += `<th>${col}</th>`;
        });

        // 构建示例数据行
        let tableRows = '';
        for (let i = 0; i < 3; i++) {
            let row = '<tr>';
            [...requiredColumns, ...optionalColumns].forEach(col => {
                if (col === 'item_id') {
                    row += `<td>ITEM00${i + 1}</td>`;
                } else if (col === 'product_name') {
                    row += `<td>产品${String.fromCharCode(65 + i)}</td>`;
                } else if (col === 'size') {
                    row += `<td>${['M', 'L', 'XL'][i]}</td>`;
                } else if (col === 'color') {
                    row += `<td>${['红色', '蓝色', '绿色'][i]}</td>`;
                } else if (col === 'standard_unit_price') {
                    row += `<td>${(99.99 + i * 30).toFixed(2)}</td>`;
                } else {
                    row += `<td>示例${i + 1}</td>`;
                }
            });
            row += '</tr>';
            tableRows += row;
        }

        // 构建列名映射信息
        let mappingInfo_html = '';
        Object.entries(columnMappings).forEach(([standardCol, aliases]) => {
            const isRequired = requiredColumns.includes(standardCol);
            mappingInfo_html += `
                <div class="mapping-item">
                    <div class="standard-column ${isRequired ? 'required' : 'optional'}">
                        ${standardCol} ${isRequired ? '<span class="required-badge">必需</span>' : '<span class="optional-badge">可选</span>'}
                    </div>
                    <div class="column-aliases">
                        可接受的别名: ${aliases.map(a => `<span class="alias-tag">${a}</span>`).join(' ')}
                    </div>
                </div>
            `;
        });

        // 设置模态框内容
        modal.innerHTML = `
            <div class="modal-content">
                <div class="modal-header">
                    <h3>规格表格式指南</h3>
                    <span class="close" onclick="document.getElementById('${modalId}').style.display='none'">&times;</span>
                </div>
                <div class="modal-body">
                    <div class="example-info">
                        <p><strong>说明：</strong>系统现在支持灵活的列名映射，您可以使用以下标准列名或其别名：</p>
                    </div>
                    
                    <div class="mapping-container">
                        ${mappingInfo_html}
                    </div>
                    
                    <div class="example-table-container">
                        <h5>示例数据格式：</h5>
                        <table class="data-table">
                            <thead>
                                <tr>
                                    ${tableHeaders}
                                </tr>
                            </thead>
                            <tbody>
                                ${tableRows}
                            </tbody>
                        </table>
                    </div>
                    
                    <div class="example-notes">
                        <h5>重要说明：</h5>
                        <ul>
                            <li>系统会自动识别常见的列名变体，如"产品ID"会被映射为"item_id"</li>
                            <li>标记为<span class="required-badge-inline">必需</span>的列必须存在，否则上传将失败</li>
                            <li>标记为<span class="optional-badge-inline">可选</span>的列可以不提供</li>
                            <li>如果系统无法识别您的列名，会提供修改建议</li>
                        </ul>
                        <p class="tip">💡 建议先下载模板文件，然后在模板基础上填写您的产品数据。</p>
                    </div>
                </div>
            </div>
        `;
    } catch (error) {
        hideLoading();

        // 如果获取配置失败，显示默认内容
        modal.innerHTML = `
            <div class="modal-content">
                <div class="modal-header">
                    <h3>规格表格式示例</h3>
                    <span class="close" onclick="document.getElementById('${modalId}').style.display='none'">&times;</span>
                </div>
                <div class="modal-body">
                    <div class="example-info">
                        <p><strong>说明：</strong>Excel文件必须包含以下列，系统支持多种列名格式：</p>
                    </div>
                    <div class="example-table-container">
                        <table class="data-table">
                            <thead>
                                <tr>
                                    <th>item_id</th>
                                    <th>product_name</th>
                                    <th>size</th>
                                    <th>color</th>
                                    <th>standard_unit_price</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr>
                                    <td>ITEM001</td>
                                    <td>产品A</td>
                                    <td>M</td>
                                    <td>红色</td>
                                    <td>99.99</td>
                                </tr>
                                <tr>
                                    <td>ITEM002</td>
                                    <td>产品B</td>
                                    <td>L</td>
                                    <td>蓝色</td>
                                    <td>129.99</td>
                                </tr>
                                <tr>
                                    <td>ITEM003</td>
                                    <td>产品C</td>
                                    <td>XL</td>
                                    <td>绿色</td>
                                    <td>159.99</td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                    <div class="example-notes">
                        <h5>重要说明：</h5>
                        <ul>
                            <li><strong>item_id</strong>: 产品唯一标识符，不能为空</li>
                            <li><strong>product_name</strong>: 产品名称</li>
                            <li><strong>size</strong>: 产品尺寸</li>
                            <li><strong>color</strong>: 产品颜色</li>
                            <li><strong>standard_unit_price</strong>: 标准单价，必须为数字</li>
                        </ul>
                        <p class="tip">💡 建议先下载模板文件，然后在模板基础上填写您的产品数据。</p>
                    </div>
                </div>
            </div>
        `;

        console.error('获取列名映射配置失败:', error);
    }

    // 显示模态框
    modal.style.display = 'block';

    // 点击模态框外部关闭
    window.onclick = function (event) {
        if (event.target === modal) {
            modal.style.display = 'none';
        }
    };
}

// 工具函数

// 格式化预览数据
function formatPreviewData(rawData, rawColumns) {
    // 如果列名是数字，生成更有意义的列名
    const columns = rawColumns.map((col, index) => {
        if (typeof col === 'number') {
            return `列${col + 1}`;
        }
        return col;
    });

    // 将二维数组转换为对象数组
    const data = rawData.map(row => {
        const rowObj = {};
        columns.forEach((col, index) => {
            rowObj[col] = row[index] || '';
        });
        return rowObj;
    });

    return { data, columns };
}

// 显示多表格预览
function displayMultiTablePreview(previewData, container) {
    if (!previewData || previewData.length === 0) {
        container.innerHTML = '<p style="text-align: center; color: #6c757d;">暂无数据</p>';
        return;
    }

    let html = '';

    previewData.forEach((tableData, index) => {
        // 表格标题
        html += `<div class="table-section">`;

        // 智能处理准确率显示
        let accuracyPercent;
        if (tableData.accuracy <= 1) {
            // 如果是0-1之间的小数，转换为百分比
            accuracyPercent = (tableData.accuracy * 100).toFixed(1);
        } else {
            // 如果已经是百分比格式，直接使用
            accuracyPercent = Math.min(tableData.accuracy, 100).toFixed(1);
        }

        html += `<h4>表格 ${tableData.table_index} (页面 ${tableData.page}) - 准确率: ${accuracyPercent}%</h4>`;
        html += `<p class="table-info">共 ${tableData.total_rows} 行 ${tableData.total_columns} 列，显示前 ${Math.min(tableData.data.length, 20)} 行</p>`;

        // 格式化数据
        const formattedData = formatPreviewData(tableData.data, tableData.columns);

        // 生成表格HTML
        html += '<table class="preview-table"><thead><tr>';
        formattedData.columns.forEach(col => {
            html += `<th>${col}</th>`;
        });
        html += '</tr></thead><tbody>';

        formattedData.data.forEach(row => {
            html += '<tr>';
            formattedData.columns.forEach(col => {
                const value = row[col] || '';
                html += `<td>${value}</td>`;
            });
            html += '</tr>';
        });

        html += '</tbody></table>';
        html += '</div>';

        // 如果不是最后一个表格，添加分隔符
        if (index < previewData.length - 1) {
            html += '<hr style="margin: 20px 0;">';
        }
    });

    container.innerHTML = html;
}

// 显示表格
function displayTable(data, columns, container) {
    if (!data || data.length === 0) {
        container.innerHTML = '<p style="text-align: center; color: #6c757d;">暂无数据</p>';
        return;
    }

    let html = '<table class="preview-table"><thead><tr>';
    columns.forEach(col => {
        html += `<th>${col}</th>`;
    });
    html += '</tr></thead><tbody>';

    data.slice(0, 50).forEach(row => { // 只显示前50行
        html += '<tr>';
        columns.forEach(col => {
            const value = row[col] || '';
            const cellClass = row['核对状态'] === '有问题' ? 'error-cell' : '';
            html += `<td class="${cellClass}">${value}</td>`;
        });
        html += '</tr>';
    });

    html += '</tbody></table>';

    if (data.length > 50) {
        html += `<p style="text-align: center; color: #6c757d; margin-top: 10px;">
            显示前50行，共${data.length}行数据
        </p>`;
    }

    container.innerHTML = html;
}

// 格式化文件大小
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// 格式化日期时间
function formatDateTime(dateString) {
    if (!dateString) return '';
    const date = new Date(dateString);
    return date.toLocaleString('zh-CN');
}

// 显示错误消息
function showErrorMessage(message, errorData) {
    // 如果提供了错误数据对象，使用增强型错误反馈组件
    if (errorData && typeof errorData === 'object' && window.errorFeedback) {
        window.errorFeedback.showModal(errorData);
    } else {
        // 否则使用简单的错误消息
        elements.errorText.textContent = message;
        elements.errorMessage.style.display = 'block';
        setTimeout(hideErrorMessage, 5000);
    }
}

// 隐藏错误消息
function hideErrorMessage() {
    elements.errorMessage.style.display = 'none';
}

// 显示成功消息
function showSuccessMessage(message) {
    elements.successText.textContent = message;
    elements.successMessage.style.display = 'block';
    setTimeout(hideSuccessMessage, 3000);
}

// 隐藏成功消息
function hideSuccessMessage() {
    elements.successMessage.style.display = 'none';
}

// 显示加载遮罩
function showLoading() {
    elements.loadingOverlay.style.display = 'flex';
}

// 隐藏加载遮罩
function hideLoading() {
    elements.loadingOverlay.style.display = 'none';
}

// 检查页面切换状态
function checkTabStatus() {
    const activeTab = document.querySelector('.nav-tab.active');
    const activeContent = document.querySelector('.tab-content.active');

    console.log('当前活跃标签:', activeTab ? activeTab.dataset.tab : '无');
    console.log('当前活跃内容:', activeContent ? activeContent.id : '无');

    return {
        activeTabName: activeTab ? activeTab.dataset.tab : null,
        activeContentId: activeContent ? activeContent.id : null
    };
}

// 添加调试辅助函数
function debugTabVisibility() {
    console.group('页面可见性状态');
    console.log('PDF转换页面:', elements.pdfConvertTab.classList.contains('active') ? '可见' : '隐藏');
    console.log('订单核对页面:', elements.orderCheckTab.classList.contains('active') ? '可见' : '隐藏');
    console.log('规格管理页面:', elements.specManageTab.classList.contains('active') ? '可见' : '隐藏');

    // 检查CSS计算样式
    console.log('PDF转换页面计算样式:', window.getComputedStyle(elements.pdfConvertTab).display);
    console.log('订单核对页面计算样式:', window.getComputedStyle(elements.orderCheckTab).display);
    console.log('规格管理页面计算样式:', window.getComputedStyle(elements.specManageTab).display);
    console.groupEnd();
}

// 添加全局调试函数，可以在浏览器控制台中调用
window.debugTabs = function () {
    debugTabVisibility();
    return checkTabStatus();
};

// 添加手动切换函数，可以在浏览器控制台中调用
window.manualSwitchTab = function (tabName) {
    if (['pdf-convert', 'order-check', 'spec-manage'].includes(tabName)) {
        switchTab(tabName);
        return true;
    } else {
        console.error('无效的标签页名称。有效值: pdf-convert, order-check, spec-manage');
        return false;
    }
};

// 检查文件是否存在
async function checkFileExists(fileId) {
    try {
        showLoading();
        const response = await fetch(`/api/pdf/status/${fileId}`);
        const result = await response.json();
        hideLoading();

        if (response.ok) {
            if (result.excel_exists) {
                showSuccessMessage(`文件 ${fileId} 存在，状态正常`);
            } else {
                showErrorMessage(`文件 ${fileId} 不存在或已被删除`);
                // 刷新文件列表
                loadConvertedFiles();
            }
        } else {
            showErrorMessage('检查文件状态失败: ' + (result.error || '未知错误'));
        }
    } catch (error) {
        hideLoading();
        showErrorMessage('检查文件状态失败: ' + error.message);
    }
}

// 显示警告消息
function showWarningMessage(message) {
    if (!elements.warningMessage) {
        // 如果警告消息元素不存在，创建一个
        const warningDiv = document.createElement('div');
        warningDiv.id = 'warning-message';
        warningDiv.className = 'message warning-message';
        warningDiv.innerHTML = `
            <div class="message-content">
                <i class="fas fa-exclamation-triangle"></i>
                <span id="warning-text"></span>
                <button id="warning-close" class="close-btn">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `;
        document.body.appendChild(warningDiv);

        // 更新元素引用
        elements.warningMessage = warningDiv;
        elements.warningText = document.getElementById('warning-text');
        elements.warningClose = document.getElementById('warning-close');

        // 添加关闭事件
        elements.warningClose.addEventListener('click', hideWarningMessage);
    }

    elements.warningText.textContent = message;
    elements.warningMessage.classList.add('show');

    // 5秒后自动隐藏
    setTimeout(hideWarningMessage, 5000);
}

// 隐藏警告消息
function hideWarningMessage() {
    if (elements.warningMessage) {
        elements.warningMessage.classList.remove('show');
    }
}

// 显示格式指南
async function showFormatGuide() {
    try {
        // 确保格式指南组件已初始化
        if (window.formatGuide) {
            await window.formatGuide.initialize();
            window.formatGuide.showModal();
        } else {
            showErrorMessage('格式指南组件未加载');
        }
    } catch (error) {
        console.error('显示格式指南失败:', error);
        showErrorMessage('显示格式指南失败: ' + error.message);
    }
}

// 加载列名映射配置
async function loadColumnMappingConfig() {
    try {
        const response = await fetch('/api/config/column_mappings');
        const result = await response.json();

        if (response.ok && result.success) {
            updateFormatInfo(result.config);
            return result.config;
        } else {
            console.error('加载列名映射配置失败:', result.error || '未知错误');
            return null;
        }
    } catch (error) {
        console.error('加载列名映射配置失败:', error);
        return null;
    }
}

// 更新格式信息显示
function updateFormatInfo(config) {
    if (!config) return;

    // 更新必需列列表
    const requiredColumnsElement = document.getElementById('format-required-columns');
    if (requiredColumnsElement) {
        requiredColumnsElement.innerHTML = '';
        config.required_columns.forEach(column => {
            const tag = document.createElement('span');
            tag.className = 'column-tag';
            tag.textContent = column;
            requiredColumnsElement.appendChild(tag);
        });
    }
}

// 更新文件统计信息
function updateFileStats(files) {
    const totalFiles = files.length;
    const totalRecords = files.reduce((sum, file) => sum + (file.record_count || 0), 0);
    const totalSize = files.reduce((sum, file) => sum + (file.file_size || 0), 0);
    const missingFiles = files.filter(file => !file.exists).length;

    const totalFilesEl = document.getElementById('total-files');
    const totalRecordsEl = document.getElementById('total-records');
    const totalSizeEl = document.getElementById('total-size');
    const missingFilesEl = document.getElementById('missing-files');

    if (totalFilesEl) totalFilesEl.textContent = totalFiles;
    if (totalRecordsEl) totalRecordsEl.textContent = totalRecords;
    if (totalSizeEl) totalSizeEl.textContent = formatFileSize(totalSize);
    if (missingFilesEl) {
        missingFilesEl.textContent = missingFiles;
        missingFilesEl.parentElement.style.color = missingFiles > 0 ? '#dc3545' : '#28a745';
    }
}

// 显示文件统计信息
function showFileStats() {
    const fileStats = document.getElementById('file-stats');
    if (fileStats) {
        fileStats.style.display = 'flex';
    }
}

// 强制显示文件统计信息（即使没有文件）
function forceShowFileStats() {
    showFileStats();
}

// 隐藏文件统计信息
function hideFileStats() {
    const fileStats = document.getElementById('file-stats');
    if (fileStats) {
        fileStats.style.display = 'none';
    }
}

// 更新批量操作按钮状态
function updateBatchButtons() {
    const checkboxes = document.querySelectorAll('.file-checkbox:checked');
    const selectedCount = checkboxes.length;

    const batchPreviewBtn = document.getElementById('batch-preview-btn');
    const batchDownloadBtn = document.getElementById('batch-download-btn');
    const batchDeleteBtn = document.getElementById('batch-delete-btn');

    if (selectedCount > 0) {
        if (batchPreviewBtn) {
            batchPreviewBtn.style.display = 'inline-block';
            batchPreviewBtn.disabled = false;
        }
        if (batchDownloadBtn) {
            batchDownloadBtn.style.display = 'inline-block';
            batchDownloadBtn.disabled = false;
        }
        if (batchDeleteBtn) {
            batchDeleteBtn.style.display = 'inline-block';
            batchDeleteBtn.disabled = false;
        }
    } else {
        if (batchPreviewBtn) batchPreviewBtn.style.display = 'none';
        if (batchDownloadBtn) batchDownloadBtn.style.display = 'none';
        if (batchDeleteBtn) batchDeleteBtn.style.display = 'none';
    }

    // 更新选中数量显示
    updateSelectedCount();
}

// 批量预览文件
async function batchPreviewFiles() {
    const selectedFiles = getSelectedFiles();
    if (selectedFiles.length === 0) {
        showErrorMessage('请先选择要预览的文件');
        return;
    }

    // 创建批量预览模态框
    const modalId = 'batch-preview-modal';
    let modal = document.getElementById(modalId);

    if (!modal) {
        modal = document.createElement('div');
        modal.id = modalId;
        modal.className = 'modal';
        document.body.appendChild(modal);
    }

    modal.innerHTML = `
        <div class="modal-content large">
            <div class="modal-header">
                <h3>批量预览 - ${selectedFiles.length} 个文件</h3>
                <span class="close" onclick="document.getElementById('${modalId}').style.display='none'">&times;</span>
            </div>
            <div class="modal-body">
                <div class="batch-preview-container" id="batch-preview-container">
                    <p>正在加载预览...</p>
                </div>
            </div>
        </div>
    `;

    modal.style.display = 'block';

    // 加载每个文件的预览
    const container = document.getElementById('batch-preview-container');
    container.innerHTML = '';

    for (const fileId of selectedFiles) {
        try {
            const response = await fetch(`/api/pdf/preview/${fileId}`);
            const result = await response.json();

            if (response.ok && result.preview_data) {
                const fileDiv = document.createElement('div');
                fileDiv.className = 'batch-file-preview';
                fileDiv.innerHTML = `<h4>文件: ${fileId}</h4>`;

                displayMultiTablePreview(result.preview_data, fileDiv);
                container.appendChild(fileDiv);

                // 添加分隔符
                if (fileId !== selectedFiles[selectedFiles.length - 1]) {
                    const separator = document.createElement('hr');
                    separator.style.margin = '30px 0';
                    container.appendChild(separator);
                }
            }
        } catch (error) {
            console.error(`预览文件 ${fileId} 失败:`, error);
        }
    }
}

// 批量下载文件
function batchDownloadFiles() {
    const selectedFiles = getSelectedFiles();
    if (selectedFiles.length === 0) {
        showErrorMessage('请先选择要下载的文件');
        return;
    }

    if (confirm(`确定要下载 ${selectedFiles.length} 个文件吗？`)) {
        selectedFiles.forEach((fileId, index) => {
            setTimeout(() => {
                downloadOrder(fileId);
            }, index * 500); // 延迟下载避免浏览器阻止
        });

        showSuccessMessage(`开始下载 ${selectedFiles.length} 个文件`);
    }
}

// 批量删除文件
async function batchDeleteFiles() {
    const selectedFiles = getSelectedFiles();
    if (selectedFiles.length === 0) {
        showErrorMessage('请先选择要删除的文件');
        return;
    }

    if (confirm(`确定要删除 ${selectedFiles.length} 个文件吗？此操作不可撤销！`)) {
        showLoading();
        let successCount = 0;
        let failCount = 0;

        for (const fileId of selectedFiles) {
            try {
                const response = await fetch(`/api/pdf/delete_converted/${fileId}`, {
                    method: 'DELETE'
                });

                if (response.ok) {
                    successCount++;
                } else {
                    failCount++;
                }
            } catch (error) {
                failCount++;
                console.error(`删除文件 ${fileId} 失败:`, error);
            }
        }

        hideLoading();

        if (successCount > 0) {
            showSuccessMessage(`成功删除 ${successCount} 个文件${failCount > 0 ? `，${failCount} 个文件删除失败` : ''}`);
            loadConvertedFiles(); // 刷新文件列表
            loadOrderFiles(); // 刷新订单核对页面的文件列表
        } else {
            showErrorMessage('删除失败');
        }
    }
}

// 获取选中的文件ID列表
function getSelectedFiles() {
    const checkboxes = document.querySelectorAll('.file-checkbox:checked');
    return Array.from(checkboxes).map(cb => cb.dataset.fileId);
}
// 全选/取消全选功能
function toggleSelectAll() {
    const selectAllCheckbox = document.getElementById('select-all-checkbox');
    const fileCheckboxes = document.querySelectorAll('.file-checkbox');

    fileCheckboxes.forEach(checkbox => {
        checkbox.checked = selectAllCheckbox.checked;
        const fileItem = checkbox.closest('.file-item');
        fileItem.classList.toggle('selected', checkbox.checked);
    });

    updateBatchButtons();
    updateSelectedCount();
}

// 更新选中文件数量显示
function updateSelectedCount() {
    const selectedCount = document.querySelectorAll('.file-checkbox:checked').length;
    const totalCount = document.querySelectorAll('.file-checkbox').length;
    const selectedCountEl = document.getElementById('selected-count');
    const selectAllCheckbox = document.getElementById('select-all-checkbox');

    if (selectedCountEl) {
        selectedCountEl.textContent = `已选择 ${selectedCount} 个文件`;
    }

    // 更新全选复选框状态
    if (selectAllCheckbox) {
        if (selectedCount === 0) {
            selectAllCheckbox.indeterminate = false;
            selectAllCheckbox.checked = false;
        } else if (selectedCount === totalCount) {
            selectAllCheckbox.indeterminate = false;
            selectAllCheckbox.checked = true;
        } else {
            selectAllCheckbox.indeterminate = true;
        }
    }
}

// 显示全选控制
function showSelectAllContainer() {
    const container = document.getElementById('select-all-container');
    if (container) {
        container.style.display = 'flex';
    }
}

// 隐藏全选控制
function hideSelectAllContainer() {
    const container = document.getElementById('select-all-container');
    if (container) {
        container.style.display = 'none';
    }
}