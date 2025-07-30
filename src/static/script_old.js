// 全局变量
let currentFileId = null;
let currentFile = null;

// DOM元素
const uploadSection = document.getElementById('upload-section');
const progressSection = document.getElementById('progress-section');
const previewSection = document.getElementById('preview-section');
const errorSection = document.getElementById('error-section');
const loadingOverlay = document.getElementById('loading-overlay');

const uploadArea = document.getElementById('upload-area');
const fileInput = document.getElementById('file-input');
const selectFileBtn = document.getElementById('select-file-btn');
const fileInfo = document.getElementById('file-info');
const fileName = document.getElementById('file-name');
const fileSize = document.getElementById('file-size');
const changeFileBtn = document.getElementById('change-file-btn');
const uploadBtn = document.getElementById('upload-btn');

const progressFill = document.getElementById('progress-fill');
const stepUpload = document.getElementById('step-upload');
const stepParse = document.getElementById('step-parse');
const stepConvert = document.getElementById('step-convert');
const stepComplete = document.getElementById('step-complete');

const conversionSummary = document.getElementById('conversion-summary');
const tablesContainer = document.getElementById('tables-container');
const downloadBtn = document.getElementById('download-btn');
const newConversionBtn = document.getElementById('new-conversion-btn');

const errorMessage = document.getElementById('error-message');
const retryBtn = document.getElementById('retry-btn');

// 工具函数
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

function showSection(section) {
    document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
    section.classList.add('active');
}

function showLoading() {
    loadingOverlay.style.display = 'flex';
}

function hideLoading() {
    loadingOverlay.style.display = 'none';
}

function showError(message) {
    errorMessage.textContent = message;
    showSection(errorSection);
    hideLoading();
}

function updateProgress(percentage, activeStep) {
    progressFill.style.width = percentage + '%';
    
    // 重置所有步骤
    [stepUpload, stepParse, stepConvert, stepComplete].forEach(step => {
        step.classList.remove('active', 'completed');
    });
    
    // 设置活动步骤
    if (activeStep) {
        activeStep.classList.add('active');
    }
    
    // 设置已完成的步骤
    const steps = [stepUpload, stepParse, stepConvert, stepComplete];
    const currentIndex = steps.indexOf(activeStep);
    for (let i = 0; i < currentIndex; i++) {
        steps[i].classList.add('completed');
    }
}

// 文件处理函数
function handleFileSelect(file) {
    if (!file) return;
    
    // 验证文件类型
    if (file.type !== 'application/pdf') {
        showError('请选择PDF文件');
        return;
    }
    
    // 验证文件大小 (50MB)
    if (file.size > 50 * 1024 * 1024) {
        showError('文件大小不能超过50MB');
        return;
    }
    
    currentFile = file;
    fileName.textContent = file.name;
    fileSize.textContent = formatFileSize(file.size);
    
    uploadArea.style.display = 'none';
    fileInfo.style.display = 'block';
}

function resetFileSelection() {
    currentFile = null;
    currentFileId = null;
    fileInput.value = '';
    uploadArea.style.display = 'block';
    fileInfo.style.display = 'none';
}

// API调用函数
async function uploadFile(file) {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await fetch('/api/pdf/upload', {
        method: 'POST',
        body: formData
    });
    
    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.error || '上传失败');
    }
    
    return await response.json();
}

async function convertPdf(fileId) {
    const response = await fetch(`/api/pdf/convert/${fileId}`, {
        method: 'POST'
    });
    
    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.error || '转换失败');
    }
    
    return await response.json();
}

async function downloadFile(fileId) {
    const response = await fetch(`/api/pdf/download/${fileId}`);
    
    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.error || '下载失败');
    }
    
    // 创建下载链接
    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.style.display = 'none';
    a.href = url;
    a.download = `converted_${new Date().toISOString().slice(0, 19).replace(/:/g, '-')}.xlsx`;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
}

// 预览显示函数
function displayPreview(data) {
    // 显示转换摘要
    conversionSummary.innerHTML = `
        <div class="summary-item">
            <span class="summary-label">转换状态:</span>
            <span class="summary-value">成功</span>
        </div>
        <div class="summary-item">
            <span class="summary-label">检测到的表格数量:</span>
            <span class="summary-value">${data.tables_count}</span>
        </div>
        <div class="summary-item">
            <span class="summary-label">文件ID:</span>
            <span class="summary-value">${data.file_id}</span>
        </div>
    `;
    
    // 显示表格预览
    tablesContainer.innerHTML = '';
    
    data.preview_data.forEach((table, index) => {
        const tableDiv = document.createElement('div');
        tableDiv.className = 'table-preview';
        
        let tableHtml = `
            <div class="table-header">
                表格 ${table.table_index} (页面 ${table.page}) - 准确率: ${(table.accuracy * 100).toFixed(1)}%
            </div>
            <div class="table-content">
                <table class="preview-table">
                    <thead>
                        <tr>
        `;
        
        // 添加表头
        table.columns.forEach(col => {
            tableHtml += `<th>${col || '未命名列'}</th>`;
        });
        tableHtml += '</tr></thead><tbody>';
        
        // 添加数据行
        table.data.forEach(row => {
            tableHtml += '<tr>';
            row.forEach(cell => {
                tableHtml += `<td>${cell || ''}</td>`;
            });
            tableHtml += '</tr>';
        });
        
        tableHtml += `
                    </tbody>
                </table>
            </div>
            <div class="table-info">
                总行数: ${table.total_rows} | 总列数: ${table.total_columns} | 
                ${table.data.length < table.total_rows ? `显示前 ${table.data.length} 行` : '显示全部数据'}
            </div>
        `;
        
        tableDiv.innerHTML = tableHtml;
        tablesContainer.appendChild(tableDiv);
    });
}

// 主要处理流程
async function processFile() {
    if (!currentFile) return;
    
    try {
        showSection(progressSection);
        
        // 步骤1: 上传文件
        updateProgress(25, stepUpload);
        const uploadResult = await uploadFile(currentFile);
        currentFileId = uploadResult.file_id;
        
        // 步骤2: 解析PDF
        updateProgress(50, stepParse);
        await new Promise(resolve => setTimeout(resolve, 1000)); // 模拟处理时间
        
        // 步骤3: 转换Excel
        updateProgress(75, stepConvert);
        const convertResult = await convertPdf(currentFileId);
        
        // 步骤4: 完成
        updateProgress(100, stepComplete);
        await new Promise(resolve => setTimeout(resolve, 500));
        
        // 显示预览
        displayPreview(convertResult);
        showSection(previewSection);
        
    } catch (error) {
        console.error('处理失败:', error);
        showError(error.message);
    }
}

// 事件监听器
document.addEventListener('DOMContentLoaded', function() {
    // 文件选择事件
    selectFileBtn.addEventListener('click', () => {
        fileInput.click();
    });
    
    uploadArea.addEventListener('click', () => {
        fileInput.click();
    });
    
    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            handleFileSelect(e.target.files[0]);
        }
    });
    
    // 拖拽事件
    uploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadArea.classList.add('dragover');
    });
    
    uploadArea.addEventListener('dragleave', (e) => {
        e.preventDefault();
        uploadArea.classList.remove('dragover');
    });
    
    uploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadArea.classList.remove('dragover');
        
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            handleFileSelect(files[0]);
        }
    });
    
    // 按钮事件
    changeFileBtn.addEventListener('click', resetFileSelection);
    uploadBtn.addEventListener('click', processFile);
    
    downloadBtn.addEventListener('click', async () => {
        if (currentFileId) {
            try {
                showLoading();
                await downloadFile(currentFileId);
                hideLoading();
            } catch (error) {
                hideLoading();
                showError('下载失败: ' + error.message);
            }
        }
    });
    
    newConversionBtn.addEventListener('click', () => {
        resetFileSelection();
        showSection(uploadSection);
    });
    
    retryBtn.addEventListener('click', () => {
        if (currentFile) {
            processFile();
        } else {
            resetFileSelection();
            showSection(uploadSection);
        }
    });
});

// 防止页面刷新时丢失拖拽事件
window.addEventListener('dragover', (e) => {
    e.preventDefault();
});

window.addEventListener('drop', (e) => {
    e.preventDefault();
});

