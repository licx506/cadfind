document.addEventListener('DOMContentLoaded', function() {
    const searchBtn = document.getElementById('search-btn');
    const keywordInput = document.getElementById('keyword');
    const searchStatus = document.getElementById('search-status');
    const resultsBody = document.getElementById('results-body');
    const previewContainer = document.getElementById('preview-container');

    const API_BASE_URL = 'http://localhost:5000/api';

    searchBtn.addEventListener('click', performSearch);
    keywordInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            performSearch();
        }
    });

    function performSearch() {
        const keyword = keywordInput.value.trim();
        if (!keyword) {
            alert('请输入搜索关键字');
            return;
        }

        searchStatus.textContent = '正在搜索...';
        resultsBody.innerHTML = '';

        // 创建倒计时窗口
        const countdownModal = createCountdownModal();
        document.body.appendChild(countdownModal);

        let countdown = 20;
        const countdownInterval = setInterval(() => {
            countdown--;
            document.getElementById('countdown-timer').textContent = countdown;
            if (countdown <= 0) {
                clearInterval(countdownInterval);
                document.body.removeChild(countdownModal);
                searchStatus.textContent = '搜索超时，返回已查询的结果或提示未找到匹配的结果';
            }
        }, 1000);

        fetch(`${API_BASE_URL}/search?keyword=${encodeURIComponent(keyword)}`)
            .then(response => {
                clearInterval(countdownInterval);
                document.body.removeChild(countdownModal);
                if (!response.ok) {
                    throw new Error('搜索请求失败');
                }
                return response.json();
            })
            .then(data => {
                if (data.results && data.results.length > 0) {
                    searchStatus.textContent = `找到 ${data.results.length} 条结果`;
                    displayResults(data.results);
                } else {
                    searchStatus.textContent = '没有找到匹配的结果';
                    resultsBody.innerHTML = '<tr><td colspan="3" class="no-results">没有找到匹配的结果</td></tr>';
                }
            })
            .catch(error => {
                searchStatus.textContent = '搜索出错';
                console.error('搜索出错:', error);
                alert('搜索出错: ' + error.message);
            });
    }

    function createCountdownModal() {
        const modal = document.createElement('div');
        modal.className = 'modal';

        const modalContent = document.createElement('div');
        modalContent.className = 'modal-content';

        const title = document.createElement('h3');
        title.textContent = '正在查询，请稍候...';

        const timer = document.createElement('p');
        timer.id = 'countdown-timer';
        timer.textContent = '20';

        modalContent.appendChild(title);
        modalContent.appendChild(timer);
        modal.appendChild(modalContent);

        return modal;
    }

    function displayResults(results) {
        resultsBody.innerHTML = '';
        results.forEach(result => {
            const row = document.createElement('tr');

            const filenameCell = document.createElement('td');
            filenameCell.textContent = result.filename;

            const rowNumberCell = document.createElement('td');
            rowNumberCell.textContent = result.row_number;

            const actionsCell = document.createElement('td');

            const downloadBtn = document.createElement('button');
            downloadBtn.className = 'action-btn download-btn';
            downloadBtn.textContent = '下载CAD文件';
            downloadBtn.addEventListener('click', () => {
                downloadCadFile(result.filename);
            });

            const previewBtn = document.createElement('button');
            previewBtn.className = 'action-btn preview-btn';
            previewBtn.textContent = '查看详情';
            previewBtn.addEventListener('click', () => {
                showDetails(result);
            });

            actionsCell.appendChild(downloadBtn);
            actionsCell.appendChild(document.createTextNode(' '));
            actionsCell.appendChild(previewBtn);

            row.appendChild(filenameCell);
            row.appendChild(rowNumberCell);
            row.appendChild(actionsCell);

            resultsBody.appendChild(row);
        });
    }

    function downloadCadFile(filename) {
        window.location.href = `${API_BASE_URL}/download/${encodeURIComponent(filename)}`;
    }

    function showDetails(result) {
        const statusDiv = document.getElementById('search-status');
        statusDiv.textContent = `正在获取 ${result.filename} 的详情...`;

        fetch(`${API_BASE_URL}/details?filename=${encodeURIComponent(result.filename)}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error('获取详情请求失败');
                }
                return response.json();
            })
            .then(data => {
                if (data.error) {
                    statusDiv.textContent = `获取详情失败: ${data.error}`;
                    return;
                }

                statusDiv.textContent = `成功获取 ${result.filename} 的详情`;

                const modal = document.createElement('div');
                modal.className = 'modal';

                const modalContent = document.createElement('div');
                modalContent.className = 'modal-content fixed-size';

                const closeButton = document.createElement('span');
                closeButton.className = 'close-button';
                closeButton.textContent = '×';
                closeButton.addEventListener('click', () => {
                    document.body.removeChild(modal);
                });

                const title = document.createElement('h3');
                title.textContent = `文件: ${result.filename}`;

                const keywordList = document.createElement('ul');
                keywordList.className = 'keyword-list';

                const keywords = data.details.keywords || [];
                if (keywords.length > 0) {
                    keywords.forEach(keyword => {
                        const listItem = document.createElement('li');
                        listItem.textContent = keyword;
                        keywordList.appendChild(listItem);
                    });
                } else {
                    const noKeywords = document.createElement('p');
                    noKeywords.textContent = '没有找到相关关键字';
                    modalContent.appendChild(noKeywords);
                }

                modalContent.appendChild(closeButton);
                modalContent.appendChild(title);
                modalContent.appendChild(keywordList);
                modal.appendChild(modalContent);
                document.body.appendChild(modal);
            })
            .catch(error => {
                statusDiv.textContent = `获取详情失败: ${error.message}`;
                console.error('获取详情出错:', error);
            });
    }
});
