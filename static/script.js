// 基础URL配置
const BASE_URL = '/api';

// DOM元素
const loading = document.getElementById('loading');
const loadingText = document.getElementById('loadingText');
const resultCard = document.getElementById('resultCard');
const resultContent = document.getElementById('resultContent');

// 单张图片对比元素
const originalImage = document.getElementById('originalImage');
const compareImage = document.getElementById('compareImage');
const originalImagePreview = document.getElementById('originalImagePreview');
const compareImagePreview = document.getElementById('compareImagePreview');
const compareBtn = document.getElementById('compareBtn');
const resetBtn = document.getElementById('resetBtn');

// 多张图片对比元素
const multipleOriginalImage = document.getElementById('multipleOriginalImage');
const multipleCompareImages = document.getElementById('multipleCompareImages');
const multipleOriginalImagePreview = document.getElementById('multipleOriginalImagePreview');
const multipleCompareImagesPreview = document.getElementById('multipleCompareImagesPreview');
const multipleCompareBtn = document.getElementById('multipleCompareBtn');
const multipleResetBtn = document.getElementById('multipleResetBtn');

// AI分析元素
const llmOriginalImage = document.getElementById('llmOriginalImage');
const llmCompareImage = document.getElementById('llmCompareImage');
const llmOriginalImagePreview = document.getElementById('llmOriginalImagePreview');
const llmCompareImagePreview = document.getElementById('llmCompareImagePreview');
const userQuestion = document.getElementById('userQuestion');
const llmCompareBtn = document.getElementById('llmCompareBtn');
const llmResetBtn = document.getElementById('llmResetBtn');

// 存储已上传的图片数据
let multipleImagesData = [];

// 初始化事件监听
function initEventListeners() {
    // 单张对比事件监听
    originalImage.addEventListener('change', handleImageUpload.bind(null, originalImagePreview));
    compareImage.addEventListener('change', handleImageUpload.bind(null, compareImagePreview));
    compareBtn.addEventListener('click', handleSingleCompare);
    resetBtn.addEventListener('click', resetSingleCompare);

    // 多张对比事件监听
    multipleOriginalImage.addEventListener('change', handleImageUpload.bind(null, multipleOriginalImagePreview));
    multipleCompareImages.addEventListener('change', handleMultipleImagesUpload);
    multipleCompareBtn.addEventListener('click', handleMultipleCompare);
    multipleResetBtn.addEventListener('click', resetMultipleCompare);

    // AI分析事件监听
    llmOriginalImage.addEventListener('change', handleImageUpload.bind(null, llmOriginalImagePreview));
    llmCompareImage.addEventListener('change', handleImageUpload.bind(null, llmCompareImagePreview));
    llmCompareBtn.addEventListener('click', handleLLMCompare);
    llmResetBtn.addEventListener('click', resetLLMCompare);
}

// 处理图片上传和预览
function handleImageUpload(previewElement, event) {
    const file = event.target.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = function(e) {
            const img = previewElement.querySelector('img');
            img.src = e.target.result;
            previewElement.classList.add('has-image');
            
            // 存储图片数据到预览元素的dataset中
            previewElement.dataset.imageData = e.target.result;
        };
        reader.readAsDataURL(file);
    }
}

// 处理多张图片上传
function handleMultipleImagesUpload(event) {
    const files = event.target.files;
    if (files) {
        for (let i = 0; i < files.length; i++) {
            const file = files[i];
            const reader = new FileReader();
            const index = multipleImagesData.length;
            
            reader.onload = function(e) {
                // 存储图片数据
                multipleImagesData.push({
                    file: file,
                    dataUrl: e.target.result
                });
                
                // 创建预览元素
                const previewItem = document.createElement('div');
                previewItem.className = 'multiple-preview-item';
                previewItem.dataset.index = index;
                
                const img = document.createElement('img');
                img.src = e.target.result;
                
                const removeBtn = document.createElement('button');
                removeBtn.className = 'remove-btn';
                removeBtn.textContent = '×';
                removeBtn.addEventListener('click', function() {
                    const idx = parseInt(previewItem.dataset.index);
                    multipleImagesData.splice(idx, 1);
                    previewItem.remove();
                    // 更新索引
                    updateMultiplePreviewIndices();
                });
                
                previewItem.appendChild(img);
                previewItem.appendChild(removeBtn);
                multipleCompareImagesPreview.appendChild(previewItem);
            };
            
            reader.readAsDataURL(file);
        }
    }
    
    // 清空input以允许选择相同文件
    event.target.value = '';
}

// 更新多张预览图的索引
function updateMultiplePreviewIndices() {
    const previewItems = multipleCompareImagesPreview.querySelectorAll('.multiple-preview-item');
    previewItems.forEach((item, index) => {
        item.dataset.index = index;
    });
}

// 显示加载状态
function showLoading(text = '处理中，请稍候...') {
    loadingText.textContent = text;
    loading.style.display = 'flex';
}

// 隐藏加载状态
function hideLoading() {
    loading.style.display = 'none';
}

// 显示结果
function showResult(html) {
    resultContent.innerHTML = html;
    resultCard.style.display = 'block';
    // 滚动到结果区域
    resultCard.scrollIntoView({ behavior: 'smooth' });
}

// 显示错误
function showError(message) {
    const errorHtml = `
        <div class="error-message">
            <h3>处理失败</h3>
            <p>${message}</p>
        </div>
    `;
    showResult(errorHtml);
}

// 将DataURL转换为Base64
function dataUrlToBase64(dataUrl) {
    return dataUrl.split(',')[1];
}

// 单张图片对比
async function handleSingleCompare() {
    // 验证图片是否已上传
    if (!originalImagePreview.classList.contains('has-image') || 
        !compareImagePreview.classList.contains('has-image')) {
        alert('请先上传原图和对比图');
        return;
    }
    
    showLoading('正在计算相似度...');
    
    try {
        // 准备请求数据
        const originalData = dataUrlToBase64(originalImagePreview.dataset.imageData);
        const compareData = dataUrlToBase64(compareImagePreview.dataset.imageData);
        
        const requestData = {
            original_image: { base64: originalData },
            compare_image: { base64: compareData }
        };
        
        // 调用API
        const response = await axios.post(`${BASE_URL}/image/similarity/single`, requestData);
        const similarity = response.data.similarity;
        
        // 显示结果
        const resultHtml = `
            <div class="text-center">
                <div class="similarity-score">${(similarity * 100).toFixed(1)}%</div>
                <p class="text-muted">两张图片的相似度</p>
                <div class="similarity-bar">
                    <div class="similarity-progress" style="width: ${similarity * 100}%"></div>
                </div>
                <p>${getSimilarityDescription(similarity)}</p>
            </div>
        `;
        
        showResult(resultHtml);
    } catch (error) {
        console.error('比较失败:', error);
        showError(error.response?.data?.error || '计算相似度时发生错误，请重试');
    } finally {
        hideLoading();
    }
}

// 多张图片对比
async function handleMultipleCompare() {
    // 验证图片是否已上传
    if (!multipleOriginalImagePreview.classList.contains('has-image') || 
        multipleImagesData.length === 0) {
        alert('请先上传原图和至少一张对比图');
        return;
    }
    
    showLoading('正在计算多张图片相似度...');
    
    try {
        // 准备请求数据
        const originalData = dataUrlToBase64(multipleOriginalImagePreview.dataset.imageData);
        
        const compareImages = multipleImagesData.map(img => ({
            image: { base64: dataUrlToBase64(img.dataUrl) }
        }));
        
        const requestData = {
            original_image: { base64: originalData },
            compare_images: compareImages
        };
        
        // 调用API
        const response = await axios.post(`${BASE_URL}/image/similarity/multiple`, requestData);
        const results = response.data.results;
        
        // 显示结果
        let resultHtml = `
            <h3 class="text-center mb-4">相似度比较结果</h3>
            <div class="results-container">
        `;
        
        // 按照相似度降序排序
        const sortedResults = [...results].sort((a, b) => (b.similarity || 0) - (a.similarity || 0));
        
        sortedResults.forEach((result, index) => {
            const originalIndex = result.index;
            if (result.error) {
                resultHtml += `
                    <div class="multiple-result-item">
                        <div class="result-flex">
                            <div class="result-info">
                                <h5>图片 ${originalIndex + 1}</h5>
                                <p class="text-danger">错误: ${result.error}</p>
                            </div>
                        </div>
                    </div>
                `;
            } else {
                const similarity = result.similarity;
                resultHtml += `
                    <div class="multiple-result-item">
                        <div class="result-flex">
                            <img src="${multipleImagesData[originalIndex].dataUrl}" alt="对比图 ${originalIndex + 1}">
                            <div class="result-info">
                                <h5>图片 ${originalIndex + 1}</h5>
                                <div class="similarity-bar">
                                    <div class="similarity-progress" style="width: ${similarity * 100}%"></div>
                                </div>
                                <p class="text-center font-weight-bold">${(similarity * 100).toFixed(1)}%</p>
                                <p class="text-muted text-center">${getSimilarityDescription(similarity)}</p>
                            </div>
                        </div>
                    </div>
                `;
            }
        });
        
        resultHtml += `</div>`;
        showResult(resultHtml);
    } catch (error) {
        console.error('多张图片比较失败:', error);
        showError(error.response?.data?.error || '计算相似度时发生错误，请重试');
    } finally {
        hideLoading();
    }
}

// 结合AI的图片分析
async function handleLLMCompare() {
    // 验证图片和问题
    if (!llmOriginalImagePreview.classList.contains('has-image') || 
        !llmCompareImagePreview.classList.contains('has-image')) {
        alert('请先上传原图和对比图');
        return;
    }
    
    if (!userQuestion.value.trim()) {
        alert('请输入您的问题');
        return;
    }
    
    showLoading('正在分析图片并生成回答...');
    
    try {
        // 准备请求数据
        const originalData = dataUrlToBase64(llmOriginalImagePreview.dataset.imageData);
        const compareData = dataUrlToBase64(llmCompareImagePreview.dataset.imageData);
        
        const requestData = {
            original_image: { base64: originalData },
            compare_image: { base64: compareData },
            question: userQuestion.value.trim()
        };
        
        // 调用API
        const response = await axios.post(`${BASE_URL}/image/similarity/llm`, requestData);
        const data = response.data;
        
        // 显示结果
        const resultHtml = `
            <div>
                <h3>您的问题：${userQuestion.value}</h3>
                
                <div class="row mt-4 mb-4">
                    <div class="col-md-6">
                        <h4>原图分析</h4>
                        <div class="image-description">
                            ${data.original_image_description}
                        </div>
                    </div>
                    <div class="col-md-6">
                        <h4>对比图分析</h4>
                        <div class="image-description">
                            ${data.compare_image_description}
                        </div>
                    </div>
                </div>
                
                <div class="text-center mb-4">
                    <div class="similarity-score">${(data.similarity * 100).toFixed(1)}%</div>
                    <p class="text-muted">两张图片的相似度</p>
                    <div class="similarity-bar">
                        <div class="similarity-progress" style="width: ${data.similarity * 100}%"></div>
                    </div>
                </div>
                
                <h4>AI分析结果</h4>
                <div class="llm-response">
                    ${data.llm_response}
                </div>
            </div>
        `;
        
        showResult(resultHtml);
    } catch (error) {
        console.error('AI分析失败:', error);
        showError(error.response?.data?.error || '分析过程中发生错误，请重试');
    } finally {
        hideLoading();
    }
}

// 获取相似度描述
function getSimilarityDescription(similarity) {
    if (similarity >= 0.9) return '非常相似';
    if (similarity >= 0.8) return '高度相似';
    if (similarity >= 0.7) return '较为相似';
    if (similarity >= 0.6) return '一般相似';
    if (similarity >= 0.5) return '略有相似';
    return '不太相似';
}

// 重置单张对比
function resetSingleCompare() {
    originalImage.value = '';
    compareImage.value = '';
    originalImagePreview.classList.remove('has-image');
    compareImagePreview.classList.remove('has-image');
    originalImagePreview.querySelector('img').src = '';
    compareImagePreview.querySelector('img').src = '';
    delete originalImagePreview.dataset.imageData;
    delete compareImagePreview.dataset.imageData;
}

// 重置多张对比
function resetMultipleCompare() {
    multipleOriginalImage.value = '';
    multipleCompareImages.value = '';
    multipleOriginalImagePreview.classList.remove('has-image');
    multipleOriginalImagePreview.querySelector('img').src = '';
    delete multipleOriginalImagePreview.dataset.imageData;
    
    multipleCompareImagesPreview.innerHTML = '';
    multipleImagesData = [];
}

// 重置AI分析
function resetLLMCompare() {
    llmOriginalImage.value = '';
    llmCompareImage.value = '';
    userQuestion.value = '';
    llmOriginalImagePreview.classList.remove('has-image');
    llmCompareImagePreview.classList.remove('has-image');
    llmOriginalImagePreview.querySelector('img').src = '';
    llmCompareImagePreview.querySelector('img').src = '';
    delete llmOriginalImagePreview.dataset.imageData;
    delete llmCompareImagePreview.dataset.imageData;
}

// 页面加载完成后初始化
window.addEventListener('DOMContentLoaded', initEventListeners);